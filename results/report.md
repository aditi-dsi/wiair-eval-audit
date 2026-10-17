# Model A vs Model B: evaluation report

Benchmark: 400 arithmetic word problems (single-step and multi-step).

## Exact-match accuracy

Unparseable answers (no number given) are counted as wrong.

| Model | Accuracy | Single-step | Multi-step | Unparseable |
|---|---|---|---|---|
| A | 75.5% | 77.3% | 73.3% | 0 |
| B | 74.5% | 85.9% | 60.6% | 21 |

## LLM judge (pairwise)

B's win rate with both position orders weighted equally: 53.9% (team's original reported: 64.1%).

## Conclusion

Exact-match gap (B - A): -1.0 points. This report does not make a ship decision, see FINDINGS.md for the full audit.
