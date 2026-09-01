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
  - skills/task-lifecycle/SKILL.md
---

# Three of the five transitions worth testing have no eval case

## Context

Task 004 built the suite and wrote two of the five cases it named. The other three were left
deliberately, and they are the ones where the skill does something a model would not do on its own
— which, per 004's measured result, is exactly where a case earns its cost. The two that shipped
score **+0.50** and **+0.115**; the shape of the winner is "cross-file consequence nobody asked
for", and all three below have that shape.

Read `evals/README.md` before writing any of these. It documents the grader-cost model, three
graders that passed while proving nothing, and the design rule that decides whether a case is worth
running at all.

## The three, hardest first

**Collision-safe numbering.** The skill's numbering scan reads every ref *and* every worktree,
because two branches picking the same "next" number is its stated #1 collision source. The case
needs a scaffold with a second worktree holding an uncommitted `NNN-*.md`, then asks for a new task
and checks the number picked accounts for it.

⚠️ **Unverified and the reason this is listed first:** the eval sandbox runs with a synthetic
`HOME`, and whether `git worktree add` behaves there is unknown. Find that out before designing the
case — if worktrees do not work in the sandbox, the case has to be rebuilt around a second *ref*
instead, which tests less but still tests something. Budget a throwaway scaffold to answer it.

**Overtaken-by-events.** A task whose work already shipped under a different number. The skill says
close it with the evidence rather than restart it. The scaffold needs a git history where the grep
in the skill's validation step actually hits — a commit whose message names the number, and a file
that implements it. Graded on: did it *check*, and did it close rather than build.

**Invariant refusal.** A state that cannot satisfy an invariant — the sharpest is a task with a
`## Done when` heading and nothing under it, being asked to close. The skill says stop and surface,
don't move the file. This is the one case whose expected outcome is the agent **not** acting, so
grade `landed-in-done` inverted and put the weight on the refusal being *explained* rather than
silent.

## Watch for

The trap 004 hit twice: writing a case around something the model gets right unaided, then
reporting the score as if the skill earned it. Run `--ablation with-without` on each before
committing it. **A delta near zero means the case is wrong, not the skill.** Two of the three above
are guesses about where the skill matters, and the guesses in 004 were wrong both times.

## Done when

- [ ] Whether `git worktree add` works in the eval sandbox is answered, in writing, before the
      numbering case is designed
- [ ] All three cases exist under `evals/`, each with a scaffold and a recorded delta
- [ ] Every case shows a real delta, or is dropped with the measurement that killed it recorded —
      a case that tests the model is worse than no case, because it reports a number
- [ ] `evals/README.md`'s case table and the README's with/without table both updated
- [ ] Total suite cost and runtime re-measured and recorded; 004's figures ($4.52 / 12m09s) are
      for two cases and stop being true
