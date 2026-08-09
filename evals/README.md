# Behavioral evals

Every other gate in this repo checks that the skill is *well-formed*: portable, manifest-valid,
board-generator-correct, workflow-safe. None of them checks that it is *followed*. That is the only
property anyone installing this actually cares about, and it is what these cases measure.

Each case scaffolds a throwaway repository mid-flight, hands the agent a realistic instruction, and
grades the **state it leaves behind** — where the files ended up, what the frontmatter says, whether
the dependency graph still resolves.

## Running them

```bash
CLAUDE_CODE_WALNUT_SPIRE=1 claude plugin eval . \
  --ablation with-without --scaffold \
  --allow-tools Bash Read Edit Write Glob Grep Skill
```

Four things about that command are load-bearing:

- **`CLAUDE_CODE_WALNUT_SPIRE=1`** — `claude plugin eval` is early access. Without the flag it
  prints `` `plugin eval` is currently in early access `` and **exits 0**. A silent success is the
  worst failure shape there is; if you see no case output, this is why.
- **`.`, not `cannery-row`** — cases are discovered under the *target*. Targeting the installed
  plugin by name looks for `evals/` inside the plugin cache, where these files do not exist. The
  path target runs your working tree, which is what you want when you are changing the skill.
- **`--ablation with-without`** is implicit for a name target and defaults to `none` for a path
  target, so pass it explicitly. Without it you learn the score and not the only number that
  matters.
- **`--scaffold`** runs each case's `scaffold.sh` as you. Read them before you run them; they are
  short, and they only `mkdir`/`git init` inside the sandbox.

Useful while iterating: `--case <glob>` for one case, `--runs 1` to halve the bill, `--keep-temp` to
preserve the sandbox so you can look at what the agent actually did.

## What the delta means, and why cases get rewritten

`--ablation with-without` runs each case twice — once with the plugin, once without — and reports
the difference. **The delta is the whole result.** A case where both arms score the same is not
measuring the skill; it is measuring whether the model is competent, which it is, and which is not
in question.

This is not theoretical. The first draft of `done-when-reconciliation` scored **1.00 with, 0.95
without** — the model reaches "strike the dropped criterion, don't tick it" on its own, because
that is ordinary good judgment rather than a convention.

The rule that fell out of that, and it is the design rule for every case here:

> Grade the things a capable model has no way to guess. Conventions, cross-file consequences, and
> project-specific procedure — not judgment calls it would make correctly anyway.

The sweep case is the clean example: **0.50 → 1.00**. Nobody infers "go rewrite the `blocked-by:`
paths in other files" from "wrap up task 012." The baseline missed the sweep in all three runs.

**Predicting which half will discriminate is harder than it looks, and the suite is what corrects
you.** `done-when-reconciliation` was rewritten around a generated board that goes stale on the
move, on the theory that a projection nobody mentions has to be *known*. It does not discriminate
either — the baseline finds `scripts/board.py`, works out what it is for, and runs it, 3 runs out
of 3. What the skill actually supplies in that case turned out to be plain completeness: the
baseline leaves a `- [ ]` box unresolved and never commits the move. The board graders stayed
anyway, because they assert something the skill requires and a regression would surface there —
but the comment above them now records the wrong prediction instead of quietly claiming credit.

### The scaffolds deliberately omit `tasks/README.md`

It ships with the plugin and it describes the sweep and the reconciliation rule in prose. A scaffold
containing it would hand the baseline arm the procedure, and the delta would measure
skill-over-README instead of skill-over-nothing. The skill is the independent variable; it stays the
only source of the procedure.

### What this suite does not measure

`README.md` leads with the claim that two passes beat one — that a spec written in one session and
executed cold in another produces better work than doing both in one window. **No case here tests
that, and none is planned.**

The axis this suite varies is *whether the skill is present* inside a single session. Varying session
**topology** instead would need two agents chained through a filesystem handoff with no shared
context, which the harness may not be able to express at all. Even granting that it can, the result
would be hard to read: a small delta is indistinguishable from "two passes don't pay off on work this
small," and separating a topology effect from ordinary run variance would take considerably more than
3 runs an arm. That is a real bill for a claim already backed by ~380 tasks of direct use.

So it stays an argument with one worked example behind it, and the README says so in those words.
Recorded here so the omission reads as a decision rather than an oversight someone later tries to
fix. Decided 2026-08-08; see `tasks/done/016-two-pass-claim-is-unmeasured.md` for the four options
weighed.

## Grader semantics — read this before adding a case

The grader types are not interchangeable, and two of them do not do what their names suggest. Both
traps produced graders that passed while proving nothing, and both were caught only by keeping a
sandbox and looking at it.

| Grader | What it actually reads | Cost |
|--------|------------------------|------|
| `file_exists` | the **created-files diff** — "was this path created during this run" | free |
| `regex` + `target: {source: file, path}` | the real file on disk in the post-run sandbox | free |
| `regex` + `target: last_message` / `trace` / `files` | the transcript, or the created-files list | free |
| `tool_used` / `tool_order` | the tool calls in the trace | free |
| `llm` | judge model over the chosen focus | **paid** |
| `baseline` | judge model against a reference file | **paid** |

**Trap 1 — `file_exists` is not a filesystem check.** It grades the created-files diff. A file that
existed before the run and was merely edited reads as *missing*; `exists: false` on such a file
passes for the wrong reason. It is correct for exactly one thing: the destination of a move. Use a
file-target `regex` for everything else — the read throws when the path is gone, so a single grader
asserts both "still here" and "says the right thing".

**Trap 2 — `not_contains` passes vacuously on a missing file.** `dependent-has-no-stale-path` will
happily pass when the agent deleted the file outright. Always pair a `not_contains` with a
positive `contains` on the same file, so a missing file fails something.

**Cost follows directly:** only `llm` and `baseline` call a model. Every state assertion here — the
frontmatter is synced, the path was rewritten, the box was struck, the board was regenerated — is a
free deterministic read. That is what keeps a behavioral suite cheap enough to be worth running, and
it is why the paid graders are reserved for the two things that genuinely need judgment (did the
strike carry a *reason*; was the unblocked task *surfaced*).

## Cases

3 runs per arm, CLI 2.1.220, skill 0.4.3. Whole suite: **$4.52, 12m09s**.

| Case | What the baseline gets wrong | Without | With | Δ |
|------|------------------------------|---------|------|---|
| `reverse-dependency-sweep` | never rewrites the dependents' `blocked-by:` paths (3/3); moves the newly-unblocked task instead of surfacing it (3/3); fails to mention it at all (1/3) | 0.50 | 1.00 | **+0.50** |
| `done-when-reconciliation` | leaves a `- [ ]` criterion unresolved and closes anyway (3/3); never commits the move (3/3) | 0.88 | 1.00 | **+0.115** |

The plugin arm scored **1.00 on every run of both cases** — no variance — so the default
`--threshold 1.0` is a usable gate rather than a source of flakes. The baseline arm was nearly as
steady (0.55 / 0.40 / 0.55 and 0.88 / 0.88 / 0.88), which is why 3 runs is enough to trust a delta
this size.

Re-measure when the skill changes materially. A delta that collapses means either the skill stopped
teaching something or the case drifted into testing the model — and the second is the likelier of
the two.

## Why this is not in CI

Deliberate, and recorded in full in task 004. In short: a CI run would need both the early-access
flag and working Claude credentials, and this repo's strongest security property is that it holds
**no secrets at all** — a public repo with no secrets and no self-hosted runner has no attack
surface worth exploiting. Trading that for a check any contributor can run locally in twelve
minutes for about $5 is a bad trade. Run it before merging a skill change; the workflow gates the
form, you gate the behavior.

What CI *can* do for free is `scripts/check-evals.py`, which asserts the suite is well-formed — so
nobody pays for a run to discover a renamed scaffold or a case whose graders are all `with-only`
and whose delta is therefore computed against nothing.

## Adding a case

1. `mkdir evals/<name>` with a `case.yaml` and a `scaffold.sh`.
2. Scaffold a repo state where the wrong answer still *looks* like work. Silent failures are the
   only ones worth the money.
3. Write the prompt the way a human would actually say it. Naming the steps hands the procedure to
   the baseline arm and collapses the delta to zero.
4. Weight the graders by what the case exists to catch, and keep the paid ones to judgment calls.
5. Run it with `--ablation with-without`. **If the delta is near zero, the case is wrong, not the
   skill** — rewrite it around something the model cannot guess.
