---
created: 2026-08-06
updated: 2026-08-07
completed: 2026-08-07
status: done
owner: justmaniv
blocked-by: ""
links:
  - CONTRIBUTING.md
  - skills/task-lifecycle/SKILL.md
---

# Nothing tests whether the skill is followed, only that it is well-formed

## The gap

CI proves the skill is portable, the manifests load, the board generator is correct, and the
workflows are safe. Every one of those is a check on *form*. None of them runs the skill and asks
whether Claude did the right thing with it.

That is the only property anyone installing this actually cares about.

`claude plugin eval` exists for this: scored cases (`evals/**/case.yaml`), graders, and an
`--ablation with-without` arm that runs the same case with the plugin disabled, so the score
difference attributes the outcome to the skill rather than to the model being competent anyway.
`--threshold` makes it a build gate.

## Cases worth writing first

Pick the transitions where getting it wrong is silent — a wrong answer that still looks like work:

- **Reverse-dependency sweep on close.** A task moves to `done/`; another task's `blocked-by:`
  points at its old path. Does the sweep happen? This is the highest-value case: skipping it leaves
  work sitting in `blocked/` behind something finished, and nothing surfaces it.
- **"Done when" reconciliation.** An unmet checklist item must become `- [x]` or a struck-through
  line with a reason — never a pre-filled ✅ on something that did not happen.
- **Overtaken-by-events check.** A stale task whose work already shipped under another number
  should be closed with evidence, not restarted.
- **Collision-safe numbering.** With a second worktree holding an uncommitted `NNN-*.md`, does the
  next number account for it, or does it collide?
- **Invariant refusal.** Given a state that cannot satisfy an invariant, the skill says stop and
  surface — it does not move the file anyway.

## Cost note

Eval runs cost model calls, and `--runs` defaults to 3 per case. Decide whether this gates every PR
or runs on a schedule before wiring it into CI; a suite that is too expensive to run is a suite
that gets disabled.

## Validated on pickup — 2026-08-07

The gap is real and unchanged: `evals/` does not exist, `ci.yml` runs five form checks and no
behavioral one. But one premise needs correcting before the "gates PRs or runs on a schedule"
decision can be made, and it was not knowable when this was written:

⚠️ **`claude plugin eval` is early-access gated.** On CLI 2.1.220 it prints
`` `plugin eval` is currently in early access `` and exits 0 — a *silent* no-op, which is the
worst possible failure shape for a CI step. The gate is
`tengu_walnut_spire || env.CLAUDE_CODE_WALNUT_SPIRE` (read out of the binary); exporting
`CLAUDE_CODE_WALNUT_SPIRE=1` enables it locally and is how this suite was authored.

That is decisive for the third checklist item, not a footnote. A GitHub-hosted CI job would need
that flag **and** working Claude credentials — and this repo is specified to hold zero secrets
(`tasks/done/…`/ADR 0038: "no secret should exist in that repo at all", because a public repo with
no secrets and no self-hosted runner has no attack surface worth exploiting). Adding an API key to
gate evals would trade the strongest security property this repo has for a check that anyone can
run locally in twelve minutes. See the decision recorded below.

Two mechanics worth knowing that shape the design:

- **Grader cost is not uniform.** `regex`, `tool_used`, `tool_order`, `file_exists` are free —
  they read the trace and the sandbox filesystem. Only `llm` and `baseline` call a judge model.
- **`regex` can target a file:** `target: {source: file, path: …}` reads a file out of the
  post-run sandbox. So *state* assertions — the frontmatter is synced, the dependent's path was
  rewritten, the checklist box is resolved — are free and deterministic. That is what makes a
  behavioral suite cheap enough to matter.

## What the suite found — 2026-08-07

**It found a bug in the skill on the first case, which is the whole argument for having it.**
Invariant 6 said a closed blocker's `blocked-by:` reference could be *cleared*; the reverse-sweep
procedure said *rewrite it to the new path*. Both are shipped text, both read fine alone, and
nobody was going to catch the contradiction by proofreading. Claude followed the invariant, deleted
the reference, and left a task sitting in `blocked/` with an empty `blocked-by:` — blocked by
nothing, which no future sweep would ever surface again. Exactly the rot the sweep exists to
prevent, licensed by the skill's own invariant. Fixed in `0.4.3`; the case went 0.65 → 1.00.

### Results — 3 runs per arm, CLI 2.1.220, skill 0.4.3

| Case | Without | With | Δ | What the baseline actually gets wrong |
|------|---------|------|---|----------------------------------------|
| `reverse-dependency-sweep` | 0.50 | **1.00** | **+0.50** | never rewrites the dependents' paths (3/3); moves the newly-unblocked task instead of surfacing it (3/3); never mentions it (1/3) |
| `done-when-reconciliation` | 0.88 | **1.00** | **+0.115** | leaves a `- [ ]` unresolved and closes anyway (3/3); never commits the move (3/3) |

Whole suite: **$4.52, 12m09s, 12 runs.** The plugin arm scored 1.00 on every run of both cases, so
the default `--threshold 1.0` is a usable gate rather than a flake generator.

### Two wrong predictions, both corrected by measurement

1. **The strikethrough is not what the skill teaches.** The first draft of the reconciliation case
   scored 1.00/0.95 — striking a dropped criterion rather than ticking it is ordinary good
   judgment. The case was rewritten.
2. **Neither is the stale board.** It was added to that case *specifically* to discriminate, on the
   theory that a projection nobody mentions has to be known. The baseline finds `scripts/board.py`,
   works out what it is for, and regenerates it, 3/3. What the skill actually supplies there is
   duller than either guess: finish the checklist, commit the move.

Both are recorded in the case files rather than quietly dropped. A wrong prediction that the
measurement corrects is the measurement working.

### Three graders that passed while proving nothing

Caught only by keeping a sandbox with `--keep-temp` and looking at it. Written up in
`evals/README.md` so the next author does not re-derive them:

- **`file_exists` grades the created-files diff, not the filesystem.** A file that existed before
  the run and was merely edited reads as *missing*; `exists: false` on such a file passes for the
  wrong reason. It is correct for exactly one thing — the destination of a move.
- **`not_contains` passes vacuously on a missing file.** It must be paired with a positive match on
  the same file, or deleting the file scores as tidying it.
- **A `not_contains` on `blocked-by:\s*(""|''|\n)` backtracks** and false-fails a perfectly correct
  YAML block-sequence rewrite. Verified directly, never observed in a run; deleted rather than
  documented, because a latent false-fail in a suite that costs $5 a run is not worth keeping.

## Decision — behavior is gated locally, form is gated in CI

Neither option the task offered. "Gate every PR" and "run on a schedule" both assume the suite
*can* run in CI, and it cannot without trading away this repo's best property.

| Option | Verdict |
|--------|---------|
| Gate every PR | ❌ Needs `CLAUDE_CODE_WALNUT_SPIRE` **and** Claude credentials in a public repo whose entire security argument is that it holds no secrets and no self-hosted runner. Also hands any fork's PR a way to spend money. |
| Scheduled run | ❌ Same secret, same exposure, and it decouples the signal from the change that caused it — a red Tuesday build nobody owns. |
| **Local before merging a skill change, + a free structural gate in CI** | ✅ **Chosen.** |

`scripts/check-evals.py` (new, stdlib-only, 13 tests) runs in CI for free and catches the five
breakages that would otherwise be discovered *after* paying for a run — a missing `case.yaml`,
missing required keys, a `name` disagreeing with its directory, a renamed `scaffold_script`, and
the sharp one: a case whose graders are all `arm: with-only`, so the baseline arm scores nothing
and the delta the suite exists to report is computed against an empty set.

The cost that drove it: **$4.52 and twelve minutes per full run**, times every PR, against a check
one contributor runs once before merging a skill change. CI gates the form; the human gates the
behavior. `CONTRIBUTING.md` says so where a contributor will actually read it.

## Done when

- [x] `evals/` suite exists with at least the reverse-sweep and "Done when" cases — both, plus
      `evals/README.md` carrying the design rules and the grader-semantics traps
- [x] `--ablation with-without` shows a real score delta — **+0.50** and **+0.115**, consistent
      across 3 runs. The task's own warning fired twice and both cases were rewritten rather than
      shipped as model tests
- [x] A decision recorded on whether this gates PRs or runs on a schedule, with the cost that drove
      it — recorded above; the answer is *neither*, and the reason is that the premise was wrong
- [x] `CONTRIBUTING.md` updated to point at it instead of naming this task — plus `README.md`,
      which now leads with the with/without table, because "does this prompt actually do anything"
      is the first question a stranger asks

## Follow-ups worth a task, deliberately not folded in

- ⚠️ **Three cases the spec named are unwritten:** overtaken-by-events, collision-safe numbering,
  and invariant refusal. Numbering is the interesting one — it needs a scaffold with a second
  worktree holding an uncommitted `NNN-*.md`, which no case here exercises.
- ⚠️ **The suite pins no model.** `execution.model` is unset, so a case inherits whatever the
  runner defaults to and a delta is only comparable against runs on the same model. Pinning it
  makes the numbers durable; leaving it unpinned tests what users actually get. Not obvious which
  is right, which is why it is a task and not a silent choice.
