"""Pairwise LLM-judge win rates.

For each question, the judge saw both models' responses (labelled "Response 1" and
"Response 2") and returned which one was better, or a tie.
"""


def judge_win_rate(judge_rows: list, model: str = "B") -> dict:
    wins = {"A": 0, "B": 0, "tie": 0}
    for row in judge_rows:
        v = row["verdict"]
        if v == "tie":
            wins["tie"] += 1
        elif v == "response_1":
            wins[row["response_1_model"]] += 1
        elif v == "response_2":
            wins[row["response_2_model"]] += 1
    decided = wins["A"] + wins["B"]
    return {
        "win_rate": wins[model] / decided if decided else 0.0,
        "counts": wins,
    }
