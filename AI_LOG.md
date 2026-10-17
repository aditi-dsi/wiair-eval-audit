# AI usage log

## Tools used

I used Claude Code, throughout the task for:
- Reading and understanding the code and data, and turning my suspicions into checks.
- Helping in suggesting fixes and writing `audit.py`. It pointed me to the correct files where my fixes should go, tested them on a copy of the repo, and I made every edit myself.
- I told it my suspicions and reasoning to let it draft the wording of PREDICTIONS.md and FINDINGS.md, which I then edited.

## Where AI helped most

- Checking every response at once. It found that 49 of B's answers use a thousands comma ("10,191"), which the old code read as 10. I would not have spotted this by reading a few lines.
- Splitting the judge's results by which answer was shown first, which showed the position bias.

## At least one time an AI suggestion was wrong, or you chose not to follow it

- **Wrong numbers in my predictions:** For Q3 it said if I fixed my found issues, A's improvements can move between 15–18 points. It couldn't explain how it came upon this number, so I didn't follow it. I kept only the numbers I could calculate, at least, roughly.
- **A misleading claim while drafting the write-up:** It wrote that "the extraction rule alone can flip the winner". I checked our results: after the extraction fix, B was still ahead (+3.1), and A only went ahead once refusals were counted as wrong. I replaced this claim with what actually happened.
- **Experiments I chose not to include:** It suggested comparing the judge with the human labels. I skipped it because I could not clearly see a solid reason how human vs judge comparison will fix an existing problem significantly, though it can be an experiment for the future tasks.

## Anything you deliberately did without AI, and why

- Before asking the AI anything, I wrote my own first notes on the problems and suspicions that I found while reading the codebase (without AI), to avoid getting influenced by AI on less significant problems and missing the important obvious ones.
- I typed every code change myself, even the ones where I took the help of AI to suggest syntaxes or methods, instead of letting the AI automatically edit the files, so I can ensure the code remains strictly bounded to what I exactly want it to do.
- I decided which hypothesis to check and what to keep in the write-up, and the final recommendation.
