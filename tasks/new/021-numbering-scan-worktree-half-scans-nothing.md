---
created: 2026-08-09
updated: 2026-08-09
completed:
status: new
owner: justmaniv
blocked-by: ""
links:
  - skills/task-lifecycle/SKILL.md
---

# The numbering scan's worktree half silently scans nothing

## What's wrong

`SKILL.md` §"Assigning the next task number" ships this scan, and calls numbering off a plain
`ls tasks/` the "**#1 collision source**". The scan has two halves: committed task files on every
ref, and working-tree files in every worktree. **The second half has never run.**

```bash
git worktree list --porcelain 2>/dev/null | awk '/^worktree /{print new}'
```

`new` is an undefined awk variable. It is not a field reference, so awk prints the empty string for
every matching line. Verified on this repo:

```
$ git worktree list --porcelain | awk '/^worktree /{print new}' | od -c
0000000   \n
0000001
```

One newline — one empty line for the one worktree, and no path. The `while read -r wt` loop that
consumes it then runs `find "/tasks" -type f -name '*.md'`, which matches nothing and is discarded
by `2>/dev/null`. The intended field is `$2`:

```
$ git worktree list --porcelain | awk '/^worktree /{print $2}'
/Users/agentsmith/aiOS/cannery-row
```

## Why it stayed invisible

The committed-refs half works, so the scan almost always returns the right number and the bug never
announces itself. It only bites in the precise case the worktree half exists to cover: a task file
**created but not yet committed** in a sibling worktree. That file is on no ref, so the first half
cannot see it, and the second half is dead — the scan reports a number that is already taken, both
sessions use it, and they collide at merge.

That is the documented failure this section was written to prevent, and it is the one case where
the scan silently does nothing. The stakes are low by design — the skill notes task numbers carry
no meaning and the loser renumbers with `git mv` before merge — but a documented safeguard that
does not run is worse than a known gap, because it is trusted.

**Blast radius:** every consumer of the plugin runs this scan, and the same dead half is in every
installed copy.

## The fix

One character class: `print new` → `print $2`. No structural change; the surrounding pipeline
already handles the paths correctly once they arrive.

Worth checking the same file for the same class of error while there — an unquoted bareword inside
`awk` that was meant as a field reference fails silently rather than erroring, so the one that was
found is not evidence it is the only one.

## Done when

- [ ] The scan in `SKILL.md` prints one absolute path per worktree, verified by running it in a
      repository with at least two worktrees
- [ ] The failure is reproduced before the fix and shown gone after: a task file created and left
      **uncommitted** in a sibling worktree is absent from the pre-fix scan's numbering and present
      in the post-fix scan's
- [ ] The rest of `SKILL.md`'s shell blocks are checked for the same silent-bareword class of bug,
      and the result is stated either way
- [ ] `check-portability.py` passes on the changed shipped files
- [ ] `version` bumped in both manifests with a matching `CHANGELOG.md` heading, and the
      behavioral evals run before merge
- [ ] Every doc describing the changed behavior is updated in the same change — or the docs
      checked are named here, with why none needed it
