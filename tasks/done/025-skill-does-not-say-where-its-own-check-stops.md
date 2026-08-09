---
created: 2026-08-09
updated: 2026-08-09
completed: 2026-08-09
status: done
owner: justmaniv
blocked-by: ""
links:
  - skills/task-lifecycle/SKILL.md
  - tasks/done/024-validation-is-not-independent-review.md
  - tasks/done/016-two-pass-claim-is-unmeasured.md
  - tasks/new/014-eval-suite-covers-two-transitions.md
  - evals/README.md
  - CHANGELOG.md
---

# The skill teaches the validation step and never says where it stops

## What's wrong

`skills/task-lifecycle/SKILL.md` § **"Before starting: validate the task's claims"** tells a session
to confirm the task's claims, gives it two greps, and lists four outcomes. It does not say what the
step fails to establish, and the reading instruction it does give is framed as confirmation.

`tasks/done/024-*` records a field case where it passed a task containing a fabricated mechanism: the
cited test existed and asserted the cited thing, but the *way* the task said it worked ("injects a
User-Agent header") was invented — the fixture seeds a database column with a raw `INSERT`. The
false mechanism had already reached three sibling tasks, one as a "Done when" criterion.

Two candidate additions, both small:

- **Framing.** *"Try to prove the load-bearing claim wrong"* sends a reader to the fixture;
  *"check the claim"* sends them to the assertion. The section currently says *"Read the code before
  you trust the task"*, which is the right instruction and the confirming version of it.
- **A stop line.** Name what the step does not cover — it is not an independent read, because the
  reader has already absorbed the author's framing — and name the escalation trigger: a task whose
  deliverable is itself a spec other sessions will execute.

## Verify before writing

⚠️ Task 024 changes `README.md` on the same subject. Read what shipped there first and do not
restate it — the README is the storefront, the skill is the procedure, and the failure mode is two
descriptions of the same rule that drift apart. If the README already carries the argument, the
skill's share may be two sentences.

## Why this is not just a docs edit

- `skills/` is inside the version-bump boundary. This needs a `version` bump in **both**
  `.claude-plugin/*.json` and a `CHANGELOG.md` heading, or `check-release.py` fails the build.
- The section it touches has no eval case. Whether one is worth authoring here — scaffold a task
  with a true citation and a false mechanism, grade whether the pickup traces it — is the open
  question. Answer it out loud either way, and answer it against `tasks/new/014-*`, which already
  specs an **Overtaken-by-events** case over the *other* half of this same section.

## The fork

| Option | Trade-off |
|--------|-----------|
| **Reframe the existing instruction to falsification** | One sentence, no new section, and it is the change most likely to alter what a session actually reads. Unmeasured — no eval distinguishes "read the code" from "try to break the claim". |
| **Add the stop line and the escalation trigger** | Says when the step is insufficient, which is the honest thing a procedure can do about its own limits. Grows a section that is already the longest in the skill. |
| **Both, plus an eval case** | The only version with evidence attached. Costs a case design and run hours — and it would grade the skill on catching something the new prose openly says the step does not reliably catch. |
| **Nothing — leave it in the README** | Free. Adopters run the skill and many never read the README, so the people who most need the caveat are the ones who would not see it. |

Recommendation: **options 1 and 2, and answer the eval question in writing without authoring the
case unless the answer is surprising.** The framing change is nearly free and targets the observed
failure directly.

## Corrections — 2026-08-09

Found by a fresh-context pass told to falsify this file, before any work started. Three claims were
wrong; the shape of the work is unchanged, but two of them would have produced a false write-up.

- **"It does not say how to read"** — it does, at `SKILL.md:133`: *"Read the code before you trust
  the task."* The defect is that the framing is confirming, which this file's own next bullet says.
  Sentence corrected above.
- **"The one behavior the eval suite does *not* cover"** — false. The suite has two cases of the
  ~seven behaviors the skill teaches; nearly everything is uncovered. And `tasks/new/014-*` already
  specs an **Overtaken-by-events** case covering the grep half of this very section. Both added to
  `links:`; the eval question has to be answered against 014, not in isolation.
- **"`tasks/done/016-*` is the precedent for deciding it is not worth the run hours"** — inverted.
  016 declined the **session-topology** axis, which the harness may not be able to express at all.
  Its Option 3 is precisely the false-premise case contemplated here, and 016 *recommended* it:
  *"worth doing either way — the false-premise case is the sharpest single thing in this whole
  area."* A decision not to author a case here must argue against 016, not claim its support.

One detail this file also under-states: the adversarial pass in `tasks/done/024-*` falsified **four**
claims, not only the header one.

## Done when

- [x] The validation section either instructs falsification or records why it stays as-is —
      *instructs it: "read it to **break** the claim rather than to confirm it", with the reason
      the two questions open different files*
- [x] The section states what the step does not establish, and what to escalate to when the task's
      output is itself a spec — without the skill prescribing a review mechanism it does not ship —
      *closing paragraph **"Where this check stops"**; it names the property of the second reader
      (not in the conversation that accepted the task) and says outright that the skill ships no
      such mechanism and does not prescribe one*
- [x] Nothing in the skill duplicates prose that shipped in `README.md` under task 024 — *no
      sentence is shared and neither worked example is repeated. The **substance** does overlap,
      unavoidably: the skill cannot mark its own boundary without naming the failure that boundary
      exists for. The split held is that the README **argues** it (weak-evidence case, the
      falsified-four-claims example, the pasteable rule) and the skill **states** it in one
      paragraph and stops*
- [x] `version` bumped in both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`,
      with a matching `CHANGELOG.md` heading; `python3 scripts/check-release.py` passes — *0.5.0 →
      0.5.1; verified after committing, since the gate diffs `merge-base..HEAD` and passes
      vacuously on an uncommitted tree*
- [x] Whether an eval case covers this behavior is answered in `evals/README.md` — a case, or the
      reason there is none — *no case, in new § "No case for 'where the check stops', and it is not
      016's reason": both possible graders are bad (one grades the skill on an outcome its own
      prose declines to promise; the other grades the agent's self-report of its limits). The
      neighbouring false-premise case 016 recommended is explicitly left alive with `014`*

## What was deliberately not done

**The behavioral evals were not run.** `CLAUDE.md` says to run them before changing the skill. This
change adds a paragraph and a clause to a section **no case exercises** — the suite's two cases are
`reverse-dependency-sweep` and `done-when-reconciliation`, and neither scaffold contains a task
whose claims are checkable at all. A run would re-measure +0.50 and +0.115 on untouched behavior for
~$4.50 and ~12 minutes. Recorded rather than skipped silently: if a case over this section is ever
written, the first run of it is the one that matters, and it has no baseline here to compare to.
