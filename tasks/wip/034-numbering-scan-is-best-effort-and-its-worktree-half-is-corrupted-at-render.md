---
created: 2026-08-30
updated: 2026-08-30
completed:
status: wip
owner: justmaniv
blocked-by: ""
links:
  - skills/task-lifecycle/SKILL.md
  - tasks/new/021-numbering-scan-worktree-half-scans-nothing.md
---

# The numbering scan is presented as the safeguard, and its worktree half is corrupted before Claude reads it

## Two defects in one section, and they compound

§"Assigning the next task number" says **"Always compute the next number with this scan"** and
offers *"the loser renumbers via `git mv` before merge"* as the remedy for a collision. That
presents a best-effort scan as the control. It is not one, and the section never says so.

### 1. The scan cannot win the race it is written to prevent

**It cannot see a number a concurrent session has decided on but has not committed anywhere
yet.** Two sessions that both scan before either writes read the same max and both take it —
a lost-update race. Running the scan more carefully does not close it.

And the stated remedy has no trigger: it fires when a person happens to notice. Measured in an
adopting repository where concurrent sessions are the default — **three collisions in six
days**:

| # | What actually failed | Detected by |
|---|---|---|
| 1 | Two correct scans, neither able to see the other's unpushed file | A person, **5 hours** after both were on the main branch |
| 2 | Scan run once, then the next two numbers assumed | Nobody at the time — a **third** session tripped over it |
| 3 | Correct scan, lost to a sibling's uncommitted decision | A merge conflict on a **derived** file |

### 2. A bare `$` + digit in this file is replaced with a caller argument before Claude reads it

**[Verified 2026-08-30]** The worktree half of the scan shipped as `awk '/^worktree /{print $2}'`.
Claude Code substitutes bare `$0`–`$9` in a skill body with the caller's argument words whenever
the skill is invoked with arguments:

| `args` at invocation | what arrives in context |
|---|---|
| `alpha bravo charlie delta` | `awk '/^worktree /{print charlie}'` |
| `one two three` | `awk '/^worktree /{print three}'` |
| *(none)* | `awk '/^worktree /{print $2}'` — intact |

`${name}`, `"$var"`, `$(...)` and `$((...))` all survive byte-identical; only the bare digit form
is touched. **The corrupted line is valid shell** — an undefined `awk` variable prints an empty
string, so the half prints one blank line per worktree instead of erroring. `find "/tasks" …`
then matches nothing and `2>/dev/null` swallows it.

So the half that exists to catch an **uncommitted sibling** — the one case the committed-refs
half structurally cannot cover — has never run in any session that passed arguments. A documented
safeguard that silently does nothing is worse than a known gap, because it is trusted.

⚠️ **This supersedes the diagnosis in
[task 021](021-numbering-scan-worktree-half-scans-nothing.md), which is wrong about the cause.**
That task reports the shipped text as `awk '/^worktree /{print new}'`. It never was:
`git log -S'print new' -- skills/task-lifecycle/SKILL.md` returns nothing, and `{print $2}` has
been in the file since the initial commit. Its author was reading the **rendered** skill in a
session whose third argument word was `new` — the substitution above, one render earlier. The
`od -c` evidence in 021 is real and reproduces exactly; only the attribution to the file is
wrong. 021 is left open for its owner to dispose of; the code fix is here.

## The fix

- **Dollar-free**, so no future argument can corrupt it: `sed -n 's/^worktree //p'` replaces the
  `awk`. Verified across two worktrees, and end-to-end on the failure it exists to catch — a task
  file created and left **uncommitted** in a sibling worktree is absent from the corrupted scan's
  max (`033`) and present in the fixed scan's (`099`).
- **It also fixes a second defect nobody had noticed**, present even with no substitution:
  splitting on whitespace truncates a worktree path at its first space. Verified against a
  worktree literally named `a path with spaces` — the field form returns `…/a`, the replacement
  returns the whole path. Anyone whose checkouts live under `~/My Projects/` has been running a
  half-scan that silently found nothing.
- **Say the scan is best-effort**, name the race, and point at a merge-time check as the
  guarantee — bounded honestly: such a check makes both halves of a collision unable to *land*;
  it does not make the collision impossible, because it runs against one tree and is blind to one
  still split across two unproposed branches.
- **Warn skill authors** about `$0`–`$9` in a skill body, since the next such line will fail the
  same silent way.

The skill does not ship the check itself — whether a project runs automated checks is its
business, and this skill assumes no host.

## Done when

- [ ] The scan's worktree half prints one absolute path per worktree, verified in a repository
      with at least two worktrees, and contains no `$` + digit
- [ ] The failure is reproduced before the fix and shown gone after: an **uncommitted** task file
      in a sibling worktree is absent from the pre-fix scan's numbering and present in the
      post-fix scan's
- [ ] The rest of `SKILL.md` is checked for bare `$0`–`$9`, and the result is stated either way
- [ ] The section states that the scan is best-effort and that a merge-time check is the
      guarantee, **with the bound on what such a check does and does not buy**
- [ ] `check-portability.py` passes on the changed shipped files
- [ ] `version` bumped in both manifests with a matching `CHANGELOG.md` heading, and the
      behavioral evals run before merge
- [ ] Every document this change makes wrong is updated — or the docs checked are named here,
      with why none needed it
