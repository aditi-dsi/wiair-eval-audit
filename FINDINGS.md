# Findings

Name: Aditi Bindal

How to reproduce every number below: `python audit.py` (it also regenerates `results/report.md`)

## Recommendation

My recommendation is to not ship Model B on this evidence. After fixing the scoring bugs, A and B are about similar on all 400 questions (A 75.5%, B 74.5%). Whereas on the 352 questions not found in B's fine-tune sample, A is ahead (76.1% vs 71.6%). The judge's preference for B comes mostly from the order the answers were shown in. I am confident the original claim ("B beats A") does not hold. I am less sure that A is actually better, because the gap is small (1.0 point overall, 4.5 on clean questions) and B is better on single-step questions. B winning on a fresh test set with new question types, judged in both orders, would change my mind.

## Issues found

| # | Issue | Evidence (how you know) | Effect on the result | Fixed? |
|---|-------|-------------------------|----------------------|--------|
| 1 | Answer extraction took the first number in the response | A: all 76 "Let's work through it step by step..." answers were scored on a number from the working (q0002 read as 5, gold 275), 57 of them were actually correct. B: 49 answers with a thousands comma were read as the digits before the comma (q0021 "10,191" read as 10), 38 of them were actually correct. Taking the last number instead gives B 0.3%, so the scores depend heavily on how the answer is read. | A 61.3% → 75.5%, B 68.6% → 78.6% (refusals still dropped). Gap (B − A): +7.4 → +3.1 | Yes. `eval/extract.py` reads the stated answer ("Answer: N", "The answer is N", a leading **N**) and handles commas. `method="first_number"` reproduces the old scores |
| 2 | B's refusals were left out of its score | 21 B answers contain no number (e.g. "There seem to be missing details here..."), all on multi-step questions. A answered 15 of these 21 correctly, so the questions are answerable. `score.py` skipped them, so B was scored on 379 questions and A on 400. | B 78.6% → 74.5%. Gap: +3.1 → −1.0 | Yes. `score.py` counts them as wrong. `unparseable="drop"` reproduces the old scores |
| 3 | 48 test questions, with their answers, are in B's fine-tune data | 48 of 400 test questions appear word for word in the fine-tune sample, and all 48 completions give the gold answer. B scores 95.8% on them vs 71.6% on the other 352. A, not trained on them, scores 70.8% vs 76.1%, which indicates they are not easier questions. All 12 question templates in the test set also appear in the fine-tune sample. | On the 352 clean questions the gap is −4.5 (A 76.1%, B 71.6%), vs −1.0 on all 400 | Measured, can't be fixed in code. 48 is a lower bound as we only have a sample of the fine-tune data |
| 4 | The judge favors whichever answer it sees first, and B was shown first in 294 of 400 comparisons | Response 1 won 268 times, Response 2 won 94 times. A wins 68.4% when shown first vs 23.9% when second, B wins 76.1% vs 31.6%. When only A was correct, the judge still picked B 23 of 66 times. It picked B's refusal over A's answer 7 of 21 times. | B's win rate 64.1% → 53.9% when both orders are weighted equally | Not a complete fix until judge is run again with every pair in both orders. For now `eval/judge.py` adds a position-balanced win rate. |
| 5 | The report's conclusion was hard-coded and subset results were hidden | `run_eval.py` printed "the judge independently prefers B. Recommendation: ship Model B." whatever the numbers were. Per-subset accuracy was computed but never shown: B is better on single-step (85.9% vs 77.3%) and worse on multi-step (60.6% vs 73.3%). | The headline claimed B wins but the data does not show | Yes, the report now prints only computed numbers and doesn't make ship decision |

## Corrected results

| Step | A | B | Gap (B − A) |
|---|---|---|---|
| Team's report | 61.3% | 68.6% (379 scored) | +7.4 |
| Fix answer extraction | 75.5% | 78.6% (379 scored) | +3.1 |
| Count refusals as wrong | 75.5% | 74.5% | −1.0 |
| Only the 352 clean questions | 76.1% | 71.6% | −4.5 |

Judge: B's win rate is 53.9% with both orders weighted equally, not 64.1%.

My best estimate is that A and B are close overall, with A ahead on questions B was not trained on. The single number hides that B is better on single-step questions and clearly worse on multi-step ones. Also, even the clean questions use the 12 templates B was trained on, so this benchmark cannot show how B handles new kinds of problems. A 1-point gap is only 4 questions out of 400, so I would not treat it as a real difference. The 4.5-point gap on clean questions and B's jump of about 24 points on the leaked questions are bigger, so I trust them more, but they are still based on a limited number of questions (352 and 48).


## Discussion

**What matters most:** Three problems decide the answer: First, the scoring code misread both models, so both accuracy numbers in the original report were wrong, and fixing extraction alone cut B's lead from 7.4 to 3.1 points. Second, B was trained on 48 test questions with their answers. Its near-perfect score on them, while A does worse on the same questions. This indicates some extent of memorization. Third, the judge is not independent evidence: it mostly picks the first answer, B was usually first, and it sometimes preferred B's refusal over A's actual answer. Separately, B refusing 21 answerable multi-step questions is a problem in itself, not formatting noise.

**Predictions vs findings.** I was right that A's step-by-step answers were misread (all 76, 57 correct), that A would rise to about 75% (75.5%), that dropping refusals inflated B, that the judge's rate would fall toward 50% once position was controlled (53.9%), and that exact overlaps with the fine-tune data might exist (48). I predicted the extractor worked fine for B's answers, so I expected A to lead by about 10 points. But, in fact, it also misread 49 of B's answers that used a comma like in "10,191", so fixing it raised B too, and A leads by only 1.0 on all 400 questions (4.5 on the unleaked ones). I also thought A's format depended on the subset, but it does not (37 multi-step vs 39 single-step step-by-step answers). My guess that the judge liked B's plainer format was not supported: with A shown first, B wins 30% against A's bold answers and 29% against its step-by-step answers (groups of 51 and 17).

**Assumptions.** Refusals count as wrong, since the questions are answerable. Gold answers are correct, I did not re-solve them. Clean data means not found word for word in the fine-tune sample.

**What I would check next.** First, the 120 human labels, which were collected in random order, I did not use them, but they can be checked to see how judge aligns with human preference. Second, the full fine-tune data, to see how many more test questions were leaked. Third, a fresh test set with new kinds of questions, since all 12 templates here appear in B's fine-tune data.
