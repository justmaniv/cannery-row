#!/usr/bin/env python3
"""Fail if a shipped file uses a `$` followed by a digit.

Claude Code substitutes positional tokens in a skill body with the caller's
argument words before Claude ever reads the file. Verified 2026-08-30 against
this skill: invoked with the arguments `alpha bravo charlie delta`, an on-disk
`awk '/^worktree /{print $2}'` arrived as `awk '/^worktree /{print charlie}'`.
Indexing is zero-based, so the token resolves to the *third* word, and nothing
is substituted when the caller supplies too few words to reach that position —
which is why the corruption hid for weeks.

It hides well for a second reason: the corrupted line is usually still valid.
An undefined `awk` variable prints an empty string rather than erroring, so the
numbering scan's worktree half emitted one blank line per worktree, `find`
matched nothing, and `2>/dev/null` swallowed the rest. A silent half-scan is
worse than a missing one, because it is trusted.

The forms below are deliberately allowed. All of them were measured arriving
byte-identical in the same experiment, and flagging a price or a `${name}` is
how a gate earns a `# noqa` habit:

    ${name}   "$var"   $(...)   $((...))   $4.52

Run from the repo root: python3 scripts/check-skill-args.py
"""

from __future__ import annotations

import pathlib
import re
import sys
from typing import NamedTuple

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

# What crosses into somebody else's repository or context. Kept in step with
# check-portability.py's list on purpose: the two gates guard the same cargo for
# different reasons, and a file added to one belongs in the other.
SCANNED = [
    "skills/task-lifecycle/SKILL.md",
    "skills/task-lifecycle/scripts/archive-done-tasks.py",
    "tasks/README.md",
    "scripts/generate-task-board.py",
    "docs/task-board.md",
]

# A `$` directly followed by a digit. `(?<![\w}])` keeps `${next:-0}` and any
# other braced default out — the digit there is preceded by `-`, but the closing
# brace form is what a reader recognises, so both are excluded explicitly.
# A decimal amount like `$4.52` is a `$` followed by a digit too, so it is
# excluded by requiring the digit NOT be part of a longer number.
POSITIONAL = re.compile(r"(?<![\w}$])\$(\d)(?![\d.])")


class Finding(NamedTuple):
    path: str
    line: int
    token: str
    text: str


def scan(root):
    """Return (findings, errors) for the shipped files under `root`."""
    findings: list[Finding] = []
    errors: list[str] = []
    for rel in SCANNED:
        path = root / rel
        if not path.is_file():
            errors.append(f"{rel}: scanned file is missing")
            continue
        for number, text in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for match in POSITIONAL.finditer(text):
                findings.append(Finding(rel, number, match.group(0), text.strip()))
    return findings, errors


def main():
    findings, errors = scan(REPO_ROOT)
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    for finding in findings:
        print(f"{finding.path}:{finding.line}: {finding.token} is replaced by a caller argument")
        print(f"    {finding.text}")
    if findings or errors:
        print(
            f"\n{len(findings)} positional token(s). A reader who runs this line runs something "
            "else. Rewrite without a `$` and a digit — `sed -n 's/^worktree //p'` in place of an "
            "`awk` field reference, for one.",
            file=sys.stderr,
        )
        return 1
    print(f"ok: {len(SCANNED)} shipped files carry no positional tokens")
    return 0


if __name__ == "__main__":
    sys.exit(main())
