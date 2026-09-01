---
created: 2026-08-07
updated: 2026-08-07
completed: 2026-08-07
status: done
owner: justmaniv
blocked-by: ""
links:
  - CONTRIBUTING.md
  - scripts/check-release.py
  - .claude-plugin/plugin.json
---

# Eight versions have shipped and none of them is findable in git

> **Corrected at pickup.** As written this task said five versions had shipped and then listed
> four (`0.3.0`, `0.4.1`, `0.4.2`, `0.4.3`), omitting `0.4.0` and the three pre-pull-request
> releases. Walking `.claude-plugin/plugin.json` through history shows **eight**: `0.1.0`, `0.1.1`,
> `0.2.0`, `0.3.0`, `0.4.0`, `0.4.1`, `0.4.2`, `0.4.3`. Backfilling only the four named would have
> left `0.4.0` — a real release between two tagged ones — invisible, which is the exact problem
> this task exists to remove.

## What's wrong

`git tag -l` is empty. `gh release list` is empty. Eight versions have been installable off `main`,
and **there is no way to answer "which commit is 0.4.2"** except by bisecting
`.claude-plugin/plugin.json` by hand.

That is tolerable while the only user is the author. It stops being tolerable the moment someone
else is running it for a week and says "it broke after I updated" — the first question is *what
changed between those two versions*, and right now nobody can produce the diff without archaeology.

`check-release.py` already enforces that the version **moves** when shipped content changes. It
does not, and should not, make the version *locatable*. That is this task.

## The tool already exists

`claude plugin tag` is purpose-built for it and validates the thing most likely to go wrong:

```bash
claude plugin tag --dry-run          # prints the tag it would create
claude plugin tag --push -m "cannery-row %s"
```

It creates `{name}--v{version}` and **refuses if `plugin.json` and the marketplace entry disagree**
— the same invariant `check-release.py` guards, checked again at the moment it matters. It also
refuses on a dirty tree.

## The fork worth deciding

| Option | Trade-off |
|--------|-----------|
| **Tag manually at merge** | One command, no CI changes, and it is on the release loop in `CONTRIBUTING.md` where the version bump already lives. Relies on remembering — the same class of failure the pinned-version incident (task 003) already proved this project is bad at. |
| **Tag from CI on push to main** | Cannot be forgotten. Needs a workflow with `contents: write`, which this repo currently does not grant — `permissions: contents: read` is a deliberate line, and widening it deserves an argument rather than a shrug. |
| **Backfill the four historical tags too** | Cheap (`git tag <name> <sha>` against the commits that bumped the manifest) and makes the existing history navigable rather than only future releases. Recommended regardless of which option above wins. |

Recommendation: **manual at merge, plus the backfill**, and revisit if it gets forgotten once. The
CI option trades a permission this repo has been deliberate about for a convenience, and the release
loop is already a written checklist that a human walks.

## What was decided and done

**Manual at merge, plus a backfill from `0.3.0` onward.** Recorded in `CONTRIBUTING.md` under *Why
tagging is manual rather than CI*, with the `contents: write` trade-off stated: every workflow here
grants `contents: read`, and a read-only token plus no secrets is the property that makes a fork's
pull request uninteresting to abuse.

The recommendation added one thing the task did not consider. The task framed the fork as
manual-vs-CI, but the escalation if tagging *is* forgotten need not be CI-with-write — a
**read-only gate** that fails the build when an already-shipped version has no tag converts the
memory problem into a build-breaker while leaving the token read-only. That is written down as the
next move rather than built now, since nothing has been forgotten yet.

Tags point at the commit that **bumped the manifest**, not the tip of `main` while that version was
current, so a tag-to-tag diff is exactly the shipped change:

| Tag | Commit | |
|-----|--------|---|
| `cannery-row--v0.3.0` | `cc1b91b` | docs+skill: validate on authorship not age |
| `cannery-row--v0.4.0` | `c0a326e` | task(007): H1 and Done when enforced |
| `cannery-row--v0.4.1` | `1f6a6bc` | task(008): gate tests, 85% floor |
| `cannery-row--v0.4.2` | `e3b3572` | task(009): board adoption path |
| `cannery-row--v0.4.3` | `e46b13e` | task(004): eval suite |

`0.1.0`, `0.1.1` and `0.2.0` predate the pull-request loop and were left untagged deliberately —
they were direct-to-`main` commits from the first day and nobody will diff them.

## Done when

- [x] A decision recorded on manual-vs-CI tagging, with the `contents: write` trade-off stated —
      `CONTRIBUTING.md`, *Why tagging is manual rather than CI*
- [x] `0.3.0`, `0.4.1`, `0.4.2`, `0.4.3` tags exist and point at the commits that shipped them —
      **plus `0.4.0`**, which the task omitted; all five pushed to `origin`
- [x] `CONTRIBUTING.md`'s release loop names the tagging step alongside the version bump — new
      step 4, with the warning that the tool tags `HEAD` rather than the bump commit
- [x] `claude plugin tag --dry-run` is shown to agree with the tag that actually gets created —
      before the backfill it printed `Tag: cannery-row--v0.4.3`; after, it exits `1` with
      `Tag "cannery-row--v0.4.3" already exists locally`. The collision *is* the agreement: the
      name it computes and the name created by hand are the same string.
