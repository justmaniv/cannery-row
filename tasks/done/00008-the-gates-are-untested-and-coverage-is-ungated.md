---
created: 2026-08-07
updated: 2026-08-07
completed: 2026-08-07
status: done
owner: justmaniv
blocked-by: ""
links:
  - CONTRIBUTING.md
  - .github/workflows/ci.yml
  - tasks/done/00007-task-body-contract-is-undocumented-and-unenforced.md
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

- [x] `check-portability.py` has unit tests over `scan()` — 19 tests. Added beyond the list: one
      that asserts every entry in `SCANNED` is actually scanned, because a path silently dropped
      from that list is the one failure the gate cannot self-report.
- [x] `check-workflows.py` has unit tests over `check_file()` — 18 tests, including the
      self-description property: the same forbidden terms inside a *comment* must not trip it,
      which is the entire reason this check is structural rather than a grep.
- [x] `check-release.py` has unit tests over `main()` with `git` stubbed — 14 tests. Two of them
      drive the **real** `git` subprocess against a throwaway repository, so the one piece of
      actual plumbing isn't left untested behind its own stub.
- [x] CI measures branch coverage across every test file and **fails under 85%**, test files
      themselves excluded — `.coveragerc`, wired into CI as `unit tests + coverage floor`.
      Breaker verified by raising the floor to 99 (exit 2) and lowering it back (exit 0), not
      assumed from the config being present.
- [x] `CONTRIBUTING.md` states the testing discipline, including that squash-merge means the
      RED/GREEN commit shape is a branch-level convention main cannot be audited for
- [x] `CONTRIBUTING.md`'s hard-coded test count is **removed rather than corrected** — a
      hand-maintained count in a file nobody re-reads goes stale again. It was wrong within a day
      the first time.
- [x] Every existing gate still passes; no production behavior changed — **not one line**. The
      backfill found no defects, which is a result worth recording: these gates were correct, they
      were simply unprotected.

## Outcome

Production branch coverage **60% → 95%**; the three gates went 0% → 98% / 97% / 97%. 51 new tests,
123 total.

Two things came out of doing it that weren't in the plan:

- **The release gate caught its own change.** Committing the test files tripped `check-release.py`
  — `scripts/*_test.py` sit under a shipped prefix, so installed copies receive them and the
  version had to move. Unplanned, and the best available evidence that gate works.
- **Nothing needed fixing.** Backfilling tests onto three untested enforcers turned up zero
  defects. The risk was never that they were wrong; it was that nothing would notice when they
  became wrong.
