---
created: 2026-08-09
updated: 2026-08-09
completed:
status: new
owner: justmaniv
blocked-by: ""
links:
  - README.md
  - CONTRIBUTING.md
  - skills/task-lifecycle/SKILL.md
---

# Nobody outside the repo can say which of these tasks matters most

## What's wanted

The lane tree is the tracker and it works, but it is write-only from the outside. A reader who
installs the plugin, hits the missing opt-out or the hardcoded task root, and wants to say *"this
one, please"* has no surface to say it on. Priority is currently one person's read of a directory.

Some way for interested users to signal importance — reactions, votes, a poll — so ordering in
`prioritized/` can answer to more than the author's own guess.

## Verified state, and why it argues for waiting

The repository is **three days old** (created 2026-08-06). Measured today:

| Signal | Value |
|---|---|
| Stars | 1 |
| Forks | 0 |
| Issues, open or closed | 0 |
| Contributors in `git log` | 2, both the author's own identities |
| Issues feature | enabled |
| Discussions feature | disabled |

**There are no voters.** A voting surface opened now would be process built for a population of
zero, and it would not sit idle — it would need triage, conversion rules, and a place in
`CONTRIBUTING.md` from the first day, all maintained against no incoming signal. This project's own
standard is that tooling should be enforced and evergreen rather than informational shelfware; a
poll nobody answers is the shelfware case exactly.

So the recommendation is **not yet** — but the design question is worth settling now, while it is
cheap and nobody is waiting on the answer, because the moment real traffic arrives is the worst
moment to be inventing a policy.

## The tension to settle before building anything

A public voting surface means a **second place where work is described**, and this project's whole
argument is that work belongs in one place, in the repo, in git. `README.md`'s comparison table
sells the differentiator as *"one file per task, inside the repo, in git"*, and positions against
*"one markdown list… outside the repo."* Adopting a host's issue tracker as a peer of `tasks/`
would undercut that in public, on the front page.

The skill already names the failure mode in §"Before creating: check for prior coverage": two
artifacts answering the same question differently *silently diverge*, and that has already happened
once in the upstream project. Two trackers is that failure institutionalized.

The shape that survives the tension is a **strict asymmetry**:

- The host's issues are **intake and signal only — never state.** An issue carries a title, a
  description, and a count of who cares. It never carries a status, an assignee, or acceptance
  criteria, because those live in the task file.
- Conversion is **one-way and terminal.** A triaged issue becomes a task file; the issue then
  points at the task path and closes. It does not stay open in parallel.
- The vote is **read at triage time**, not continuously synced. Anything that tries to keep a
  count mirrored into frontmatter is a sync problem nobody needs.

Anything that lets an issue accumulate its own status is the two-tracker failure returning under a
different name.

## The fork

| Option | Trade-off |
|--------|-----------|
| **Issues as intake + 👍 signal** | Zero setup, already enabled, and the reaction count is the one prioritization signal every user already knows how to give. Reads as an issue tracker unless the asymmetry above is stated loudly and enforced at triage. |
| **Discussions with polls** | Currently disabled; turning it on is free. Reads unambiguously as "not the tracker," which protects the thesis. Lower traffic — people file issues by reflex and have to be redirected. |
| **A task-file PR** — a contributor proposes work by writing the task | Perfectly on-thesis, and it is what the project already implicitly asks for. Far too much friction for a *vote*: nobody writes a file to say "me too." Good for proposals, useless for ranking. |
| **Nothing yet** | No surface to maintain, no thesis risk, no signal. Correct while the population is zero; wrong the moment it is not. |

Recommendation: **Nothing yet, then Issues-as-intake when the trigger fires.** Discussions is the
tidier fit conceptually, but it fights user reflex, and a signal channel people do not use is worth
less than a slightly awkward one they do. Write the asymmetry into `CONTRIBUTING.md` in the same
change that opens the channel — not after the first misfiled issue.

**Trigger to revisit, so this is not a judgment call every week:** the first unsolicited issue
filed by someone who is not the author, or the first external fork or contributor. Any one of them
means a population exists and the answer changes.

## Done when

- [ ] A decision is recorded on whether a public importance signal exists, which surface carries
      it, and the trigger that opens it — durable enough that it does not get re-litigated
- [ ] If a channel is opened: `CONTRIBUTING.md` states the asymmetry — issues are intake and
      signal, never state; conversion to a task file is one-way and closes the issue
- [ ] If a channel is opened: the task file created from an issue records where it came from, and
      the issue records the task path, so neither side can be read as the sole record
- [ ] The `README.md` claim *"one file per task, inside the repo, in git"* is checked against
      whatever is decided, and either still holds verbatim or is revised in the same change
- [ ] `check-portability.py` passes — note the shipped-file list is `SKILL.md`, `tasks/README.md`,
      `generate-task-board.py` and `docs/task-board.md`; host vocabulary like `PR` and `pull
      request` is banned there but `CONTRIBUTING.md` is not scanned and may name names
- [ ] Every doc describing the changed behavior is updated in the same change — or the docs
      checked are named here, with why none needed it
