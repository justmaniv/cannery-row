---
created: 2026-08-09
updated: 2026-08-11
completed: 2026-08-11
status: done
owner: justmaniv
blocked-by: ""
links:
  - tasks/README.md
  - skills/task-lifecycle/SKILL.md
  - tasks/done/007-task-body-contract-is-undocumented-and-unenforced.md
  - tasks/prioritized/019-user-cannot-opt-out-of-remote-operations.md
---

# A closure's findings reach the docs and the open tasks they change, not just whoever remembers

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
`SKILL.md` §"The shape of a task file". Neither mentions documentation, and neither mentions the
other tasks the work just changed the meaning of.

**Verified state of the repo today** — ⚠️ *as of 2026-08-09, before this task's own change. Every
`SKILL.md` line number below is now off by roughly 57 lines, and the `wip → done` row says seven
numbered steps where there are now eight. Left as written rather than re-pointed: this table is the
**before** picture and is what the change is measured against. This is the fourth citation-drift
note on this file; see the pattern rather than the individual numbers.*

| Where propagation could be required | What is actually there |
|---|---|
| `tasks/README.md` body template | two generic placeholders; no docs criterion |
| `SKILL.md` "shape of a task file" | same two placeholders |
| `SKILL.md` `wip → done` procedure (`:51-63`) | seven numbered steps: reconcile, three frontmatter fields, `git mv`, sweep dependents, clean the campsite — no step for either half below |
| `SKILL.md` §"Phase-tipping tasks" (`:370-383`) | **the one closure-time doc-currency step that already exists** — scoped to a single named document and its rendered visual |
| `SKILL.md` reverse-dependency sweep (`:345`) | walks `blocked-by:`, but the shipped command greps the *slug* anywhere in the file, so a task that **cites** this one does surface |
| `SKILL.md` mentions of `docs/` | two sites, both incidental: `grep` targets for prior coverage (`:200`), and locating the board's output (`:325`) |
| board generator (`:151-176`) | gates three things and only these: a missing H1, a missing `## Done when`, and a `## Done when` with zero items |

Outside the phase doc, nothing asks whether the change left a document wrong, and nothing anywhere
asks whether the closing session learned something an open task needs. Propagation is therefore a
habit, not a contract — and habits are exactly what the two-pass model cannot rely on, because the
session that closes a task is not the session that knew which artifacts described the old behavior.

## Two halves, one pain point

This task was originally scoped to the first half only. Both halves have the same cause — the
lifecycle propagates *structure* and never *content* — and one spec should carry them.

- **(a) The document the change left wrong.** Something asserts the old behavior and is now false.
- **(b) The finding no document is wrong about.** The closing session learned something true that
  nothing anywhere says. No existing sentence is incorrect; a sentence is *missing*, and only the
  closer knows it.

**Almost everything `wip → done` propagates today is structural**, found by a mechanical query over
paths: the reverse-dependency sweep (`grep` for the slug across `tasks/`), the projections
(`git grep -l "tasks/"`). That is why (b) has no owner — it cannot be reached by traversing a path.

The one exception is the precedent to build on rather than a counter-example. **§"Phase-tipping
tasks" (`:370-383`) is already a content step and already unqueryable** — *"explicitly evaluate
whether this closure moves the project across a phase boundary… Do this every time"* — and it
carries no `grep`, because there is none to carry. It works because its scope is one named
document. What is missing is the same shape for the artifacts nobody named in advance.

⚠️ **The reverse-dependency sweep does not already cover this, and it will be assumed to.** Read it
precisely (corrected 2026-08-11 — the first version of this row overstated it). The shipped command
is `grep -rl "blocked-by:" tasks/ | xargs grep -l "NNN-slug"`, and since every task file contains
`blocked-by:`, the first filter removes nothing — so a task that **cites this one by slug** does
surface, whether or not it is a blocker. What is never visited is the task that describes the same
surface and **never names this one**, and step 1 of the sweep tells you what to do with a hit
anyway: rewrite the path. Nothing tells you to read the file for content that just went stale.

## Evidence

**1. A ruling landed in `tasks/` and the front page kept advertising the opposite.** Task 019's
§"Scope ruling" settled that the opt-out covers the remote and never git, citing `SKILL.md:302`
(*"Git is assumed throughout this skill"*). `README.md:62-63` still tells readers *"the lanes and
the board work on a filesystem alone"* — where `SKILL.md:302` uses "on a filesystem" to mean
local-only **git**, the front page uses "on a filesystem alone" to mean **no git**. That one
fragment is the whole contradiction. This is half (a), in this repo.

⚠️ **Three corrections to this entry, the first two made 2026-08-11 and the third the same day
after an independent read — the citation drift is itself the point.**

1. The line was first cited as `README.md:57`, then as `63`. Both are wrong: the sentence **starts
   at 62** and runs onto 63. Two revisions, two bad line numbers, on the one claim this task offers
   as its in-repo proof.
2. The entry originally extended the quote with *"…Take as many of those layers as your project
   actually has."* That clause is at `README.md:65-66` and is about the **remote** layer — the
   elided sentences say *"Git adds the history… A shared remote adds backup and collaboration"* and
   it closes *"plenty of real use is local-only."* It is not evidence of a git-less claim and has
   been dropped from the quote.
3. The entry claimed *"a docs criterion on 019 is what would have caught it."* **019 already has
   one** — `tasks/prioritized/019-…:104-108` quotes the same fragment and names the
   *"A host is a bonus, not a dependency"* bullet. The drift persists because 019 is unstarted, not
   because it lacks the criterion. That sentence is struck.

So this evidence item is real but *owned*, which is the stopping rule below working exactly as
intended — the right move is to name it and leave it with 019, not to fix it here.

⚠️ **Evidence 2 and 3 are external and cannot be checked from this repository** — added 2026-08-11
after an independent read went looking for them. Both describe an unnamed adopting project; nothing
here corroborates them, and every count in them (*"seven live tasks"*, *"~30 sites across five
areas"*, *"four lines"*) is unattributable to any artifact a second reader can open. They are
load-bearing anyway: 2 is the only support for half (b), and 3 is the only support for the stopping
rule. Weigh them as testimony, not as citations. The in-repo half (a) evidence above stands on its
own; **half (b) is being taken on argument, and that is the honest description of it.**

**2. An adopting project shipped a state no one can see, and almost recorded it nowhere.** A closure
made a failure surface report the correct cause instead of a wrong one. During closure the author
established that the new state is **never visible in normal use** — a separate shipped feature
covers the whole screen whenever the condition that produces it is true. Nothing was wrong in any
document. What was missing was a note in the test script that named the original defect, telling a
future tester to verify the fix at the request log rather than by looking for it on screen. Without
it, the next verification run reads "the fix did not land," or a later reader deletes the new state
as dead code. It was caught by a reviewer asking *"is that written down anywhere?"* — not by any
step in the lifecycle. This is half (b), and it is the case the current template misses entirely.

**3. The same project needed a whole separate task to do one closure's propagation.** A decision
record accepted mid-flight contradicted acceptance criteria written before it. The reconciliation
became its own after-the-fact task, which **found ~30 sites across five areas from a scope of four
lines** — including the seven open tasks noted above, and one document whose stale text actively
instructed testers *not* to report the very gap that had been closed. It also found that one of its
own premises was false. Two lessons: the work is real, and it does not stay small.

## The vacuity problem — this is the whole design difficulty

`- [ ] Docs updated` is worse than nothing. It is tickable without reading a single document, and
it converts a real obligation into a box that is always green. This project's coverage standard
names the failure exactly — `CONTRIBUTING.md:107-109`: *"A test that executes code without
asserting its result is not a test; it is a hole with a green check over it. Coverage counts only
when the assertion would fail if the code broke."* (Corrected 2026-08-11: this was attributed to
`README.md`, which carries a related but different warning — about an *empty* checklist and about
ticking an *unmet* box, not about a criterion that is truthfully tickable without doing any work.)

The criterion has to be unsatisfiable without doing the work. The mechanism available is
**naming** — a criterion that cannot be resolved without listing what was inspected:

```markdown
- [ ] Every doc and open task describing the changed behavior is updated in the same change — or
      the ones checked are named here, with why none needed it
```

A closer who ticks that without naming anything has visibly not resolved it, and the strikethrough
convention already covers the legitimate "none applied" case with a stated reason.

## The bounding problem — "all relevant" is not evaluable

`SKILL.md` holds itself to a bar this criterion can fail: *"Write criteria a different person can
evaluate."* **"All relevant open tasks and documentation" cannot be evaluated** — it is satisfied by
finding nothing and refuted by nothing. Every other propagation step in the skill is bounded by a
query someone else can re-run. This one needs the same or it will be ticked blind.

A bound that is mechanical and cheap, in the closer's hands at the moment they have the context:

```bash
grep -rl "NNN-slug\|<the finding or decision id>" tasks/ docs/    # what already cites this work
# plus: the task's own `links:`, and the artifacts the closer had to read to do the work
```

The third clause is the one that catches half (b) — the artifact the 427-style note belonged in was
one the author had read during the work, not one that cited the task.

## The stopping rule — record and route, do not edit everything

Evidence 3 is the warning: a four-line scope opened into ~30 sites. Without a stopping rule this
criterion turns every closure into an unbounded sweep, and closers will start ticking it blind to
escape — which lands back in the vacuity problem from the other side.

The rule that keeps it bounded: **the closer names the artifact and routes it to its owning task;
they do not have to fix everything they find.** The skill already works this way one step over — the
reverse-dependency sweep *surfaces* newly-unblocked tasks for triage rather than auto-moving them.
Evidence 3 did exactly this by hand and it was the right call: four stale test-script rows were
named in a table and routed to the task that owned that script, rather than edited in passing.

## The fork

**How the default is carried.** The options are unchanged by widening the scope; both halves ride
whichever is chosen.

| Option | Trade-off |
|--------|-----------|
| **A. Convention only** — add the criterion to both templates | Cheapest, no new gate surface. Relies on the author not deleting the line, and nothing notices if they do. |
| **B. Convention + gate** — the board generator refuses a task whose checklist has no such criterion | Enforced the way 007 enforced H1 and `## Done when`, so there is precedent. But a gate can only see that a *line exists*, never that anything was actually read — so it buys shape and may actively manufacture ticked-but-untrue criteria, which is the vacuity problem wearing a green check. |
| **C. Convention + a closure-time step** in `SKILL.md`'s `wip → done` procedure | Puts the check at the moment the information exists — the closer just did the work and knows what changed. No new gate surface, and it composes with the campsite gate already there. |

Recommendation: **A + C, explicitly not B.** The generator should keep gating structure it can
actually verify. A gate that greps for a sentence teaches authors to keep the sentence, which is
the opposite of the goal; the closure-time step in the skill is where a real answer is available.
Record the reasoning for declining B in the change, so it is not re-proposed as an oversight.

**Shape of the `SKILL.md` step.** Model it on the clean-campsite gate, not on a per-task criterion:
an invariant plus a bounded procedure step. The campsite gate's own wording is the precedent —
*"you do not need to restate it per file, but you must satisfy it every time."* The template line
still earns its place for the case a task knows its blast radius up front.

**Downstream propagation.** `tasks/README.md` is copied into consumer repos rather than shipped by
the plugin, so a template change reaches an existing adopter only when they re-fetch it. The
skill's copy travels with the plugin version. These two move at different speeds, and the change
must say so rather than assume adopters are current.

**Wording constraint.** The criterion lands in `tasks/README.md` and `SKILL.md`, both in
`check-portability.py`'s `SCANNED` list — so it must be phrased without stack or methodology
vocabulary. Corrected 2026-08-11: an earlier version named "test script", "decision record" and
"acceptance criteria" as the nouns to check, and **none of them, nor any component word, is in
`FORBIDDEN`** — the pattern is `\bterm\w*\b`, so it does not reach them either. The terms actually
at risk in prose about propagating work are the methodology class: `story`, `epic`, `backlog`,
`sprint`, `retro`. Run `--list` rather than guessing.

## Done when

- [x] The body template in `tasks/README.md` carries a criterion covering **both** halves — the docs
      the change left wrong and the findings nothing yet records — worded so it cannot be resolved
      without naming what was checked
- [x] `SKILL.md` §"The shape of a task file" carries the identical criterion — the two templates
      are compared line by line and do not disagree. Verified by `diff` on the extracted ranges,
      not by eye: byte-identical including the six-space continuation indent
- [x] `SKILL.md` §`wip → done` carries the propagation step as a numbered step, alongside the
      checklist reconciliation and the campsite gate, modelled on the campsite gate's shape
      (invariant + bounded procedure, not a line restated per task file)
- [x] The step names a **mechanical bound** a second person can re-run — at minimum a `grep` over
      `tasks/` and `docs/`, the task's own `links:`, and the artifacts the closer read to do the
      work — so "all relevant" never stands alone as the whole instruction
- [x] The step names a **stopping rule**: the closer names the artifact and routes it to its owning
      task rather than being obliged to fix every site found. Cross-referenced to the
      reverse-dependency sweep's existing surface-don't-auto-move precedent
- [x] `SKILL.md` states how this differs from the reverse-dependency sweep — carries its own ⚠️
      paragraph. Corrected against the shipped command rather than the assumed one: the sweep does
      surface a task that *cites* this one; what it never visits is the task that describes the
      same surface without naming it
- [x] The decision on option B is recorded with its reasoning — in `structural_problems()`'s
      docstring, where someone proposing a fourth check will read it, and in `CHANGELOG.md`
- [x] The change states how an existing adopter picks the new template up, given
      `tasks/README.md` is copied and the skill is versioned — `CHANGELOG.md` § *Changed*, second
      entry, which states the asymmetry rather than implying the bump delivers anything
- [x] `check-release.py:38`'s comment no longer says `SHIPPED_PREFIXES` is *"what an installed copy
      actually receives"*. Corrected further after the pre-commit read: the first rewrite said
      "`tasks/README.md` and `scripts/`", but only `generate-task-board.py` is adopter-fetched —
      the other four scripts are this repo's own CI and reach nobody
- [x] `check-portability.py` passes on the changed shipped files — `ok: 4 shipped files carry no
      stack-coupled vocabulary`
- ~~`version` bumped in both manifests with a matching `CHANGELOG.md` heading, and the behavioral
      evals run before merge~~ — **struck rather than ticked, because only the first half is true.**
      The bump landed: `0.5.1` → `0.6.0` in both manifests, `## [0.6.0]` heading, `check-release.py`
      green. The evals did **not** run before merge. Auto-merge was enabled while CI was pending and
      the merge completed twelve seconds later; `gh pr merge --disable-auto` then failed because
      there was nothing left to hold. They ran immediately after against `main` at `97521e0`, which
      is byte-identical to what merged — the right code measured at the wrong time. **The result is
      not clean:** `done-when-reconciliation`'s with-skill arm fell 1.00 → 0.94, and the failing
      grader is the weight-5 `dropped-criterion-not-claimed-met`, the one that case exists for.
      Three runs cannot separate that from variance. Routed to
      `tasks/new/030-the-with-arm-regressed-on-the-grader-that-case-exists-for.md`
- [x] Every doc and open task describing the changed behavior is updated in the same change — or
      the ones checked are named here, with why none needed it. **Dogfooding this task's own
      criterion, so the list is the deliverable, not a formality:**

      *Updated:* `README.md` — the "What's in the box" row, **and** the "What a task looks like"
      example task file, which the pre-commit read caught still showing the two-line template. That
      is this change failing its own gate on its own change, found by the mechanism this task
      exists to install. `SKILL.md`'s `description:` frontmatter (drives invocation; describing the
      old procedure would be a silent mismatch) and §Transitions' one-line summary of the close.
      `.claude-plugin/marketplace.json`, which claimed the plugin ships the board view — it does
      not, and that contradicted the `check-release.py` correction in the same release.

      *Checked, no change needed:* `README.md`'s description of what the generator gates — named in
      this criterion specifically, and correct as-is precisely **because** option B was declined.
      `CONTRIBUTING.md` — no template or close-procedure description (greps for `wip → done`,
      `template`, `checklist`, `criterion` return nothing). `evals/*/case.yaml` — neither case
      grades propagation.

      *Named and routed, not fixed here:* `README.md:62-63`'s filesystem-alone fragment, owned by
      task 019 (evidence 1 above). `0.5.1` was never tagged → `tasks/new/028`, which is the
      escalation task 010 pre-wrote for exactly this. The eval regression → `tasks/new/029`.
      `README.md`'s scored table still reads 1.00 / 0.88 and no longer matches the newest
      measurement — deliberately left for 029 to settle rather than republished off a 3-run sample
