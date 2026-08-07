---
created: 2026-08-07
updated: 2026-08-07
completed: 2026-08-07
status: done
owner: justmaniv
blocked-by: ""
links:
  - README.md
  - tasks/README.md
  - skills/task-lifecycle/SKILL.md
  - scripts/generate-task-board.py
---

# A task file's body has a contract, and nothing states it or checks it

## The gap

`tasks/README.md` documents frontmatter down to the field, with a comment on every key. It says
nothing about the body. Yet the body carries the two things the tooling actually consumes:

| Element | Read by | Documented? | Enforced? |
|---|---|---|---|
| Frontmatter | the board generator | ✅ field by field | ❌ |
| **H1 title** | the board generator | ❌ never mentioned | ❌ |
| **`## Done when`** | the skill's `wip → done` procedure | ⚠️ referenced 3×, never shown | ⚠️ vacuously |

"Done when" appears three times in `tasks/README.md` — in the WIP-limit rule, in the completion
step, and in the closing note — every time as though the reader already knows what it is. It is
never defined and no example of one appears anywhere in the repository's own documentation. An
adopter copies `tasks/README.md` into their project, gets a complete YAML specification, and has
no signal that the body is anything but free prose.

## Verified failure modes

Both were reproduced against the real generator, not reasoned about:

- **No H1** → the board renders the card with a **blank title**: `**[090](../tasks/new/090-x.md)**
  <br><sub>tester · 2026-08-07</sub>`. Exit code 0. Nothing anywhere reports it.
- **No frontmatter at all** → the card still renders, owner and date silently become `—`. Exit 0.
- **No `## Done when`** → the completion gate is "resolve every `- [ ]`". Zero checkboxes is
  trivially resolved, so a task with no acceptance criteria closes clean and on nobody's authority
  but the closer's. A heading with no items under it has exactly the same hole.

## Why this one matters more than a formatting nit

The whole argument for this project is that the handoff has to carry everything, because the
session that wrote it is gone. "Done when" **is** the acceptance criteria — it is the only part of
the file a later session is held to. A tracker that silently accepts a task with no acceptance
criteria is not enforcing the thing it exists to enforce, and the repository that ships the
argument was making that failure available by default.

Ruling from the maintainer, 2026-08-07: a task **always** needs an H1 and a `## Done when`. Hard
failure, every lane, not a warning and not restricted to `done/`.

## Fix

1. **Enforce.** The generator refuses to write, and `--check` refuses to pass, when any task file
   lacks an H1, lacks a `## Done when` heading, or has that heading with no checklist items under
   it. Loud: the offending path, what is missing, and the fix, per file.
2. **Document.** The root README grows a worked task file — which doubles as the fastest available
   demonstration of what this thing is. `tasks/README.md` gains the body contract next to the
   frontmatter contract. The skill gains it as an invariant, so creation is governed and not just
   validation-after-the-fact.
3. **Lead with the benefit.** The README's opening line states the mechanism ("state as files,
   location is status") and leaves the reader to derive the payoff, which sits 35 lines down. Say
   what you get, then how it works.

## Done when

- [x] Generator fails hard — missing H1, missing `## Done when`, or an empty one — in both write
      and `--check` mode, naming every offending file and what to do about it. Three distinct
      diagnostics, because they are three different mistakes; each names the path and the fix.
      Validation runs **before** rendering, so a broken task produces no board at all rather than
      a board with a warning printed next to it.
- [x] Tests cover all three violations plus the passing case, written before the implementation —
      19 new tests over three seams (`parse_done_when`, `structural_problems`, `main`), committed
      RED before any production code, 70/70 green after. The `main` tests assert the gate stops
      the *artifact*, not just that it prints: exit 1 **and** no file written.
- [x] All six existing task files pass the new gate unchanged — seven, counting this one. Zero
      edits needed to any of them, which is the evidence the contract was already the convention
      and only the enforcement was missing.
- [x] `tasks/README.md` documents the body contract alongside the frontmatter contract
- [x] `SKILL.md` carries the requirement as an invariant, so tasks are created right rather than
      only caught afterwards — invariant 8 plus a "shape of a task file" section with a worked
      example
- [x] Root README opens with the benefit and shows a complete task file
- [x] Portability gate stays green across all new prose
- [x] Version bumped in both manifests — 0.3.0 → 0.4.0

## Scope note

The ruling tightened the fix mid-task, and the wider version is what shipped. The proposal was a
*warning* on a missing H1 and a `done/`-only audit for missing criteria. The maintainer's ruling
was that a task **always** needs both — hard failure, every lane. That is the stronger position
and it cost nothing: every existing task already complied, so the gate landed with no migration.

One thing was added beyond both the proposal and the ruling: a `## Done when` heading with **no
criteria under it** fails too. It is the same hole wearing a hat — the completion gate resolves
every unchecked box, and zero boxes is trivially resolved whether the heading is absent or empty.
Enforcing presence but not content would have left the defect reachable by anyone who wrote the
heading and meant to fill it in later.
