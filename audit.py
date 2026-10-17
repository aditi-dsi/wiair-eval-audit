"""Audit of the eval team's Model A vs Model B comparison."""
import json
import os
from collections import Counter

from eval.extract import extract_answer
from eval.judge import judge_win_rate, position_balanced_win_rate
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
    res = {m: score_model(outputs[m], questions, extract_method="first_number", unparseable="drop") for m in MODELS}
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
        res = {m: score_model(outputs[m], questions, extract_method=method, unparseable="drop") for m in MODELS}
        gap = 100 * (res["B"]["accuracy"] - res["A"]["accuracy"])
        print(f"   {method:12s}  A {res['A']['accuracy']:.1%}  B {res['B']['accuracy']:.1%}  gap (B - A) {gap:+.1f}")

def refusal_audit(questions, outputs):
    header("Unparseable answers (refusals)")

    refused = [qid for qid in questions if extract_answer(outputs["B"][qid]) is None]
    print(f"B gave no answer on {len(refused)} of {len(questions)} questions")
    print("By subset:", dict(Counter(questions[qid]["subset"] for qid in refused)))
    print("Texts:", dict(Counter(outputs["B"][qid] for qid in refused)))
    a_right = sum(is_correct(extract_answer(outputs["A"][qid]), questions[qid]["gold_answer"]) for qid in refused)
    print(f"A answered the same questions correctly: {a_right} of {len(refused)}")
    ft = load_jsonl("model_b_finetune_sample.jsonl")
    print("Fine-tune completions that are not 'The answer is N':",
          sum(not r["completion"].startswith("The answer is") for r in ft), "of", len(ft))

    print("\nAccuracy with fixed extraction:")
    for label, qs, policy in [("refusals dropped (team's way)", questions, "drop"),
                              ("refusals counted as wrong", questions, "wrong")]:
        res = {m: score_model(outputs[m], qs, unparseable=policy) for m in MODELS}
        gap = 100 * (res["B"]["accuracy"] - res["A"]["accuracy"])
        print(f"{label:38s} A {res['A']['accuracy']:.1%}  B {res['B']['accuracy']:.1%}  gap (B - A) {gap:+.1f}")


def judge_audit(questions, outputs):
    header("LLM judge")
    judge = load_jsonl("judge_pairwise.jsonl")
    human = {r["id"]: r["human_preference"] for r in load_jsonl("human_preferences_sample.jsonl")}
    winner = {r["id"]: "tie" if r["verdict"] == "tie" else r[r["verdict"] + "_model"] for r in judge}
    first = {r["id"]: r["response_1_model"] for r in judge}

    def right(m, qid):
        pred = extract_answer(outputs[m][qid])
        return pred is not None and is_correct(pred, questions[qid]["gold_answer"])

    pos_a = position_balanced_win_rate(judge, model="A")
    print(f"A win rate when shown first {pos_a['shown_first']:.1%}, when shown second {pos_a['shown_second']:.1%}")
    pos = position_balanced_win_rate(judge)
    print(f"B win rate when shown first {pos['shown_first']:.1%}, when shown second {pos['shown_second']:.1%}")
    print(f"B shown as Response 1 in {sum(m == 'B' for m in first.values())} of {len(judge)} comparisons")
    print("Verdicts:", dict(Counter(r["verdict"] for r in judge)))
    print(f"B win rate: team's way {judge_win_rate(judge)['win_rate']:.1%}, position-balanced {pos['balanced']:.1%}")

    print()
    for m, other in (("A", "B"), ("B", "A")):
        ids = [qid for qid in questions if right(m, qid) and not right(other, qid)]
        print(f"Only {m} correct ({len(ids)}): judge picked {dict(Counter(winner[qid] for qid in ids))}")
    refused = [qid for qid in questions if extract_answer(outputs["B"][qid]) is None]
    print(f"B refused ({len(refused)}): judge picked {dict(Counter(winner[qid] for qid in refused))}")

    print()
    for style in ("bold_first", "step_by_step"):
        for shown_first in MODELS:
            ids = [qid for qid in questions if right("A", qid) and right("B", qid)
                   and response_style(outputs["A"][qid]) == style and first[qid] == shown_first]
            c = Counter(winner[qid] for qid in ids)
            print(f"Both correct, A {style}, {shown_first} first ({len(ids)}): B win rate {c['B'] / (c['A'] + c['B']):.0%}")


def main():
    questions = {r["id"]: r for r in load_jsonl("test_questions.jsonl")}
    outputs = {
        m: {r["id"]: r["response"] for r in load_jsonl(f"model_{m.lower()}_outputs.jsonl")}
        for m in MODELS
    }
    baseline(questions, outputs)
    extraction_audit(questions, outputs)
    refusal_audit(questions, outputs)
    judge_audit(questions, outputs)


if __name__ == "__main__":
    main()
