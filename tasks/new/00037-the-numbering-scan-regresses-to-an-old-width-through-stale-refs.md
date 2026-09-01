---
created: 2026-09-01
updated: 2026-09-01
completed:
status: new
owner: justmaniv
blocked-by: ""
links:
  - skills/task-lifecycle/SKILL.md
  - scripts/skill_numbering_scan_test.py
  - tasks/done/00035-task-numbers-are-capped-at-three-digits-and-gates-go-blind-past-999.md
  - tasks/done/00036-done-tasks-cannot-be-archived-on-command.md
---

# The numbering scan permanently regresses to a repository's old number width, because old refs keep the old filenames

## Reproduced here, on this repository, today

`main` is uniformly five digits. Every task file is `00001-…` through `00036-…`. Run the scan the
skill ships (`SKILL.md` § "Assigning the next task number") from a clean checkout of `main`:

```
next: 037
```

**Three digits.** In a five-digit repository, with no mixed-width file anywhere in the working
tree. A session that trusts it mints `037-slug.md` beside `00036-slug.md`, which is exactly the
mixed-width state task 035 was built to prevent — reintroduced by the scan 035 shipped.

## Why, precisely

The scan unions filenames from **every local and remote ref**, not just the checked-out tree:

```bash
git for-each-ref --format='%(refname)' refs/heads refs/remotes | while read -r ref; do
  git ls-tree -r --name-only "$ref" -- tasks/
done
```

That is correct and load-bearing — it is what makes the scan see a sibling branch's numbers. But
this repository was repadded in 035 (`9d63cda`, "pad every task number to five digits"), and the
branches that predate the repad **still exist on `origin`** with the old names. So the union
contains both forms:

```
00036
00036
036
036
036
```

The width is then derived from whichever line survives `sort -n | tail -1`, and `${#next}` is that
line's length.

⚠️ **`sort -n` does not preserve input order on numeric ties, and its tie-break deterministically
picks the *narrowest* form.** Measured 2026-09-01:

```
$ printf '00036-a.md\n036-b.md\n' | grep -oE '^[0-9]{3,}' | sort -n | tail -1
036
$ printf '036-b.md\n00036-a.md\n' | grep -oE '^[0-9]{3,}' | sort -n | tail -1   # reversed input
036
$ printf '00036-a.md\n036-b.md\n' | grep -oE '^[0-9]{3,}' | sort -n -s | tail -1  # stable sort
036
```

`036` and `00036` compare equal numerically, so `sort` falls back to a last-resort byte comparison,
where `036` sorts after `00036` (`'3'` > `'0'` at the second character). `-s` does not help: the
last-resort comparison is what `-s` disables, and disabling it leaves the *original* order, which
is `ls-tree`'s, not a chosen one. **The narrow form wins whenever both exist.**

## Why this does not heal itself

`SKILL.md` already anticipates a mixed tree:

> ⚠️ In a tree that is *already* mixed it takes the width of the highest number; make the tree
> uniform rather than relying on that.

**That advice does not reach this failure.** The tree *is* uniform. What is mixed is the set of
refs, and refs are history — a merged branch's old filenames are immutable and permanent. So this
is not a transient state that a cleanup pass resolves: **every repository that ever repads is
permanently pinned to its pre-pad width by the scan**, for as long as any pre-pad ref is reachable.
Deleting merged remote branches would mask it on this repository and would not fix the scan, and
`main`'s own history still carries the old names regardless.

The failure is silent in the way this repository keeps rediscovering: nothing errors, the number is
well-formed, and it is wrong.

## What is not the bug

- **Not `grep -oE '^[0-9]{3,}'`.** 035 already fixed the exact-`{3}` prefix-match defect; the
  reduction correctly extracts `00036` from `00036-a.md`.
- **Not the `%0*d` successor.** `printf '%0*d'` is a minimum width and never truncates; hand it
  width 5 and it emits `00037`.
- **Not the ref union.** Removing it would reintroduce the collision race task 034 established.

The bug is one line: deriving the width from a value chosen by a numeric sort that treats padding as
noise, then reading the padding back off it.

## Candidate fixes, none yet chosen

- **A — derive the width and the maximum separately.** Take the maximum numerically as now, and take
  the width from the *widest* prefix seen rather than from the winning line. Widest-wins is the
  conservative direction: it can only over-pad, and `%0*d` over-padding a three-digit repo is
  visible immediately, where under-padding a five-digit repo is silent.
- **B — derive the width from the working tree only, and the maximum from every ref.** The tree is
  the thing that is supposed to be uniform, and it is what a human reads with `ls`. Refs contribute
  numbers, not formatting. This is probably closest to the intent.
- **C — sort on the padded string rather than numerically**, after normalising to a common width.
  More moving parts; mentioned for completeness.

**Recommend B**, but take the decision explicitly. Whichever is chosen, the reduction stays a `sed`
pipeline with no `$`-then-digit form in it — see the positional-argument warning in `SKILL.md`.

## Done when

- [ ] The fix is chosen from the forks above and the reasoning recorded in this file
- [ ] The scan returns `00037` — not `037` — when run against this repository's refs, verified by
      **running it**, not by reading it
- [ ] `scripts/skill_numbering_scan_test.py` gains a case feeding both `00036-a.md` and `036-b.md`
      through the shipped reduction and asserting the emitted number is five digits, written
      test-first (a RED commit, then a GREEN commit)
- [ ] A case pins the opposite direction: a repository uniformly at three digits, with no wide refs,
      still gets three digits — the fix must not over-pad every adopter
- [ ] `SKILL.md`'s "in a tree that is already mixed" note is corrected: the tree being uniform is
      **not** sufficient, because refs carry the old width permanently after a repad
- [ ] `tasks/done/00035-*` is annotated with a dated note — its width derivation is the code this
      defect is in, and a reader of that task should not have to find this one by luck
- [ ] `CHANGELOG.md` says what an installed copy receives, and both `.claude-plugin/*.json` versions
      are bumped
- [ ] `everything-has-a-price` is checked for the same exposure and routed if it has it — that repo
      is at three digits and has **not** repadded, so it is likely unaffected today and would be
      affected the moment it pads. Record which
- [ ] Every document and open task this change makes wrong is updated, and anything the work turned
      up that nothing yet records is written down — or what was checked is named here, with why none
      of it needed changing

---

## Provenance

Found on 2026-09-01 while closing [[00036-done-tasks-cannot-be-archived-on-command]], by running
the scan to number this very file. It was not found by reading the scan, and 036's own
fresh-context falsification read confirmed the scan lines it cited were correct — because they
are. The defect is in what the correct lines do together, against a ref set this repository only
acquired when 035 repadded it eight commits earlier.
