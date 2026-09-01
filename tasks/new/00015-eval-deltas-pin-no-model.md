---
created: 2026-08-07
updated: 2026-08-07
completed: ""
status: new
owner: justmaniv
blocked-by: ""
links:
  - tasks/done/00004-author-eval-suite-for-the-skill.md
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

## The third case is no longer hypothetical (observed 2026-09-01)

The 0.9.0 run measured it directly. `done-when-reconciliation` fell from **Δ +0.19** (CLI 2.1.221,
skill 0.8.0) to **Δ +0.14** (CLI 2.1.236, skill 0.9.0) — and the `with` arm did not move. It is
1.00 in both. The entire narrowing is the **baseline** rising, 0.81 → 0.86, on a different CLI
build against a model neither run names.

So the failure this task predicts is now on the record with numbers attached: a delta shrank, the
skill was not touched in that case, and the only way to tell those apart was to read **both arms**
of two runs rather than their deltas. A reader seeing only the current number would read a 26%
narrowing as decay.

⚠️ **And that comparison was luck.** `evals/results/` is in `.gitignore` (`.gitignore:8`), so no
`aggregate-result.json` is tracked — the August run survived only because it was still sitting on
one contributor's machine. On any other checkout the earlier arms are simply gone, and the
narrowing is unattributable. Whatever this task decides, *"the prior arms are recoverable"* has to
be part of it; today it is a property of one laptop.

⚠️ **A second, unrelated hazard turned up in the same run: the result file's schema changed shape.**
The 2026-08-12 aggregate (CLI 2.1.221) uses snake_case with runs at the top of the case —
`claude_version`, `score_without`, `runs`, `runs_without`. The 2026-09-01 one (CLI 2.1.236) uses
camelCase and different nesting — `claudeVersion`, `aggregates.scoreWithout`, `arms.with[]`.
Both declare a schema version of `1`, under different key spellings for that too.

Nothing reads these programmatically today, so nothing broke. But any option below that proposes
comparing runs mechanically has to handle both shapes, and a comparison written against one will
fail on the other by finding no key — which, for a script summarising a delta, is a silent zero
rather than an error.

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
