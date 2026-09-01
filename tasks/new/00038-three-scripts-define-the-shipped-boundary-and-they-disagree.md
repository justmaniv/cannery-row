---
created: 2026-09-01
updated: 2026-09-01
completed:
status: new
owner: justmaniv
blocked-by: ""
links:
  - scripts/check-release.py
  - scripts/check-portability.py
  - scripts/check-skill-args.py
  - .coveragerc
  - .claude-plugin/marketplace.json
  - tasks/done/00036-done-tasks-cannot-be-archived-on-command.md
---

# Three scripts define "what ships" three different ways, and a new shipped file is invisible to two of them

## The divergence

| file | how it defines shipped | shape |
|---|---|---|
| `scripts/check-release.py:48` | `SHIPPED_PREFIXES = ("skills/", "scripts/", "tasks/README.md", ".claude-plugin/")` | **prefixes** — every file under those roots |
| `scripts/check-portability.py:39` | `SCANNED = [...]` | **five hardcoded paths** |
| `scripts/check-skill-args.py:39` | `SCANNED = [...]` | **five hardcoded paths**, a duplicate of the above |
| `.claude-plugin/marketplace.json` | `"source": "./"` | **the entire repository** |

Four answers. `check-release.py` says all of `skills/` and `scripts/` ships and demands a version
bump when any of it changes. The two `SCANNED` lists name five specific files. And what an installed
copy *actually* receives is the whole repository — verified 2026-09-01 by listing
`~/.claude/plugins/cache/cannery-row/cannery-row/0.9.0/`, which contains `scripts/`, `tasks/`,
`docs/`, `evals/`, `CLAUDE.md` and `README.md`.

## Why it matters, concretely

**A new shipped file is silently exempt from the portability and positional-argument gates until a
human remembers to add it to two hand-maintained lists.** Those gates are the ones that keep
stack-coupled vocabulary and `$`-then-digit forms out of files that land in somebody else's
repository — the failure class this project exists to prevent, and the one
`check-portability.py`'s own docstring says *"nobody catches by eye."*

It nearly happened in task 036, and the only reason it did not is luck compounded twice:

1. 036's task file warned about `check-skill-args.py` — but cited it at the wrong lines
   (`:41-46`; it is `:39-44`).
2. `:41-46` is the line range of the **identical** list in `check-portability.py`, which 036's
   file never mentioned at all. The fresh-context falsification read found the second list only
   because it went to check the first citation and found a different file there.

A citation being wrong is what surfaced a gate nobody had listed. That is not a mechanism.

⚠️ **`.coveragerc` had the same hole and it was fixed in 036 rather than here.** `source = scripts`
meant a script bundled under `skills/` was measured by nothing and silently exempt from the 85%
branch floor — a floor with an invisible carve-out, which this repo's own `.coveragerc` comment
says it will not have. Now `source = scripts, skills/task-lifecycle/scripts`. That is a **fifth**
hand-maintained list of where code lives, and it is listed here because the next one will not be
noticed either.

## What is genuinely different, and must survive any fix

These are not four accidental copies of one idea. `check-release.py` deliberately answers *"did
shipped content change, so does the version need to move"* and its comment at `:39-45` reasons about
why `scripts/` is kept whole even though most of it reaches nobody. The `SCANNED` lists answer
*"what crosses into somebody else's repository or context"* (`check-skill-args.py:36-38`) — a
narrower and genuinely different question, and `README.md` is excluded from them on purpose,
because the storefront has to name the neighbours it is compared to.

So **do not collapse them into one list.** The defect is that the *narrow* answer is enumerated by
hand with no gate noticing an omission, while the broad answer is computed from prefixes.

## Candidate approaches, none yet chosen

- **A — derive `SCANNED` from a prefix walk with an explicit exclusion list.** Walk
  `skills/` + `scripts/` + `tasks/README.md` + `.claude-plugin/`, subtract a small named set
  (`README.md`, `check-portability.py` itself, `*_test.py`). A new shipped file is then scanned on
  arrival, and an *exclusion* is a deliberate act somebody has to write down. Inverts the failure:
  today omission is silent, under A inclusion is automatic.
- **B — keep both lists hand-maintained, add a gate that fails when a file under the shipped
  prefixes is absent from either `SCANNED`.** Smaller change, keeps the two questions visibly
  separate, and the lists stay readable. Costs a fourth script.
- **C — one shared definition module imported by all three.** Rejected on sight unless someone
  argues for it: it merges two questions that are correctly different, and the repo is stdlib-only
  by policy, not by accident.

**Recommend A**, on the grounds that the current failure mode is *silent omission* and A is the only
option that removes it rather than detecting it. But `check-portability.py` cannot scan itself, so
whichever is chosen must keep that exemption explicit — it is described in that file as "the one
hole in the gate," and a derived list must not quietly widen it.

## Done when

- [ ] The approach is chosen from the forks above and the reasoning recorded in this file
- [ ] A file added under the shipped prefixes is scanned by **both** `check-portability.py` and
      `check-skill-args.py` without anyone editing a list — or, if B, a gate fails until they do
- [ ] Written test-first: a RED commit adding a failing test that a newly-added shipped file is
      covered, then a GREEN commit
- [ ] `check-portability.py`'s self-exemption stays explicit and is still tested — it necessarily
      contains every term it forbids, and a derived list must not swallow that reasoning
- [ ] `README.md`'s deliberate absence from the narrow lists survives, with the reason still stated
      where a reader will find it
- [ ] `.coveragerc`'s `source` is brought into whatever mechanism is chosen, or a note records why
      it stays separate — it is a fifth hand-maintained list of the same shape
- [ ] `marketplace.json`'s `"source": "./"` and what it actually copies is documented somewhere a
      contributor reads — `CONTRIBUTING.md` is the likely home. Its description was stale until 036
      and claimed the board generator was "fetched from the repository" when installing copies it
- [ ] `CLAUDE.md`'s "Non-negotiable → Portability" section says where the boundary is defined, so
      the next person does not have to find four answers
- [ ] Every document and open task this change makes wrong is updated, and anything the work turned
      up that nothing yet records is written down — or what was checked is named here, with why none
      of it needed changing

---

## Provenance

Surfaced 2026-09-01 by the propagation gate on [[00036-done-tasks-cannot-be-archived-on-command]],
which added the first script to ship beside `SKILL.md` and had to be added by hand to two `SCANNED`
lists and one `.coveragerc` `source` line, none of which any gate would have missed it from.
