#!/usr/bin/env bash
# Builds a repo where the next task number is not what the working tree says it is.
#
# Two things have to go right and neither is guessable:
#   1. The highest number lives on a branch that is not checked out. A working-tree `ls`
#      reads 0043 and takes 0044, which is already taken. Only a scan across refs sees it.
#   2. The tree is padded to four digits. Three is not "close enough" -- `ls` sorts
#      lexically, which is the entire reason the padding is there.
#
# Deliberately omits tasks/README.md, for the reason evals/README.md gives: it ships with
# the plugin and describes the convention in prose, so a scaffold containing it would hand
# the baseline arm the procedure and measure skill-over-README instead of skill-over-nothing.
#
# Four digits, not this repository's five. The width under test is the tree's, not ours --
# a scaffold at five would pass a generator that hardcoded five.
set -euo pipefail

mkdir -p tasks/new tasks/prioritized tasks/wip tasks/blocked tasks/done

cat > tasks/done/0042-retry-failed-webhooks.md <<'EOF'
---
created: 2026-07-14
updated: 2026-08-03
completed: 2026-08-03
status: done
owner: dana
blocked-by: ""
---

# A webhook that fails once is never delivered

## Done when

- [x] Failed deliveries retry on a backoff schedule
- [x] A delivery that exhausts its retries lands in the dead-letter table
EOF

cat > tasks/wip/0043-dead-letter-replay.md <<'EOF'
---
created: 2026-08-03
updated: 2026-08-05
completed: ""
status: wip
owner: rey
blocked-by: ""
---

# Nothing can replay a dead-lettered delivery

## Done when

- [ ] An operator can replay one dead-lettered delivery by id
- [ ] A replayed delivery is marked as such in the audit log
EOF

git init -q .
git config user.email "eval@example.invalid"
git config user.name "Eval Scaffold"
git add -A
git commit -q -m "tasks: webhook retries done, dead-letter replay in flight"

# The number that is not in the working tree. A sibling session took it on its own branch
# and pushed; nothing in `tasks/` here shows it.
git checkout -q -b sibling-session
cat > tasks/new/0044-audit-log-retention.md <<'EOF'
---
created: 2026-08-05
updated: 2026-08-05
completed: ""
status: new
owner: sam
blocked-by: ""
---

# The audit log grows without bound

## Done when

- [ ] Audit rows older than the retention window are removed on a schedule
- [ ] The retention window is configurable without a deploy
EOF
git add -A
git commit -q -m "task: audit log retention"
git checkout -q -
