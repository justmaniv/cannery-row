#!/usr/bin/env python3
"""Assert the two manifests agree on a version, that it moved when the plugin did, and that
the changelog says what moved.

`plugin.json` pins a version. A pinned version means installed copies stay put until the
string changes — so a fix pushed to `main` without a bump reaches nobody, and
`plugin update` cheerfully reports "already at the latest version". That is a silent
staleness, which is the exact failure this project exists to argue against.

Three checks:

1. **The manifests agree.** `plugin.json` wins at load time when they differ, so a
   marketplace entry left behind is invisible until someone reads both files.
2. **The version moved when shipped content did.** Compared against the merge base with
   `origin/main`, so it only fires on a branch that actually changes what users install.
   Skipped when no baseline is available, which is the case on the first commit and in a
   shallow clone.
3. **The new version has a changelog entry.** The bump changes what runs in someone else's
   repository; without an entry the only record is a commit message, and reading it requires
   knowing this repository exists. Presence is all a script can judge — a thin entry passes.
   That is still worth gating, because the failure it catches is forgetting entirely, and the
   remedy is visible in review where a missing file is not.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"

# What an installed copy actually receives. A README change does not need a bump.
SHIPPED_PREFIXES = ("skills/", "scripts/", "tasks/README.md", ".claude-plugin/")


def git(*args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), *args],
            capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return out.stdout.strip()


def changelog_names(version: str) -> bool:
    """True when CHANGELOG.md carries a heading for this version. `## [0.4.1]` and `## 0.4.1`
    both count; `## [0.4.10]` does not, and neither does the version mentioned in a paragraph —
    an entry has to be somewhere a reader can navigate to."""
    if not CHANGELOG.exists():
        return False
    heading = re.compile(rf"^##\s+\[?{re.escape(version)}\]?(?![\w.])", re.MULTILINE)
    return bool(heading.search(CHANGELOG.read_text(encoding="utf-8")))


def main() -> int:
    plugin = json.loads(PLUGIN.read_text(encoding="utf-8"))
    marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))

    problems: list[str] = []

    plugin_version = plugin.get("version")
    entries = [p for p in marketplace.get("plugins", []) if p.get("name") == plugin.get("name")]
    if not entries:
        problems.append(
            f"marketplace.json has no entry named {plugin.get('name')!r}; "
            "the plugin would not be installable from this marketplace"
        )
    for entry in entries:
        if entry.get("version") != plugin_version:
            problems.append(
                f"version mismatch: plugin.json {plugin_version!r} vs marketplace entry "
                f"{entry.get('version')!r}. plugin.json wins at load time, so this divergence "
                "is invisible until someone reads both files."
            )

    base = git("merge-base", "HEAD", "origin/main")
    if base and plugin_version:
        changed = git("diff", "--name-only", base, "HEAD") or ""
        shipped_changed = [
            f for f in changed.splitlines() if f.startswith(SHIPPED_PREFIXES)
        ]
        old_manifest = git("show", f"{base}:.claude-plugin/plugin.json")
        old_version = json.loads(old_manifest).get("version") if old_manifest else None
        if shipped_changed and old_version == plugin_version:
            problems.append(
                f"version is still {plugin_version!r} but installed content changed:\n    "
                + "\n    ".join(shipped_changed)
                + "\n  A pinned version that does not move means `plugin update` reports "
                "'already at the latest version' and users keep the old copy."
            )
        elif shipped_changed and old_version and not changelog_names(plugin_version):
            problems.append(
                f"version moved {old_version!r} → {plugin_version!r} but CHANGELOG.md has no "
                f"'## [{plugin_version}]' heading.\n  A bump changes what runs in someone else's "
                "repository. Without an entry the only record of what changed is a commit "
                "message, and reading it requires already knowing this repository exists."
            )

    for problem in problems:
        print(f"release: {problem}", file=sys.stderr)
    if problems:
        print(f"\nFAIL: {len(problems)} release problem(s).", file=sys.stderr)
        return 1

    print(f"ok: manifests agree on version {plugin_version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
