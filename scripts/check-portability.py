#!/usr/bin/env python3
"""Fail if the shipped artifacts name a stack, a vendor, or a planning cadence.

Cannery Row's whole claim is that it works in any repository. That claim decays
by accident, not by intent: the codebase this was extracted from has a specific
language, a specific database, a specific host, and a specific planning
methodology, and prose written there reaches for that vocabulary without anybody
noticing. It already happened once — a section added two days after a clean
portability audit read as perfectly generic and still carried four occurrences of
a cadence word. Nobody catches that by eye. So a grep does.

The gate is deliberately dumb. It looks for whole words, it explains every hit,
and it suggests the neutral phrasing. False positives are a feature: being made
to justify a methodology term in a stack-agnostic skill is the point.

This file is not scanned, and cannot be: it necessarily contains every term it
forbids. That exemption is the one hole in the gate, so keep the vocabulary a
plain data table and keep the logic boring.

    check-portability.py            # report and exit non-zero on any hit
    check-portability.py --list     # print the vocabulary and exit
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Scan exactly what crosses into somebody else's repository or context: the skill Claude loads,
# the conventions doc users copy, and the scripts they run. Those must read as if written for
# their project, because for them it is.
#
# Two files are deliberately absent, and the line between them and the list is the whole rule:
#   - README.md is the storefront, not cargo. It has to name the neighbours it is compared to and
#     credit where it came from; forbidding that vocabulary would forbid the positioning.
#   - This script necessarily contains every term it forbids.
SCANNED = [
    "skills/task-lifecycle/SKILL.md",
    "tasks/README.md",
    "scripts/generate-task-board.py",
    # The board is scanned as well as its generator, and that is not redundancy. The first
    # version of this list held only the generator, and a dead relative link plus a foreign CI
    # gate number sailed through — they lived in an emitted string, so nothing in the source
    # read as stack-coupled. What reaches a user is the output. Scan the output.
    "docs/task-board.md",
]

# Links a downstream repository cannot resolve. Distinct from FORBIDDEN because these are not
# vocabulary — a term can be argued for, a 404 cannot. Any relative markdown link emitted into
# a generated artifact has to resolve in the repo it lands in, and only same-directory or
# tasks/ links do.
LINK_RE = re.compile(r"\[[^\]]*\]\((?!https?://|#)([^)]+)\)")
PORTABLE_LINK_PREFIXES = ("../tasks/", "tasks/", "./")

# term -> (why it is not portable, what to write instead)
FORBIDDEN = {
    # Upstream project identity
    "ehap": ("the upstream project's infrastructure name", "drop it"),
    "kist": ("the upstream product's brand", "drop it"),
    "justhud": ("the upstream company", "drop it"),
    # Language and toolchain
    "rust": ("a language this must not assume", "no language, or name it as an example"),
    "cargo": ("a Rust toolchain", "the project's build tool"),
    "rustacean": ("a Rust community term", "drop it"),
    "clippy": ("a Rust linter", "the project's linter"),
    # Hosting and vendors
    "fly.io": ("a specific host", "the deploy target"),
    "flyctl": ("a specific host's CLI", "the deploy tool"),
    "supabase": ("a specific backend vendor", "the database"),
    "dioxus": ("a specific UI framework", "drop it"),
    "postgres": ("a specific database", "the database"),
    # Planning methodology — the class that actually bit us
    "bmad": ("a specific planning methodology", "drop it"),
    "sprint": ("a cadence not every team runs", '"planning cycle" or "iteration"'),
    "epic": ("a methodology-specific unit of work", '"a larger piece of work"'),
    "story": ("a methodology-specific unit of work", '"a unit of work" or "a feature"'),
    "backlog": ("a methodology-specific artifact", '"the queue" or "unstarted work"'),
    "velocity": ("a methodology-specific metric", "drop it"),
    "retro": ("a methodology-specific ceremony", '"a review"'),
    "standup": ("a methodology-specific ceremony", "drop it"),
    "runway": ("an artifact name from the upstream project", '"the doc that tracks phases"'),
    # Collaboration topology — a remote and a host are a bonus, not a dependency (task 017).
    # Deliberately absent from this class: "push" and "remote", because the skill's own fix is
    # a *conditional* push gated on `git remote` output — the words are the repair, not the
    # coupling; and "fork", because these files use it constantly in its decision-point sense
    # and the host sense never appears without other flagged vocabulary alongside.
    "origin": ("the conventional remote name — a repository may have no remote", '"the remote", or gate the step on `git remote` output'),
    "PR": ("a host's review mechanism, not a git primitive", '"review branch" or "proposed change"'),
    "pull request": ("a host's review mechanism, not a git primitive", '"review" or "propose the change"'),
    "branch protection": ("a host feature, not a git primitive", '"a reviewed main branch"'),
}

# Whole-word, case-insensitive, suffixes included ("sprints" is "sprint" wearing a plural).
# Two exceptions: `fly.io` needs its dot escaped and `\b` after a dot would not match, so
# non-alnum tails anchor on a non-word boundary instead; and all-caps terms ("PR") match as
# exact case-sensitive words plus a plural s — the suffix wildcard would swallow every word
# starting with those letters ("provenance"), and lowercase look-alikes are innocent.
def _pattern(term: str) -> re.Pattern[str]:
    if term.isupper():
        return re.compile(r"\b" + re.escape(term) + r"s?\b")
    return re.compile(
        (r"(?<!\w)" + re.escape(term) + r"(?!\w)")
        if not term[-1].isalnum()
        else (r"\b" + re.escape(term) + r"\w*\b"),
        re.IGNORECASE,
    )


PATTERNS = {term: _pattern(term) for term in FORBIDDEN}


def scan(repo_root: Path) -> tuple[list[str], list[str]]:
    """Return (findings, errors). Errors are structural, e.g. a missing file."""
    findings: list[str] = []
    errors: list[str] = []
    for rel in SCANNED:
        path = repo_root / rel
        if not path.exists():
            errors.append(f"scanned file is missing: {rel}")
            continue
        is_generated = rel.startswith("docs/")
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for term, pattern in PATTERNS.items():
                match = pattern.search(line)
                if not match:
                    continue
                why, instead = FORBIDDEN[term]
                findings.append(
                    f"{rel}:{lineno}: {match.group(0)!r} — {why}; write {instead}\n"
                    f"    {line.strip()}"
                )
            if not is_generated:
                continue
            for target in LINK_RE.findall(line):
                if target.startswith(PORTABLE_LINK_PREFIXES):
                    continue
                findings.append(
                    f"{rel}:{lineno}: relative link {target!r} — a generated artifact must not "
                    f"link outside the repo it is generated into; this 404s downstream\n"
                    f"    {line.strip()}"
                )
    return findings, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="print the vocabulary and exit")
    args = parser.parse_args()

    if args.list:
        width = max(len(t) for t in FORBIDDEN)
        for term, (why, instead) in sorted(FORBIDDEN.items()):
            print(f"{term:<{width}}  {why}; write {instead}")
        return 0

    findings, errors = scan(REPO_ROOT)

    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    for finding in findings:
        print(f"not portable: {finding}", file=sys.stderr)

    if errors or findings:
        print(
            f"\nFAIL: {len(findings)} stack-coupled term(s), {len(errors)} structural error(s).\n"
            "These files ship to repositories that share none of this project's stack.",
            file=sys.stderr,
        )
        return 1

    print(f"ok: {len(SCANNED)} shipped files carry no stack-coupled vocabulary")
    return 0


if __name__ == "__main__":
    sys.exit(main())
