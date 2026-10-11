import re

def normalize_whitespace(text):
    """Normalize tabs, newlines, and multiple spaces into a single space."""
    if not text:
        return ""
    # Remove special punctuation differences if needed
    cleaned = re.sub(r'[\r\n\t]+', ' ', text)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def verify_exact_quote(quote, rule_text):
    """
    Verify whether the quote is a real substring of the rule text after whitespace normalization.
    Handles intra-word OCR splits (e.g. 'bu ildings') as well as standard whitespace differences.
    """
    if not quote or not rule_text:
        return False, "Quote or rule text is empty"

    norm_quote = normalize_whitespace(quote).lower()
    norm_rule = normalize_whitespace(rule_text).lower()

    if len(norm_quote) < 5:
        return False, "Quote too short (less than 5 characters)"

    # Direct normalized substring match
    if norm_quote in norm_rule:
        return True, "Verified exact substring"

    # Space-insensitive substring match (essential for OCR line wraps and split words like 'bu ildings')
    quote_compact = re.sub(r'[^a-zA-Z0-9\u0900-\u097F]', '', norm_quote)
    rule_compact = re.sub(r'[^a-zA-Z0-9\u0900-\u097F]', '', norm_rule)

    if len(quote_compact) >= 5 and quote_compact in rule_compact:
        return True, "Verified substring (after whitespace and punctuation normalization)"

    return False, f"Quote not found in rule text: '{norm_quote[:40]}...'"

def verify_all_citations(citations, candidate_rules):
    """
    Verify a list of citations against candidate rule documents.
    Returns (all_valid, verified_citations, failure_reasons).
    """
    if not citations:
        return False, [], ["No citations provided"]

    # Index candidates by rule_number
    rules_map = {}
    for r in candidate_rules:
        r_num = str(r["rule_number"]).upper().strip()
        rules_map[r_num] = r
        # Also index by inserted rules
        for sub in r.get("inserted_rules", []):
            rules_map[str(sub["rule_number"]).upper().strip()] = r

    all_valid = True
    verified = []
    failures = []

    for cit in citations:
        c_rnum = str(cit.get("rule_number", "")).upper().replace("RULE", "").strip()
        # Extract base rule number (e.g. 56(1)(a) -> 56, 21(3)(b) -> 21, 12-A -> 12-A, 26-B -> 26-B)
        base_match = re.match(r'^(\d+(?:\-[A-Z]+)?|\d+)', c_rnum)
        base_rnum = base_match.group(1) if base_match else c_rnum

        target_rule = rules_map.get(base_rnum)
        if not target_rule:
            # Fallback check any rule that matches numeric part
            num_match = re.match(r'^([0-9]+)', base_rnum)
            if num_match:
                target_rule = rules_map.get(num_match.group(1))

        if not target_rule:
            all_valid = False
            failures.append(f"Referenced rule {c_rnum} not present in candidate rules")
            continue

        quote = cit.get("exact_quote", "")
        is_valid, msg = verify_exact_quote(quote, target_rule["full_text"])
        if is_valid:
            page_range = target_rule.get("page_range", [1, 1])
            page_str = f"Page {page_range[0]}" if page_range[0] == page_range[1] else f"Pages {page_range[0]}-{page_range[1]}"
            r_display = str(cit.get("rule_number", ""))
            if not r_display.upper().startswith("RULE"):
                r_display = f"Rule {r_display}"
            verified.append({
                "rule_number": r_display,
                "page_range": cit.get("page_range") or page_str,
                "exact_quote": quote,
                "verified": True
            })
        else:
            all_valid = False
            failures.append(f"Rule {c_rnum}: {msg}")

    return all_valid, verified, failures

if __name__ == "__main__":
    test_rule_text = "Every Residential Building having height up to 12.5 meters, facing street shall have a front open space mentioned below"
    test_quote = "Every Residential Building having height up to 12.5 meters"
    ok, msg = verify_exact_quote(test_quote, test_rule_text)
    print("Verification test:", ok, msg)
