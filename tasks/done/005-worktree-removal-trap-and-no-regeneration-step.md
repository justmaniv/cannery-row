---
created: 2026-08-06
updated: 2026-08-06
completed: 2026-08-06
status: done
owner: justmaniv
blocked-by: ""
links:
  - skills/task-lifecycle/SKILL.md
---

# Two defects found by a session using the skill for real work

## Provenance

Reported by an independent session that used the skill end to end to create a task in a large
repository — the first use by someone who was not its author. Both findings are things the author
could not see, which is the whole argument for shipping it.

## 1. The clean-campsite checklist walks you into a trap

`git worktree remove` deletes the directory. Run it from inside that directory — the obvious place
to be, since you were just working there — and the shell's cwd vanishes mid-command. Everything
chained after it dies with `fatal: Unable to read current working directory`, which reads as a git
failure and is not one. The rest of the cleanup silently does not happen.

The skill presented the checklist as a block of commands to walk with no mention of where to stand.

**Corroboration:** the author hit this three separate times in one session while publishing this
repository, and did not recognize it as a skill defect until an outside report named it. Familiarity
is not review.

**Fix:** an explicit caveat with the `cd` to the main tree first, and a note that the failure looks
like a git problem.

## 2. The skill regenerates nothing

A directory-as-tracker naturally attracts generated views — a board, an index, a roll-up. Every one
goes stale the moment a task file is added or moved. The reporting session caught a stale CI-gated
projection by checking on their own initiative; the skill never told them to.

This is a self-inconsistency worth naming: **this repository ships a board generator and the skill
that governs the tracker never mentioned regenerating it.**

**Fix:** a "regenerate any projection of `tasks/` in the same commit" step in the commit section,
with a grep to discover what reads the tracker, and the reason for same-commit rather than
follow-up: split commits mean every bisect between them lands on a tree where the tracker and its
view disagree. No-op where a project has no projection.

## Not reproduced

The overtaken-by-events check was not exercised — that run only created a task, never pulled a stale
one. Still unverified by anyone but the author. `tasks/new/004-author-eval-suite-for-the-skill.md`
covers it.

## Also confirmed working

The collision-safe numbering scan. A plain `ls tasks/` would have returned a stale maximum — three
task numbers existed only as commits and as a sibling worktree's uncommitted files. The all-refs
plus all-worktrees scan returned the right number first try. That is the one piece of this skill
whose cost is obvious and whose benefit is invisible until it saves you, so a confirmed save is
worth recording.

## Done when

- [x] Worktree-removal caveat in the clean-campsite gate, with the `cd`-first form
- [x] Regeneration step in the commit section, with discovery greps and the same-commit rationale
- [x] Version bumped in both manifests so the fix actually reaches installed copies
- [x] Reporter told what landed
