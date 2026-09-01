---
created: 2026-08-09
updated: 2026-08-12
completed:
status: blocked
owner: justmaniv
blocked-by: "tasks/new/00029-propagation-sweep-hardcodes-two-directories.md"
links:
  - skills/task-lifecycle/SKILL.md
  - tasks/new/00029-propagation-sweep-hardcodes-two-directories.md
  - tasks/new/00031-a-project-cannot-say-where-else-to-look-for-work.md
---

# The prior-coverage sweep certifies an absence it never established — fix the rationale, not just the command

⚠️ **Corrected twice on 2026-08-12, before any work started.** Drafted 2026-08-09, this task sat in
an unmerged PR for three days. In that window `029` and `031` were written and merged and took over
**both** of its mechanical proposals. Two fresh-context reads then falsified much of what remained:
the first killed the two proposals, the second killed the sentence this task most wanted to ship.
Two of the six numbered proposals below are struck; four survive. Read §"What the second read
overturned" before trusting any framing here that predates it.

§*"Before creating: check for prior coverage"* (`SKILL.md:244-273`) calls itself **"cheap and
mandatory"** and closes with *"a false 'nothing found' is the expensive outcome."* Both are right,
and the section still cannot deliver either one. `029` is repairing the *command*. What is left —
and what this task now owns — is the part that tells a reader **what a sweep can and cannot
certify**, and how to choose the words it runs on. That is where the original miss actually
happened, and it is not fixed by any command.

## The miss [Verified 2026-08-09, re-verified and partly corrected 2026-08-12]

In the consuming project `everything-has-a-price`, task 468 was drafted to design a client-side
mechanism for surfacing failed writes. The sweep ran as written and returned nothing, so the task
was drafted, reviewed and merged. It was deleted the same day, in commit `569a19f9` — *"task(468):
delete — Epic 4 already owns it; link the story instead"*, whose body carries a four-row table
mapping 468's open questions onto stories 4.2–4.5.

The owning artifact was `_bmad-output/planning-artifacts/epics-and-stories.md:1331`, *"Epic 4:
Offline queue + PWA shell + sync flush"*. Working code existed too:
`frontend/src/capture/mod.rs:115` defines an `UploadFailed` status and `:308` a
`pub fn retry(&mut self, id: Uuid)`, behind a user-facing *"Capture failed — retry"* chip specified
at `epics-and-stories.md:874`.

⚠️ **Two things the original draft got wrong here, both corrected 2026-08-12.**

**It was not wholly deferred.** `epics-and-stories.md:1333` carries *"PARTIALLY PULLED INTO SPRINT 8
— Stories 4.2 + 4.4 (task 360, 2026-08-05)"*, and `:1345` *"Stories 4.1, 4.3 and 4.5 remain
deferred."* Two of the four stories in the deletion commit's own mapping table had been pulled into
active work four days before the miss. "An entire deferred epic" overstated it.

**`tasks/` was not silent.** This is the important one, because the original draft's headline
generalization was *"nothing is in `tasks/`"* and proposed shipping it into `SKILL.md`. Run against
the tree as it stood at the moment of the miss:

```
$ git grep -ril "offline queue" 569a19f9^ -- tasks/     # 9 files, one of them 468 itself
$ git grep -ril "epic 4"        569a19f9^ -- tasks/     # 20 files
```

The ownership *was* in `tasks/`, in eight files besides 468's own. The sweep's directory scope did
not cause this miss.

## What the second read overturned — the failure mode, restated

The original ⚠️ claim (*"feature-shaped work is usually owned outside `tasks/`… nothing is in
`tasks/`"*) is **false on its own example** and must not ship. What the same evidence does support
is narrower, and it points at §5 rather than §4:

1. **The drafter's words were not the project's words.** 468 was titled *"surface unrecoverable
   client failures on the next connection."* The project called the same capability *"offline
   queue"*, *"sync flush"*, *"Epic 4"*. No directory scope rescues a sweep run on vocabulary the
   owning artifact never uses. The deletion commit's own diagnosis says the sweep *"never swept the
   backlog"*; the stronger reading, available now and not then, is that it would also have missed
   the eight in-tree hits, because it was searching for the wrong words.
2. **Where `tasks/` did mention it, the mentions read as history.** Seven of the eight hits were in
   `tasks/done/` — closed tasks and grooming notes. One was in `new/`, on an unrelated topic. A
   sweep whose hits are all in `done/` invites exactly the wrong conclusion: *"handled already"*
   rather than *"owned, and still open elsewhere."* The section says nothing about how to read a
   hit's lane.

Both are properties of **how the sweep is run and read**, not of which directories it covers — which
is why they survive `029` landing, and why they are what this task is now for.

## Why not key the sweep on an index file

The obvious fix — look for `index.md` (or `docs/README.md`, `MAP.md`) and sweep what it names — was
evaluated against the same project and **rejected on its own evidence**. All three points
re-verified 2026-08-12:

- That project **does** carry `docs/index.md`, whose frontmatter `purpose:` (`:5`) reads *"Canonical
  index of project documentation; entry point for newcomers and fresh-context agents."*
- Its planning-artifacts table (`:76-84`) lists nine rows — the requirements document, architecture,
  UX specification, personas, product brief, its distillate, a valuation matrix and two review
  passes — **and not the artifact that owned the work.** `epics-and-stories.md` appears nowhere in
  the file. An index-keyed sweep would have missed the identical thing.
- Its own frontmatter (`:9-10`) admits why: *"A follow-up task wires the generator and CI-gates
  freshness."* That never ran. It is hand-maintained, and still stamped `updated: 2026-05-16`.

An index is a **cache of repo structure**. Keying a correctness check on a cache is safe only if the
cache is freshness-gated, and the one real-world example is not. It also fails in the expensive
direction: a stale index makes the sweep look thorough while silently narrowing it, whereas a
*missing* index fails obviously. ❌ **Do not adopt an index-file lookup**; the skill would inherit
the freshness problem of a file it does not own.

## What this task no longer proposes

Both struck 2026-08-12. Recorded rather than deleted, so neither is re-proposed cold.

### ~~1. Default the command to a repo-wide `git grep`~~ → `029` owns it, and this task's version was wrong

`029` owns the command repair and its verified inventory is strictly better. Two specific errors in
what was proposed here, both reproduced in a scratch repository on 2026-08-12:

- **It was not repo-wide.** `git grep` searches from the **current directory downward**. Run from
  inside `tasks/`, the proposed command returned only paths under `tasks/` and missed a match in a
  sibling directory entirely. It needs a `:/` pathspec, which the proposal did not have.
- **It was blind to uncommitted files.** A unique token written to an untracked file: bare
  `git grep -ril` exited **1 with no output**, while plain `grep -ril` found it. `SKILL.md:374`
  blesses bulk creation of many task files before a commit — precisely when this matters. `029`
  prescribes `--untracked` for exactly this reason and notes it was itself invisible to the bare
  form while being written. ⚠️ The original draft called this *"a regression against today's
  command"* and demonstrated it on a repo-root file; today's command
  (`SKILL.md:257`) only searches `tasks/ docs/decisions/ docs/working-agreement/`, so it would not
  have found a root-level file either. The regression is real but only *within* those directories —
  state it that way or not at all.

The stated mechanism was also wrong: `git grep` does not *"respect `.gitignore`"* — it searches
**tracked files**. That is a *different* set, not a subset: a file that is tracked *and* gitignored
is still found by `git grep` and skipped by a gitignore-respecting search. The original draft called
it "strictly narrower"; it is not.

⚠️ **`029` also found this section's second command is not merely narrow — it is dead.** This task's
filename and original framing say the sweep is *scoped*; it is worse than that. `SKILL.md:258`'s
`grep -ril "TOPIC" -- '*README*' 'ci/**'` pastes `git grep` pathspecs into plain `grep`, which
receives them as literal filenames, exits 2, and is silenced by its own `2>/dev/null`. Half the
mandatory sweep has been returning nothing indistinguishably from finding nothing.

### ~~2. Let a repo declare extra high-signal sources in `tasks/README.md`~~ → `031` owns the capability

`031` owns per-project declaration of where else to look for work, and settled its scope on
2026-08-11 (`031:78`). Two reasons this task's version does not survive contact with it:

- **The placement fails a constraint `031` states.** `031:67` requires the declaration be
  *"Findable without knowing the task home"* — and `tasks/README.md` is inside the task home.
  `019:89-103` is the fork table that recommends that placement; `022:88-93` is the objection
  (*"finding `tasks/README.md` requires already knowing where the task tree is"*). ⚠️ `031` does not
  *rule the placement out* — the original draft said it did. `031:130-132` leaves it open, requiring
  only that the two be **reconciled** against whatever surface `031` lands.
- **"No new file convention is introduced" was false.** `SKILL.md:11` names `tasks/README.md`
  exactly once — it is the only occurrence in the file — as documenting *"layout and frontmatter for
  humans"*, explicitly contrasted with the operations the skill governs. A block the procedure
  **reads** is a new convention by any reading.

⚠️ **Do not restate the reason the original draft gave for striking this.** It argued the block was
unsupported because the motivating miss was in-repo and a whole-repository search already reaches
it. That is the same *"a whole-repository search reaches everything in-repo for free"* framing
`029:104-108` explicitly struck — *"That framing is superseded and should not be revived. Ruled
2026-08-11 by the owner."* The correct reason to strike §2 here is simply that **`031` owns the
capability**; the trade itself is `031`'s to make, not this task's.

## What this task still proposes

All four are rationale and procedure. `029` repairs the command; it does not touch any of these.
⚠️ One overlap to respect rather than duplicate: `029:145-148` already requires the surviving
`2>/dev/null` be justified, on the grounds that *"a silenced error that returns no hits reads
identically to a clean search that found nothing"* — the same instinct as §3, applied to the
command. Cite it; do not re-litigate it.

### 3. Require saying when the sweep was narrow

Add to the *"act on the hits"* list:

> - **Swept narrowly →** if you scoped the search for speed, say so in the task and the commit —
>   *"coverage checked in X and Y only."* A narrow sweep is a fine trade; reporting it as
>   "nothing found" is not. Absence claims require the whole-repository sweep.

This is the criterion that needs `029` to have landed — see §Sequencing.

### 4. Name the failure mode in the section's rationale — the corrected one

Ship §"What the second read overturned", not the original claim. In portable wording: the owning
artifact names a capability in **the project's** vocabulary, not the drafter's; and hits that land
only in `done/` mean *owned and possibly still open elsewhere*, not *handled*. ❌ Do not ship
*"feature-shaped work is usually owned outside `tasks/`"* — it is false on the only example this
task has.

### 5. Make "widen the keywords" a requirement, not an aside

The closing line's *"when in doubt, widen the keywords"* should become a requirement to sweep the
**project's** words for the capability, not only the drafter's phrasing for the task. This is now
the load-bearing item: per §"What the second read overturned", keyword choice — not directory scope
— is what actually produced the miss, and it is the one input that governs both the noise cost of a
whole-repository search and its false-negative risk.

### 6. Record the index-file rejection

Land §*"Why not key the sweep on an index file"* above, with its evidence, so the idea is not
re-proposed cold by a later session that has not seen the counter-example.

## Portability — the note this task got backwards [Corrected 2026-08-12]

The original draft warned that the concrete `_bmad-output/…` example would trip
`check-portability.py` and must be kept out of shipped files. **Tested directly against
`scripts/check-portability.py`; that is not what happens.** Every row below was re-run by an
independent read and confirmed:

| Text | Fires |
|---|---|
| `` - `_bmad-output/planning-artifacts/epics-and-stories.md` — epics/stories; … `` | `epic` only |
| `bmad-output/planning-artifacts.md` (no leading underscore) | `bmad` |
| "the stories mapped one-to-one" | *nothing* |
| "the planning **backlog** your project keeps outside `tasks/`" | `backlog` |
| "the planning **artifacts** your project keeps outside `tasks/`" | *nothing* |

The gate builds `\bbmad\w*\b`; in `_bmad-output` the leading `_` **is** a word character, so there
is no boundary and `bmad` never matches. `stories` escapes too, because the pattern is
`\bstory\w*\b` and "stories" is not "story" plus a suffix.

⚠️ So the trip hazard is the reverse of what was written: **the vendor path sails through and the
generic noun is what fails.** The rule to carry into the implementation is *"methodology nouns fail;
paths and irregular plurals are invisible to the gate"* — the same blind spot `029:46` records for
directory names (*"the gate matches terms, not paths"*).

☠️ **The original draft's own suggested replacement fails the gate.** It offered *"the planning
backlog your project keeps outside `tasks/`"* as portable wording; `backlog` is in `FORBIDDEN`
(`check-portability.py:81`). Use *"planning artifacts"* — verified to pass. Do not paste the earlier
suggestion in.

## Sequencing — why this is blocked on `029`

`029` replaces the prior-coverage command with one that can search the whole repository. **§3 is
incoherent until it does:** a *"swept narrowly"* branch needs a wide default to be narrow *against*,
and today's command is only narrow. Writing §3 first would either describe a contrast that does not
exist or duplicate `029`'s command repair inside this task.

§§4–6 are pure rationale and depend on nothing. If `029` stalls, they can be lifted into their own
change rather than held hostage — say so explicitly if that happens, rather than quietly closing
this task on three of its four surviving items.

Not blocked on `031`: nothing surviving here touches per-project declaration.

## How this task became wrong, which is its own evidence

`029` and `031` were drafted 2026-08-11 and neither references `027`. They are not at fault. This
task existed only on an unmerged branch, and **a prior-coverage sweep over `tasks/` structurally
cannot see a task that has not landed** — the same defect class this task is about, with the branch
playing the role the backlog played in the original miss. `029`'s `--untracked` finding is the
in-repo half; the cross-branch half is unowned and belongs with whoever picks up `029`.

Two stale citations were also found and fixed here on 2026-08-12: `019:66-76` → `019:89-103` and
`022:83-87` → `022:88-93`. Both drifted ~23 lines in commit `54e1325`, which is the commit that
created `031` — so `031:56-57` was already stale the day it was written, and this task copied it
forward without reopening the file. `031` has been corrected in the same change.

## Honest limit of this change

The consuming project's own always-loaded `CLAUDE.md` named the backlog explicitly and was in
context at the time. The information was available and simply not connected. **A procedure change
cannot guarantee someone looks** — what it can do is stop the sweep from *certifying* an absence it
never established. Judge this task on that narrower claim; it is the one it can actually deliver.

## Done when

- [ ] The *"act on the hits"* list carries a **swept narrowly** branch requiring the narrowing be
      stated in the task and the commit — written against `029`'s landed command, not today's
- [ ] The rationale names the corrected failure mode — the owning artifact uses the project's
      vocabulary rather than the drafter's, and hits confined to `done/` do not mean "handled". ❌ It
      must **not** claim feature-shaped work is usually owned outside `tasks/`; that was falsified
      on 2026-08-12 against the only example this task has
- [ ] The closing "widen the keywords" line names a second search on the project's own vocabulary
      for the capability as a required step, not a suggestion — checkable by reading whether a
      reader who ran one search has been told to run another
- [ ] ❌ No index-file lookup is added, and the rejection plus its evidence is recorded in the
      section so the idea is not re-proposed cold
- [ ] `check-portability.py` passes on the changed shipped files. ⚠️ Necessary, not sufficient — per
      §Portability the gate cannot see methodology vocabulary embedded in a path, so any example
      path in the new wording is also read by eye
- [ ] `version` bumped in both manifests with a matching `CHANGELOG.md` heading, and the behavioral
      evals run before merge
- [ ] Every document and open task this change makes wrong is updated, and anything the work turned
      up that nothing yet records is written down — or what was checked is named here, with why none
      of it needed changing. At minimum: `029`, which should inherit the one-line note that a sweep
      cannot see work parked on an unmerged branch
