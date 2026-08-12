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

## [0.7.0] — 2026-08-12

### Changed

- **Projections of `tasks/` are refreshed on demand, not regenerated as part of a status move**
  (task 032). *"Regenerate any projection of `tasks/` in the same commit"* is gone from the Commit
  block, along with its discovery snippet. **This changes what happens in your repository**: the
  skill will no longer regenerate your board, index, or roll-up when it moves a task, and it will
  not treat a stale one as an unfinished move.

  The rule it replaces (0.4.x, task 005) had a real argument — split commits mean a bisect between
  them lands on a tree where the tracker and its view disagree. What that argument never priced is
  concurrency. A projection is one file that *every* lane change rewrites, so where parallel
  sessions are normal it becomes the most contended file in the tree, and the conflict is pure
  ceremony because the file is derived. Nobody hand-merges two renderings of the same directory.
  Measured in an adopter running concurrent sessions as its default: the board changed in **204 of
  894 commits over 30 days**, while regenerating it costs **~0.2s**. Making the rule cheaper to run
  would not have helped — it was already free. The cost is the collision, and it lands on whoever
  merges second.

  ⚠️ **If your project fails a build on a stale projection, you must change something too.** A
  freshness check fails on a stale view, and a task move now leaves the view stale — so every
  task-move change goes red, and the fix is to hand-run the generator anyway. That combination is
  strictly worse than either alternative. Either keep regenerating as part of the move as a
  *project* rule, or drop the check. `tasks/README.md` states the trade with both rows; the skill
  now tells you to follow whichever the project chose rather than adding a gate on its behalf.

- **`scripts/generate-task-board.py` no longer stamps the old rule into the board it generates.**
  The header line said *"Move a file, regenerate, commit."* — it now says the board is regenerated
  on demand and that the tracker wins when the two disagree. Behaviour, `--check` mode, and the
  structural refusal on a missing H1 or `## Done when` are unchanged.

- **`tasks/README.md`** carries the same correction, plus the `--check`-in-CI trade as a table with
  two defensible answers instead of a blanket recommendation.

## [0.6.0] — 2026-08-11

### Added

- **A propagation gate at close** (task 020). Closing a task now has a step between the
  reverse-dependency sweep and the campsite check, and a new invariant 9 behind it: what the
  closure made wrong gets corrected, and what the closure turned up gets written down somewhere it
  will be read again.

  The gap it fills is narrow and worth stating precisely. Every other thing this skill propagates
  is reachable by walking a path — the sweep walks the tasks that name this one, the projection
  step walks whatever reads `tasks/`, the phase check walks a document the project already
  identified. **Content has no path to walk**, so the artifact that describes what you just changed,
  and never mentions
  your task, was never visited by anything. Neither was the thing you learned during the work that
  no document says at all — no sentence is wrong, a sentence is missing, and the only session that
  can write it is the one about to end.

  ⚠️ **This is not the reverse-dependency sweep**, and it will be mistaken for it. That sweep finds
  tasks that *name* this one and rewrites a stale path; it is bookkeeping on a reference. The new
  gate reads for content that stopped being true, and its most valuable hits are files that never
  named the task.

  Two things keep it from becoming an unbounded sweep, because *"update everything relevant"* is
  satisfied by finding nothing and refuted by nothing:

  - **A bound** — what already cites the work (`grep -rl "NNN-slug" tasks/ docs/`), the task's own
    `links:`, and the artifacts you had to read to do the work. The third has no query behind it
    and is the one that reaches the missing sentence.
  - **A stopping rule** — name the artifact and route it to the task that owns it. You are not
    obliged to fix every site you find. This is the same call the sweep already makes one step
    over, where it surfaces newly-unblocked tasks rather than moving them itself.

- **A third line in the task-file template**, in both `tasks/README.md` and the skill's copy, worded
  identically: *"Every document and open task this change makes wrong is updated, and anything the
  work turned up that nothing yet records is written down — or what was checked is named here, with
  why none of it needed changing."*

  `- [ ] Docs updated` would have been worse than no line: tickable without opening a file, green
  forever. The wording is unsatisfiable in silence — a closer who ticks it having named nothing has
  visibly not resolved it, and the strikethrough convention already covers the honest "nothing
  applied" case.

  It is a **default, not a requirement**. Invariant 9 holds whether or not a task file carries the
  line, so an author who deletes it changes nothing about the obligation — same relationship the
  campsite gate has to the tasks that never mention it.

### Changed

- **The board generator gates exactly what it gated before, deliberately.** Making it refuse a task
  whose checklist lacks the propagation line was considered and declined; the reasoning is now a
  comment in `structural_problems()` so it does not get re-proposed as an oversight. A grep can see
  that a *line exists*; it cannot see that anything was read. Gating on the line teaches authors to
  keep the line, which manufactures the always-green box the wording exists to prevent — and hands
  it a passing build as evidence. H1 and `## Done when` survive that test because presence *is* the
  property being checked. This one isn't.

- The skill's `description:` frontmatter names the new gate. That string is what Claude reads when
  deciding whether to invoke the skill, so leaving it describing the old procedure would have been
  a silent mismatch — the same slip 0.5.1 fixed.

- The marketplace entry said the plugin *"ships the task-lifecycle skill and a generated board
  view."* It does not ship the board view — that is the `curl` above, and the sentence contradicted
  the `check-release.py` correction in the same release.

- `check-release.py`'s comment on `SHIPPED_PREFIXES` said it was *"what an installed copy actually
  receives."* It isn't, and the difference is the thing an adopter needs to know: `skills/` and
  `.claude-plugin/` travel with the plugin version, so you get them by updating. **`tasks/README.md`
  and `scripts/` never install** — you fetched them with `curl` and you re-fetch them the same way.
  So the template line above is live for anyone fetching from `main` today, and an existing adopter
  who pinned nothing will not see it until they re-run the `curl` from the README's Install section.
  The bump is what forces this entry to exist; it is not what delivers those two files.

## [0.5.1] — 2026-08-09

### Changed

- **The claim-validation step now says where it stops, and tells you to read against the claim
  rather than for it** (task 025). Two changes to § *"Before starting: validate the task's
  claims"*, both small:

  *"Read the code before you trust the task"* now adds that you read it to **break** the claim, not
  to confirm it — *"check this claim"* finds the thing the task cited and stops there; *"try to
  prove this wrong"* opens what that thing actually does.

  A closing paragraph states what the step does not establish. It is answered by a reader who has
  just absorbed the task's argument, so it is validation and not an independent read, and it is
  weak against a claim about *how* something works where every citation is real and the mechanism
  is invented. When the task's output is itself a spec, that kind of error reaches the `## Done
  when` list and becomes self-enforcing — so it names the escalation: a reader that was not in the
  conversation which accepted the task.

  **The skill still ships no review mechanism and does not prescribe one.** It marks the boundary;
  what you put on the other side of it is yours. The field case behind this is one where every
  cited test existed and asserted the cited thing, and the task's account of *how* — a request
  header — was invented; it had already reached three sibling tasks, one as an acceptance
  criterion.

  Nothing about the four outcomes, the two greps, or when the step fires has changed. If you were
  following this section, you keep following it; it now admits a case it does not close.

## [0.5.0] — 2026-08-08

### Changed

- **The skill no longer assumes a remote exists** (task 017). The section that closed every
  transition as "commit + push" is now **Commit** — the invariant, because provenance needs
  history, not a remote — plus **Push, when a remote exists**, gated on `git remote` printing
  anything. On a repository *with* a remote nothing changes: pushes still happen immediately, at
  the same points and cadence as before. On a local-only repository the skill no longer instructs
  a command that exits non-zero on every transition.
- Incidental host assumptions swept from the skill and `tasks/README.md`: `origin/main` in the
  campsite worktree step, "an open PR" in branch cleanup, "PR-protected" in the numbering
  rationale, and "a PR number" in the overtaken check. Each now reads correctly for a repository
  with no host attached.
- The skill now states its baseline once, in the Commit section: git is assumed — a remote is not.

### Added

- `check-portability.py` forbids host-workflow vocabulary in shipped files: `origin`, `PR`,
  `pull request`, `branch protection`. This is the class the gate's docs claimed to cover while
  its term list didn't, and the second portability class found by eye after passing CI. All-caps
  terms match as exact case-sensitive words so `PR` cannot swallow "provenance". `push`, `remote`,
  and `fork` are deliberately not forbidden — the reasons are recorded at the term table, and a
  test pins the `push` decision so a future sweep cannot quietly break the skill's own gate.

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

⚠️ **`0.5.1` is untagged by accident, not by choice**, which is why `0.6.0` above compares against
`0.5.0` and why `0.5.1` has no link line. Found 2026-08-11 during task 020's independent read.
Tagging it retroactively is an outward-facing act on the remote, so it is routed rather than done
in passing — `tasks/new/028-a-shipped-version-went-untagged-as-010-said-it-would.md`, which is the
escalation task 010 pre-wrote for exactly this condition.

[0.7.0]: https://github.com/justmaniv/cannery-row/compare/cannery-row--v0.6.0...cannery-row--v0.7.0
[0.6.0]: https://github.com/justmaniv/cannery-row/compare/cannery-row--v0.5.0...cannery-row--v0.6.0
[0.5.0]: https://github.com/justmaniv/cannery-row/compare/cannery-row--v0.4.4...cannery-row--v0.5.0
[0.4.4]: https://github.com/justmaniv/cannery-row/compare/cannery-row--v0.4.3...cannery-row--v0.4.4
[0.4.3]: https://github.com/justmaniv/cannery-row/compare/cannery-row--v0.4.2...cannery-row--v0.4.3
[0.4.2]: https://github.com/justmaniv/cannery-row/compare/cannery-row--v0.4.1...cannery-row--v0.4.2
[0.4.1]: https://github.com/justmaniv/cannery-row/compare/cannery-row--v0.4.0...cannery-row--v0.4.1
[0.4.0]: https://github.com/justmaniv/cannery-row/compare/cannery-row--v0.3.0...cannery-row--v0.4.0
[0.3.0]: https://github.com/justmaniv/cannery-row/releases/tag/cannery-row--v0.3.0
