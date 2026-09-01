---
created: 2026-08-06
updated: 2026-08-06
completed: 2026-08-06
status: done
owner: justmaniv
blocked-by: ""
links:
  - .claude-plugin/plugin.json
  - scripts/check-release.py
  - tasks/done/00001-generated-board-leaked-upstream-links.md
---

# A pinned version withheld the fix, and reported success while doing it

## What happened

Task 001's fix was committed, pushed, and CI-green. Running `claude plugin update` on the one
machine that consumes this plugin returned:

    ✔ cannery-row is already at the latest version (0.1.0).

The installed copy still had the defect. `plugin.json` pins `version`, and pinning means installed
copies stay put until that string changes. The fix was public and unreachable at the same time,
and the update command reported success.

## Why this matters more than the defect it hid

The canonical-copy decision assumes a fix propagates. It doesn't propagate on merge; it propagates
on a version bump nobody was tracking. That reintroduces exactly the staleness the single-canonical
-copy rule was chosen to eliminate — just relocated from "two files" to "one file and a stale
cache," which is worse because it looks fine from both ends.

Found by dogfooding: the update was run because the fix had to reach the consumer, and the output
was read instead of assumed.

## Fix

- Bumped to `0.1.1`, in both manifests.
- `scripts/check-release.py` in CI: fails if the manifests disagree on a version, and fails if
  shipped content changed since the merge base without the version moving. README-only changes
  don't require a bump.

## Deliberately not done

Dropping the pin so every commit becomes a version (the SHA fallback). It would remove this failure
outright, but it also removes any way to signal a breaking change. Kept the pin plus a gate, which
preserves the signal and makes the omission loud. Revisit if the bump becomes friction.

## Done when

- [x] Version bumped, both manifests agree
- [x] CI fails on a version mismatch — verified by introducing one
- [x] CI fails when shipped content changes without a bump
- [x] The consuming machine actually received the fix
