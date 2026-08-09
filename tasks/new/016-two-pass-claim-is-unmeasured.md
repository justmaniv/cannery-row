---
created: 2026-08-08
updated: 2026-08-08
completed: ""
status: new
owner: justmaniv
blocked-by: ""
links:
  - tasks/done/004-author-eval-suite-for-the-skill.md
  - tasks/new/014-eval-suite-covers-two-transitions.md
  - tasks/new/015-eval-deltas-pin-no-model.md
  - evals/README.md
  - README.md
---

# The README's headline claim is the one thing the eval suite does not measure

## Context

`README.md`'s opening now leads with two-pass execution: one session writes the task, a *different*
session executes it, every time and on purpose. It argues two benefits — the executing session gets
a window holding one task instead of the reasoning that produced it, and it gets an independent read
that can catch a premise the author could not.

Both are arguments. Neither is measured, and the front page is where the project makes its strongest
claim.

What the suite measures today is a different axis. `--ablation with-without` varies **whether the
skill is present** inside one session, and the two shipped cases score **+0.50** and **+0.115** on
that axis. Every case is single-session by construction: the scaffold lays down a repository state,
one agent acts, graders read what it left. Nothing anywhere varies **how many sessions** the work
crosses, so the claim that two passes beat one is supported by a worked example and an argument from
first principles — and nothing else.

The worked example in `README.md` (a task claiming a table was never seeded; seven migrations
already doing it; caught in four minutes by the session that picked it up) is real and it is
evidence. It is also n=1, retrospective, and self-reported by the project making the claim.

## Why this is not just another case in 014

`tasks/new/014-*` adds cases along the existing axis — three more transitions the skill teaches and
a model would not guess. This is a different independent variable, and the harness may not be able
to express it. That question is the first piece of work here, not an implementation detail:

**`--ablation with-without` compares plugin-on to plugin-off. This comparison needs both arms
plugin-on and the *session topology* varied instead.** A case is one prompt to one agent. A two-pass
arm needs session A to produce a task file, then session B to start cold holding only that file —
two agent invocations with a filesystem handoff between them and no shared context. Whether
`case.yaml` can express that at all is unknown and cheap to find out.

## The fork

| Option | Trade-off |
|--------|-----------|
| **Two-arm case inside the harness** — arm 1: one session plans and executes; arm 2: session A writes the spec, session B executes it cold | The honest comparison, and the only one that produces a delta on the actual claim. Requires the harness to chain two agents with a handoff; if it cannot, this option does not exist. |
| **Two separate cases, compared by score** — one single-session case, one where the scaffold *contains* a pre-written spec | Expressible today with no harness change. But the arms differ in prompt and starting state, so the difference is not a delta in the sense `evals/README.md` uses — and a pre-written spec in a scaffold is not the same thing as a spec an agent actually produced. Weakest evidence, cheapest to get. |
| **Measure the independence half only** — scaffold a spec with a deliberately false premise, grade whether the cold session catches it before building | Narrow, but it targets the benefit that matters most and is the one the worked example already demonstrates. Says nothing about the clean-window half. |
| **Don't measure it; mark it as an argument** | Free, and honest if said out loud. The README stops implying the claim is validated, and `evals/README.md` records why this axis is out of reach. |

Recommendation: **answer the harness question first, then take option 1 if it is available and
option 3 if it is not.** Option 3 is worth doing either way — the false-premise case is the sharpest
single thing in this whole area, and it is the failure the project has actually observed. Option 2
buys a number that would need a paragraph of caveats to read correctly, which is how the suite's two
earlier mistakes started.

⚠️ Whatever ships, the trap from task 004 applies twice over here: a case that measures the model
rather than the topology will still print a number, and this number would sit on the front page next
to the project's main claim. **A delta near zero means the case is wrong, not the methodology** —
but it could equally mean the methodology does not pay off on work this small, and those two are
not distinguishable by staring at the score. Say which one you concluded and how you ruled the other
out.

## Done when

- [ ] Whether `claude plugin eval` can chain two agents with a filesystem handoff and no shared
      context is answered in writing, before any case is designed
- [ ] Either a case exists measuring two-pass against one-pass on the same work, with its delta
      recorded — or the decision not to measure it is recorded in `evals/README.md` with the reason
- [ ] `README.md` does not imply the two-pass claim is measured while it is not; if it stays
      unmeasured, the opening says it is an argument and points at the worked example as the n=1
      evidence it is
- [ ] If a case ships: `evals/README.md`'s case table, the README's with/without table, and the
      suite's recorded cost and runtime are all updated together
