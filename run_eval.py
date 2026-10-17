"""Run the full evaluation and write results/report.md.

Usage:  python run_eval.py
"""
import json
import os

from eval.judge import judge_win_rate, position_balanced_win_rate
from eval.score import score_model

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")


def load_jsonl(name):
    with open(os.path.join(DATA, name)) as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    questions = {r["id"]: r for r in load_jsonl("test_questions.jsonl")}
    outs_a = {r["id"]: r["response"] for r in load_jsonl("model_a_outputs.jsonl")}
    outs_b = {r["id"]: r["response"] for r in load_jsonl("model_b_outputs.jsonl")}
    judge = load_jsonl("judge_pairwise.jsonl")

    res_a = score_model(outs_a, questions)
    res_b = score_model(outs_b, questions)
    jw = judge_win_rate(judge, model="B")
    pos = position_balanced_win_rate(judge, model="B")

    lines = [
        "# Model A vs Model B: evaluation report",
        "",
        f"Benchmark: {len(questions)} arithmetic word problems (single-step and multi-step).",
        "",
        "## Exact-match accuracy",
        "",
        "Unparseable answers (no number given) are counted as wrong.",
        "",
        "| Model | Accuracy | Single-step | Multi-step | Unparseable |",
        "|---|---|---|---|---|",
        f"| A | {res_a['accuracy']:.1%} | {res_a['per_subset']['single_step']:.1%} | "
        f"{res_a['per_subset']['multi_step']:.1%} | {res_a['n_unparseable']} |",
        f"| B | {res_b['accuracy']:.1%} | {res_b['per_subset']['single_step']:.1%} | "
        f"{res_b['per_subset']['multi_step']:.1%} | {res_b['n_unparseable']} |",
        "",
        "## LLM judge (pairwise)",
        "",
        f"B's win rate with both position orders weighted equally: {pos['balanced']:.1%} "
        f"(team's original reported: {jw['win_rate']:.1%}).",
        "",
        "## Conclusion",
        "",
        f"Exact-match gap (B - A): {100 * (res_b['accuracy'] - res_a['accuracy']):+.1f} points. "
        "This report does not make a ship decision, see FINDINGS.md for the full audit.",
        "",
    ]

    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    with open(os.path.join(ROOT, "results", "report.md"), "w") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
