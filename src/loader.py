import re
import json
import os

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
FULLTEXT_PATH = os.path.join(DATA_DIR, "bhumi_vikas_rules_fulltext_by_page.txt")
RULES_JSONL_PATH = os.path.join(DATA_DIR, "bhumi_vikas_rules.jsonl")
SAMPLE_JSONL_PATH = os.path.join(DATA_DIR, "bhumi_vikas_rules_sample.jsonl")
AMENDMENT_PATH = os.path.join(DATA_DIR, "amendment_overlay.json")

PARTS_RANGES = [
    (1, 5, "PART-I : GENERAL"),
    (6, 11, "PART - II : ORGANISATION AND ENFORCEMENT"),
    (12, 35, "PART-III : PERMISSION AND INSPECTION"),
    (36, 53, "PART-IV: DEVELOPMENT CONTROL"),
    (54, 105, "PART-V: GENERAL BUILDING REQUIREMENTS"),
]

def get_part_name(r_num_str):
    if r_num_str == "26-B":
        return "PART-III : PERMISSION AND INSPECTION"
    try:
        n = int(r_num_str)
        for start, end, part in PARTS_RANGES:
            if start <= n <= end:
                return part
    except ValueError:
        pass
    return "PART-V: GENERAL BUILDING REQUIREMENTS"

def clean_rule_text(text):
    # Remove running page headers e.g. "Rule 56 M.P. Bhumi Vikas Rules, 2012 78"
    text = re.sub(r'Rule\s+[\d\-A-Za-z]+\s+M\.P\.\s+Bhumi\s+Vikas\s+Rules,\s+2012\s+\d+', '', text, flags=re.IGNORECASE)
    # Remove OCR top artifacts like "fu;e 2 1"
    text = re.sub(r'fu;e\s+\d+\s+\d+', '', text)
    # Remove bottom-of-page footnote paragraphs
    text = re.sub(r'\n\s*\d+\s+(?:Ins\.|Subs\.|Inserted|Published|Added)\s+by\s+Notification[^\n]+(?:\n\s+[^\n]+)*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\n\s*\d+\s+Pubished\s+in[^\n]+(?:\n\s+[^\n]+)*', '', text, flags=re.IGNORECASE)
    # Remove standalone footnote superscript markers like "1[" or "2["
    text = re.sub(r'\b\d+\[', '', text)
    # Remove standalone footnote numbers at line ends or before brackets
    text = re.sub(r'\]\s*\d+\s*$', ']', text, flags=re.MULTILINE)
    # Normalize multiple newlines but preserve spacing and table structure
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def build_dataset():
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(FULLTEXT_PATH, "r", encoding="utf-8") as f:
        raw = f.read()

    pages_raw = raw.split("===== PDF page ")
    pages = {}
    for p in pages_raw:
        if not p.strip():
            continue
        lines = p.splitlines()
        pnum = int(lines[0].replace("=====", "").strip())
        ptext = "\n".join(lines[1:])
        pages[pnum] = ptext

    rule_keys = [str(i) for i in range(1, 27)] + ["26-B"] + [str(i) for i in range(27, 106)]

    rule_locations = []
    for idx, r_key in enumerate(rule_keys):
        if r_key == "26-B":
            pat = re.compile(r'(?:^|\n)\s*26-B\.\s+([^\n\r]+)', re.IGNORECASE)
        elif r_key == "37":
            pat = re.compile(r'(?:^|\n)\s*37\.\s*\(1\)\s*([^\n\r]+)', re.IGNORECASE)
        else:
            pat = re.compile(rf'(?:^|\n)\s*(?:\[?\d+\]?\s*|\d+\[\s*)?{r_key}\.\s+([^\n\r]+)')

        for pnum in sorted(pages.keys()):
            ptext = pages[pnum]
            m = pat.search(ptext)
            if m:
                title = m.group(1).strip()
                title = re.sub(r'^[–—\-\.\s]+', '', title)
                title = re.split(r'[\.\-–—]\s*(?:\(1\)|$|[A-Z])', title)[0].strip()
                rule_locations.append({
                    "rule_number": r_key,
                    "start_page": pnum,
                    "start_char": m.start(),
                    "title": title
                })
                break

    # Sub-rule mappings (inserted rules inside parent rule)
    inserted_rules_map = {
        "12": [{"rule_number": "12-A", "title": "Instant/Deemed Approval for Residential Plots up to 186 sqm", "page": 21}],
        "17": [{"rule_number": "17-a", "title": "Agricultural Tourist Facility in Agricultural Zones", "page": 34}],
        "25": [{"rule_number": "25(A)", "title": "Appeal and Revision", "page": 42}],
        "26": [{"rule_number": "26-A", "title": "Authorization of Architect/Structural Engineer", "page": 47}],
        "42": [{"rule_number": "42-A", "title": "Norms for Information Technology (IT/ITES/ESDM)", "page": 60}],
        "93": [
            {"rule_number": "93(a)", "title": "Dual Water Piping System", "page": 101},
            {"rule_number": "93(b)", "title": "Digital Communication Infrastructure", "page": 102}
        ]
    }

    rules_data = []
    for i, curr in enumerate(rule_locations):
        r_num = curr["rule_number"]
        spage = curr["start_page"]
        schar = curr["start_char"]

        if i + 1 < len(rule_locations):
            nxt = rule_locations[i+1]
            epage = nxt["start_page"]
            echar = nxt["start_char"]
        else:
            epage = 108
            echar = len(pages[108])

        if spage == epage:
            raw_text = pages[spage][schar:echar]
        else:
            parts = [pages[spage][schar:]]
            for p in range(spage + 1, epage):
                parts.append(pages[p])
            parts.append(pages[epage][:echar])
            raw_text = "\n".join(parts)

        cleaned_text = clean_rule_text(raw_text)
        part_name = get_part_name(r_num)
        inserted = inserted_rules_map.get(r_num, [])

        rule_obj = {
            "rule_number": r_num,
            "title": curr["title"],
            "part": part_name,
            "page_range": [spage, epage],
            "inserted_rules": inserted,
            "full_text": cleaned_text
        }
        rules_data.append(rule_obj)

    # Write bhumi_vikas_rules.jsonl
    with open(RULES_JSONL_PATH, "w", encoding="utf-8") as f:
        for r in rules_data:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Written {len(rules_data)} rules to {RULES_JSONL_PATH}")

    # Write sample rules (12, 17, 23, 52, 56)
    sample_rules = [r for r in rules_data if r["rule_number"] in ["12", "17", "23", "52", "56"]]
    with open(SAMPLE_JSONL_PATH, "w", encoding="utf-8") as f:
        for r in sample_rules:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Written {len(sample_rules)} sample rules to {SAMPLE_JSONL_PATH}")

    # Write amendment overlay
    amendment_overlay = {
        "amendment_date": "2026-08-28",
        "rule_id": "2(5)(c)",
        "source_url": "https://teamleaseregtech.com/updates/article/59469/government-of-madhya-pradesh-amendment-to-land-development-rules",
        "description": "Government of Madhya Pradesh Amendment to Land Development Rules regarding deemed building permissions and authority jurisdiction for plots up to 500 sq m.",
        "trigger_conditions": {
            "max_plot_size_sqm": 500.0,
            "rules": ["2(5)(c)", "2", "12", "12-A"]
        },
        "warning_en": "IMPORTANT NOTICE: Rule 2(5)(c) regarding plots up to 500 sq m was amended by the State Government on 28 August 2026. This amendment is not included in the consolidated March 2025 rulebook. Please confirm specific provisions from the 28 Aug 2026 notification before making a final determination.",
        "warning_hi": "महत्वपूर्ण सूचना: 500 वर्ग मीटर तक के भूखंडों के लिए नियम 2(5)(c) में राज्य सरकार द्वारा 28 अगस्त 2026 को संशोधन किया गया है। यह संशोधन 6 मार्च 2025 तक समेकित नियमावली में शामिल नहीं है। अंतिम निर्णय लेने से पहले 28 अगस्त 2026 की अधिसूचना से पुष्टि अवश्य करें।"
    }
    with open(AMENDMENT_PATH, "w", encoding="utf-8") as f:
        json.dump(amendment_overlay, f, indent=2, ensure_ascii=False)
    print(f"Written amendment overlay to {AMENDMENT_PATH}")

if __name__ == "__main__":
    build_dataset()
