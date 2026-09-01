<!--
  GENERATED FILE — do not hand-edit.
  Source: tasks/<status>/NNN-*.md frontmatter + H1 titles.
  Regenerate: scripts/generate-task-board.py  (--check reports staleness)
-->

# Task board

Projection of `tasks/` — the directory is the tracker, this is its view. Columns are the
lanes in flow order; `prioritized/` is in pull order. Regenerated on demand, not on every
move — so this view can lag the tracker, and the tracker wins.
Cards show `owner · last updated`, and `⛔` on a blocked task — a task number when another
task gates it, `condition` when nothing but a judgement call does.

**36 tasks** — 13 new · 1 prioritized · 0 wip · 2 blocked · 20 done.

WIP limit: within 3 per human owner.

| new (13) | prioritized (1) | wip (0) | blocked (2) |
|---|---|---|---|
| **[00012](../tasks/new/00012-install-is-verified-once-by-hand.md)** Installability is the product, and it is checked once by h…<br><sub>justmaniv · 2026-08-07</sub> | **[00036](../tasks/prioritized/00036-done-tasks-cannot-be-archived-on-command.md)** Completed tasks accumulate in `done/` forever, with no way…<br><sub>justmaniv · 2026-09-01</sub> | _nothing pulled_ | **[00019](../tasks/blocked/00019-user-cannot-opt-out-of-remote-operations.md)** A user can turn off remote and host operations even when a…<br><sub>justmaniv · 2026-08-11 · ⛔ condition</sub> |
| **[00013](../tasks/new/00013-adopters-copy-of-the-generator-drifts.md)** The adopter's copy of the board generator can never be upd…<br><sub>justmaniv · 2026-08-07</sub> |  |  | **[00027](../tasks/blocked/00027-prior-coverage-sweep-is-scoped-so-it-cannot-prove-absence.md)** The prior-coverage sweep certifies an absence it never est…<br><sub>justmaniv · 2026-08-12 · ⛔ 00029</sub> |
| **[00014](../tasks/new/00014-eval-suite-covers-two-transitions.md)** Three of the five transitions worth testing have no eval c…<br><sub>justmaniv · 2026-08-07</sub> |  |  |  |
| **[00015](../tasks/new/00015-eval-deltas-pin-no-model.md)** The eval numbers have no model attached, so they expire wi…<br><sub>justmaniv · 2026-08-07</sub> |  |  |  |
| **[00018](../tasks/new/00018-capability-surface-is-undocumented.md)** Nobody can say what Cannery Row's feature set is, includin…<br><sub>justmaniv · 2026-08-09</sub> |  |  |  |
| **[00021](../tasks/new/00021-numbering-scan-worktree-half-scans-nothing.md)** The numbering scan's worktree half silently scans nothing<br><sub>justmaniv · 2026-08-30</sub> |  |  |  |
| **[00022](../tasks/new/00022-task-root-is-hardcoded-to-repo-root.md)** The task tree can only live at `<repo>/tasks/`, which some…<br><sub>justmaniv · 2026-08-11</sub> |  |  |  |
| **[00023](../tasks/new/00023-no-public-signal-for-what-to-build-next.md)** Nobody outside the repo can say which of these tasks matte…<br><sub>justmaniv · 2026-08-09</sub> |  |  |  |
| **[00028](../tasks/new/00028-a-shipped-version-went-untagged-as-010-said-it-would.md)** A shipped version went untagged, which is the one conditio…<br><sub>justmaniv · 2026-08-30</sub> |  |  |  |
| **[00029](../tasks/new/00029-propagation-sweep-hardcodes-two-directories.md)** The searches the skill hands out look in two named directo…<br><sub>justmaniv · 2026-08-11</sub> |  |  |  |
| **[00030](../tasks/new/00030-the-with-arm-regressed-on-the-grader-that-case-exists-for.md)** The with-skill arm ticked a criterion that never came true…<br><sub>justmaniv · 2026-08-11</sub> |  |  |  |
| **[00031](../tasks/new/00031-a-project-cannot-say-where-else-to-look-for-work.md)** A project can tell this tool where else to look for its wo…<br><sub>justmaniv · 2026-08-12</sub> |  |  |  |
| **[00033](../tasks/new/00033-the-mandated-second-reader-has-write-access-it-does-not-need.md)** The mandated second reader runs with write access it does…<br><sub>justmaniv · 2026-08-12</sub> |  |  |  |

## Blocked-by graph

```mermaid
graph LR
  X1["|"]
  T19["00019 · user-cannot-opt-out-of-remote-operations"]
  T29["00029 · propagation-sweep-hardcodes-two-directories"]
  T27["00027 · prior-coverage-sweep-is-scoped-so-it-cannot-prove-absence"]
  X1 --> T19
  T29 --> T27
  classDef satisfied fill:#EAF2EA,stroke:#3A7D44,color:#1F3D24;
  classDef external fill:#F4F1E8,stroke:#B58500,color:#5A4300;
  class X1 external
```

Edge reads *blocker → blocked*. Green = blocker already closed (stale reference). Amber = a condition, not a task.

## done (20)

Collapsed — the 12 most recently completed of 20. The full pile is `tasks/done/`; git history is its journey.

| # | Task | Completed |
|---|---|---|
| [00035](../tasks/done/00035-task-numbers-are-capped-at-three-digits-and-gates-go-blind-past-999.md) | Task numbers are capped at three digits, and the numbering scan and five adopter gates fail silently past 999 | 2026-09-01 |
| [00034](../tasks/done/00034-numbering-scan-is-best-effort-and-its-worktree-half-is-corrupted-at-render.md) | The numbering scan is presented as the safeguard, and its worktree half is corrupted before Claude reads it | 2026-08-30 |
| [00032](../tasks/done/00032-same-commit-regeneration-rule-is-too-chatty.md) | Regenerating the board in the same commit is too chatty for a multi-session repo — make it on-demand | 2026-08-12 |
| [00020](../tasks/done/00020-task-template-has-no-docs-criterion.md) | A closure's findings reach the docs and the open tasks they change, not just whoever remembers | 2026-08-11 |
| [00026](../tasks/done/00026-the-second-reader-is-advice-not-a-rule.md) | The README recommends a second reader and gives nobody a way to have one | 2026-08-09 |
| [00025](../tasks/done/00025-skill-does-not-say-where-its-own-check-stops.md) | The skill teaches the validation step and never says where it stops | 2026-08-09 |
| [00024](../tasks/done/00024-validation-is-not-independent-review.md) | The README says independence comes free; a field report says it does not | 2026-08-09 |
| [00017](../tasks/done/00017-skill-assumes-a-remote-exists.md) | The skill mandates a push, so it fails on a project that has no remote | 2026-08-08 |
| [00016](../tasks/done/00016-two-pass-claim-is-unmeasured.md) | The README's headline claim is the one thing the eval suite does not measure | 2026-08-08 |
| [00011](../tasks/done/00011-no-changelog.md) | An adopter who updates cannot find out what changed | 2026-08-07 |
| [00010](../tasks/done/00010-releases-have-no-tags.md) | Eight versions have shipped and none of them is findable in git | 2026-08-07 |
| [00009](../tasks/done/00009-adopters-cannot-run-the-board-or-the-gate.md) | An adopter following the README cannot run the board, or the gate that enforces the contract | 2026-08-07 |
