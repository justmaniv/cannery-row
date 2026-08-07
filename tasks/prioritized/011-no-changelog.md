---
created: 2026-08-07
updated: 2026-08-07
completed: ""
status: prioritized
owner: justmaniv
blocked-by: ""            # cleared 2026-08-07 — 010 closed; see "What this was blocked on"
links:
  - CONTRIBUTING.md
  - tasks/done/010-releases-have-no-tags.md
---

# An adopter who updates cannot find out what changed

## What's wrong

There is no `CHANGELOG.md`, and `grep -ril changelog` over the whole repository returns nothing.

The release loop tells consumers to run `plugin update`, and the plugin then changes underneath
them — `0.4.3` altered a **stated invariant** in the skill, which is about as material as a change
to this project gets. Nothing tells them that. The only record is a commit message, and the only
way to read it is to know the repository exists and go looking.

This matters more here than in a typical library. The artifact is a *procedure Claude follows*, so
a change to it changes behavior in someone's repository without changing a line of their code.
"Why did it start rewriting `blocked-by:` instead of clearing it?" has an answer, and that answer
should not require `git log`.

## What this was blocked on — cleared 2026-08-07

**[[010-releases-have-no-tags]]** — a changelog's entries anchor to released versions, and at the
time no version corresponded to anything you could check out. Writing the entries first would have
meant writing `## 0.4.2` next to a version that cannot be located, which is the stale-pointer
problem this project keeps arguing against. Tag first, then the changelog has something to point at.

**Resolved.** `cannery-row--v0.3.0` through `v0.4.3` are tagged and pushed, each at the commit that
bumped the manifest. Every entry this task needs to write now has a locatable anchor, and
`git log cannery-row--v0.4.1..cannery-row--v0.4.2` produces the source material for it.

## Scope

Small deliberately — `Keep a Changelog` format, one entry per released version, backfilled from the
commits that bumped `plugin.json`. There are **five** tagged (`0.3.0`, `0.4.0`, `0.4.1`, `0.4.2`,
`0.4.3` — this said four, inheriting the undercount that 010 was corrected for), and the history is
short enough to write honestly rather than reconstruct. Each tag points at its bump commit, so
`git log cannery-row--v0.4.1..cannery-row--v0.4.2` is the source material for an entry.

The entry that matters most is `0.4.3`, because it changed a documented invariant. Write that one
first and let it set the bar for how much detail an entry carries.

Worth deciding at the same time, but not worth a separate task: whether `check-release.py` should
also require a changelog entry when it requires a version bump. It already knows exactly when a
release is happening, so the check is nearly free — but a gate that can be satisfied by typing a
line of prose is a gate that will be satisfied by typing a line of prose. Argue it either way in
the closing note.

## Done when

- [ ] `CHANGELOG.md` exists with an entry per released version, `0.3.0` through current
- [ ] The `0.4.3` entry states plainly that invariant 6 changed and what it changed to
- [ ] `CONTRIBUTING.md`'s release loop names the changelog entry as part of shipping
- [ ] A recorded decision on whether `check-release.py` enforces an entry, with the reasoning
