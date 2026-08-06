#!/usr/bin/env python3
"""Assert this public repo's CI can never execute a fork's code somewhere dangerous.

Two rules, and only these two, because they are the ones whose violation causes
real harm rather than mess:

1. **No `self-hosted` runner label.** On a public repository, a self-hosted runner
   means any fork's pull request runs arbitrary code on that machine. The upstream
   project this was extracted from runs its CI on a self-hosted runner that holds
   deploy credentials; a job copy-pasted from there carries its `runs-on` label with
   it, and nothing else would notice.
2. **No `pull_request_target` trigger.** It runs the base repository's workflow with
   a token that has write access, in a context a fork can influence. This repo has
   no secrets and nothing to deploy, so there is no reason to reach for it.

The check is structural, not textual: it reads `runs-on:` values and the keys under
`on:`. A grep for the forbidden strings would match this file's own explanation, and
a gate that cannot describe itself gets deleted the first time it is inconvenient.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"

RUNS_ON_RE = re.compile(r"^\s*runs-on:\s*(.+?)\s*$")
# A trigger key sits at exactly two spaces of indent under a top-level `on:` block,
# or inline as `on: [pull_request_target]` / `on: pull_request_target`.
TRIGGER_KEY_RE = re.compile(r"^\s{0,4}(pull_request_target)\s*:")
INLINE_ON_RE = re.compile(r"^\s*on:\s*(.+?)\s*$")

ALLOWED_RUNNERS = {"ubuntu-latest", "ubuntu-24.04", "ubuntu-22.04"}


def check_file(path: Path) -> list[str]:
    problems: list[str] = []
    rel = path.relative_to(REPO_ROOT)
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.split("#", 1)[0]

        m = RUNS_ON_RE.match(stripped)
        if m:
            value = m.group(1)
            labels = {v.strip().strip("[]\"'") for v in value.split(",")}
            if any("self-hosted" in label for label in labels):
                problems.append(
                    f"{rel}:{lineno}: runs-on {value!r} uses a self-hosted runner. "
                    "On a public repo any fork PR would execute on that machine."
                )
            elif not labels & ALLOWED_RUNNERS:
                problems.append(
                    f"{rel}:{lineno}: runs-on {value!r} is not a standard GitHub-hosted runner "
                    f"({', '.join(sorted(ALLOWED_RUNNERS))}). Larger runners bill even on public repos."
                )

        if TRIGGER_KEY_RE.match(stripped):
            problems.append(
                f"{rel}:{lineno}: pull_request_target trigger. It grants a write-scoped token in a "
                "context a fork influences; use pull_request."
            )

        m = INLINE_ON_RE.match(stripped)
        if m and "pull_request_target" in m.group(1):
            problems.append(f"{rel}:{lineno}: pull_request_target trigger. Use pull_request.")

    return problems


def main() -> int:
    if not WORKFLOW_DIR.is_dir():
        print(f"error: no workflow directory at {WORKFLOW_DIR}", file=sys.stderr)
        return 1

    workflows = sorted(WORKFLOW_DIR.glob("*.yml")) + sorted(WORKFLOW_DIR.glob("*.yaml"))
    if not workflows:
        print(f"error: no workflows found in {WORKFLOW_DIR}", file=sys.stderr)
        return 1

    problems = [p for wf in workflows for p in check_file(wf)]
    for problem in problems:
        print(f"unsafe: {problem}", file=sys.stderr)

    if problems:
        print(f"\nFAIL: {len(problems)} unsafe workflow setting(s).", file=sys.stderr)
        return 1

    print(f"ok: {len(workflows)} workflow(s) — GitHub-hosted runners only, no pull_request_target")
    return 0


if __name__ == "__main__":
    sys.exit(main())
