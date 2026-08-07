---
created: 2026-08-07
updated: 2026-08-07
completed: ""
status: new
owner: justmaniv
blocked-by: ""
links:
  - tasks/done/004-author-eval-suite-for-the-skill.md
  - evals/README.md
---

# The eval numbers have no model attached, so they expire without saying so

## Context

`execution.model` is unset in both cases, so each run inherits whatever the runner defaults to. The
recorded deltas — **+0.50** and **+0.115**, measured on CLI 2.1.220 — are therefore true of a model
that is not named anywhere, and a re-run six months from now will compare against a different one
while reporting the same units.

Those numbers are load-bearing. They are in `README.md`, on the front page, as the answer to "does
this skill actually do anything". A number that quietly stops meaning what it meant is worse than
no number, and this one has no expiry stamped on it.

The suite also has no way to notice. A delta that collapses reads identically whether the skill
regressed, the case drifted into testing the model, or the baseline model simply got better at the
thing the skill used to teach. That third case is the interesting one — **it is a success, and it
looks exactly like a failure.**

## The fork

| Option | Trade-off |
|--------|-----------|
| **Pin `execution.model` per case** | Numbers stay comparable across time, and a regression is unambiguous. Freezes the suite against a model nobody will be running, so it stops describing what users get — and pinned model names go stale on their own schedule. |
| **Leave it unpinned, stamp the run** | Every recorded delta carries the model and CLI version that produced it, so a comparison across different models is *visible* rather than silent. Tests what users actually get. Does not make runs comparable, only makes incomparability obvious. |
| **Both — pin one case, float the other** | Answers two different questions with two cases. Doubles the interpretation burden on whoever reads the table next, for a suite that currently has two cases total. |

Recommendation: **unpinned, stamped**. The suite's job is to catch the skill regressing, and a
baseline that tracks the real model is the more honest comparison — a skill that stops adding value
because the model absorbed the lesson *should* show a shrinking delta, and that is information
worth having rather than an artifact to freeze out. Pinning optimizes for a tidy number.

Whichever wins, the recorded numbers need the model beside them.

## Done when

- [ ] A decision recorded, naming which question the suite is meant to answer — "did the skill
      regress" or "does the skill still help the model people are running"
- [ ] Every recorded delta carries the model and CLI version that produced it — `README.md`,
      `evals/README.md`, and task 004's table
- [ ] `evals/README.md` says what a shrinking delta means and how to tell the three causes apart,
      since "the model got better" and "the skill broke" currently look identical
