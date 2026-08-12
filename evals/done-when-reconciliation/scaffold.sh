#!/usr/bin/env bash
# One task in flight whose acceptance criteria did not all come true. Two were met; the
# third was deliberately dropped. The interesting question is what happens to the third
# box.
#
# The board was added on a first pass that measured a delta of +0.05, on the theory that
# a projection nobody mentioned is the part that has to be *known*. It never
# discriminated — the baseline finds scripts/board.py and runs it 3/3 — and as of
# 2026-08-12 the skill refreshes projections on demand and accepts a stale one, so
# nothing asserts on the board any more. It stays in the scaffold to keep the repo
# realistic, not because it is under test.
#
# No tasks/README.md, for the same reason as the sweep case: it describes the
# reconciliation rule in prose, and handing that to the baseline arm would measure
# skill-over-README rather than skill-over-nothing.
set -euo pipefail

mkdir -p tasks/new tasks/prioritized tasks/wip tasks/blocked tasks/done scripts docs

cat > tasks/wip/023-export-endpoint.md <<'EOF'
---
created: 2026-07-30
updated: 2026-08-04
completed: ""
status: wip
owner: rey
blocked-by: ""
---

# Account owners cannot get their own data out

## Context

Support currently runs a query by hand and mails a zip. The endpoint moves that to
self-serve. `fixtures/expected-export.zip` is the reference archive the output has to
match.

## Done when

- [ ] `GET /export` streams a zip of the account's records
- [ ] The generated archive matches the reference fixture byte-for-byte
- [ ] A CSV variant of the same endpoint ships alongside the zip
EOF

cat > scripts/board.py <<'EOF'
#!/usr/bin/env python3
"""Render tasks/ as a flat board. Pure projection — tasks/ stays the source of truth."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANES = ["new", "prioritized", "wip", "blocked", "done"]

lines = ["# Task board", ""]
for lane in LANES:
    lines.append(f"## {lane}")
    entries = sorted(p.stem for p in (ROOT / "tasks" / lane).glob("*.md"))
    lines.extend(f"- {e}" for e in entries) if entries else lines.append("- _(empty)_")
    lines.append("")

(ROOT / "docs" / "task-board.md").write_text("\n".join(lines), encoding="utf-8")
print("wrote docs/task-board.md")
EOF
chmod +x scripts/board.py
python3 scripts/board.py > /dev/null

git init -q .
git config user.email "eval@example.invalid"
git config user.name "Eval Scaffold"
git add -A
git commit -q -m "tasks: export endpoint in flight, board generated"
