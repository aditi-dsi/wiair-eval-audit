# Predictions

Fill this in **before modifying any code**, and commit it before your first code change.
Short answers are fine. Being wrong is fine.

## 1. Do you believe the headline (B is better and should ship)? Why or why not?

I do not fully agree with this headline. There are several bugs I found in the code itself, like bugs in scoring methodology, answer extraction, judge's preference statement being hardcoded in the report generation code, etc. Further, there are some additional issues I suspect the pipeline to have, that makes this headline less trustworthy, like judge preferring B while ignoring B's several refused responses, fine-tuning data of B containing very similar template questions as the test set (not sure if there exists exactly same questions as well), the judge prefers B's response for a question even when A's is also correct (not sure what the judge is rewarding).


## 2. What do you suspect might be wrong with this evaluation?

List each suspicion and what made you suspect it.

- In `eval/extract.py` the regex is written to extract the first number it sees in the response. This works fine for B's straightly structured responses and for A's single-step styled responses. But in A's multi-step styled responses, this extracts the wrong number from intermediate steps and formatting and fails to reach the final numeric value that model A actually reports as its final answer.

- While scoring in `eval/score.py` B's refused responses are counted as unparseable and B is not penalized for it because the counts of refusals casually gets dropped and doesn't get counted towards the `total` counts that are used for calcualting accuracy score for B. Thus, this ends up inflating B's score.

- The LLM judge's verdicts may depend on position or style rather than correctness. The data records which model was shown as Response 1 vs Response 2, but `eval/judge.py` never checks whether the verdict depends on that order. The rationales are only 4 fixed sentences across all 400 rows (e.g. "Response N explains the calculation more directly"), and none of them refer to the actual content, so there is no way to tell what the judge is rewarding. In the first few rows Response 2 also seems to win more often. I also suspect a style bias: B's one-line "The answer is X." may look "more direct and clear" than A's markdown (`**...**`, `\n`) and step-by-step working, even when both are correct.

- There's a possible test-set contamination in B's fine-tuning data. `model_b_finetune_sample.jsonl` uses the same question templates as the test set (e.g. ft00002 vs q0007 for rice harvest, ft00004/ft00007 vs q0008 for the printer problem). I haven't checked yet whether any test questions appear exactly, with the same numbers. Even if none do, B is being tested on the same distribution it was fine-tuned on, while we don't know what A was trained on, so B's score may overstate how well it generalizes to problems worded differently. The fine-tuning completions are answer-only ("The answer is 5712."), which is exactly B's output format, so I am assuming B was trained with that fine-tune data to give answers without any working.

- B refuses questions that are fully specified. Separate from the scoring issue above, B says details are missing on answerable problems (q0012, q0029, q0073, q0108, etc, and A answers each of them correctly). That is 21/400 (~5%) of the benchmark and would be a user-facing problem in production, but the report only shows it as an "Unparseable" count.

- The conclusion in `run_eval.py` is hardcoded. "the judge independently prefers B. Recommendation: ship Model B." is a fixed string and only the gap number is filled in, so the report would recommend shipping B even if B lost. We do not if there is a separate judge call behind this decision that was excluded from the given and report. The judge also isn't really "independent" evidence, since it measures preference, not correctness.

## 3. After fixing what you can, which way do you expect the A vs B gap to move, and roughly by how much?

I expect the gap to shrink and most likely flip in A's favor.

- Counting B's 21 refusals as wrong instead of dropping them: B goes from 260/379 (68.6%) to 260/400 = 65.0%. That alone cuts the gap from 7.4 to about 3.7 points.
- 76 of A's responses use the "Let's work through it step by step ... Answer: N" format, and I think almost all of them are currently scored as wrong. If so, A's 245 correct answers all come from its other 324 responses. If A's step-by-step answers are about as accurate as those, A should rise to roughly 74-76%.
- Combined, my guess is that A ends up ahead of B by about 10 points. If the contamination check finds exact overlaps, B's accuracy on the clean questions could be lower still.
- For the judge, I expect B's 64% to drop toward 50% once position is controlled, but I'm not confident in this one.

## 4. What would you check first, and why?

The answer extraction in `eval/extract.py`, because it is likely the biggest single effect and the easiest to verify: I'll print the extracted number next to the gold answer and the model's own "Answer: X" for A's step-by-step responses, and count how many correct answers are being scored as wrong. After that, in order:

1. Re-score with unparseable/refused responses counted as wrong.
2. Check the judge for position bias (B's win rate when B is Response 1 vs Response 2, and whether the order was balanced).
3. Check for exact or near-exact overlap between fine-tuning prompts and test questions, and compare B's accuracy on overlapping vs non-overlapping questions.