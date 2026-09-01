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
  - tasks/new/021-numbering-scan-worktree-half-scans-nothing.md
  - tasks/done/034-numbering-scan-is-best-effort-and-its-worktree-half-is-corrupted-at-render.md
---

# Task numbers are capped at three digits, and the numbering scan and three adopter gates fail silently past 999

## The deadline is real and it is close

`everything-has-a-price` is at **737** (verified 2026-09-01, `tasks/*/` max prefix). It has 262
numbers left before the convention this repo ships stops working. Nothing in either repo announces
the boundary — every failure below is silent.

## What actually breaks, and what does not

The board generator's *parsing and rendering* are already tolerant: `generate-task-board.py:59-60`
use `\d{3,}`, and every format site (253, 254, 290, 317, 324, 326, 333) is `:03d`, which is a
*minimum* width — `f"{1234:03d}"` is `'1234'`. Mermaid node ids stay unique. But it has one
width-dependent line, and it only bites under option B:

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

### 2. Three adopter gates stop seeing four-digit tasks entirely (`everything-has-a-price`)

All three anchor an exact three-digit run followed by `-`, so a four-digit filename does not match
at all — it is not flagged, it is invisible:

| file | line | pattern | what goes blind |
|---|---|---|---|
| `scripts/check-task-numbers.py` | 75 | `^(\d{3})-[^/]*\.md$` | gate 20 — no two tasks share a number |
| `scripts/check-task-paths.py` | 55 | `tasks/(new\|…)/(\d{3}-[a-z0-9-]+\.md)` | gate 19 — task citations name the real lane |
| `scripts/check-obligation-liveness.py` | 84, 90, 95, 235 | `^\d{3}-…`, `(?:task\s+)?(\d{3})\b` | gate 21 — expiry clauses and ownership markers |

Gate 20 is the one that matters most: it is the *only* trigger behind the numbering race that
task 034 established the scan cannot win. Past 999 the scan reports a colliding number (defect 1)
and the gate that would have caught it no longer looks (defect 2). Those compose into a collision
that nothing anywhere reports.

That repo is a downstream adopter, not this repo's code. This task fixes what this repo ships and
**routes** the gate patches there; see "Scope" below.

### 3. Prose asserts the cap

- `tasks/README.md:16` — "the **three-digit** prefix orders the queue"
- `everything-has-a-price/tasks/README.md:16` — same sentence

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

Measured across `everything-has-a-price` `docs/` + `tasks/` on 2026-09-01:

| citation form | count | effect of padding |
|---|---|---|
| bare *"task NNN"* in prose | 2909 | **unaffected** — the number does not change, only filename width |
| `tasks/<lane>/NNN-slug.md` paths | 2016 | breaks; regex-rewritable, and **gate 19 verifies the result** |
| `[[NNN-slug]]` wiki-links | 1002 | breaks; regex-rewritable |

The largest class does not break at all. The ~3000 that do are structured, mechanically rewritable
in one pass, and two-thirds of them have a CI gate that fails if the rewrite is wrong. Renaming is
a scripted `git mv` over 718 + 35 files, which preserves history.

⚠️ **Five digits, not four.** Same rename either way, and four digits schedules this exact task
again at 9999. The width is free; the rename is not.

### Sequencing — regexes first, rename second

`\d{3}` does not match `00035-slug.md` either, so the moment files are renamed every gate below goes
blind unless it already accepts the new width. Land the width-tolerant patterns **first** (`{3,}`
accepts both, so the tree is valid at every commit), then rename, then tighten if desired.

**Phase 1 — accept any width (no renames, safe to merge alone):**

- `SKILL.md:350` — `grep -oE '^[0-9]{3}'` → `{3,}`. Today `00035-slug.md` yields `000`, so the scan
  reports max 0 and hands back `1`. Verified:
  `printf '0999-a.md\n1000-b.md\n1001-c.md\n' | grep -oE '^[0-9]{3}' | sort -n | tail -1` → `100`;
  with `{3,}` → `1001`.
- `everything-has-a-price/scripts/check-task-numbers.py:75` — `^(\d{3})-[^/]*\.md$`
- `everything-has-a-price/scripts/check-task-paths.py:55` — `(\d{3}-[a-z0-9-]+\.md)`
- `everything-has-a-price/scripts/check-obligation-liveness.py:84, 90, 95, 235`

**Phase 2 — pad:**

- Scripted `git mv` over both repos' `tasks/*/` to `%05d`
- One rewrite pass over the 2016 path citations and 1002 wiki-links
- `SKILL.md:351` `printf '%03d'` → `%05d`; `generate-task-board.py` `:03d` → `:05d` (7 sites) so
  link text matches the filename
- `tasks/README.md:16` in both repos — "three-digit prefix" → five-digit
- `generate-task-board.py:211`'s lexical sort becomes correct on its own once widths are uniform;
  leave it, and record that as the reason it was not touched

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

- [ ] **Phase 1 merged:** no shipped file in this repo asserts an exact three-digit prefix, and the
      numbering scan returns `1001` for the `0999/1000/1001` input above, not `100`
- [ ] A test in `scripts/` fails if the board generator regresses to an exact-width assumption,
      asserting the returned value and not merely running the code. ⚠️ Nothing in `scripts/` reads
      `SKILL.md`'s bash block today, so covering the scan itself means new scaffolding — decide
      whether that is in scope and say which you chose
- [ ] **Phase 2 merged:** every task file in both repos is `%05d`-padded, and `ls tasks/prioritized/`
      lists in numeric order
- [ ] All 2016 path citations and 1002 wiki-links are rewritten; `everything-has-a-price` gate 19
      is green, which is the mechanical check on two-thirds of them
- [ ] `generate-task-board.py:211`'s lexical sort is left in place with the reason recorded — under
      uniform width it is correct, and changing it is a signal the task was widened past its scope
- [ ] `version` bumped in both `.claude-plugin/*.json` with a matching `CHANGELOG.md` heading
- [ ] The `everything-has-a-price` half is **routed, not applied from here** — a task exists in that
      repo covering its four gate patches and its rename, and this file links it
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
