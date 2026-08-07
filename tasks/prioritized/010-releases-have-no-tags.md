---
created: 2026-08-07
updated: 2026-08-07
completed: ""
status: prioritized
owner: justmaniv
blocked-by: ""
links:
  - CONTRIBUTING.md
  - scripts/check-release.py
  - .claude-plugin/plugin.json
---

# Five versions have shipped and none of them is findable in git

## What's wrong

`git tag -l` is empty. `gh release list` is empty. Versions `0.3.0`, `0.4.1`, `0.4.2` and `0.4.3`
have all been installed by someone, and **there is no way to answer "which commit is 0.4.2"**
except by bisecting `.claude-plugin/plugin.json` by hand.

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

## Done when

- [ ] A decision recorded on manual-vs-CI tagging, with the `contents: write` trade-off stated
- [ ] `0.3.0`, `0.4.1`, `0.4.2`, `0.4.3` tags exist and point at the commits that shipped them
- [ ] `CONTRIBUTING.md`'s release loop names the tagging step alongside the version bump
- [ ] `claude plugin tag --dry-run` is shown to agree with the tag that actually gets created
