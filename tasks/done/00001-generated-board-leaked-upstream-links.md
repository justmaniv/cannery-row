---
created: 2026-08-06
updated: 2026-08-06
completed: 2026-08-06
status: done
owner: justmaniv
blocked-by: ""
links:
  - scripts/generate-task-board.py
  - scripts/check-portability.py
---

# The generated board carried two links back to the repo it came from

## What was wrong

`render_board()` emitted a header containing a relative link to
`working-agreement/triage-criteria.md` and a reference to "CI gate 7". Neither exists in any
repository except the one this project was extracted from. Every downstream board would have
shipped a 404 and a foreign gate number, in the *first paragraph* of the artifact meant to sell
the tool.

## Why the portability gate missed it

The gate scanned `scripts/generate-task-board.py` and passed, correctly: the offending text sits
inside an emitted string, and "triage-criteria" is not stack vocabulary. It is a *project artifact
name*, a category the vocabulary list does not and cannot enumerate ahead of time.

The deeper miss is that the gate was scanning **inputs**. What reaches a user is the **output**.

## How it was found

By asking whether the project had been dogfooded, and looking at `docs/task-board.md`. It took one
read of the file. Nobody had read it, because `tasks/` was empty and the board rendered `0 tasks` —
a repository whose entire pitch is task tracking, shipping with an unused tracker.

## Fix

- Header reworded: no relative link, no foreign gate number.
- `docs/task-board.md` added to the portability gate's scanned set, so the emitted artifact is
  checked and not only its generator.
- A link rule added for generated artifacts: any relative markdown link that is not same-directory
  or `tasks/` fails. Vocabulary can be argued for; a 404 cannot.

## Done when

- [x] Board header emits no unresolvable link and no foreign CI gate reference
- [x] `docs/task-board.md` is in the gate's scanned set
- [x] The gate fails on a reintroduced bad link — verified by reintroducing one
- [x] This repo tracks its own work, so the board has content to read
