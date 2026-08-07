---
created: 2026-08-07
updated: 2026-08-07
completed: ""
status: new
owner: justmaniv
blocked-by: ""
links:
  - tasks/done/009-adopters-cannot-run-the-board-or-the-gate.md
  - tasks/README.md
  - scripts/generate-task-board.py
---

# The adopter's copy of the board generator can never be updated

## Context

Task 009 gave the generator an adoption path: `curl` it from `main` into the adopter's `scripts/`,
because the plugin installs a skill and does not place files in anyone's repository. That fixed a
genuine dead end — before it, the first command in the copied conventions doc failed outright.

It also created a second one, one step further along. The curled file is now **a fork with no
upstream**. Nothing records which revision they took, nothing tells them a newer one exists, and
nothing tells *us* that adopters are running a generator from three versions ago. The file is
explicitly "theirs to keep and edit", which is the right call — but "yours to edit" and "no way to
find out what you're missing" are different properties, and only the first was decided.

This is the same shape as the defect that produced [[003-pinned-version-silently-withheld-the-fix]]:
a fix lands upstream, both ends look healthy, and it reaches nobody.

## Why it bites during a trial

The generator **is** the structural gate — it refuses to build a board from a task missing its H1
or its `## Done when` (task 007). So an adopter on an old copy silently has weaker enforcement than
the README describes, and the README is what they will quote back when it does not behave.

## Options

| Option | Trade-off |
|--------|-----------|
| **Stamp a version header on the file** | One comment line the curl carries with it; `--version` prints it. Makes drift *visible* when someone asks, but still nobody checks. Nearly free. |
| **`--check-upstream` flag** | The generator fetches its own raw URL and reports if it differs. Self-updating-ish, no infrastructure. Adds a network call to a script whose whole appeal is having no dependencies, and it fails closed in an offline CI. |
| **Ship it as a plugin command instead of a curl** | Removes the copy entirely — the adopter runs the plugin's copy, which updates with the plugin. Biggest change, and it reverses task 009's reasoning that the cache path is versioned and internal. Worth re-examining anyway: `plugin update` is a real update path and `curl` is not. |
| **Do nothing, document it** | Honest. The file is 250 lines and an adopter who edits it has forked deliberately. |

Recommendation: **stamp the version, and re-examine the plugin-command option properly** — task 009
ruled out the cache path for good reasons, but it was solving "how do they get it at all", not "how
do they keep it current", and those may not have the same answer.

## Done when

- [ ] A decision recorded, with the drift risk weighed against adding a network call or a dependency
- [ ] If the curl stays: the fetched file carries something identifying its revision, and
      `tasks/README.md` says how to re-fetch
- [ ] `tasks/README.md`'s acquisition step reflects whatever wins — it is the copied file, so a
      stale instruction there propagates into every adopting repository
