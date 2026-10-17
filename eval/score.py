"""Exact-match accuracy against gold answers."""
from collections import defaultdict

from eval.extract import extract_answer

TOLERANCE = 1e-6


def is_correct(pred, gold) -> bool:
    return abs(pred - float(gold)) < TOLERANCE


def score_model(outputs: dict, questions: dict, extract_method: str = "final") -> dict:
    """Score one model.

    outputs:   {id: response_text}
    questions: {id: {"gold_answer": ..., "subset": ...}}
    extract_method: passed to extract_answer ("first_number" reproduces the original report)
    """
    correct, total = 0, 0
    per_subset = defaultdict(lambda: [0, 0])
    n_unparseable = 0

    for qid, q in questions.items():
        pred = extract_answer(outputs.get(qid, ""), method=extract_method)
        if pred is None:
            # Unparseable outputs are formatting noise, not reasoning errors; skip them so
            # they don't distort the accuracy number.
            n_unparseable += 1
            continue
        ok = is_correct(pred, q["gold_answer"])
        correct += ok
        total += 1
        per_subset[q["subset"]][0] += ok
        per_subset[q["subset"]][1] += 1

    return {
        "accuracy": correct / total if total else 0.0,
        "n_scored": total,
        "n_unparseable": n_unparseable,
        "per_subset": {s: c / t for s, (c, t) in per_subset.items()},
    }
