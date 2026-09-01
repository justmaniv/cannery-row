---
created: 2026-08-06
updated: 2026-08-06
completed: 2026-08-06
status: done
owner: justmaniv
blocked-by: ""
links:
  - NOTICE
  - LICENSE
---

# Decide whether NOTICE should carry a legal name

`NOTICE` currently reads `Copyright 2026 justmaniv` — the GitHub handle, chosen because it is
verifiable and does not invent a legal identity.

Apache-2.0 §4(d) requires downstream redistributors to carry this file forward, so whatever it says
propagates. A handle is legally workable but weak if the copyright ever needs asserting.

Not urgent, and not a blocker on anything. It is here because "the placeholder is fine" should be a
decision someone made rather than a thing nobody looked at.

## Ruling — 2026-08-06

**The handle stays. Confirmed deliberate, not left by default.**

Copyright vests in the author automatically; a notice is *evidentiary, not constitutive* — it
documents the claim rather than creating it. So a pseudonymous holder is workable, and Apache-2.0
§4(d) makes redistributors carry the file forward regardless of the name in it.

The only scenario where a handle is weaker than a legal name is **enforcement**, where the handle
would have to be tied to a legal person. The GitHub account already does that, publicly and with a
timestamped history. That is a thin but real link, and it is proportionate to a markdown-and-Python
project with no commercial weight.

Revisit alongside the ADR that governs this repo's licensing posture if the project ever carries
commercial weight — the same trigger already recorded there for re-opening the license with counsel.
Not before; changing it now would be ceremony.

## Done when

- [x] Either the handle is confirmed deliberate, or a legal name replaces it — **confirmed
      deliberate**, with the reasoning above rather than a bare yes
- [x] If changed, the Steinbeck / Monterey non-affiliation note below it is preserved — not changed,
      so the note stands untouched
