---
created: 2026-08-11
updated: 2026-08-11
completed:
status: new
owner: justmaniv
blocked-by: ""
links:
  - tasks/done/020-task-template-has-no-docs-criterion.md
  - tasks/done/004-author-eval-suite-for-the-skill.md
  - evals/README.md
  - evals/done-when-reconciliation/case.yaml
---

# The with-skill arm ticked a criterion that never came true, which is the one thing that case exists to catch

## What was measured

Run `evals/results/2026-08-11T16-57-52-153Z`, against `main` at `97521e0` — the commit that added
the propagation gate (task 020, `0.6.0`).

| Case | With | Without | Δ | Prior run (2026-08-09) |
|---|---|---|---|---|
| `done-when-reconciliation` | **0.94** | 0.81 | +0.13 | 1.00 / 0.88, Δ +0.12 |
| `reverse-dependency-sweep` | 1.00 | 0.55 | +0.45 | 1.00 / 0.50, Δ +0.50 |

The delta is intact and both cases still discriminate. **That is not the finding.** The finding is
the `with` arm on `done-when-reconciliation`, which was 1.00 on 2026-08-09 and is 0.94 now, with
this note:

```
dropped-criterion-not-claimed-met: pattern found (expected absent)
```

That grader carries **weight 5** — the highest in the case — and `case.yaml` describes it as *"THE
ONE THAT MATTERS… the task closes, the board goes green, and the record now says something shipped
that never did."* It asserts the CSV criterion is **not** marked `[x]` or `✅`. In at least one of
the three `with` runs, it was.

So a run with the skill loaded did the specific thing the skill exists to prevent.

## Why task 020 is the suspect and not obviously the cause

020 added a mandatory eighth step to `wip → done` — the propagation gate — plus a `grep` pass and a
three-source bound to walk. Both eval cases run under `max_turns: 30`. A longer close procedure
inside a fixed turn budget is a plausible mechanism: reconciliation is step 1, the new work is step
7, and a run that spends turns on propagation has fewer left for care.

**Three runs cannot distinguish a regression from variance**, and this task should not pretend
otherwise. A single failure of a weight-5 grader across three runs moves the mean by roughly this
much on its own. The prior 1.00 was also three runs. Two three-run samples disagreeing by one
grader is weak evidence in both directions.

What makes it worth a task rather than a shrug: the direction is the expensive one. A false alarm
costs a re-measure; a real regression means the gate shipped in `0.6.0` degrades the behaviour the
suite was built to protect, and nothing else in the repository would ever report it.

## What would settle it

The question is *"did `0.6.0` cost reconciliation fidelity, or is the with-arm noisy at n=3?"* —
and it is answerable without guessing at mechanisms:

- **More runs at the same commit.** Raise `runs:` for this case and re-measure `97521e0`. If the
  with-arm returns to 1.00 across a larger sample, it was variance and the only output is a note in
  `evals/README.md` recording that n=3 is too small for this grader.
- **The same larger sample at `0.5.1`** (`main` before the gate). This is the actual control. Both
  arms move together under variance; only a real regression separates them by commit.
- **Read the failing run's trace.** `--keep-temp` preserves each sandbox and `trace.jsonl`. If the
  run hit `max_turns` mid-close, that is visible rather than inferred, and it converts this from a
  statistics question into an observation.

⚠️ **`max_turns: 30` is now a load-bearing number and nothing says so.** If the close procedure has
grown past what 30 turns comfortably fits, then the suite is measuring turn budget rather than
skill-following, and every future step added to `wip → done` will look like a regression. Whatever
this task concludes, that relationship belongs in `evals/README.md` — it is the kind of thing that
is obvious once and invisible afterwards.

## Not to be fixed by loosening the grader

Stated up front because it is the tempting move and it is wrong: the answer is not to lower
`dropped-criterion-not-claimed-met`'s weight, widen its pattern, or raise `max_turns` until the
number comes back. That grader is the case. If the close procedure genuinely no longer fits the
budget, the finding is about the procedure or about the budget — and either is a real result worth
writing down, not a number to tune away.

## Done when

- [ ] `done-when-reconciliation` re-measured at `97521e0` with enough runs to separate signal from
      variance, and the sample size is stated alongside the result rather than left implicit
- [ ] The same measurement taken at the commit before the propagation gate shipped, so there is an
      actual control and not just a comparison against a differently-sized prior sample
- [ ] A verdict recorded: variance, or a regression caused by the longer close procedure. If it is
      a regression, a follow-up task exists for the fix, and the fix is not "adjust the grader"
- [ ] The failing run's trace is read and the task says whether it hit `max_turns` — an observation,
      not an inference from the score
- [ ] `evals/README.md` records what n is adequate for this case's weight-5 grader, and states that
      `max_turns` bounds how much close-time procedure the suite can measure at all
- [ ] `README.md`'s scored table is either updated to the settled numbers or explicitly left at the
      2026-08-09 figures with a note saying which run they are from — it currently reads **1.00 /
      0.88** and no longer matches the newest measurement
- [ ] Every document and open task this change makes wrong is updated, and anything the work
      turned up that nothing yet records is written down — or what was checked is named here,
      with why none of it needed changing
