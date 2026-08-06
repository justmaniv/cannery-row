---
created: 2026-08-06
updated: 2026-08-06
completed: ""
status: new
owner: justmaniv
blocked-by: ""
links:
  - CONTRIBUTING.md
  - skills/task-lifecycle/SKILL.md
---

# Nothing tests whether the skill is followed, only that it is well-formed

## The gap

CI proves the skill is portable, the manifests load, the board generator is correct, and the
workflows are safe. Every one of those is a check on *form*. None of them runs the skill and asks
whether Claude did the right thing with it.

That is the only property anyone installing this actually cares about.

`claude plugin eval` exists for this: scored cases (`evals/**/case.yaml`), graders, and an
`--ablation with-without` arm that runs the same case with the plugin disabled, so the score
difference attributes the outcome to the skill rather than to the model being competent anyway.
`--threshold` makes it a build gate.

## Cases worth writing first

Pick the transitions where getting it wrong is silent — a wrong answer that still looks like work:

- **Reverse-dependency sweep on close.** A task moves to `done/`; another task's `blocked-by:`
  points at its old path. Does the sweep happen? This is the highest-value case: skipping it leaves
  work sitting in `blocked/` behind something finished, and nothing surfaces it.
- **"Done when" reconciliation.** An unmet checklist item must become `- [x]` or a struck-through
  line with a reason — never a pre-filled ✅ on something that did not happen.
- **Overtaken-by-events check.** A stale task whose work already shipped under another number
  should be closed with evidence, not restarted.
- **Collision-safe numbering.** With a second worktree holding an uncommitted `NNN-*.md`, does the
  next number account for it, or does it collide?
- **Invariant refusal.** Given a state that cannot satisfy an invariant, the skill says stop and
  surface — it does not move the file anyway.

## Cost note

Eval runs cost model calls, and `--runs` defaults to 3 per case. Decide whether this gates every PR
or runs on a schedule before wiring it into CI; a suite that is too expensive to run is a suite
that gets disabled.

## Done when

- [ ] `evals/` suite exists with at least the reverse-sweep and "Done when" cases
- [ ] `--ablation with-without` shows a real score delta — if the baseline scores the same, the case
      is testing the model, not the skill, and needs rewriting
- [ ] A decision recorded on whether this gates PRs or runs on a schedule, with the cost that drove it
- [ ] `CONTRIBUTING.md` updated to point at it instead of naming this task
