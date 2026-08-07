#!/usr/bin/env python3
"""Assert the eval suite is well-formed, since CI cannot afford to run it.

`claude plugin eval` needs an early-access flag and working credentials, so the behavioral
suite runs on a contributor's machine and costs real money (see `evals/README.md`). That
makes a malformed case an expensive way to find out: you pay for the run, then discover a
renamed scaffold or a case that never scores its baseline arm.

These are the breakages that are free to catch and silent otherwise:

1. **A case directory with no `case.yaml`.** It is skipped without comment.
2. **Missing `schema_version` / `name` / `graders`.** The runner rejects the case; better
   to hear it here than after the first paid run.
3. **`name` disagreeing with the directory.** `--case <glob>` filters on the declared
   name, so a mismatch means the case you asked for silently is not the case that ran.
4. **A `scaffold_script` that does not exist.** Renaming `scaffold.sh` leaves a case that
   fails at run time, after the scaffold slot is already billed.
5. **Every grader marked `arm: with-only`.** Those are not scored in the baseline arm, so
   the case reports a delta computed against nothing. A suite whose whole purpose is the
   with/without delta must never contain a case that cannot produce one.

**Structural line read, not a YAML parse.** Every other gate here is stdlib, and PyYAML
would be this repository's first runtime dependency — bought for five checks over keys at
known indentation. Top-level keys sit at column zero, which is enough to tell a case's own
`name:` from a grader's. The runner does the real schema validation and reports it
precisely; this gate only has to catch the mistakes that would otherwise cost a run.

Form only. Whether the cases *measure* anything is the delta's job, and no script can
check that.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVALS_DIR = REPO_ROOT / "evals"

REQUIRED_KEYS = ("schema_version", "name", "graders")

TOP_LEVEL_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):")
TOP_LEVEL_NAME_RE = re.compile(r"^name:\s*(?:\"([^\"]*)\"|'([^']*)'|(\S+))\s*$")
SCAFFOLD_RE = re.compile(r"^\s+scaffold_script:\s*(?:\"([^\"]*)\"|'([^']*)'|(\S+))\s*$")
GRADER_ENTRY_RE = re.compile(r"^\s+-\s+type:\s*\S")
WITH_ONLY_RE = re.compile(r"^\s+arm:\s*with-only\s*$")


def _value(match: re.Match[str]) -> str:
    """First non-None capture — the double-quoted, single-quoted, or bare form."""
    return next(g for g in match.groups() if g is not None)


def check_case(case_dir: Path) -> list[str]:
    rel = case_dir.relative_to(REPO_ROOT)
    case_file = case_dir / "case.yaml"
    if not case_file.is_file():
        return [f"{rel}/ has no case.yaml; the runner skips it without comment"]

    lines = case_file.read_text(encoding="utf-8").splitlines()

    top_level_keys = {m.group(1) for m in map(TOP_LEVEL_KEY_RE.match, lines) if m}
    problems = [f"{rel}/case.yaml is missing {k!r}" for k in REQUIRED_KEYS if k not in top_level_keys]

    for line in lines:
        m = TOP_LEVEL_NAME_RE.match(line)
        if m and _value(m) != case_dir.name:
            problems.append(
                f"{rel}/case.yaml declares name {_value(m)!r} but sits in {case_dir.name!r}; "
                "--case filters on the declared name, so they must agree"
            )
        m = SCAFFOLD_RE.match(line)
        if m and not (case_dir / _value(m)).is_file():
            problems.append(
                f"{rel}/case.yaml names scaffold_script {_value(m)!r}, which does not exist"
            )

    graders = sum(1 for line in lines if GRADER_ENTRY_RE.match(line))
    if "graders" in top_level_keys and graders == 0:
        problems.append(f"{rel}/case.yaml needs at least one grader")
    elif graders and graders == sum(1 for line in lines if WITH_ONLY_RE.match(line)):
        problems.append(
            f"{rel}/case.yaml scores every grader 'with-only', so the baseline arm "
            "scores nothing and the reported delta is meaningless"
        )

    return problems


def main() -> int:
    if not EVALS_DIR.is_dir():
        print("evals: no evals/ directory; nothing to check")
        return 0

    # `--output-dir` defaults to evals/results/<timestamp>/, which is not a case.
    case_dirs = sorted(d for d in EVALS_DIR.iterdir() if d.is_dir() and d.name != "results")
    problems: list[str] = []
    for case_dir in case_dirs:
        problems.extend(check_case(case_dir))

    for problem in problems:
        print(f"evals: {problem}", file=sys.stderr)
    if problems:
        print(f"\nFAIL: {len(problems)} eval suite problem(s).", file=sys.stderr)
        return 1

    print(f"ok: {len(case_dirs)} eval case(s) well-formed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
