---
created: 2026-09-01
updated: 2026-09-01
completed:
status: wip
owner: justmaniv
blocked-by: ""
links:
  - skills/task-lifecycle/SKILL.md
  - tasks/README.md
  - scripts/generate-task-board.py
  - scripts/check-skill-args.py
  - scripts/check-portability.py
  - tasks/new/00013-adopters-copy-of-the-generator-drifts.md
  - tasks/done/00035-task-numbers-are-capped-at-three-digits-and-gates-go-blind-past-999.md
---

# Completed tasks accumulate in `done/` forever, with no way to shelve the old ones on command

## What is wanted

An archive operation, invoked through the skill, that moves tasks out of `done/` once they have
been closed long enough to stop being interesting. **Default 14 days, overridable per call.**

## Build it here; the pain is downstream

⚠️ **This repo does not have the problem.** `tasks/done/` holds **20 files** (2026-09-01).
`everything-has-a-price` holds **596**. `generate-task-board.py:36` carries the comment
*"`done/` is 270+ entries and grows monotonically"* — that describes the adopter, not this
repository, and it was already stale when measured.

So do not motivate this on cannery-row's own ergonomics; a 20-file directory needs nothing. The
skill is the product, and its largest consumer is drowning. That is the whole argument, and it is
enough.

**Two motivations that do not survive contact:**

- **Board noise — already solved.** `render_done` (`:280`) collapses the table to `DONE_RECENT = 12`
  (`:38`) with the note *"The full pile is `tasks/done/`; git history is its journey."*
  `render_board_columns` uses `LIVE_LANES`, and `render_blocked_graph` opens with
  `if t.lane == "done": continue`. Nothing in the rendering grows with `done/`.
- **`ls` / `grep` ergonomics** — real, but weak at 20 files and not why this is worth building.

**One that does, and is not obvious:** `structural_problems` (`:152`) validates *every* done file on
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
  `load_tasks` takes `lane` from the path. (Downstream, exactly **one** non-test script reads a task's
  `status:` — `check-task-order.py:81,:97`. The first draft said "about six"; the others read ADR,
  upstream-watch, job or points status, which are unrelated fields.)

### The one hazard the name introduces — caught by CI, fixed in one character

`generate-task-board.py:34` derives the board columns by a **positional slice** that assumes `done`
is last. Append `done-archived` to `LANES` and `LIVE_LANES` becomes
`("new", "prioritized", "wip", "blocked", "done")` — `done` is promoted to a live board column.

**The fix is `LIVE_LANES = LANES[:-2]`, and the existing suite already catches the mistake.**
Measured 2026-09-01 by patching a scratch copy and running `generate_task_board_test.py`:

| form | result |
|---|---|
| `LANES += ("done-archived",)`, slice left at `[:-1]` | fails the suite (the header test below, plus `LANE_EMPTY` has no `"done"` key) |
| slice changed to `[:-2]` | `OK (78 tests)` |

`test_header_columns_are_the_lanes_in_flow_order` (`:223-226`) feeds `gen.LIVE_LANES` in and asserts
the header against a hardcoded `["new", "prioritized", "wip", "blocked"]`, so the promoted column
reddens the build. This is runtime-silent but **not** CI-silent — do not carry it as a hidden
hazard. The slice stays positional and will re-break when a seventh lane is appended; that test
catches that too, which is the property worth having.

Four more sites hard-code the string and need the same treatment:

| line | code | status after `[:-2]` |
|---|---|---|
| 34 | `LIVE_LANES = LANES[:-1]` | **fixed** by `[:-2]`; pinned by an existing test |
| 317 | `if t.lane == "done": continue` | ⚠️ **still wrong** — an archived task is not skipped, so it enters the mermaid graph as a dependent. No test covers it |
| 331 | `known.lane == "done"` | fine — an archived blocker simply never marks satisfied; decide whether that is wanted |
| 402 | `by_lane["done"]` | fine — `by_lane` is built over all of `LANES` (`:383`), so archived tasks miss both tables. ⚠️ But `:384`'s `tally` also iterates `LANES`, so they **do** appear in the header count and total. "Render nowhere" is not what the code does |

⚠️ **A green suite does not mean the lane is done.** All 78 tests pass under `[:-2]` because nothing
in the suite exercises a `done-archived` task at all. `:317` is wrong and untested — that gap is the
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

**Three more scripts in that repo carry the identical five-lane tuple** and need the same routing:
`check-doc-references.py:84`, `check-obligation-liveness.py:83`, `check-review-gate-landing.py:82`.

`check-task-paths.py` is a **fourth site with a different shape** — it carries no five-lane tuple. Its
lane enumeration is a regex at `:55`, `tasks/(new|prioritized|wip|blocked|done)/(\d{3}-[a-z0-9-]+\.md)`,
so it needs an alternation edit rather than a tuple edit. (Its `\d{3}` is exact and its charset is
`[a-z0-9-]+` — both narrower than cannery-row's `\d{3,}` / `[A-Za-z0-9._-]+`, which is a separate
latent problem there, not this task's.) Its only tuple, at `:49`, is the four-lane `OPEN_LANES`.

### 3. `blocked-by:` edges to archived tasks become prose conditions, silently

`generate-task-board.py:60`'s `TASK_REF_RE` hard-codes the five lanes, so
`tasks/done-archived/042-slug.md` does not match and `classify_blocker` (`:192-203`) falls through to
`("external", raw)`. Concretely, and no more dramatically than this: the node is emitted with the
same shape as every other (`:346`) but carries the `external` CSS class — amber fill, and the legend
says *"Amber = a condition, not a task."* The card meta shows `⛔ condition` instead of `⛔ NNN`, and
the label is the raw path (untruncated; `EXTERNAL_LABEL_MAX = 60`). The `satisfied` list cannot
rescue it — that is only appended when `kind == "task"`. Compounding: `load_tasks` (`:206`, loop at `:208`)
iterates `LANES`, so even a matching ref would yield `by_number.get(...) → None` and the label
`"NNN · missing"` (`:330`).

Nothing errors. A live task gated on a closed-then-archived blocker renders as gated on a condition.

## Design

**Age comes from `completed:` frontmatter, never mtime.** mtime does not survive a clone and `git mv`
does not set it meaningfully, so mtime archives everything on a fresh checkout. `completed:` is
authoritative by invariant 4.

**A `done/` task with no `completed:` date is a guard, not a live problem.** Measured 2026-09-01:
**20/20** here and **596/596** downstream carry a non-empty `completed:`. Zero violations. Refuse to
archive such a file and report it — but write it as a guard against a future invariant-4 breach, not
as cleanup of existing corruption, because there is none.

### Invocation — DECIDED 2026-09-01: option A, relocated

**Decision: a bundled script, `skills/task-lifecycle/scripts/archive-done-tasks.py`, invoked from a
new `SKILL.md` transition section.** Taken by the requester after checking the fork against
published practice rather than against this repo's habits alone.

The fork was real — `SKILL.md` invokes **no** repo script anywhere
(`grep -n "scripts/\|python3" skills/task-lifecycle/SKILL.md` returns nothing), there is no
`$ARGUMENTS` marker, and the plugin ships no `commands/` directory and exactly one skill. So this is
still the skill's **first** script dependency. What settled it:

- **Bundling a script beside `SKILL.md` is the documented, demonstrated practice, not a deviation.**
  Every Anthropic-published skill of this shape does it — `pdf`, `docx`, `xlsx`, `pptx` each ship a
  `scripts/` directory of utilities. The stated split is prose for judgment and workflow, scripts for
  deterministic operations: date arithmetic over a bulk file move is squarely the second.
- **The first draft put the script in the wrong place, and that is what made option A look costly.**
  Convention is `skills/<name>/scripts/`, referenced skill-relative — not this repo's root
  `scripts/`, which holds gate tooling. Both of A's stated costs were artefacts of the wrong
  location:
  - *"hard-codes a path into runtime-agnostic prose"* — a skill-relative path names no repo, no host
    and no language. It is exactly as portable as the rest of the file.
  - *"inherits [[00013-adopters-copy-of-the-generator-drifts]]"* — it does **not**. 013 is about the
    board generator, which an adopter hand-copies into their own repo because it has to match their
    layout. A skill-bundled script travels with the skill and is replaced by `plugin update` on a
    version bump. The drift mechanism does not apply.
- **B was rejected** on the original ground, unchanged: no test can pin prose, and threshold
  arithmetic is what a model does unreliably.

⚠️ **The first draft's claim about the shipped boundary was wrong in both directions.** It said
`scripts/` ships to adopters *and* that `check-skill-args.py` "does not scan the shipped boundary."
Measured 2026-09-01 by listing the installed plugin cache: `marketplace.json` declares
`"source": "./"`, so installing copies **the whole repository** — `scripts/`, `tasks/`, `docs/`,
`evals/` and all — into `~/.claude/plugins/cache/cannery-row/cannery-row/<version>/`. So the
root `scripts/` does reach an adopter. But the four-file `SCANNED` list **is** this repo's
*declared* boundary — `check-skill-args.py:36-38` defines it as *"what crosses into somebody else's
repository or context"* — so the accurate statement is that the declaration is narrower than what
actually ships. Also: `marketplace.json`'s description still says *"the board generator and the
conventions doc are fetched from the repository."* That is stale, and this task should fix it.

⚠️ **Two `SCANNED` lists must gain the new script, not one.** The first draft named only
`check-skill-args.py` and cited it at `:41-46`; it is at **`:39-44`**. `:41-46` is the line range of
the *identical* list in `check-portability.py` (there `:39-50`, padded by an inline comment), whose
own comment says the two are kept in step. Miss either and a shipped file goes unscanned by that
gate. Note also `check-skill-args.py`'s pattern is narrower than "`$` then a digit":
`POSITIONAL = re.compile(r"(?<![\w}$])\$(\d)(?![\d.])")` leaves `$14` and `$4.52` alone.

**Default 14 days, overridable per call, plus `--dry-run`** — this is the one lifecycle operation
that moves files in bulk with no per-file human decision behind it.

## Interaction with task 035

**035 landed first (2026-09-01, `0.9.0`), and it changed this obligation rather than settling it.**
The archive operation must **not** hardcode a width — no shipped file does any more. `SKILL.md` and
`generate-task-board.py` both read the width off what is already there, because they install into
repositories that chose different ones. An archive step that emits `%05d` would hand a three-digit
adopter `00042-…` beside their `042-…`, which is the mixed-width state 035 exists to prevent.

Archiving **renames nothing**, so the correct behaviour is simply to carry each filename across
unchanged. The obligation is only that nothing in the new code reconstructs a name from its number.

Two things 035 already handles, so this task does not have to:

- **The numbering scan reaches an archive lane for free.** Its committed half is
  `git ls-tree -r … -- tasks/` and its worktree half is `find "$wt/tasks" -type f -name '*.md'` —
  both recurse, neither enumerates lanes. A new directory under `tasks/` is scanned on arrival.
- **This repo's own files are `%05d` now**, so a rename step here would find nothing to do.

`generate-task-board.py`'s `LANES` tuple *does* enumerate lanes and would need the new one.

## Done when

- [x] The invocation fork above is decided and recorded in this file before implementation starts
      — **option A, relocated to `skills/task-lifecycle/scripts/`**; see the Invocation section
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
      (`generate_task_board_test.py:223`) already pins this, so no new test is needed for the slice itself
- [ ] `:317`'s graph skip handles `done-archived` — an archived task must not enter the mermaid graph
      as a dependent — with a test, since nothing currently exercises the new lane
- [ ] `:331` and `:402`'s behavior for archived tasks is decided and recorded, with a test per
      behavioral choice. Note archived tasks are **not** invisible: `:384`'s `tally` iterates all of
      `LANES`, so they appear in the header count whatever the tables do
- [ ] The script is added to the `SCANNED` list in **both** `check-skill-args.py` and
      `check-portability.py`, with a test per gate asserting the list covers it
- [ ] `tasks/README.md:11`'s "archive here for history" is rewritten so `done/` and `done-archived/`
      are distinguishable by a reader who was not here
- [ ] `marketplace.json`'s stale description — *"the board generator and the conventions doc are
      fetched from the repository"* — is corrected; `"source": "./"` ships the whole repo
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
      **and `check-task-order.py`, the one script there that reads a task's `status:` field**, and
      this file links it
- [ ] Every document and open task this change makes wrong is updated, and anything the work turned
      up that nothing yet records is written down — or what was checked is named here, with why none
      of it needed changing

---

## Correction log

**2026-09-01** — corrected before commit by the fresh-context falsification read `CLAUDE.md` requires
for a deliverable that is itself a spec. Six claims in the first draft were wrong or overstated:

- **The motivation was wrong for this repo.** The draft argued filesystem ergonomics for
  `tasks/done/` — which holds 20 files here. The 596-file directory is downstream. Rewritten to
  motivate on the adopter and on `structural_problems`' growing failure surface, which is the only
  thing here that scales badly.
- **"Archived numbers stop being reserved" was overstated**, and the draft contradicted itself two
  paragraphs later. The allocator walks `archive/` and stays correct; only the cross-branch detector
  goes blind. The `0042` example was also impossible under the `\d{3}` pattern of the time — it is possible
  now (035 relaxed it to `{3,}` in `0.8.2`), in a four-digit adopter, so the example stands where
  the claim around it did not.
- **"SKILL.md instructs Claude to run the script" described a precedent that does not exist** —
  `SKILL.md` invokes no repo script at all. This is the skill's first script dependency, so it is
  now written as an open fork with a recommendation, not a settled convention.
- **`check-skill-args.py` does not scan the shipped boundary** — it is a hardcoded four-file
  whitelist, so the warning was aimed at a gate that would not fire on a new script. Its pattern is
  also narrower than the draft claimed.
- **"Rendered as an unsatisfiable node" was invented vocabulary.** The real behavior is an amber
  `external` CSS class and a `⛔ condition` card marker.
- **The missing-`completed:` case has zero instances** in either repo (20/20 and 596/596 populated).
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

**2026-09-01 (fourth pass)** — picked up for implementation. The mandated fresh-context falsification
read found nine wrong claims, all corrected above; the pattern is that *mechanisms* held and
*measurements* did not, which is the opposite of the failure this repo usually sees:

- **Every count was stale.** `tasks/done/` is 20 files, not 19; downstream is 596, not 594; the board
  suite is **78 tests**, not 70. The zero-violation `completed:` property survives at 20/20 and
  596/596. Baseline measured on pickup: full `scripts/` suite 186 tests green, all five gates green.
- **Every `generate-task-board.py` line number past ~150 was off**, by +1 to +4 inconsistently — so
  not one stale snapshot. Corrected against a clean tree at HEAD.
- **`test_header_columns_are_the_lanes_in_flow_order` is at `:223-226`, not `:150-153`** — off by 73
  lines. The mechanism was right; `:150-153` is a different test entirely.
- **`:402`'s "archived tasks render nowhere" was half wrong** — `:384`'s `tally` iterates all of
  `LANES`, so archived tasks appear in the header count. That consequence was unrecorded.
- **`check-task-paths.py:55` is a regex, not a five-lane tuple** — right routing target, different
  edit. And **one** downstream script reads a task's `status:`, not "about six".
- **The shipped-boundary claim was wrong in both directions**, and there are **two** `SCANNED` lists,
  not one. See the Invocation section.
