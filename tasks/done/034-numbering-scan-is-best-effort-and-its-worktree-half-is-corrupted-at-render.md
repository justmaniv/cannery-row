---
created: 2026-08-30
updated: 2026-08-30
completed: 2026-08-30
status: done
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
| `alpha bravo charlie delta` | `{print charlie}` — the **third** word |
| `one two three` | `{print three}` |
| `one two` | intact, raw arguments appended as a footer |
| *(none)* | intact |

**The indexing is zero-based, and the substitution only fires when the caller passes enough words
to reach the index.** That narrowness is why it survived: a two-word invocation renders correctly,
and so does every description-triggered invocation with no arguments. `${name}`, `"$var"`,
`$(...)` and `$((...))` all survive byte-identical; only the bare positional form is touched. **The corrupted line is valid shell** — an undefined `awk` variable prints an empty
string, so the half prints one blank line per worktree instead of erroring. `find "/tasks" …`
then matches nothing and `2>/dev/null` swallows it.

So the half that exists to catch an **uncommitted sibling** — the one case the committed-refs
half structurally cannot cover — has never run in a session that passed three or more argument
words. A documented safeguard that silently does nothing is worse than a known gap, because it is
trusted.

⚠️ **"Usually" is doing work in "usually valid shell."** An argument word carrying a quote or a
brace breaks the single-quoted `awk` program loudly instead of quietly. The silent failure is the
common case, not a property of the mechanism.

⚠️ **This supersedes the diagnosis in
[task 021](021-numbering-scan-worktree-half-scans-nothing.md), which is wrong about the cause.**
That task reports the shipped text as an `awk` program printing an undefined variable. It never
was. `git log -S` alone would not settle this — a string added and removed inside one commit nets
to zero and `-S` misses it — so **every blob of that path across `git rev-list --all` was
enumerated**: ten distinct blobs, none containing the quoted text, nine carrying the field
reference, the tenth being this change. `--follow` shows no rename. *[Inference, high confidence]*
its author was reading the **rendered** skill in a session whose argument at that index was the
word they quoted; that fits the measured mechanism exactly but cannot be proved, because only the
current installed copy survives on disk. The `od -c` evidence in 021 is real and reproduces
exactly; only the attribution to the file is wrong. 021 is left open for its owner to dispose of; the code fix is here.

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
  backstop — bounded honestly. ⚠️ The first draft of this bound was wrong and a fresh-context
  reader broke it: *"unmerged branches"* is not *"branches nobody has proposed"*. **Two open
  reviews are two unmerged branches**, each passing against a tree the other's file was never in,
  so without a branch-must-be-current rule the second's stale pass is accepted and lands. A
  tree-local check therefore buys a **trigger**, not prevention. The same reader noted the
  blindness is a property of *what the check reads*, not a law — a check that unions
  `refs/heads refs/remotes`, as the scan itself does, would see a pushed half.
- **Warn skill authors** about `$0`–`$9` in a skill body, since the next such line will fail the
  same silent way.

The skill does not ship the check itself — whether a project runs automated checks is its
business, and this skill assumes no host.

## Done when

- [x] ✅ The scan's worktree half prints one absolute path per worktree — verified across two
      worktrees — and contains no `$` at all, not merely no digit after one
- [x] ✅ Reproduced before and gone after: an **uncommitted** `099-` task file in a sibling
      worktree yields max `033` under the pre-fix form and `099` under the post-fix form
- [x] ✅ The rest of `SKILL.md` was checked: **zero** bare positional tokens remain, repo-wide
      across `skills/`. The gate below now asserts it on every build rather than leaving it to a
      one-time grep
- [x] ✅ **Enforced, not just written** — `scripts/check-skill-args.py`, blocking in `ci.yml`,
      test-first (RED `9cc466a`, GREEN `7f9190f`), 96% covered including `main()`. Discriminating:
      against `origin/main`'s skill it reports line 348 and exits 1; against this branch, exits 0.
      It does not flag `${name}`, `"$var"`, `$(...)`, `$((...))` or `$4.52` — all measured
      surviving substitution. It caught its own author mid-change, on a table header inside the
      note explaining the hazard
- [x] ⚠️ The section states the scan is best-effort and names a merge-time check — **as the
      backstop, not "the guarantee"**, which is how this criterion was worded and it was wrong. A
      fresh-context reader broke the first draft's bound: two open reviews are two unmerged
      branches, so without a branch-must-be-current rule the second's stale pass is accepted and
      both halves land. A tree-local check buys a **trigger**, not prevention. The section says so,
      and names the two design choices that decide its reach
- [x] ✅ `check-portability.py` passes — 4 shipped files, no stack-coupled vocabulary
- [x] ✅ `version` 0.7.0 → 0.8.0 in **both** `.claude-plugin/*.json` with a matching `[0.8.0]`
      heading and compare link; `check-release.py` green. Evals run against the final text before
      merge: **both cases 1.00 with the plugin**, mean Δ **+0.30**, `840s`, `$5.41`, exit 0.
      `evals/README.md` re-pinned to 0.8.0 with this measurement — and the narrowed
      `done-when-reconciliation` delta (+0.19 → +0.14) noted as the *baseline* improving, since the
      with-arm was 1.00 on 3/3 in both
- [x] ✅ Corrected: `README.md` advertised *"collision-safe numbering across worktrees"* — the
      exact claim this change withdraws; `evals/README.md`'s measurement header pinned skill 0.7.0;
      `CHANGELOG.md` initially described softening an imperative that had not been touched, so the
      imperative was actually softened; task 021's cause, its `[Inference]` label, and its two
      references to 034 that named a lane and a relative path resolving to nothing. **Checked and
      unchanged:** `CONTRIBUTING.md` and `CLAUDE.md` (the dev/release loops are untouched);
      `docs/task-board.md` (regenerated per this repo's same-commit rule); `tasks/README.md` (layout
      only — numbering is the skill's ground, not its). **021 is left open for its owner**, its
      criteria now met by this merge, which is the owner's disposition to take, not ours.
