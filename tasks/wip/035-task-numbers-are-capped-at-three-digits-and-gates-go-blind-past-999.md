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
  - tasks/new/021-numbering-scan-worktree-half-scans-nothing.md
  - tasks/done/034-numbering-scan-is-best-effort-and-its-worktree-half-is-corrupted-at-render.md
---

# Task numbers are capped at three digits, and the numbering scan and five adopter gates fail silently past 999

## The deadline is real and it is close

`everything-has-a-price` is at **737** (re-verified 2026-09-01 at `55e7575`, `tasks/*/` max
prefix). It has 262 numbers left before the convention this repo ships stops working. Nothing in
either repo announces the boundary — every failure below is silent.

## What actually breaks, and what does not

The board generator's *parsing and rendering* are already tolerant: `generate-task-board.py:59-60`
use `\d{3,}`, and every format site in that file (253, 254, 290, 317, 324, 326, 333 — seven, all
`:03d`) is a *minimum* width — `f"{1234:03d}"` is `'1234'`. Mermaid node ids stay unique. But it has
one width-dependent line, and it only bites under option B:

```python
211:    for path in sorted(lane_dir.iterdir()):
```

**Lane and queue order is lexical filename order, never re-sorted numerically.** `by_lane` filters
`tasks` in load order and `render_board_columns` does not re-sort;
`generate_task_board_test.py:163-166` pins this, asserting the input order `["300","101","205"]`
survives verbatim. So under mixed-width numbering `1000-x.md` sorts *before* `999-x.md` in the
board column — contradicting `tasks/README.md:16`, which says the prefix orders the queue. Nothing
crashes; the queue is just silently wrong. **Option B must sort `by_lane` on `t.number`.** Under
option A lexical order equals numeric order, so this line needs nothing — the one genuine point in
A's favor.

### 1. The numbering scan silently returns the wrong maximum (`SKILL.md:350`)

```bash
} | sed -E 's#.*/##' | grep -oE '^[0-9]{3}' | sort -n | tail -1 )
```

`{3}` is exact, and `grep -o` matches a **prefix**, so `1000-b.md` yields `100`. Measured:

```
$ printf '0999-a.md\n1000-b.md\n1001-c.md\n' | grep -oE '^[0-9]{3}' | sort -n | tail -1
100
$ printf '0999-a.md\n1000-b.md\n1001-c.md\n' | grep -oE '^[0-9]{3,}' | sort -n | tail -1
1001
```

The scan does not error, does not skip the file, and does not print a warning — it reports the max
as 100 and the session takes 101, which is already in use. This is the same failure class as
[[021-numbering-scan-worktree-half-scans-nothing]] and
[[034-numbering-scan-is-best-effort-and-its-worktree-half-is-corrupted-at-render]]: a scan half that
goes quiet and is trusted. The difference is that those two lose a race; this one hands back a
number that is *guaranteed* to collide, on every run, forever after 999.

### 2. Five adopter gates stop seeing four-digit tasks entirely, and a generator keeps minting three (`everything-has-a-price`)

Each anchors an exact three-digit run, so a four-digit filename does not match at all — it is not
flagged, it is invisible:

| file | line | pattern | what goes blind |
|---|---|---|---|
| `scripts/check-task-numbers.py` | 75 | `^(\d{3})-[^/]*\.md$` | gate 20 — no two tasks share a number |
| `scripts/check-task-paths.py` | 55 | `tasks/(new\|…)/(\d{3}-[a-z0-9-]+\.md)` | gate 19 — task citations name the real lane |
| `scripts/check-obligation-liveness.py` | 84, 90, 95, 215, 235 | `^\d{3}-…`, `(?:task\s+)?(\d{3})\b`, `"%03d" % task` | gate 21 — expiry clauses and ownership markers |
| `scripts/check-doc-references.py` | 85, 156 | `^\d{3}-[a-z0-9-]+\.md$` | gate 11 — doc references resolve |
| `scripts/check-review-gate-landing.py` | 83, 235, 245 | `^(\d{3})-(.+)\.md$` | gate 24 — review-gate landings |
| `scripts/upstream-watch-run.py` | 271, 417 | `^(\d{3})-`, `f"tasks/new/{number:03d}-…"` | not a gate — it **files** tasks, and would keep emitting three-digit names after a rename |

⚠️ **The last row is the one that undoes the work.** `upstream-watch-run.py:417` constructs task
filenames at `:03d`. Left alone it re-introduces the mixed-width state phase 2 exists to eliminate,
one drift task at a time, with no gate objecting.

`check-obligation-liveness.py:215` (`lane = lane_of("%03d" % task)`) is coupled to `:235`'s
`(\d{3})-` capture — `build_lanes` keys on that capture, and `:215` reconstructs the key. **The two
must move together** or every liveness lookup misses.

Gate 20 is the one that matters most: it is the *only* trigger behind the numbering race that
task 034 established the scan cannot win. Past 999 the scan reports a colliding number (defect 1)
and the gate that would have caught it no longer looks (defect 2). Those compose into a collision
that nothing anywhere reports.

That repo is a downstream adopter, not this repo's code. This task fixes what this repo ships and
**routes** the whole `everything-has-a-price` half — gate patches, rename, and citation rewrite —
to a task filed in that repo. Nothing under `everything-has-a-price/` is edited from here.

### 3. Prose asserts the cap

- `tasks/README.md:16` — "the **three-digit** prefix orders the queue within a directory.
  Numbering restarts per project; …"
- `everything-has-a-price/tasks/README.md:16` — **not** the same sentence: "three-digit prefix
  orders the queue within a directory." and nothing after. A `sed` written against one will not
  match the other; patch them separately.

`tasks/README.md` is inside the shipped boundary (`check-release.py:48`), so this prose is a
**phase 1** item here, not a phase 2 one — see the sequencing note below.

## The decision: zero-pad to five digits, and remove the exact-width assumptions

Both halves are needed, and the order they land in matters.

### Why padding, not just `{3,}`

Relaxing the regexes to `\d{3,}` removes the ceiling for the *code*, and it is not enough, because
**the filesystem is the UI here.** `tasks/<status>/NNN-slug.md` IS the tracker — the queue is read
with `ls`, in an editor sidebar, and in `git status`, all of which sort lexically. Mixed widths
break that ordering and no code change can fix it:

```
$ printf '0999-a.md\n1000-b.md\n0998-c.md\n' | sort
0998-c.md
0999-a.md
1000-b.md          # correct only because all three are padded to the same width
```

Uniform width is what makes lexical order equal numeric order. That is the property being bought,
and it is the premise of a directory-as-tracker rather than a cosmetic preference.

### The rename is far cheaper than it first looks

Re-measured across `everything-has-a-price` `docs/` + `tasks/` on 2026-09-01 at `55e7575`:

| citation form | count | effect of padding |
|---|---|---|
| bare *"task NNN"* in prose | 2928 | **unaffected** — the number does not change, only filename width |
| `tasks/<lane>/NNN-slug.md` paths | 2017 | breaks; regex-rewritable, and **gate 19 verifies the result** |
| `[[NNN-slug]]` wiki-links | 1007 | breaks; regex-rewritable |

The largest class does not break at all. The 3024 that do are structured, mechanically rewritable
in one pass, and two-thirds of them have a CI gate that fails if the rewrite is wrong. Renaming is
a scripted `git mv` over 718 files there and 36 here, which preserves history.

⚠️ **These counts drift.** The first draft's 2909 / 2016 / 1002 / "35 files" were measured hours
earlier and were already stale the same day. Re-measure before the rewrite pass; do not use the
table as an acceptance count.

⚠️ **Five digits, not four.** Same rename either way, and four digits schedules this exact task
again at 9999. The width is free; the rename is not.

### Sequencing — regexes first, rename second

`\d{3}` does not match `00035-slug.md` either, so the moment files are renamed every gate below goes
blind unless it already accepts the new width. Land the width-tolerant patterns **first** (`{3,}`
accepts both, so the tree is valid at every commit), then rename, then tighten if desired.

**Phase 1 — accept any width (no renames, safe to merge alone). This repo only:**

- `SKILL.md:350` — `grep -oE '^[0-9]{3}'` → `{3,}`. Today `00035-slug.md` yields `000`, so the scan
  reports max 0 and hands back `1`. Verified:
  `printf '0999-a.md\n1000-b.md\n1001-c.md\n' | grep -oE '^[0-9]{3}' | sort -n | tail -1` → `100`;
  with `{3,}` → `1001`.
- `tasks/README.md:16` — drop the width assertion. It is a **shipped** file, so leaving it until
  phase 2 makes phase 1's own acceptance criterion unsatisfiable. Make it width-neutral here
  ("the numeric prefix orders the queue"); phase 2 states the five-digit width.
- An executing test — see "The test is cheap, not new scaffolding" below.

**Phase 2 — pad. This repo only:**

- Scripted `git mv` over this repo's `tasks/*/` to `%05d` (36 files), and rewrite this repo's own
  internal `tasks/<lane>/NNN-slug.md` and `[[NNN-slug]]` citations
- `SKILL.md:351` `printf '%03d'` → `%05d`; `generate-task-board.py` `:03d` → `:05d` (7 sites) so
  link text matches the filename
- ⚠️ **`generate_task_board_test.py` is an eighth `03d` site and holds ~9 hardcoded three-digit
  assertions** — `:41` builds paths at `{number:03d}`, and `:166, 191, 223, 270, 277, 278, 283,
  432, 433` assert `"300"`, `"354"`, `"097"`, `"T097 --> T080"`, `"T099"`, `"T291"`, `"007"`,
  `"008"`. The original draft's "7 sites" counted only the generator. Every one of these fails the
  moment `card()` becomes `:05d`.
- `tasks/README.md:16` here — state the five-digit width
- `generate-task-board.py:211`'s lexical sort becomes correct on its own once widths are uniform;
  leave it, and record that as the reason it was not touched. ⚠️ The reason currently recorded at
  `generate_task_board_test.py:161` is a **phantom**: it cites `triage-criteria.md`, a document
  that exists in no repository here — the same leaked upstream reference `tasks/done/001-*` removed
  from the generator's emitted output, which survived in this comment. Replace it with the real
  reason, do not preserve it.

**Routed to `everything-has-a-price`, not done here:** its five gate patches, its
`upstream-watch-run.py` generator fix, its rename, its `tasks/README.md:16`, and its path +
wiki-link citations. That repo has its own gates and its own PR-only main.

Filed 2026-09-01 as `everything-has-a-price` **task 740**,
`tasks/new/740-task-numbers-run-out-at-999-and-five-gates-go-blind-past-it.md`
(PR [Justhud/everything-has-a-price#1155](https://github.com/Justhud/everything-has-a-price/pull/1155)).
Its own falsification read corrected nine claims inherited from or shared with this file — two are
worth carrying back here:

- **That repo's max prefix is 739, not the 737 this file states**, and was 739 at the time this
  file was written. `tasks/new/738-*` and `tasks/new/739-*` were already tracked. The "262 numbers
  left" figure above is therefore 260. Left in place above as written, and corrected here, because
  the point of the ⚠️ under the citation table is exactly that these numbers move.
- **`generate-task-board.py`'s width problem is not confined to this repo.** That repo ships its own
  copy with seven `:03d` render sites, and its regexes are already `{3,}` — so after a rename it
  does not go blind, it prints a number that no longer matches its filename, and no gate notices.

### The test is cheap, not new scaffolding

The first draft warned that *"nothing in `scripts/` reads `SKILL.md`'s bash block today."* That is
false. **Two gates read it line by line today** — `check-skill-args.py:40, 70` and
`check-portability.py:42, 126` — and `check_skill_args_test.py:36-38` already ships a `scan()`
harness that feeds synthetic lines through a temp tree, with `:82` asserting on *this very
numbering-scan line*. What is missing is an assertion that **executes** the pipeline, not a file
reader. Extract the `grep -oE` line from `SKILL.md`, run it over `0999/1000/1001`, assert `1001`.

### The alternative considered and rejected

**Remove the ceiling only (`{3,}`, no renames).** Zero rename cost, and it does meet the literal
goal of not running out at 999. Rejected because it leaves `ls tasks/prioritized/` permanently
mis-ordered once numbers cross 999, and it pushes `generate-task-board.py:211` from a latent bug to
a live one requiring its own numeric-sort fix. Phase 1 is this option, which is why it is safe to
merge on its own if phase 2 is deferred — but deferring it indefinitely is choosing the rejected
option.

## Shipped boundary and release

`skills/` and `tasks/README.md` are both inside the shipped boundary (`CONTRIBUTING.md`), so this
change **requires a `version` bump in both `.claude-plugin/plugin.json` and
`.claude-plugin/marketplace.json` plus a matching `CHANGELOG.md` heading**, or `check-release.py`
fails the build. Without it the fix merges and reaches nobody while `plugin update` reports
*"already at the latest version."*

## Done when

Scope decision, 2026-09-01: **this repo only.** Every `everything-has-a-price` change is routed to a
task filed there; no criterion below is satisfied by editing that repo from here.

- [ ] **Phase 1 merged:** no shipped file in this repo (`skills/`, `scripts/`, `tasks/README.md`,
      `.claude-plugin/`) asserts an exact three-digit prefix, and the numbering scan returns `1001`
      for the `0999/1000/1001` input above, not `100`
- [ ] A test in `scripts/` executes the `SKILL.md` numbering-scan pipeline and asserts it returns
      `1001`, failing if the pattern regresses to exact width — asserting the returned value, not
      merely running the code
- [ ] A test in `scripts/` asserts the board generator loads and renders a five-digit task file,
      failing if it regresses to an exact-width assumption. State plainly whether this is test-first
      or characterization: `NAME_RE` is *already* `{3,}`, so a test written now passes on arrival
      and is characterization
- [ ] **Phase 2 merged:** every task file in **this** repo is `%05d`-padded, this repo's own path
      and wiki-link citations are rewritten, and `ls tasks/prioritized/` lists in numeric order
- [ ] `generate_task_board_test.py`'s three-digit assertions (`:41` and ~9 sites) are updated in the
      same change as `:03d → :05d`, and `:161`'s phantom `triage-criteria.md` justification is
      replaced with the real reason rather than carried forward
- [ ] `generate-task-board.py:211`'s lexical sort is left in place with the reason recorded — under
      uniform width it is correct, and changing it is a signal the task was widened past its scope
- [ ] `version` bumped in both `.claude-plugin/*.json` with a matching `CHANGELOG.md` heading, once
      per phase (both phases touch shipped files)
- [x] The `everything-has-a-price` half is **routed, not applied from here** — task 740 exists in
      that repo covering its **five** gate patches (11, 19, 20, 21, 24), its `upstream-watch-run.py`
      generator fix, its 721-file rename, its `tasks/README.md:16`, and its ~3027 citations; linked
      above. Filed 2026-09-01, PR #1155, awaiting merge
- [ ] Every document and open task this change makes wrong is updated, and anything the work turned
      up that nothing yet records is written down — or what was checked is named here, with why none
      of it needed changing

---

## Correction log

**2026-09-01** — corrected before commit by the fresh-context falsification read that
`CLAUDE.md` §"Picking up a task you did not write" requires for a deliverable that is itself a spec.
Two claims were wrong as drafted:

- **The 460-reference figure was cited to the wrong file and used for the wrong thing.**
  `working-rules.md:336` does not contain it — it reads *"28 instances 2026-05-16 → 2026-08-23, 15
  live"*. The real sources are `ci-merge-gate.md:55` and `docs/decisions/0068-*.md:66`, where 460 is
  the denominator of an **ownership-inversion** audit (~5% inversions), not a count of bare-number
  prose citations. The related claim that the repo's convention is to cite tasks *by bare number*
  was also unsupported: `working-rules.md:338` says cite by `[[NNN-slug]]` wiki-link. The cost
  argument for option A survives — a wiki-link embeds the number too — but it is restated above on
  the correct basis.
- **"The board generator needs no change" was over-broad.** `generate-task-board.py:211` sorts lane
  files lexically. As a `## Done when` criterion reading *"confirmed unchanged"* this would have
  been self-enforcing: a closer following it would have shipped a silently mis-ordered queue under
  the recommended option. This is exactly the failure `tasks/done/024-*` records.

**2026-09-01 (second pass)** — the recommendation was reversed after the requester pushed back on
filesystem ordering. The original draft recommended `{3,}`-only and called a five-digit pad
"cosmetic". That was wrong on measurement: the largest citation class (2909 bare *"task NNN"*)
does not break under padding at all, because the number is unchanged and only the filename widens —
the draft had counted it as the expensive class. The ~3000 that do break are structured and
regex-rewritable, and 2016 of them are verified by an existing CI gate. Meanwhile lexical `ls`
ordering is unfixable by code and is the premise of a directory-as-tracker. Padding is therefore
both cheaper and more valuable than drafted.

**2026-09-01 (third pass)** — corrected at pickup by the fresh-context falsification read that
`CLAUDE.md` §"Picking up a task you did not write" requires. Five material errors:

- **"Three adopter gates" was five, plus a generator.** `check-doc-references.py:85` (gate 11) and
  `check-review-gate-landing.py:83` (gate 24) were missed entirely, `check-obligation-liveness.py`'s
  line list omitted `:215` — which is coupled to `:235` and must move with it — and
  `upstream-watch-run.py:271, 417` *files* task names at `:03d`, so it would have re-introduced
  mixed widths after the rename with no gate objecting. Table replaced.
- **Phase 1's own acceptance criterion was unsatisfiable by Phase 1's action list.** It required
  that no *shipped* file assert a three-digit prefix, while assigning `tasks/README.md:16` — a
  shipped file under `check-release.py:48` — to Phase 2. The README prose moved to Phase 1.
- **"Nothing in `scripts/` reads `SKILL.md`'s bash block today" was false**, and it was used to
  argue the scan test was expensive. `check-skill-args.py` and `check-portability.py` both read that
  file line by line, and `check_skill_args_test.py:36-38` already ships the harness. The test is
  cheap; the criterion no longer offers an out.
- **Phase 2's ":03d → :05d (7 sites)" counted only the generator.**
  `generate_task_board_test.py` is an eighth site and holds ~9 hardcoded three-digit assertions that
  all fail on the change. A closer following the old list would have shipped a red suite.
- **Scoping contradicted itself.** "Routed, not applied from here" sat against four criteria and
  three Phase-2 bullets specifying work in `everything-has-a-price`. Resolved in favour of routing.

Also corrected: the three citation counts had drifted the same day (2909/2016/1002 → 2928/2017/1007,
"35 files" → 36); `tasks/README.md:16` is **not** the same sentence in both repos; and a dangling
*"see 'Scope' below"* pointed at a section that never existed.

Found while validating, and recorded here because nothing else did: `generate_task_board_test.py:161`
justifies the lexical sort by citing `working-agreement/triage-criteria.md`, which exists in no
repository here. `tasks/done/001-*` removed that exact phantom from the generator's *emitted output*;
it survived in the test comment. Phase 2 must replace it, not preserve it.
