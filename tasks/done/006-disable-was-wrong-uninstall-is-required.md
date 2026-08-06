---
created: 2026-08-06
updated: 2026-08-06
completed: 2026-08-06
status: done
owner: justmaniv
blocked-by: ""
links:
  - CONTRIBUTING.md
  - tasks/done/003-pinned-version-silently-withheld-the-fix.md
---

# CONTRIBUTING told you to disable the installed copy; disabling does not work

## What was wrong

The development loop said to `claude plugin disable cannery-row@cannery-row` before loading a
working checkout from the skills directory. That is not sufficient. **An installed plugin holds its
name whether or not it is enabled**, and the installed copy takes precedence, so the skills-dir copy
never loads:

    cannery-row-dev@skills-dir: ✘ Not loaded — the name "cannery-row" is already taken by an
    installed plugin (cannery-row@cannery-row), which takes precedence.

Anyone following the page as written would have edited one copy and tested another — the exact
failure the page was written to prevent. `claude plugin uninstall` is required.

## How it was found

By running it instead of reasoning about it. The advice was written from the documentation and read
as obviously correct; the tool disagreed on the first try. `plugin list` states the collision
plainly, which is the one reason this was cheap to catch — that line is now quoted in the guide so
the next person recognizes it rather than debugging it.

## Also changed

- **Worktree, not clone.** `git worktree add ~/.claude/skills/cannery-row-dev <branch>` makes
  switching the branch under test one command instead of a re-clone.
- **The branch-install question answered properly.** The skills-dir loop bypasses the marketplace
  entirely — fine for editing a skill, useless for testing anything about how the plugin is
  *fetched*. Both real routes are now documented: a local worktree added as a marketplace, and a
  published `ref`. With the trap that a same-named marketplace **replaces** the existing one.

## Pattern worth noticing

This is the third defect in this repository found by using the thing rather than reading it (001
the board, 003 the pinned version, 006 this). All three passed every automated gate. The gates
check form; only use checks behavior — which is the argument for
`tasks/new/004-author-eval-suite-for-the-skill.md`, now made three times.

## Done when

- [x] `disable` replaced with `uninstall`, with the collision message quoted
- [x] The superseded advice is called out as wrong rather than silently edited away
- [x] Worktree-based loop, and branch-install routes documented with their traps
- [x] Verified by running the whole loop end to end, not by reading the docs
