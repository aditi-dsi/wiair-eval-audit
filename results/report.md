# Model A vs Model B: evaluation report

Benchmark: 400 arithmetic word problems (single-step and multi-step).

## Exact-match accuracy

| Model | Accuracy | Scored | Unparseable |
|---|---|---|---|
| A | 61.3% | 400 | 0 |
| B | 68.6% | 379 | 21 |

## LLM judge (pairwise)

Judge prefers **B** in 64.1% of decided comparisons (A wins 130, B wins 232, ties 38).

## Conclusion

B beats A by 7.4 points on exact match, and the judge independently prefers B. **Recommendation: ship Model B.**
