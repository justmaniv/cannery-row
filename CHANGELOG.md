# Changelog

Every entry describes what an installed copy receives when you run:

```bash
claude plugin marketplace update cannery-row
claude plugin update cannery-row@cannery-row
# restart the session to apply
```

Only `skills/`, `scripts/`, `tasks/README.md`, and `.claude-plugin/` reach an installed copy. The
README, `CONTRIBUTING.md`, and this repository's own `tasks/` inform — they do not install, so
changes confined to them are not listed here. Nothing changes for you when they merge.

This matters more than it would for a typical library. The artifact is **a procedure Claude
follows**, so a change to it changes behavior inside your repository without changing a line of
your code. *"Why did it start rewriting `blocked-by:` instead of clearing it?"* has an answer, and
it should not require `git log`.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions are the strings
`.claude-plugin/plugin.json` pins, and each is tagged `cannery-row--v<version>` **at the commit
that bumped the manifest** — so the compare links at the bottom are exactly what shipped in that
release, with no docs-only commits mixed in.

There is no `Unreleased` section, and that is deliberate: `check-release.py` requires an entry in
the same change that moves the version, so an entry never exists before the version it names.

## [0.4.4] — 2026-08-07

### Added

- `check-release.py` gained a third check: a version that moves must have a `## [x.y.z]` heading
  in this file. It fires only when shipped content changed *and* the version actually moved, so a
  branch that forgot the bump is told about the bump rather than scolded twice. Heading matching
  is anchored and boundary-guarded — `## [0.4.10]` does not satisfy `0.4.1`, and a version named
  in a paragraph is not an entry.

  A script can only judge that an entry exists, not that it is any good, and a thin entry will
  pass. The failure worth gating is forgetting entirely: that one is silent until an adopter asks
  what changed, whereas a thin entry is sitting in the diff where a reviewer can see it.

## [0.4.3] — 2026-08-07

### Changed

- **Invariant 6 changed, and it changes what the skill does to your task files.** It used to read:

  > No task in `blocked/` references a `blocked-by:` path that points to a `done/` task — those
  > references are either cleared, or the task is moved out of `blocked/`.

  It now reads: no task sits in `blocked/` with every one of its blockers closed, and a
  `blocked-by:` entry whose task has moved is **rewritten to the new path, never deleted**. When
  the last blocker closes, the task is surfaced for re-triage rather than left sitting.

  If you saw Claude *delete* a `blocked-by:` line when a blocker closed, this is why, and this is
  the fix. The old wording contradicted the reverse-dependency sweep two sections below it, which
  had always said to rewrite. Following the invariant destroyed the record of what a task had been
  waiting on and left it in `blocked/` with an empty `blocked-by:` — blocked by nothing, which no
  later sweep would ever surface. Both halves read fine in isolation; proofreading was never going
  to catch it. The eval suite did, on the first two cases ever written.

- The sweep's steps 1 and 2 were rewritten to say the same thing as invariant 6 in the same words,
  including *why* deleting the line is wrong twice over. Agreement between two sections is not
  worth much when only one of them explains itself.

### Added

- `scripts/check-evals.py` — a structural gate asserting the eval suite is well-formed. It reads
  the case files line-wise rather than parsing them, which keeps the no-dependencies rule intact.

## [0.4.2] — 2026-08-07

### Added

- `tasks/README.md` now tells you **how to get `generate-task-board.py`**. The generator is not
  installed with the skill and is not in your repository; before this release the README described
  a board with no way to build it, and the board is the thing that makes the directory legible.
  One `curl`, and the copy is yours to keep and edit.

### Changed

- The same file stopped claiming the H1 / `## Done when` contract is *enforced*. It is enforced
  only if you have the generator and run it. Without the script those two stay conventions —
  running it in CI is what converts them into a build-breaker.

## [0.4.1] — 2026-08-07

### Added

- Unit tests for the three gates that ship in `scripts/` — `check-portability.py`,
  `check-release.py`, `check-workflows.py` — and an 85% branch-coverage floor that breaks the
  build.

  Nothing here changes the skill's behavior. It changes how likely a future release is to break it
  silently: until now CI *ran* the gates without ever testing them, so a carelessly edited regex
  would have passed. `check-workflows.py` is the one that mattered — it is all that stands between
  this public repository and a fork's pull request executing on a self-hosted runner.

## [0.4.0] — 2026-08-07

### Added

- **Invariant 8:** every task file carries an H1 title and a `## Done when` checklist with at
  least one criterion — in every lane, from the moment it is created, not added later when the
  task is closed. A new *"shape of a task file"* section in the skill shows the whole shape, and
  `tasks/README.md` carries the matching contract for humans.

- `generate-task-board.py` **refuses to build a board** when any task is missing either element,
  naming every offending file and what to do about it. Both were silent failures before: a missing
  H1 rendered a blank card and exited 0, and a missing `## Done when` made the completion gate
  vacuous — *"resolve every `- [ ]`"* is trivially satisfied when there are none.

## [0.3.0] — 2026-08-06

### Changed

- **The pre-start check is now triggered by authorship, not age.** It was *"check the task hasn't
  been overtaken"*, run only on a task that had sat for more than one planning cycle. It is now
  *"validate the task's claims"*, run on any task you did not write yourself, however fresh.

  A task can be false the day it was written — the author greps the wrong directory, or reads a
  stale document, and the file is wrong before anyone else opens it. No staleness heuristic will
  ever catch that, and it is the more expensive failure: a stale task wastes a pickup, a false
  premise sends you building the wrong thing with a well-argued spec telling you it's right.

- That check gained a fourth outcome — **a load-bearing claim is false** → rewrite the task against
  what the code actually says *before* starting, and say what was wrong and how you found it, so
  the next reader knows the file was corrected rather than drafted that way. If the correction
  changes the shape of the work rather than its details, hand it back instead of quietly
  redesigning it under the old number.

- The skill's `description` frontmatter changed to match. That string is what Claude reads when
  deciding whether to invoke the skill at all, so leaving it describing the old check would have
  been a silent mismatch.

---

`0.1.0`, `0.1.1` and `0.2.0` predate the pull-request loop and are deliberately untagged — nobody
is diffing them, and reconstructing entries for them now would be archaeology rather than a record.

[0.4.4]: https://github.com/justmaniv/cannery-row/compare/cannery-row--v0.4.3...cannery-row--v0.4.4
[0.4.3]: https://github.com/justmaniv/cannery-row/compare/cannery-row--v0.4.2...cannery-row--v0.4.3
[0.4.2]: https://github.com/justmaniv/cannery-row/compare/cannery-row--v0.4.1...cannery-row--v0.4.2
[0.4.1]: https://github.com/justmaniv/cannery-row/compare/cannery-row--v0.4.0...cannery-row--v0.4.1
[0.4.0]: https://github.com/justmaniv/cannery-row/compare/cannery-row--v0.3.0...cannery-row--v0.4.0
[0.3.0]: https://github.com/justmaniv/cannery-row/releases/tag/cannery-row--v0.3.0
