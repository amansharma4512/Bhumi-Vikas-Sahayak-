import json
import math
import re
import os
from collections import Counter

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RULES_JSONL_PATH = os.path.join(PROJECT_DIR, "data", "bhumi_vikas_rules.jsonl")

# Bilingual domain synonym dictionary to bridge Hindi and English legal terms
DOMAIN_SYNONYMS = {
    # Hindi to English mappings
    "सेटबैक": ["setback", "marginal", "open", "space", "fmos", "rmos", "smos"],
    "खुला": ["open", "space"],
    "सामने": ["front", "open", "space", "fmos"],
    "पीछे": ["rear", "open", "space", "rmos"],
    "बगल": ["side", "open", "space", "smos"],
    "आवासीय": ["residential", "dwelling", "residence"],
    "मकान": ["house", "building", "residential"],
    "सड़क": ["road", "street", "access", "width"],
    "चौड़ाई": ["width", "road"],
    "शुल्क": ["fee", "fees", "permission", "application"],
    "फीस": ["fee", "fees", "charge"],
    "अनुज्ञा": ["permission", "sanction", "approval"],
    "ऊंचाई": ["height", "clearance"],
    "बिजली": ["electric", "voltage", "overhead"],
    "विद्युत": ["electric", "voltage", "lines"],
    "फार्म": ["farm", "house", "agricultural"],
    "कृषि": ["agricultural", "farm"],
    "डीम्ड": ["deemed", "instant", "approval"],
    "तत्काल": ["instant", "deemed"],
    "विचलन": ["deviation", "sanctioned"],
    "प्लॉट": ["plot", "land", "area"],
    "भूखंड": ["plot", "land", "area"],
    "दुकान": ["shop", "commercial", "mercantile"],
    "वाणिज्यिक": ["commercial", "mercantile"],
    "तहखाना": ["basement"],
    "बेसमेंट": ["basement"],
    "लिफ्ट": ["lift", "elevator", "escalator"],
    "सीढ़ी": ["staircase", "tread", "riser"],
    "पार्किंग": ["parking", "garage"],
    "पेड़": ["tree", "plantation"],
    "वृक्षारोपण": ["plantation", "trees"],
    "वर्षा": ["rainwater", "harvesting"],
    "छत": ["roof", "rainwater"],
    "जल": ["water", "supply", "harvesting"],
    "बाउंड्री": ["boundary", "compound", "wall"],
    "अग्निशमन": ["fire", "safety"],
    "आग": ["fire", "safety"],
    # English keywords
    "gap": ["open", "space", "setback", "front", "rear", "side", "marginal", "fmos", "rmos"],
    "setback": ["front", "rear", "side", "open", "space", "marginal", "fmos", "rmos", "smos"],
    "front": ["front", "marginal", "open", "space", "fmos", "street", "road"],
    "rear": ["rear", "marginal", "open", "space", "rmos"],
    "side": ["side", "marginal", "open", "space", "smos"],
    "fmos": ["front", "marginal", "open", "space", "street"],
    "rmos": ["rear", "marginal", "open", "space"],
    "smos": ["side", "marginal", "open", "space"],
    "far": ["floor", "area", "ratio", "built", "up"],
    "floors": ["storey", "stories", "height", "far", "building"],
    "fees": ["fee", "charge", "application", "permission"],
    "fee": ["fees", "charge", "application", "permission"],
    "height": ["building", "height", "meters", "stories"],
    "stories": ["floors", "height", "high", "rise"],
    "electric": ["overhead", "voltage", "lines", "clearance"],
    "farm": ["farm", "house", "agricultural", "tree"],
}

def tokenize(text):
    text = text.lower()
    # Match words in English, Hindi/Devanagari, and numbers
    tokens = re.findall(r'[\w\u0900-\u097F]+', text)
    expanded = []
    for t in tokens:
        expanded.append(t)
        if t in DOMAIN_SYNONYMS:
            expanded.extend(DOMAIN_SYNONYMS[t])
    return expanded

class BM25Retriever:
    def __init__(self, jsonl_path=RULES_JSONL_PATH):
        self.rules = []
        self.doc_tokens = []
        self.doc_lens = []
        self.avg_dl = 0.0
        self.df = Counter()
        self.N = 0
        self.k1 = 1.5
        self.b = 0.75
        self.load_data(jsonl_path)

    def load_data(self, jsonl_path):
        self.rules = []
        self.doc_tokens = []
        self.doc_lens = []
        self.df = Counter()

        if not os.path.exists(jsonl_path):
            raise FileNotFoundError(f"Rules data not found at {jsonl_path}")

        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rule = json.loads(line)
                self.rules.append(rule)

                # Weight title, rule number, and inserted rules heavily
                inserted_text = " ".join([f"Rule {sub['rule_number']} {sub['title']}" for sub in rule.get("inserted_rules", [])])
                searchable_text = f"Rule {rule['rule_number']} {rule['title']} {rule['part']} {inserted_text} {rule['full_text']}"
                tokens = tokenize(searchable_text)

                self.doc_tokens.append(tokens)
                self.doc_lens.append(len(tokens))
                unique_tokens = set(tokens)
                for ut in unique_tokens:
                    self.df[ut] += 1

        self.N = len(self.rules)
        self.avg_dl = sum(self.doc_lens) / self.N if self.N > 0 else 1.0

    def get_idf(self, term):
        n = self.df.get(term, 0)
        return math.log(1.0 + (self.N - n + 0.5) / (n + 0.5))

    def search(self, query, top_k=3):
        # Direct rule number lookup if mentioned like "Rule 56", "Rule 12-A", "नियम 56"
        rule_num_match = re.search(r'(?:rule|नियम)\s*([0-9]+(?:\-[a-zA-Z]+|\([a-zA-Z0-9]+\)|[a-zA-Z])?)', query, re.IGNORECASE)
        forced_top = []
        if rule_num_match:
            target_num = rule_num_match.group(1).upper()
            for r in self.rules:
                if r["rule_number"].upper() == target_num:
                    forced_top.append((r, 999.0))
                else:
                    for sub in r.get("inserted_rules", []):
                        if sub["rule_number"].upper() == target_num:
                            forced_top.append((r, 990.0))

        q_tokens = tokenize(query)
        scores = [0.0] * self.N

        for token in q_tokens:
            idf = self.get_idf(token)
            for idx in range(self.N):
                tokens = self.doc_tokens[idx]
                tf = tokens.count(token)
                if tf > 0:
                    score = idf * (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * (self.doc_lens[idx] / self.avg_dl)))
                    scores[idx] += score

        ranked = sorted(range(self.N), key=lambda i: scores[i], reverse=True)
        results = []
        seen = set()

        # Add forced matches first
        for r, sc in forced_top:
            if r["rule_number"] not in seen:
                seen.add(r["rule_number"])
                results.append((r, sc))

        for idx in ranked:
            r = self.rules[idx]
            if r["rule_number"] not in seen:
                seen.add(r["rule_number"])
                results.append((r, scores[idx]))
            if len(results) >= top_k:
                break

        return results

def split_question(question_text):
    """
    Split complex multi-part questions into focused sub-questions.
    E.g.: 'My plot is 200 sq m on a 9 m road. How much gap do I leave at the front, how many floors can I build, and what fee do I pay?'
    """
    # Look for question marks, conjunctions, or numbered bullets
    sub_qs = []
    # If text contains multiple '?'
    parts = [p.strip() for p in re.split(r'[\?\;\n]+', question_text) if p.strip()]
    if len(parts) > 1:
        # Carry the context (e.g. plot area, road width) to each sub-question
        context = ""
        context_match = re.search(r'(\d+\s*(?:sq\s*m|वर्ग\s*मीटर|मीटर|m|meter)[\w\s,]+(?:road|सड़क|plot|भूखंड)?)', question_text, re.IGNORECASE)
        if context_match:
            context = context_match.group(1)

        for p in parts:
            if len(p) > 10:
                sub_qs.append(f"{context} {p}".strip())
    else:
        # Check comma or 'and' separated questions
        sub_clauses = re.split(r'(?i)(?:,\s*and\s*|,\s*aur\s*|,\s*तथा\s*|,\s*और\s*)', question_text)
        if len(sub_clauses) > 1 and any(re.search(r'(?i)\b(how|what|fee|gap|front|rear|floors|setback|कितना|क्या)\b', c) for c in sub_clauses[1:]):
            sub_qs = [c.strip() for c in sub_clauses if len(c.strip()) > 8]
        else:
            sub_qs = [question_text]

    return sub_qs if sub_qs else [question_text]

def retrieve_for_question(question_text, top_k=3):
    retriever = BM25Retriever()
    sub_questions = split_question(question_text)
    candidate_rules = {}

    for sq in sub_questions:
        res = retriever.search(sq, top_k=top_k)
        for r, score in res:
            r_num = r["rule_number"]
            if r_num not in candidate_rules or score > candidate_rules[r_num]["score"]:
                candidate_rules[r_num] = {
                    "rule": r,
                    "score": score,
                    "sub_question": sq
                }

    sorted_candidates = sorted(candidate_rules.values(), key=lambda x: x["score"], reverse=True)
    return [c["rule"] for c in sorted_candidates[:top_k]]

if __name__ == "__main__":
    test_q = "My plot is 200 sq m on a 9 m road. How much gap do I leave at the front, how many floors can I build, and what fee do I pay?"
    print(f"Testing question: {test_q}")
    candidates = retrieve_for_question(test_q, top_k=3)
    for c in candidates:
        print(f"Candidate: Rule {c['rule_number']} - {c['title']} (Pages: {c['page_range']})")
