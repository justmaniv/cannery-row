---
created: 2026-08-09
updated: 2026-08-09
completed: ""
status: new
owner: justmaniv
blocked-by: ""
links:
  - skills/task-lifecycle/SKILL.md
  - scripts/check-portability.py
  - README.md
---

# The skill mandates a push, so it fails on a project that has no remote

## What's wrong

`skills/task-lifecycle/SKILL.md` requires a push as part of every transition, and a project tracked
only on a filesystem has nothing to push to. `git push` in a repository with no remote exits
non-zero. The skill is the product, and this is the product not working for a use it was never meant
to exclude — local-only projects are a real and ordinary way to use it.

Verified in the shipped file today:

| Line | Text | Assumes |
|------|------|---------|
| 284 | `## Commit + push (closes every transition)` | a remote, in the section title |
| 286 | "committed and pushed in the same session" | a remote |
| 290–292 | "commit + push immediately" ×2, "Push when the batch is internally consistent" | a remote |
| 372 | "It mandates the commit + push" | a remote |
| 256 | "the norm now that `main` is PR-protected" | a host with PR-based branch protection |
| 101 | "branches with an open PR" | a host with pull requests |
| 86 | "reset the branch to `origin/main` first" | a remote named `origin` |

**The requirement is over-specified against its own stated reason.** Line 286 justifies it as
provenance: *"why this task moved … lives in conversation context until it's in git history."* A
local `git commit` satisfies that completely. Push is about sharing and backup — a real benefit, a
different concern, and not what the paragraph argues for.

## Why the gates didn't catch it

`scripts/check-portability.py --list` has 21 terms covering languages, vendors, databases, hosts and
cadence words. **None of them covers remote or host-workflow vocabulary** — `push`, `origin`, `PR`,
`pull request`, `fork`, `branch protection` are all invisible to it. So the skill names a specific
collaboration topology and passes a gate whose whole job is catching exactly that class of
assumption.

Worth stating plainly because the gate's own docs claim the broad version of its scope: shipped files
"must not name a language, vendor, host, or planning cadence." A remote workflow is host vocabulary
by that definition, and the term list disagrees with the sentence describing it.

## The fork

| Option | Trade-off |
|--------|-----------|
| **Make the push conditional in prose** — "commit; push if the project has a remote" | Smallest diff, keeps the section's shape. Leaves the agent to notice the condition, and an agent that skims will still try the push. |
| **Split the section** — commit is the invariant, push is a separate step gated on `git remote` returning anything | States the actual dependency structure: provenance needs a commit, sharing needs a remote. Longer, and renames a section other docs may reference. |
| **Add the missing gate terms as well** — put `push`, `origin`, `PR`, `pull request` in `check-portability.py` | Stops the whole class recurring rather than fixing seven lines. Will fire on legitimate uses in the repo's own non-shipped docs, so it needs the shipped/not-shipped boundary to hold precisely. Note `CONTRIBUTING.md` and `README.md` *should* keep saying PR — they describe this repo's own workflow, not the skill's. |

Recommendation: **option 2 plus option 3.** The prose fix alone leaves the gate blind to the next
occurrence, and this is the second time a portability class has been found by eye after passing CI
(the first is in `tasks/done/`, the cadence word added two days after a clean manual audit). Option 3
is the part that makes it stay fixed.

⚠️ **This is a skill change, so the full release ritual applies:** bump `version` in **both**
`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, add the matching `CHANGELOG.md`
heading, and run the behavioral evals before merging. `check-release.py` fails the build without the
bump — see `tasks/done/003-*` for what a merged fix with no bump costs.

Also decide whether the skill should assume **git** at all. Lane moves and the board work on a plain
directory tree; git is what makes the history story true. That is a bigger question than this task
and probably its own — but if the answer is "git is assumed, a remote is not," say so once in the
skill rather than leaving it implied.

## Done when

- [ ] The skill's commit step works as written on a repository with no remote — provenance stated as
      requiring a commit, sharing stated as requiring a remote, and no instruction that exits
      non-zero when `git remote` is empty
- [ ] `origin/main`, "PR-protected" and "an open PR" no longer appear in the skill as universals;
      the campsite and numbering sections read correctly for a local-only project
- [ ] Either the portability gate gains terms for host-workflow vocabulary, or the decision not to
      add them is recorded with the reason — the gate's docs currently claim a scope its term list
      does not cover
- [ ] `version` bumped in both manifests with a matching `CHANGELOG.md` heading, and the behavioral
      evals run before merge
