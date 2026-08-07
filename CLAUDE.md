# Cannery Row — project context

A Claude Code plugin. It ships one skill (`skills/task-lifecycle/SKILL.md`), a board generator,
and the gates that keep both honest. **The skill is the product** — everything else exists to stop
it rotting.

This repo tracks its own work with the skill it ships. `tasks/` is real, not a demo.

## The trap that wastes the most time here

**An installed plugin runs from a copy in the plugin cache, not from this checkout.** Editing a
clone changes nothing about the session you are editing in — you will test the old copy while
believing you tested the new one.

Two loops, and they are different. `CONTRIBUTING.md` is the authority; the short version:

- **Development** — `git worktree add ~/.claude/skills/cannery-row-dev <branch>`, then
  `claude plugin uninstall cannery-row@cannery-row`, then restart. A directory under a skills
  directory loads in place, so the working tree is what runs. **`disable` does not work** — the
  installed copy wins on name collision whether or not it is enabled.
- **Release** — bump `version` in **both** `.claude-plugin/plugin.json` *and*
  `.claude-plugin/marketplace.json`. `check-release.py` fails the build if you don't.

⚠️ **The bump is load-bearing, not bookkeeping.** The version is pinned, so a fix merged without
one reaches nobody while `plugin update` reports *"already at the latest version."* That happened
(`tasks/done/003-*`). README- and docs-only changes are exempt; the boundary is
`skills/ scripts/ tasks/README.md .claude-plugin/`.

## Before you change the skill

Run the behavioral evals. Nothing else in this repository checks that the skill is *followed* —
every other gate checks that it is well-*formed*.

```bash
CLAUDE_CODE_WALNUT_SPIRE=1 claude plugin eval . \
  --ablation with-without --scaffold \
  --allow-tools Bash Read Edit Write Glob Grep Skill
```

~$4.50, ~12 minutes. **`claude plugin eval` is early access — without that env var it prints a
notice and exits 0**, which looks exactly like a clean run. Target `.`, not the plugin name: cases
are discovered under the target, and a name target looks inside the plugin cache. `evals/README.md`
covers the design rules and three grader traps that produce assertions which pass while proving
nothing.

The delta, not the score, is the result. **A delta near zero means the case is wrong, not the
skill** — it is measuring the model.

## Everything else, in about a second

```bash
python3 scripts/check-portability.py       # no stack or methodology vocabulary in shipped files
python3 scripts/check-workflows.py         # GitHub-hosted runners only, no pull_request_target
python3 scripts/check-release.py           # manifests agree; version moved if shipped content did
python3 scripts/check-evals.py             # the eval suite is well-formed
python3 scripts/generate-task-board.py --check
claude plugin validate . --strict
coverage run -m unittest discover -s scripts -p '*_test.py' && coverage report   # 85% branch floor
```

## Non-negotiable

- **Never a `self-hosted` runner label, never `pull_request_target`, never a secret.** This is a
  public repo; a self-hosted runner lets any fork's PR execute arbitrary code, and holding no
  secrets is the strongest security property it has. `check-workflows.py` enforces the first two.
  Nothing enforces the third, because there has never been a reason to add one.
- **Stdlib only.** The gates have no runtime dependencies and it should stay that way — `coverage`
  is dev-only. A structural line read beats adding a parser (see `check-evals.py`).
- **Portability.** Shipped files must not name a language, vendor, host, or planning cadence. The
  gate is broader than vendor names on purpose: *methodology* vocabulary is the class that actually
  bites. Run `--list` to see the terms and why each is out.

## Conventions

- **Test-first for `scripts/`** — a RED commit that adds a failing test, then a GREEN commit that
  makes it pass. Squash-merge erases the distinction on `main`, so it is a branch-level discipline
  nothing downstream can audit. Backfilling tests onto existing code is characterization, not
  test-first; say so rather than dressing it up.
- **Tests assert behavior, never coverage.** A test that runs code without asserting its result is
  a hole with a green check over it.
- **Task hygiene** is governed by the skill this repo ships — use `cannery-row:task-lifecycle` for
  every create/start/block/close. `tasks/README.md` documents layout for humans; the skill governs
  operations. Regenerate `docs/task-board.md` in the same commit as any lane move.
- **`main` is PR-only.** Open the PR, enable auto-merge, carry it through to merged.
