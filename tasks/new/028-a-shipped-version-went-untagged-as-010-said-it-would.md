---
created: 2026-08-11
updated: 2026-08-30
completed:
status: new
owner: justmaniv
blocked-by: ""
links:
  - tasks/done/010-releases-have-no-tags.md
  - tasks/done/020-task-template-has-no-docs-criterion.md
  - CONTRIBUTING.md
---

# A shipped version went untagged, which is the one condition task 010 said should trigger the gate

## What happened

`0.5.1` shipped on 2026-08-09 and was never tagged. `git tag -l` and `git ls-remote --tags origin`
both return `v0.3.0, v0.4.0, v0.4.1, v0.4.2, v0.4.3, v0.4.4, v0.5.0` — `cannery-row--v0.5.1` exists
nowhere, local or remote.

Found 2026-08-11 by the independent read on task 020, and not by looking for it: that change added a
`[0.5.1]` compare link to `CHANGELOG.md` and the reader checked whether the tag it pointed at was
real. It was not. The link was removed and `0.6.0`'s compare link now spans `0.5.0…0.6.0`, so the
`CHANGELOG` is honest today — but it is honest by skipping a release rather than by describing one.

## Why this is 010's task and not a new question

**Task 010 already ruled on this, and pre-wrote the escalation.** It chose manual tagging over CI
because CI would need `contents: write`, and *"a read-only token plus no secrets is the property that
makes a fork's [proposed change] uninteresting to abuse."* That reasoning still holds and is not
being reopened.

What it also said, in the same closure:

> Recommendation: **manual at merge, plus the backfill**, and revisit if it gets forgotten once.

and:

> the escalation if tagging *is* forgotten need not be CI-with-write — a **read-only gate** that
> fails the build when an already-shipped version has no tag converts the memory problem into a
> build-breaker while leaving the token read-only. That is written down as the next move rather than
> built now, since nothing has been forgotten yet.

Something has now been forgotten. This task is that condition firing, not a fresh design.

## The shape of the gate

`check-release.py` already reads both manifests and `CHANGELOG.md`, already runs in CI, and already
knows what a version string is. The check is one more question it can ask with no new permission and
no new dependency: **for every version with a `CHANGELOG.md` heading other than the one this change
is introducing, does `cannery-row--v<version>` exist as a tag?**

The boundary matters and is the part to get right. The version being *introduced* by the current
change cannot have a tag yet — `CONTRIBUTING.md` establishes tags point at the commit that bumped
the manifest, which does not exist until merge. So the gate must exempt the newest heading, or it
fails every release change by construction. Getting that backwards turns the gate into a permanent
red build, which is worse than the silence it replaces.

Two open questions for whoever picks this up:

- **Where does it read tags from?** `git tag -l` sees only what the CI checkout fetched. A shallow
  or tag-less clone reports every version untagged. Whether the workflow needs `fetch-tags` or
  `fetch-depth: 0` is a real question and the answer belongs in the same change.
- **Does it also fail on a tag pointing at the wrong commit?** 010 established tags point at the
  bump commit, and `CONTRIBUTING.md` warns that `claude plugin tag` tags `HEAD` instead. Checking
  *existence* is cheap; checking *placement* is the failure 010 actually warned about. Recommend
  starting with existence and saying in the change why placement was left.

## ⚠️ Update 2026-08-30 — it is not one tag, it is three, and the step is being skipped every release

**[Verified 2026-08-30]** `git ls-remote --tags origin` against the released versions in
`CHANGELOG.md`:

| Version | Changelog heading | Tag on the remote |
|---|---|---|
| `0.5.0` | ✅ | ✅ |
| `0.5.1` | ✅ | ❌ — what this task was filed for |
| `0.6.0` | ✅ | ❌ |
| `0.7.0` | ✅ | ❌ |
| `0.8.0` | ✅ | ✅ — tagged at merge |
| `0.8.1` | ✅ | ✅ — tagged at merge |

**Three consecutive releases shipped untagged, two of them *after* this task was filed.** That
changes what this task is. It was written as a backfill — tag one commit that got missed — and the
evidence now says the manual tagging step in `CONTRIBUTING.md` §4 is not a one-time slip: it is
skipped by default and noticed by nobody, because nothing fails when it is.

**Consequences that are live right now**, not hypothetical:

- The compare links at the foot of `CHANGELOG.md` are dead for `0.6.0` and `0.7.0`. They resolve
  against tags that do not exist, and the file's own preamble promises they are *"exactly what
  shipped in that release"*.
- `0.8.0`'s compare link works only because `0.7.0`'s tag absence was worked around: it compares
  against `v0.7.0`, which will 404 until that tag is backfilled.

⚠️ **The reasoning in `CONTRIBUTING.md` §"Why tagging is manual rather than CI" is still sound** —
a tagging workflow needs `contents: write`, and a read-only token with no secrets is this repo's
strongest security property. **The conclusion drawn from it is what the evidence now falsifies.**
"Manual" was chosen on the assumption that a documented step gets run; three misses in a row say it
does not. That is a fork this task should decide rather than inherit:

| Option | Mechanism | Trade-off |
|---|---|---|
| **A — backfill and carry on** | Tag `0.5.1`, `0.6.0`, `0.7.0`; keep the manual step | Cheapest. ⚠️ Changes nothing about why they were missed — this is the third time |
| **B — a gate, not a workflow** | A check that fails when the version in `plugin.json` has no matching tag reachable from the main branch | Keeps the read-only token: it *reads* tags, never writes one. ⚠️ Fires one release late — it reds the build *after* the untagged release merged, which is detection, not prevention |
| **C — tagging workflow** | Automate it, grant `contents: write` | Cannot be forgotten. ⚠️ Spends the security property §"Why tagging is manual" was written to protect |

**[Inference] B plus A.** B is the only one that keeps the posture *and* has a trigger, and its
one-release lag is acceptable for something whose whole cost is a dead link. The recurrence is not
a discipline problem to try harder at — it is the shape this repository already argues against, in
`CONTRIBUTING.md`'s own words about gates that ran for months without being tested.

Found while shipping `0.8.0`, whose tag was created at merge per §4 — which is what made the
absence of the three before it visible.

## Done when

- [ ] `cannery-row--v0.5.1` exists and points at the commit that bumped the manifest to `0.5.1`,
      pushed to `origin` — and `CHANGELOG.md`'s `[0.5.1]` compare link is restored along with the
      ⚠️ note that currently explains its absence
- [ ] A read-only check fails the build when a version with a `CHANGELOG.md` heading has no
      matching tag, exempting the version the change under test is introducing
- [ ] A test proves the exemption works — a change that bumps to a new version and adds its heading
      passes, while a prior version missing its tag fails. Without both halves the gate is either
      vacuous or permanently red
- [ ] The workflow fetches tags, or the check is shown to work without them; whichever it is, the
      change says so rather than leaving it to the first red build to discover
- [ ] `contents: read` is unchanged in every workflow — the whole point of the read-only shape
- [ ] `CONTRIBUTING.md`'s *"Why tagging is manual rather than CI"* records that the escalation 010
      described has now fired, and what was built
- [ ] Every document and open task this change makes wrong is updated, and anything the work
      turned up that nothing yet records is written down — or what was checked is named here,
      with why none of it needed changing
