---
created: 2026-09-01
updated: 2026-09-01
completed:
status: prioritized
owner: justmaniv
blocked-by: ""
links:
  - skills/task-lifecycle/SKILL.md
  - tasks/README.md
  - scripts/generate-task-board.py
  - scripts/check-skill-args.py
  - tasks/new/013-adopters-copy-of-the-generator-drifts.md
  - tasks/wip/035-task-numbers-are-capped-at-three-digits-and-gates-go-blind-past-999.md
---

# Completed tasks accumulate in `done/` forever, with no way to shelve the old ones on command

## What is wanted

An archive operation, invoked through the skill, that moves tasks out of `done/` once they have
been closed long enough to stop being interesting. **Default 14 days, overridable per call.**

## Build it here; the pain is downstream

⚠️ **This repo does not have the problem.** `tasks/done/` holds **19 files** (2026-09-01).
`everything-has-a-price` holds **594**. `generate-task-board.py:36` carries the comment
*"`done/` is 270+ entries and grows monotonically"* — that describes the adopter, not this
repository, and it was already stale when measured.

So do not motivate this on cannery-row's own ergonomics; a 19-file directory needs nothing. The
skill is the product, and its largest consumer is drowning. That is the whole argument, and it is
enough.

**Two motivations that do not survive contact:**

- **Board noise — already solved.** `render_done` (`:278`) collapses the table to `DONE_RECENT = 12`
  (`:38`) with the note *"The full pile is `tasks/done/`; git history is its journey."*
  `render_board_columns` uses `LIVE_LANES`, and `render_blocked_graph` opens with
  `if t.lane == "done": continue`. Nothing in the rendering grows with `done/`.
- **`ls` / `grep` ergonomics** — real, but weak at 19 files and not why this is worth building.

**One that does, and is not obvious:** `structural_problems` (`:151`) validates *every* done file on
every generation and **hard-fails board generation** on a violation. That is a failure surface that
grows monotonically with `done/`, on a gate this repo runs in CI on every proposed change. It is the
one thing that genuinely scales badly, and archiving bounds it.

## This reverses a documented stance, deliberately

`tasks/README.md:11`:

```
└── done/         # completed; archive here for history
```

Today `done/` **is** the archive — the shipped position, not an oversight. This task changes it to
`done/` = recently closed, `archive/` = shelved. Say so; a reader who finds the old sentence should
not have to guess which is current.

## What breaks

### 1. Invariants 1 and 4 both fail on an archived file

`SKILL.md:17` and `:20`:

> 1. `status:` frontmatter value === directory the file is in.
> 4. `completed:` is set if and only if the file is in `done/`.

**Decided 2026-09-01: a new status `done-archived`, in a directory `done-archived/`.** Archive is a
**lane, not a shelf** — this reverses the first draft's recommendation, and it is the better design.

- **Invariant 1 holds unamended.** `status: done-archived` in `done-archived/` satisfies
  "status === directory" by construction. The shelf design needed an *exception clause* on an
  invariant, and an exception is exactly the thing that rots.
- **Invariant 4 still needs its one-line edit** — `completed:` set iff in `done/` **or**
  `done-archived/`. Unchanged under any naming; `SKILL.md:27` requires it in the same change.
- **Every lane list gains one correct entry** rather than a special case. The first draft's
  objection — *"do not invent a status, it makes every consumer of `status:` wrong"* — was wrong for
  this repo: `generate-task-board.py` never reads `status:` at all. The directory is the status;
  `load_tasks` takes `lane` from the path. (Downstream is different — about six scripts in
  `everything-has-a-price` do read the field, and they are on the routing list anyway.)

### The one hazard the name introduces — caught by CI, fixed in one character

`generate-task-board.py:34` derives the board columns by a **positional slice** that assumes `done`
is last. Append `done-archived` to `LANES` and `LIVE_LANES` becomes
`("new", "prioritized", "wip", "blocked", "done")` — `done` is promoted to a live board column.

**The fix is `LIVE_LANES = LANES[:-2]`, and the existing suite already catches the mistake.**
Measured 2026-09-01 by patching a scratch copy and running `generate_task_board_test.py`:

| form | result |
|---|---|
| `LANES += ("done-archived",)`, slice left at `[:-1]` | `FAILED (failures=2, errors=14)` |
| slice changed to `[:-2]` | `OK (70 tests)` |

`test_header_columns_are_the_lanes_in_flow_order` (`:150-153`) feeds `gen.LIVE_LANES` in and asserts
the header against a hardcoded `["new", "prioritized", "wip", "blocked"]`, so the promoted column
reddens the build. This is runtime-silent but **not** CI-silent — do not carry it as a hidden
hazard. The slice stays positional and will re-break when a seventh lane is appended; that test
catches that too, which is the property worth having.

Four more sites hard-code the string and need the same treatment:

| line | code | status after `[:-2]` |
|---|---|---|
| 34 | `LIVE_LANES = LANES[:-1]` | **fixed** by `[:-2]`; pinned by an existing test |
| 315 | `if t.lane == "done": continue` | ⚠️ **still wrong** — an archived task is not skipped, so it enters the mermaid graph as a dependent. No test covers it |
| 327 | `known.lane == "done"` | fine — an archived blocker simply never marks satisfied; decide whether that is wanted |
| 398 | `by_lane["done"]` | fine — `by_lane` is built over all of `LANES`, so archived tasks render nowhere. Probably correct; record the choice |

⚠️ **A green suite does not mean the lane is done.** All 70 tests pass under `[:-2]` because nothing
in the suite exercises a `done-archived` task at all. `:315` is wrong and untested — that gap is the
work, not the slice.

**Verified safe:** `TASK_REF_RE` does **not** falsely prefix-match — `tasks/done-archived/042-x.md`
returns `None`, because the alternation requires `/` immediately after `done`. And no
`startswith("done")` or `glob("done*")` exists in either repo's scripts. The prefix hazard is
confined to the five enumerated sites above.

### 2. Archived numbers leave the cross-branch collision *detector*, not the allocator

Precise, because the loose version of this claim is wrong: **allocation stays safe.** The skill's
numbering scan (`SKILL.md:347, :349`) runs `git ls-tree -r --name-only "$ref" -- tasks/` and
`find "$wt/tasks" -type f -name '*.md'` — both recursive — and `:350`'s `sed -E 's#.*/##'` strips the
directory entirely, so nesting under `archive/` is invisible to the extraction. Archived numbers are
still counted when a new task is numbered.

What goes blind is the downstream *detector*.
`everything-has-a-price/scripts/check-task-numbers.py:77-79`:

```python
# Only these are lanes. A number reused inside `templates/` or an archive
# directory is not a tracker collision.
LANES = ("new", "prioritized", "wip", "blocked", "done")
```

`_tracked_task_files` (`:176-181`) globs only those lanes, and `collisions` (`:95`) and `_task_entry`
(`:106`) both skip a path whose `parts[1]` is not in `LANES`. So a number reused against an archived
task passes gate 20 — the cross-branch backstop that exists because the scan can lose a race. The
scan still catches it; the check that fires when the scan *lost* does not.

**Four more scripts in that repo carry the identical five-lane tuple** and need the same routing:
`check-task-paths.py:55`, `check-doc-references.py:84`, `check-obligation-liveness.py:83`,
`check-review-gate-landing.py:82`.

### 3. `blocked-by:` edges to archived tasks become prose conditions, silently

`generate-task-board.py:60`'s `TASK_REF_RE` hard-codes the five lanes, so
`tasks/done-archived/042-slug.md` does not match and `classify_blocker` (`:191-202`) falls through to
`("external", raw)`. Concretely, and no more dramatically than this: the node is emitted with the
same shape as every other (`:344`) but carries the `external` CSS class — amber fill, and the legend
says *"Amber = a condition, not a task."* The card meta shows `⛔ condition` instead of `⛔ NNN`, and
the label is the raw path (untruncated; `EXTERNAL_LABEL_MAX = 60`). The `satisfied` list cannot
rescue it — that is only appended when `kind == "task"`. Compounding: `load_tasks` (`:206-207`)
iterates `LANES`, so even a matching ref would yield `by_number.get(...) → None` and the label
`"NNN · missing"` (`:326`).

Nothing errors. A live task gated on a closed-then-archived blocker renders as gated on a condition.

## Design

**Age comes from `completed:` frontmatter, never mtime.** mtime does not survive a clone and `git mv`
does not set it meaningfully, so mtime archives everything on a fresh checkout. `completed:` is
authoritative by invariant 4.

**A `done/` task with no `completed:` date is a guard, not a live problem.** Measured 2026-09-01:
**19/19** here and **594/594** downstream carry a non-empty `completed:`. Zero violations. Refuse to
archive such a file and report it — but write it as a guard against a future invariant-4 breach, not
as cleanup of existing corruption, because there is none.

### Invocation — an open fork, not a settled convention

⚠️ **There is no precedent to follow, and the first draft of this task asserted one.**
`SKILL.md` invokes **no repo script anywhere** — `grep -n "scripts/\|python3" skills/task-lifecycle/SKILL.md`
returns nothing. Its Bash is `git mv`, `grep`, and the inline numbering scan. There is no
`$ARGUMENTS` marker either. The plugin ships no `commands/` directory and exactly one skill.

So this change introduces the skill's **first** dependency on a shipped script, and that is a
decision to take deliberately:

- **A — script + a `SKILL.md` section that invokes it.** Deterministic, testable, and `scripts/` is
  inside the shipped boundary so adopters receive it. But it inherits
  [[013-adopters-copy-of-the-generator-drifts]] — the open problem that an adopter's copy of a
  shipped script cannot be updated — and hard-codes a path into prose that is otherwise
  runtime-agnostic.
- **B — procedure in `SKILL.md` only**, as every other operation here is written, with the date
  arithmetic done by the model. No new dependency, consistent with the file, but no test can pin it
  and the arithmetic is exactly what a model does unreliably.

**Recommend A**, on the grounds that a bulk file move with a numeric threshold is the wrong thing to
leave to prose — but take the decision explicitly and record it, rather than inheriting it from this
sentence.

⚠️ **If A: add the new script to `check-skill-args.py`'s `SCANNED` list.** That gate does **not**
scan the shipped boundary — `:41-46` is a hardcoded four-file whitelist (`SKILL.md`,
`tasks/README.md`, `generate-task-board.py`, `docs/task-board.md`). A new script under `scripts/`
ships to adopters while being invisible to it. Note also the pattern is narrower than "`$` then a
digit": `POSITIONAL = re.compile(r"(?<![\w}$])\$(\d)(?![\d.])")` leaves `$14` and `$4.52` alone.

**Default 14 days, overridable per call, plus `--dry-run`** — this is the one lifecycle operation
that moves files in bulk with no per-file human decision behind it.

## Interaction with task 035

If archiving lands first, 035's phase-2 rename must cover `tasks/done-archived/`; if 035 lands first, the
archive operation must emit `%05d`-padded names. Not a blocker either way — whichever goes second
inherits the obligation, and it is cheap to miss.

## Done when

- [ ] The invocation fork above is decided and recorded in this file before implementation starts
- [ ] Tasks move from `done/` to `tasks/done-archived/`, gaining `status: done-archived`, when
      `completed:` is more than N days old — N defaulting to 14 and settable per call
- [ ] Written test-first — a RED commit adding a failing test, then a GREEN commit — per
      `CONTRIBUTING.md`; tests assert the moved set, never merely that the code ran
- [ ] A boundary test pins the comparison at exactly N days, so "more than 14" cannot drift to
      "at least 14" unnoticed
- [ ] A `done/` task with empty or unparseable `completed:` is reported and **not** moved, with a
      test asserting it stays put
- [ ] A dry-run mode lists what would move without moving it
- [ ] `SKILL.md` invariant 4 admits `done-archived/`; invariant 1 is confirmed to need **no**
      amendment, with that reasoning recorded. `done-archived` is added to the lane list and the
      transition is documented alongside the other transitions, with its 14-day default and override
- [ ] `LIVE_LANES = LANES[:-2]`, and the suite is green — `test_header_columns_are_the_lanes_in_flow_order`
      already pins this, so no new test is needed for the slice itself
- [ ] `:315`'s graph skip handles `done-archived` — an archived task must not enter the mermaid graph
      as a dependent — with a test, since nothing currently exercises the new lane
- [ ] `:327` and `:398`'s behavior for archived tasks is decided and recorded (render nowhere is the
      likely answer), with a test per behavioral choice
- [ ] **If a script was chosen:** it is added to `check-skill-args.py`'s `SCANNED` list, with a test
      asserting the list covers it
- [ ] `tasks/README.md:11`'s "archive here for history" is rewritten so `done/` and `archive/` are
      distinguishable by a reader who was not here
- [ ] `TASK_REF_RE` accepts `done-archived/`, with a test asserting a blocker pointing at an archived task
      classifies as `("task", NNN)` and not as an external condition. Decide and record whether
      archived tasks load into the board at all — the edge must resolve either way
- [ ] `structural_problems` is confirmed to still validate archived files, or deliberately scoped to
      exclude them, with the choice recorded — this is the failure surface archiving exists to bound
- [ ] The scan is **verified** to reserve archived numbers by running it against a fixture archive,
      not by reading it
- [ ] `version` bumped in both `.claude-plugin/*.json` with a matching `CHANGELOG.md` heading
- [ ] The `everything-has-a-price` half is **routed, not applied from here** — a task exists there
      covering the five-lane tuple in `check-task-numbers.py`, `check-task-paths.py`,
      `check-doc-references.py`, `check-obligation-liveness.py` and `check-review-gate-landing.py`,
      **and the ~six scripts there that read the `status:` field**, and this file links it
- [ ] Every document and open task this change makes wrong is updated, and anything the work turned
      up that nothing yet records is written down — or what was checked is named here, with why none
      of it needed changing

---

## Correction log

**2026-09-01** — corrected before commit by the fresh-context falsification read `CLAUDE.md` requires
for a deliverable that is itself a spec. Six claims in the first draft were wrong or overstated:

- **The motivation was wrong for this repo.** The draft argued filesystem ergonomics for
  `tasks/done/` — which holds 19 files here. The 594-file directory is downstream. Rewritten to
  motivate on the adopter and on `structural_problems`' growing failure surface, which is the only
  thing here that scales badly.
- **"Archived numbers stop being reserved" was overstated**, and the draft contradicted itself two
  paragraphs later. The allocator walks `archive/` and stays correct; only the cross-branch detector
  goes blind. The `0042` example was also impossible under a `\d{3}` pattern.
- **"SKILL.md instructs Claude to run the script" described a precedent that does not exist** —
  `SKILL.md` invokes no repo script at all. This is the skill's first script dependency, so it is
  now written as an open fork with a recommendation, not a settled convention.
- **`check-skill-args.py` does not scan the shipped boundary** — it is a hardcoded four-file
  whitelist, so the warning was aimed at a gate that would not fire on a new script. Its pattern is
  also narrower than the draft claimed.
- **"Rendered as an unsatisfiable node" was invented vocabulary.** The real behavior is an amber
  `external` CSS class and a `⛔ condition` card marker.
- **The missing-`completed:` case has zero instances** in either repo (19/19 and 594/594 populated).
  Reframed from surfacing existing corruption to a forward guard.

**2026-09-01 (second pass)** — the archive design was decided by the requester as a new status
`done-archived` in a `done-archived/` directory, reversing this file's original *"shelf, not a lane;
do not invent a status"* recommendation. That recommendation was wrong on two counts: it required an
exception clause on invariant 1 (the new design satisfies it unamended), and its stated objection —
that a new status breaks consumers of `status:` — does not hold here, since `generate-task-board.py`
never reads the field. Verifying the new design turned up the `LIVE_LANES = LANES[:-1]` positional
slice, which silently promotes `done` to a live board column the moment a sixth lane is appended;
that is now a criterion rather than a discovery waiting to happen.

**2026-09-01 (third pass)** — the `LIVE_LANES` hazard was overstated as *"nothing errors."* Measured
by patching a scratch copy: the trap form fails the existing suite with 2 failures and 14 errors,
and `LIVE_LANES = LANES[:-2]` passes 70/70. It is runtime-silent but CI-loud, and the fix is one
character — not the structural rewrite this file first prescribed. The real remaining gap is `:315`,
which the green suite does not cover because no test exercises a `done-archived` task.
