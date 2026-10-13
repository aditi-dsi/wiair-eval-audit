# WiAIR Mentorship Lab: Take-Home Assignment

## Should we ship Model B?

An eval team compared two language models, **Model A** (currently in production) and
**Model B** (a fine-tuned candidate), on a benchmark of 400 arithmetic word problems. Their
report is in `results/report.md`. The short version:

> B beats A by 7.4 points on exact match, and an LLM judge independently prefers B
> 64% of the time. **Recommendation: ship Model B.**

Your job is to **audit this evaluation** and decide whether the recommendation holds up.

You are not asked to run any models. Every model output and judge verdict is already in
`data/`, so you need no GPU, no API key, and no paid tools. A laptop with Python 3.9+ is enough.

## AI tools are allowed

Use Copilot, Claude, ChatGPT, Cursor, or anything else you normally use. We are not
testing whether you can write code without help. We are testing **what you notice, how
you check it, and how you reason about evidence.** Those are things you will need to
explain in your own words on a short call (see below).

## What to do

### Step 1: Predictions (about 30 minutes, before changing any code)

Read the report, the code in `eval/`, and look at the data. **Before you modify anything**,
fill in `PREDICTIONS.md`: do you believe the headline, what you suspect might be wrong,
and which way you expect the corrected numbers to move. **Commit it before your first code
change.** Being wrong here costs you nothing. Wrong predictions you later explain are one
of the most useful things you can show us.

### Step 2: Audit

Find problems in the evaluation. For each one, show the evidence, measure how much it
changes the result, and fix it where a fix is possible. Some problems are in the code,
some are in the data, and some are in how the results are interpreted. They vary a lot
in how much they matter.

Your final analysis must run with a single command (e.g. `python audit.py`) and must
reproduce every number in your write-up.

### Step 3: Write-up

Fill in `FINDINGS.md`. **One page, at most 700 words** plus the issues table. Prioritize:
we would rather read three findings explained well than ten listed. End with your
recommendation to the team and how confident you are in it.

### Step 4: AI usage log

Fill in `AI_LOG.md`: which tools you used, for what, and at least one case where an AI
suggestion was wrong or where you chose not to follow it, and why.

## Rules

- **Time:** aim for about 5 hours of work. Please don't go beyond 8. If you run out of
  time, write down what you would check next. That counts.
- **Commit as you go.** We read the git history. Small, honest commits are better than
  one big commit at the end.
- **Your own words.** The write-up can be edited with AI, but the reasoning must be
  yours. You will be asked to defend it.
- **Work alone.** You may read anything public, but please don't discuss the assignment
  with other applicants.
- **Questions:** if something is genuinely ambiguous, make a reasonable assumption, state
  it in `FINDINGS.md`, and keep going.

## Follow-up call (15 minutes)

If your submission moves forward, we will schedule a short call where we pick one decision
from your work and ask you to walk us through it: what you saw, what else you considered,
and what would change your mind. There is no trick to prepare for. If you did the work
yourself, it will be easy.

## What we look for

1. **Noticing:** do you find the problems that matter most to the conclusion?
2. **Evidence:** do you back each claim with a check, rather than a hunch?
3. **Measuring:** do you quantify how much each problem moves the result, including uncertainty?
4. **Judgment:** is your final recommendation proportionate to the evidence?
5. **Communication:** is the write-up clear, prioritized, and honest about what you don't know?

Code style is not graded, but we need to be able to run it.

## Submitting

**Deadline: Saturday, October 17, 2026, 11:59pm AoE** (Sunday, October 18, 11:59 UTC).

1. Zip the whole folder **including the hidden `.git` directory**, for example:
   `zip -r wiair-eval-audit.zip wiair-eval-audit`
2. Upload the zip through this form (it asks you to sign in with Google):
   **https://forms.gle/5pi2snpfBFk6X5168**

If the upload doesn't work for you, email the zip to **smritisingh26@utexas.edu** instead.

## Contact

Email **smritisingh26@utexas.edu** with questions, concerns, or extension requests. If you
need more time, please ask before the deadline; reasonable requests will be accommodated.
For questions about the task itself, see the note under Rules: state your assumption and
keep going.

---

## Repository layout

```
run_eval.py                         the eval team's pipeline (writes results/report.md)
eval/extract.py                     pulls the numeric answer out of a model response
eval/score.py                       exact-match accuracy against gold answers
eval/judge.py                       pairwise LLM-judge win rate
results/report.md                   the eval team's report
data/test_questions.jsonl           the benchmark
data/model_a_outputs.jsonl          Model A's responses
data/model_b_outputs.jsonl          Model B's responses
data/judge_pairwise.jsonl           LLM-judge verdicts
data/human_preferences_sample.jsonl human preference labels for a random sample
data/model_b_finetune_sample.jsonl  a sample of the data Model B was fine-tuned on
PREDICTIONS.md / FINDINGS.md / AI_LOG.md   templates for you to fill in
```

## Data reference

**`test_questions.jsonl`**: `id`, `subset` (`single_step` or `multi_step`), `question`, `gold_answer`

**`model_a_outputs.jsonl`, `model_b_outputs.jsonl`**: `id`, `response` (the model's full text reply)

**`judge_pairwise.jsonl`**: `id`, `response_1_model` and `response_2_model` (which model's
answer was shown to the judge first and second), `verdict` (`response_1`, `response_2`, or
`tie`), `rationale`

**`human_preferences_sample.jsonl`**: `id`, `human_preference` (`A`, `B`, or `tie`). A random
sample of 120 questions, labeled by annotators who saw the two responses in randomized order.

**`model_b_finetune_sample.jsonl`**: `ft_id`, `prompt`, `completion`. Shared by the team that
fine-tuned Model B.

To reproduce the team's report: `python run_eval.py`
