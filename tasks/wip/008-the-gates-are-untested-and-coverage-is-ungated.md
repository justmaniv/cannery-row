---
created: 2026-08-07
updated: 2026-08-07
completed:
status: wip
owner: justmaniv
blocked-by: ""
links:
  - CONTRIBUTING.md
  - .github/workflows/ci.yml
  - tasks/done/007-task-body-contract-is-undocumented-and-unenforced.md
---

# The gates that enforce everything are themselves untested, and nothing floors coverage

## Measured state, 2026-08-07

Branch coverage, whole repository, production files only:

| File | Statements | Coverage | |
|---|---|---|---|
| `scripts/check-portability.py` | 55 | **0%** | the portability gate |
| `scripts/check-release.py` | 43 | **0%** | the version-bump gate |
| `scripts/check-workflows.py` | 47 | **0%** | the self-hosted-runner gate |
| `scripts/generate-task-board.py` | 249 | 94% | |

Three of the four scripts have no tests at all, and they are the three that *enforce*. This
project's entire argument is that guardrails belong in structure rather than in vigilance, and its
own enforcers are held up by vigilance alone.

`check-workflows.py` is the sharpest case. It is the only thing standing between a public
repository and a fork's pull request executing on the upstream project's self-hosted runner, which
holds deploy credentials. It was verified once, by hand, by injecting violations and watching them
get caught. Nothing re-checks it. A regex edited carelessly would pass CI silently, because CI runs
the gate — it does not test it.

There is also no coverage measurement anywhere: no tooling, no threshold, no CI step. Coverage can
fall to zero without turning anything red.

## Why the floor comes second, not first

A coverage build-breaker set today would either fail the build immediately or have to be set at a
number that enshrines three untested gates as acceptable. Tests first, floor after — the floor's
job is to stop regression, and there is nothing yet worth protecting.

Ruling, 2026-08-07: write the tests, then set the breaker at **85%**, matching the upstream
project's standard — all metrics, no exclusions beyond test files themselves.

## Note on method

These are **characterization tests over existing code**, not test-driven development. There is no
new behavior to drive out; the production code already exists and the tests are being backfilled
behind it. Recording that plainly rather than staging a theatrical RED commit — a RED that is
written already knowing the implementation proves nothing about design, and the repository's own
documentation is about to start claiming test-first discipline. Claiming it here would make that
documentation false on the same day it was written.

If a test finds a real defect, *that* one gets the RED/GREEN treatment for real.

## Done when

- [ ] `check-portability.py` has unit tests over `scan()` — clean tree, a forbidden term with its
      file and line, case-insensitivity, word-boundary behavior, a missing scanned file, and the
      generated-artifact link rule
- [ ] `check-workflows.py` has unit tests over `check_file()` — a clean workflow, a `self-hosted`
      label, a non-standard runner, both `pull_request_target` spellings, and the property that a
      mention inside a comment is ignored
- [ ] `check-release.py` has unit tests over `main()` with `git` stubbed — manifests agreeing,
      manifests disagreeing, a missing marketplace entry, shipped content changed without a bump,
      and a documentation-only change correctly exempt
- [ ] CI measures branch coverage across every test file and **fails under 85%**, test files
      themselves excluded from the measurement so the number describes production code
- [ ] `CONTRIBUTING.md` states the testing discipline, including that squash-merge means the
      RED/GREEN commit shape is a branch-level convention main cannot be audited for
- [ ] `CONTRIBUTING.md`'s hard-coded test count is corrected or removed — it says 51 and there are
      70, so it was stale within a day of being written
- [ ] Every existing gate still passes; no production behavior changed except where a test finds a
      real defect
