import os
import sys
import json
import re

# Ensure console supports utf-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from src.agent import answer_question

QUESTIONS_FILE = os.path.join(PROJECT_DIR, "resources", "sample_questions.md")
RESULTS_FILE = os.path.join(PROJECT_DIR, "data", "eval_results.json")

def parse_sample_questions(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Questions file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.split("### Question ")
    questions = []

    for block in blocks[1:]:
        lines = block.splitlines()
        q_id = None
        lang = "English"
        q_text = None
        exp_rule = None
        exp_values = None
        answerable = True

        for line in lines:
            line_str = line.strip()
            if line_str.startswith("- **ID**:"):
                q_id = line_str.replace("- **ID**:", "").strip()
            elif line_str.startswith("- **Language**:"):
                lang = line_str.replace("- **Language**:", "").strip()
            elif line_str.startswith("- **Question**:"):
                q_text = line_str.replace("- **Question**:", "").strip()
            elif line_str.startswith("- **Expected Rule**:"):
                val = line_str.replace("- **Expected Rule**:", "").strip()
                exp_rule = None if val.lower() == "null" else val
            elif line_str.startswith("- **Expected Values**:"):
                val = line_str.replace("- **Expected Values**:", "").strip()
                try:
                    exp_values = None if val.lower() == "null" else json.loads(val)
                except Exception:
                    exp_values = None
            elif line_str.startswith("- **Answerable**:"):
                val = line_str.replace("- **Answerable**:", "").strip().lower()
                answerable = (val == "true")

        if q_id and q_text:
            questions.append({
                "id": q_id,
                "language": lang,
                "question": q_text,
                "expected_rule": exp_rule,
                "expected_values": exp_values,
                "answerable": answerable
            })

    return questions

def run_evaluation():
    questions = parse_sample_questions(QUESTIONS_FILE)
    print(f"\n=======================================================")
    print(f"  BHUMI VIKAS SAHAYAK - EVALUATION SUITE")
    print(f"  Running {len(questions)} Benchmark Test Questions")
    print(f"=======================================================\n")

    results = []
    passed_count = 0

    for q in questions:
        q_id = q["id"]
        q_text = q["question"]
        print(f"[{q_id}] ({q['language']}) {q_text[:75]}...")

        res = answer_question(q_text)
        passed = False
        notes = []

        if not q["answerable"]:
            # Must return found: False (rules do not cover this)
            if not res["found"]:
                passed = True
                notes.append("Correctly rejected unanswerable query (found=False)")
            else:
                notes.append(f"Expected unanswerable, but system returned found=True with rule {res.get('rule_number')}")
        else:
            if not res["found"]:
                notes.append("System failed to find answer for valid query")
            else:
                rule_match = False
                exp_r = q["expected_rule"]
                cited_rules = [c.get("rule_number", "") for c in res.get("citations", [])] + [str(res.get("rule_number", ""))]
                cited_str = " ".join(cited_rules)

                # Check rule match
                if exp_r:
                    # Clean e.g. "Rule 56(1)(a)" -> "56"
                    base_exp = re.search(r'\b([0-9]+(?:\-[A-Za-z]+)?)\b', exp_r)
                    if base_exp and base_exp.group(1) in cited_str:
                        rule_match = True

                # Check citations verification
                verif = res.get("citation_verification", {})
                all_verified = verif.get("all_verified", False)

                # Check expected values in answer
                values_match = True
                if q["expected_values"]:
                    ans_text = res.get("answer", "")
                    for k, v in q["expected_values"].items():
                        # Look for number v in answer or citations
                        v_str = str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)
                        if v_str not in ans_text:
                            # Also check citations text
                            c_text = " ".join([c.get("exact_quote", "") for c in res.get("citations", [])])
                            if v_str not in c_text:
                                values_match = False
                                notes.append(f"Value {v_str} ({k}) not found in answer or quotes")

                if rule_match and all_verified and values_match:
                    passed = True
                    notes.append("Rule, exact quotes, and calculated values verified")
                elif not rule_match:
                    notes.append(f"Expected rule {exp_r}, cited: {cited_str}")
                elif not all_verified:
                    notes.append(f"Quote verification failed: {verif.get('failures')}")

        status = "PASS" if passed else "FAIL"
        if passed:
            passed_count += 1
            print(f"  -> {status}: {'; '.join(notes)}")
        else:
            print(f"  -> {status}: {'; '.join(notes)}")

        results.append({
            "id": q_id,
            "question": q_text,
            "answerable": q["answerable"],
            "passed": passed,
            "notes": notes,
            "response": res
        })
        print()

    accuracy = (passed_count / len(questions)) * 100.0 if questions else 0.0
    summary = {
        "total": len(questions),
        "passed": passed_count,
        "failed": len(questions) - passed_count,
        "accuracy_pct": round(accuracy, 2),
        "results": results
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("=======================================================")
    print(f"  TOTAL QUESTIONS : {len(questions)}")
    print(f"  PASSED          : {passed_count}")
    print(f"  FAILED          : {len(questions) - passed_count}")
    print(f"  ACCURACY        : {accuracy:.2f}%")
    print("=======================================================\n")
    return accuracy

if __name__ == "__main__":
    acc = run_evaluation()
    sys.exit(0 if acc >= 90.0 else 1)
