---
created: 2026-08-09
updated: 2026-08-09
completed:
status: new
owner: justmaniv
blocked-by: ""
links:
  - tasks/README.md
  - skills/task-lifecycle/SKILL.md
  - tasks/done/007-task-body-contract-is-undocumented-and-unenforced.md
---

# The task template has no docs criterion, so keeping docs current depends on whoever remembers

## The gap

Task 007 established that a task file's body has a contract and made it enforceable: an H1 and a
`## Done when` with at least one criterion, in every lane, refused by the board generator when
missing. It settled the *shape* of the checklist. It said nothing about what belongs *in* it.

So the shipped template offers two placeholders and stops:

```markdown
## Done when

- [ ] A criterion someone else can check without asking what you meant
- [ ] Another one
```

That is the whole default, in both places the template appears — `tasks/README.md` §"The body" and
`SKILL.md` §"The shape of a task file". Neither mentions documentation.

**Verified state of the repo today:**

| Where docs could be required | What is actually there |
|---|---|
| `tasks/README.md` body template | two generic placeholders; no docs criterion |
| `SKILL.md` "shape of a task file" | same two placeholders |
| `SKILL.md` `wip → done` procedure | reconcile the checklist, sweep dependents, clean the campsite — no docs step |
| `SKILL.md` mentions of `docs/` | two, both incidental: `grep` targets for prior coverage (§"Before creating"), and locating the board's output (§"Regenerate any projection") |
| board generator | gates H1 and `## Done when` presence only |

Nothing anywhere asks whether the change left a document wrong. Updating docs is therefore a habit,
not a contract — and habits are exactly what the two-pass model cannot rely on, because the session
that closes a task is not the session that knew which documents described the old behavior.

**This is not theoretical in this repo.** Ruling 1 on task 019 established that git is not optional,
while `README.md:57` still tells readers *"the lanes and the board work on a filesystem alone… Take
as many of those layers as your project actually has."* A ruling landed in `tasks/` and the front
page kept advertising the opposite. A docs criterion on 019 is what would have caught it.

## The vacuity problem — this is the whole design difficulty

`- [ ] Docs updated` is worse than nothing. It is tickable without reading a single document, and
it converts a real obligation into a box that is always green. This project's own README warns
against exactly this shape of check, and its coverage standard names the failure: a test that
would not fail if the code broke is not a test.

The criterion has to be unsatisfiable without doing the work. The mechanism available is
**naming** — a criterion that cannot be resolved without listing the documents inspected:

```markdown
- [ ] Every doc describing the changed behavior is updated in the same change — or the docs
      checked are named here, with why none needed it
```

A closer who ticks that without naming anything has visibly not resolved it, and the strikethrough
convention already covers the legitimate "none applied" case with a stated reason.

## The fork

**How the default is carried.**

| Option | Trade-off |
|--------|-----------|
| **A. Convention only** — add the criterion to both templates | Cheapest, no new gate surface. Relies on the author not deleting the line, and nothing notices if they do. |
| **B. Convention + gate** — the board generator refuses a task whose checklist has no docs criterion | Enforced the way 007 enforced H1 and `## Done when`, so there is precedent. But a gate can only see that a *line exists*, never that the docs were actually read — so it buys shape and may actively manufacture ticked-but-untrue criteria, which is the vacuity problem wearing a green check. |
| **C. Convention + a closure-time question** in `SKILL.md`'s `wip → done` procedure | Puts the check at the moment the information exists — the closer just did the work and knows what changed. No new gate surface, and it composes with the campsite gate already there. |

Recommendation: **A + C, explicitly not B.** The generator should keep gating structure it can
actually verify. A gate that greps for a sentence teaches authors to keep the sentence, which is
the opposite of the goal; the closure-time question in the skill is where a real answer is
available. Record the reasoning for declining B in the change, so it is not re-proposed as an
oversight.

**Downstream propagation.** `tasks/README.md` is copied into consumer repos rather than shipped by
the plugin, so a template change reaches an existing adopter only when they re-fetch it. The
skill's copy travels with the plugin version. These two move at different speeds, and the change
must say so rather than assume adopters are current.

## Done when

- [ ] The body template in `tasks/README.md` carries a docs criterion in its `## Done when`
      example, worded so it cannot be resolved without naming the docs checked
- [ ] `SKILL.md` §"The shape of a task file" carries the identical criterion — the two templates
      are compared line by line and do not disagree
- [ ] `SKILL.md` §`wip → done` asks the docs question as a numbered step, alongside the checklist
      reconciliation and the campsite gate
- [ ] The decision on option B is recorded with its reasoning — a gate can verify a line exists,
      not that it is true — so declining it reads as deliberate rather than forgotten
- [ ] The change states how an existing adopter picks the new template up, given
      `tasks/README.md` is copied and the skill is versioned
- [ ] `check-portability.py` passes on the changed shipped files
- [ ] `version` bumped in both manifests with a matching `CHANGELOG.md` heading, and the
      behavioral evals run before merge
- [ ] Every doc describing the changed behavior is updated in the same change — at minimum
      `README.md`'s description of what the generator gates — or the docs checked are named here,
      with why none needed it
