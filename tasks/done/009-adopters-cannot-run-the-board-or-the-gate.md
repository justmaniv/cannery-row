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
  - tasks/done/007-task-body-contract-is-undocumented-and-unenforced.md
---

# An adopter following the README cannot run the board, or the gate that enforces the contract

## What's wrong

`## Install` tells a new user to create the lane directories and copy `tasks/README.md` into their
repo. That copied file then instructs:

```bash
python3 scripts/generate-task-board.py            # writes docs/task-board.md
python3 scripts/generate-task-board.py --check    # exits non-zero if the board is stale
```

`scripts/` does not exist in their repository. They copied the conventions doc; they did not copy
the script, and `## Install` never mentions it. The plugin installs the *skill* — it does not place
files in a user's repo, and its own copy sits in a cache directory under
`~/.claude/plugins/cache/` that nobody is told about.

So the board — one of four rows in "What's in the box" — has **no adoption path at all**, and the
first command a new user runs from the doc they were told to copy fails with
`No such file or directory`.

## Why this is worse than a broken command

The generator **is** the structural gate. Task 007 made an H1 and a `## Done when` checklist hard
requirements, enforced rather than remembered, and made that the centerpiece of the README. For
every adopter, that enforcement currently does not exist — the enforcer is in a cache directory
they cannot reach. The repository argues for structure over vigilance and then ships vigilance.

`tasks/README.md` even states the enforcement as fact — "refuses to build a board when any task is
missing either element" — in the file that gets copied into a repo where nothing refuses anything.

## Verified, 2026-08-07

- ✅ `SKILL.md` is **clean**. Its regeneration step is deliberately generic, greps for whatever
  projections a project has, and explicitly no-ops when there are none. It never names the script,
  so Claude will not chase a dead path. The defect is confined to the two copied documents.
- ✅ The raw URL serves the script (HTTP 200), and the whole adopter flow works when the file is
  actually present: fresh `git init`, five lane directories, `curl` the script into `scripts/`,
  write one task, generate. Board written, `docs/` created automatically. Then a malformed task —
  gate fires, exit 1, no board. Simulated end to end rather than reasoned about.

## Fix

Give the two copied files a real acquisition step, and say plainly what is lost by skipping it.
`curl` from `main` rather than a cache path: the cache layout is versioned and internal, the raw
URL is stable and one line.

## Done when

- [x] `## Install` shows how to get both `tasks/README.md` and `scripts/generate-task-board.py`
      into an adopter's repo, and states that the plugin ships the skill rather than copying files
- [x] Install says explicitly that the generator is also the gate, so skipping it downgrades the
      H1 / `Done when` contract from enforced to conventional. The claim of enforcement inside
      `tasks/README.md` is now conditional on having the script, since that file is copied into
      repositories where nothing refuses anything.
- [x] `tasks/README.md`'s board section no longer assumes a script the reader does not have
- [x] The documented commands are executed from a clean repository, not assumed — twice. Once
      against `main` via the raw URL (HTTP 200, board written, `docs/` created, malformed task
      caught with exit 1 and no board), and again against this branch's content, including
      `--check` reporting fresh.
- [x] GitHub repo description matches the README's benefit-first lead, and topics are set for
      discoverability
- [x] Version bumped — 0.4.1 → 0.4.2, `tasks/README.md` is shipped content

## Note on the acquisition method

`curl` from `main`, not from the plugin cache. The cache path
(`~/.claude/plugins/cache/cannery-row/cannery-row/<version>/…`) is versioned and internal — it
changes on every release and is not a contract with users. There is no `claude plugin path`
command to resolve it, so documenting the literal path would be documenting an implementation
detail that breaks on the next bump. The raw URL is one stable line.

The trade-off worth recording: a fetched copy does not update itself. That is acceptable and
arguably correct — the script becomes the adopter's file, to edit for their project, and a board
generator that silently changed shape under a user would be worse than one they own.
