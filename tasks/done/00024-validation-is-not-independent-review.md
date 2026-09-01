---
created: 2026-08-09
updated: 2026-08-09
completed: 2026-08-09
status: done
owner: justmaniv
blocked-by: ""
links:
  - README.md
  - skills/task-lifecycle/SKILL.md
  - tasks/done/00016-two-pass-claim-is-unmeasured.md
  - tasks/done/00025-skill-does-not-say-where-its-own-check-stops.md
---

# The README says independence comes free; a field report says it does not

## What happened

A report arrived from the project this was extracted from — the same codebase the README's
provenance section credits, which uses the skill for its own task tracking and separately runs a
project-level rule that load-bearing changes get an adversarial "find the wrong claim" pass by an
agent in a **fresh context** before commit.

On one pickup the two mechanisms disagreed, and the skill's step lost:

1. A task written by a different session was picked up. The skill's **"Before starting: validate the
   task's claims"** step ran as written: both shipped-elsewhere greps (clean), and the load-bearing
   claims checked against the code — four test files opened, the cited tests and assertions all
   present where the task said they were. Validated; work proceeded. ~4 minutes.
2. The deliverable was itself a spec, so the consumer's fresh-context adversarial pass ran before
   commit. It falsified **four** claims the pickup validation had passed.
3. The sharpest was a mechanism that does not exist. The task said a backend test *"injects a
   User-Agent header"*. No test sets any header — the fixture seeds a database column with a raw
   `INSERT`. The cited test existed, at the cited path, asserting the cited thing.
4. That false mechanism had already propagated into three sibling task files, **including a "Done
   when" criterion prescribing a change to a header that does not exist** — a spec a later session
   would have executed verbatim, and the checklist would have confirmed it did.

All four were fixed pre-commit and back-propagated to the source task files with dated correction
notes.

## Why the step missed it

- **Confirmation framing.** As practiced, the step answers *"do the claimed things exist?"* — files,
  tests, line ranges. They all existed. The fabricated part was the *mechanism* ("via a header"),
  which pattern-matched as plausible and was never traced to the fixture.
- **No independence.** The check is performed by a reader who has just absorbed the task's framing.
  By the time it runs, the validator shares the author's context — precisely the condition under
  which a shared hallucination survives. The adversarial pass caught it because it was prompted to
  *falsify* and had read nothing but the code.

## What this contradicts

`README.md`'s opening paragraph, third sentence: *"Independence comes free: the session that didn't
write the spec is the only one that can catch what the spec got wrong."* The second half is still
true and is the project's whole argument. **"Free" is the over-claim.** Independence is available
from a cold session, not automatic — it survives only as long as the reader gets to the code before
the argument, and the pickup step as written does not guarantee that.

This is not the same gap as `tasks/done/00016-*`. That one was about the two-pass claim being
*unmeasured*, and was closed by labelling it an opinion. This is about the claim being *qualified*:
one of the two benefits the opener sells has a stated failure mode and a known escalation.

## Scope

- **README only.** Whether `SKILL.md` should carry the falsification framing and the escalation
  trigger is `tasks/new/00025-*` — it needs a version bump and a decision about eval coverage, and
  neither belongs in a docs change.
- **The skill does not own pair review.** It should say where its own step stops; it should not ship
  a review mechanism. The consumer's rule is the consumer's.
- **Not a rewrite of the opinions section.** `tasks/new/00018-*` already notes the README is long. One
  bullet and one subsection, not a new chapter.

## Done when

- [x] The opener no longer says independence comes free; the qualification names what independence
      depends on rather than just softening the wording — *"available, not automatic", linked to the
      new section*
- [x] The README states plainly what the claim-validation step does *not* establish — that a cited
      artifact existing is not evidence the task's description of *how* it works is true —
      *§ "What validating the spec does not cover", first two paragraphs*
- [x] The falsification framing is stated as the cheaper of the two fixes — *"Do this one first; it
      costs a rephrasing"*
- [x] The escalation trigger is named: tasks whose output is itself a spec other sessions execute,
      because a false mechanism there lands in the acceptance-criteria layer and becomes
      self-enforcing — *second bullet of the same section*
- [x] The README says out loud that an adopter should set up *some* reader that has not read the
      task, without prescribing which mechanism — *closing paragraph of the section, plus the new
      opinion bullet in § "It's opinionated, and it's active"*
- [x] The field report is used as the second worked example, attributed the same way the first one
      is — the project this was extracted from, not this repo — *"From the same project as the
      example above"*

## What was deliberately not done

**The skill was not changed.** The prose that shipped is `README.md` only; `SKILL.md` still teaches
the validation step with no stop line and with confirming framing. That is `tasks/new/00025-*`, held
separate because it crosses the version-bump boundary and reopens the eval-coverage question that
`tasks/done/00016-*` answered once already. A reader who runs the skill and never opens the README
therefore does not yet get this caveat — which is exactly the argument 025 has to settle.

> **Correction, 2026-08-09** (while executing 025): *"the question `016-*` answered once already"*
> over-reads 016. It answered the **session-topology** question and explicitly recommended the
> false-premise case as *"worth doing either way."* 025 inherited this wording and had to argue
> against 016 rather than lean on it.

**This task was written and executed by one session.** The project's own opinion says that is the
weaker arrangement, and it was the right trade for a docs change whose source material arrived
pre-verified from the session that found the failure. Saying so rather than leaving it to be
noticed.
