"""Audit of the eval team's Model A vs Model B comparison."""
import json
import os
from collections import Counter

from eval.extract import extract_answer
from eval.score import is_correct, score_model

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
MODELS = ("A", "B")


def load_jsonl(name):
    with open(os.path.join(DATA, name)) as f:
        return [json.loads(line) for line in f if line.strip()]


def header(title):
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


def show(x):
    if x is None:
        return "none"
    return str(int(x)) if x == int(x) else str(x)


def response_style(text):
    """Label the answer format a response uses."""
    if text.startswith("Let's work through it step by step"):
        return "step_by_step"
    if text.startswith("**"):
        return "bold_first"
    if text.startswith("The answer is"):
        return "answer_is"
    return "other"


def baseline(questions, outputs):
    header("Baseline: reproduce the eval team's numbers")
    res = {m: score_model(outputs[m], questions, extract_method="first_number") for m in MODELS}
    for m in MODELS:
        r = res[m]
        print(f"{m}: accuracy {r['accuracy']:.1%}  scored {r['n_scored']}  unparseable {r['n_unparseable']}")
    print(f"Gap (B - A): {100 * (res['B']['accuracy'] - res['A']['accuracy']):+.1f} points")
    assert f"{res['A']['accuracy']:.1%}" == "61.3%" and f"{res['B']['accuracy']:.1%}" == "68.6%", \
        "could not reproduce the team's report"


def extraction_audit(questions, outputs):
    header("Answer extraction")

    for m in MODELS:
        styles = Counter(response_style(outputs[m][qid]) for qid in questions)
        print(f"{m} response formats: {dict(styles)}")
    by_subset = Counter((q["subset"], response_style(outputs["A"][qid])) for qid, q in questions.items())
    print("A format by subset: " + ", ".join(f"{s}/{f} {n}" for (s, f), n in sorted(by_subset.items())))

    for m in MODELS:
        changes = Counter()
        examples = []
        for qid, q in questions.items():
            text = outputs[m][qid]
            old = extract_answer(text, method="first_number")
            new = extract_answer(text, method="final")
            if old == new:
                continue
            old_ok = old is not None and is_correct(old, q["gold_answer"])
            new_ok = new is not None and is_correct(new, q["gold_answer"])
            changes[(response_style(text), old_ok, new_ok)] += 1
            if len(examples) < 3:
                examples.append((qid, old, new, q["gold_answer"]))
        print(f"\n{m}: original and fixed rule disagree on {sum(changes.values())} of {len(questions)} responses")
        for (style, old_ok, new_ok), n in sorted(changes.items()):
            label = f"{'correct' if old_ok else 'wrong'} -> {'correct' if new_ok else 'wrong'}"
            print(f"   {style:13s} scored {label:18s} {n}")
        for qid, old, new, gold in examples:
            print(f"   e.g. {qid}: original read {show(old)}, fixed reads {show(new)}, gold {gold}")

    print("\nAccuracy by extraction rule (unparseable still dropped):")
    for method in ("first_number", "last_number", "final"):
        res = {m: score_model(outputs[m], questions, extract_method=method) for m in MODELS}
        gap = 100 * (res["B"]["accuracy"] - res["A"]["accuracy"])
        print(f"   {method:12s}  A {res['A']['accuracy']:.1%}  B {res['B']['accuracy']:.1%}  gap (B - A) {gap:+.1f}")


def main():
    questions = {r["id"]: r for r in load_jsonl("test_questions.jsonl")}
    outputs = {
        m: {r["id"]: r["response"] for r in load_jsonl(f"model_{m.lower()}_outputs.jsonl")}
        for m in MODELS
    }
    baseline(questions, outputs)
    extraction_audit(questions, outputs)


if __name__ == "__main__":
    main()
