#!/usr/bin/env bash
# One task in flight whose acceptance criteria did not all come true. Two were met; the
# third was deliberately dropped. The interesting question is what happens to the third
# box — and, separately, whether closing the task takes the generated board with it.
#
# The board is here because a first pass of this case measured a delta of +0.05: the
# model reaches strikethrough on its own, so reconciliation alone tests the model rather
# than the skill. A projection nobody mentioned is the part that has to be *known*.
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
