---
created: 2026-08-09
updated: 2026-08-09
completed: 2026-08-09
status: done
owner: justmaniv
blocked-by: ""
links:
  - README.md
  - CLAUDE.md
  - tasks/done/00024-validation-is-not-independent-review.md
  - tasks/done/00025-skill-does-not-say-where-its-own-check-stops.md
---

# The README recommends a second reader and gives nobody a way to have one

## What's wrong

Task 024 shipped § **"What validating the spec does not cover"**, which closes by telling an adopter
to *"have some reader that arrives with no framing to confirm — a subagent in a clean context, a
second session, a person."* That is advice, not setup. Nothing in the README says **where** the
instruction lives, **when** it fires, or **what it says**, so the layer that caught the failure the
section is about is the one layer a reader cannot copy.

Every other layer of this system is concrete and one paste away: the lanes are a `mkdir`, the
conventions are a `curl`, the structural gate is a `curl` plus a CI line. The layer that catches a
fabricated *mechanism* — the failure none of the others can see — is a paragraph of encouragement.

Two related defects in the same section, found while reading it back:

- **The stated property is wrong.** It says the reader must have *"read the code and not the task."*
  A reader who has not read the task cannot check its claims. The property that actually matters is
  that it has not been in **the conversation that accepted the task** — it reads the claims and the
  code, and none of the reasoning that made them sound right.
- **No trigger.** "Spend it on tasks whose output other sessions get held to" is the right rule and
  it is stated as a preference. It needs to sit next to the instruction it modifies.

## Scope

- **This repo adopts it too.** `CLAUDE.md` here governs sessions working on the plugin, and this
  repo tracks its own work with the skill it ships. Recommending a rule publicly while not running
  it is the gap the project keeps closing elsewhere.
- **Not `SKILL.md`.** Still `tasks/new/00025-*` — and the boundary is now sharper: the skill states
  where its own check stops, the README carries the setup, and the skill never prescribes a review
  mechanism it does not ship.
- **Not `tasks/README.md`.** It is inside the portability-scanned set and cannot name a host or an
  instructions-file convention. The rule is host-shaped by nature, so the README is its only home.

## Done when

- [x] The README carries a copyable pickup rule — an adopter can paste it into their project
      instructions without composing anything — *§ "The layer the plugin can't ship: a second reader
      at pickup", in Install*
- [x] The rule names its own trigger and says what to do with what comes back, rather than leaving
      "when" and "then what" to the reader — *"before any work starts — and again before commit when
      the deliverable is itself a spec"; correction is back-propagated to siblings with a dated note*
- [x] The falsification prompt is concrete enough to send a reader to the fixture rather than the
      assertion — a cited artifact existing is explicitly called out as not being the claim
- [x] The section states the property correctly: not "hasn't read the task", but "wasn't in the
      conversation that accepted it" — *fixed in both sections; the old wording was wrong and would
      have been copied*
- [x] The stack is stated once — what each layer catches and what it cannot — so the second reader
      reads as the top layer of a system rather than an extra chore — *opening paragraph of the new
      section: lanes → skill → gate → reader*
- [x] `CLAUDE.md` in this repo carries the rule, worded for this repo — *new § "Picking up a task
      you did not write", with the trigger widened to the prose this repo actually ships*
- [x] No version bump is needed, or one is done properly — *none needed: `README.md`, `CLAUDE.md`
      and task files are all outside the `skills/ scripts/ tasks/README.md .claude-plugin/`
      boundary; `check-release.py` passes*
