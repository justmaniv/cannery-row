---
created: 2026-08-09
updated: 2026-08-09
completed: ""
status: new
owner: justmaniv
blocked-by: ""
links:
  - skills/task-lifecycle/SKILL.md
  - tasks/done/024-validation-is-not-independent-review.md
  - evals/README.md
  - CHANGELOG.md
---

# The skill teaches the validation step and never says where it stops

## What's wrong

`skills/task-lifecycle/SKILL.md` § **"Before starting: validate the task's claims"** tells a session
to confirm the task's claims, gives it two greps, and lists four outcomes. It does not say what the
step fails to establish, and it does not say how to read.

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
- The section it touches is the one behavior the eval suite does *not* cover. Whether a case is
  worth authoring here — scaffold a task with a true citation and a false mechanism, grade whether
  the pickup traces it — is the open question, and `tasks/done/016-*` is the precedent for deciding
  it is not worth the run hours. Answer it out loud either way.

## The fork

| Option | Trade-off |
|--------|-----------|
| **Reframe the existing instruction to falsification** | One sentence, no new section, and it is the change most likely to alter what a session actually reads. Unmeasured — no eval distinguishes "read the code" from "try to break the claim". |
| **Add the stop line and the escalation trigger** | Says when the step is insufficient, which is the honest thing a procedure can do about its own limits. Grows a section that is already the longest in the skill. |
| **Both, plus an eval case** | The only version with evidence attached. Costs a case design and run hours against a delta that may be noise. |
| **Nothing — leave it in the README** | Free. Adopters run the skill and many never read the README, so the people who most need the caveat are the ones who would not see it. |

Recommendation: **options 1 and 2, and answer the eval question in writing without authoring the
case unless the answer is surprising.** The framing change is nearly free and targets the observed
failure directly; the eval is the same "measuring the model" risk 016 already priced.

## Done when

- [ ] The validation section either instructs falsification or records why it stays as-is
- [ ] The section states what the step does not establish, and what to escalate to when the task's
      output is itself a spec — without the skill prescribing a review mechanism it does not ship
- [ ] Nothing in the skill duplicates prose that shipped in `README.md` under task 024
- [ ] `version` bumped in both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`,
      with a matching `CHANGELOG.md` heading; `python3 scripts/check-release.py` passes
- [ ] Whether an eval case covers this behavior is answered in `evals/README.md` — a case, or the
      reason there is none
