---
created: 2026-08-07
updated: 2026-08-07
completed: 2026-08-07
status: done
owner: justmaniv
blocked-by: ""            # cleared 2026-08-07 — 010 closed; see "What this was blocked on"
links:
  - CHANGELOG.md
  - CONTRIBUTING.md
  - scripts/check-release.py
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

- [x] `CHANGELOG.md` exists with an entry per released version, `0.3.0` through current
- [x] The `0.4.3` entry states plainly that invariant 6 changed and what it changed to
- [x] `CONTRIBUTING.md`'s release loop names the changelog entry as part of shipping
- [x] A recorded decision on whether `check-release.py` enforces an entry, with the reasoning

## Closing note — the gate question, decided: enforce it

`check-release.py` now fails a build where the version moved and `CHANGELOG.md` has no
`## [<version>]` heading. The argument, both ways, since the task asked for both.

**Against.** A gate satisfiable by typing a line of prose will be satisfied by typing a line of
prose. No script can distinguish a useful entry from a shrug, so what gets enforced is the ritual
rather than the thing the ritual is for. And this project has a stated stance against pre-emptive
gates — `CONTRIBUTING.md` says the escalation for an untagged release is *"reach for that the first
time this is forgotten, not before."* By that logic the changelog gate should wait for its first
miss too.

**For, and why it won.** Three things separate this from the tagging case:

1. **It is checkable at pull-request time, from the diff.** `check-release.py` already loads the
   version and already computes the shipped-file list against the merge base. The marginal cost is
   about ten lines and no new permission. The tag, by contrast, is created *after* the merge on a
   commit CI has already finished with — gating it needs a different trigger and a token with
   `contents: write`, which is a permanent cost to the security posture. "Wait for the failure" was
   an argument about *that* cost. There is no equivalent cost here.
2. **The prose objection applies equally to the check next to it.** Nothing stops you bumping
   `version` to a number that means nothing, and that check is still the one that would have caught
   task 003. Gates check presence; review checks quality. A presence check converts *forgot
   entirely* — silent until an adopter asks what changed — into *wrote something thin*, which is
   sitting in the diff where a reviewer can push back on it.
3. **The failure already happened.** Five releases shipped with no changelog, because nothing ever
   asked for one. Waiting for the first miss is not available; this task *is* the first miss.

Scoped narrowly on purpose: it fires only when shipped content changed **and** the version actually
moved, so a branch that forgot the bump gets told about the bump rather than scolded twice for one
mistake. Heading matching is anchored and boundary-guarded — `## [0.4.10]` does not satisfy `0.4.1`,
and a version named in a paragraph is not an entry.

**What was not done.** Nothing checks that an entry is *accurate*, and nothing ever will. The
`0.4.3` entry sets the bar by example — old wording quoted, new wording stated, observable symptom
named — and `CONTRIBUTING.md` points at it as the reference. That is a convention, not a gate, and
it is honest to say so.

**Also worth knowing.** `0.1.0`, `0.1.1` and `0.2.0` are left out, matching 010's decision to leave
them untagged. Entries are scoped to what an installed copy receives, so the four commits that
landed between `0.4.3` and this one — issue templates, `CLAUDE.md`, the tags, task files — have no
entry, because nothing changed for an adopter when they merged.
