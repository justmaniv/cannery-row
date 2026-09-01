---
created: 2026-08-07
updated: 2026-08-07
completed: ""
status: new
owner: justmaniv
blocked-by: ""
links:
  - .github/workflows/ci.yml
  - CONTRIBUTING.md
---

# Installability is the product, and it is checked once by hand

## What's wrong

`claude plugin validate . --strict` runs in CI and proves the manifests **parse**. It does not
prove the plugin **installs**. Those came apart once already in this project's short history: a
pinned version that never moved validated perfectly and shipped nothing (task 003).

The end-to-end path — `marketplace add` → `install` → skill actually loads — was walked by hand
exactly once, at `0.4.2`, and recorded in the closing note of the task that published the repo.
Every release since has inherited that verification without re-earning it. Nothing would notice if
a manifest change broke the fetch: CI stays green, `main` stays green, and the first person to find
out is whoever tries to install it.

For a repository whose entire value proposition is "install this and it works", that is the wrong
thing to be checking least.

## Why this is awkward, and the fork it creates

The obvious fix — install the plugin in CI — is not obviously available. Installing pulls from the
marketplace, which points at `main`, so a pull-request build would verify the *previous* release
rather than the change under review. And `claude plugin marketplace add <local path>` works, but
that path is not the path users take.

| Option | Trade-off |
|--------|-----------|
| **Local-path marketplace in CI** | Exercises the real fetch and install machinery on the PR's own tree, catches a broken manifest before merge. Does not exercise the GitHub fetch, which is where a `source` change would break. Needs `npm install -g @anthropic-ai/claude-code`, already done in the existing job. |
| **Post-merge install smoke on `main`** | Tests exactly what users get, including the GitHub fetch. Finds the break *after* it is public — a red `main` rather than a blocked PR. |
| **Both** | The honest answer, and probably twenty lines of workflow. |
| **A documented manual step per release** | Free, and the release loop is already a checklist a human walks. Relies on the same discipline that task 003 proved unreliable. |

Recommendation: **local-path in CI on every PR, plus the manual step in the release checklist**,
and skip the post-merge job until something actually breaks. The PR-time check is the one that
prevents the bad state rather than reporting it.

⚠️ Whatever wins must not introduce a secret or a self-hosted runner. `check-workflows.py` enforces
the second; nothing enforces the first, because there has never been a reason to add one.

## Done when

- [ ] The install path is verified automatically on every PR, or a recorded decision says why not
- [ ] The check fails when it should — verified by breaking a manifest on purpose and watching it
      go red, then reverting. Not reasoned about; the workflow gate was verified this way too
- [ ] `CONTRIBUTING.md` states which install path is covered automatically and which is not
- [ ] No secret and no self-hosted runner added; `check-workflows.py` still passes
