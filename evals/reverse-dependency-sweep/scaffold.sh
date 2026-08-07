#!/usr/bin/env bash
# Builds a repo mid-flight: one task about to close, two tasks waiting on it.
#
# Deliberately omits tasks/README.md. The README ships with the plugin and describes
# the sweep in prose, so a scaffold containing it would hand the baseline arm the
# procedure and measure skill-over-README instead of skill-over-nothing. The skill is
# the independent variable; keep it the only source of the procedure.
set -euo pipefail

mkdir -p tasks/new tasks/prioritized tasks/wip tasks/blocked tasks/done

cat > tasks/wip/012-add-rate-limiting.md <<'EOF'
---
created: 2026-07-28
updated: 2026-08-01
completed: ""
status: wip
owner: dana
blocked-by: ""
---

# Requests from one account can exhaust the whole worker pool

## Context

A single client looping on `POST /ingest` starves every other tenant — there is no
per-account ceiling anywhere in the request path. The limiter belongs in the edge
middleware, before the handler allocates a worker.

## Done when

- [ ] A per-account request ceiling is enforced in the edge middleware
- [ ] Exceeding it returns 429 with a `Retry-After` header
EOF

cat > tasks/blocked/007-document-the-limits.md <<'EOF'
---
created: 2026-07-20
updated: 2026-07-28
completed: ""
status: blocked
owner: dana
blocked-by:
  - tasks/wip/012-add-rate-limiting.md
  - tasks/wip/019-settle-the-pricing-tiers.md
---

# Customers cannot find out what their rate ceiling is

## Context

Support answers this by hand today. The public docs page needs the real numbers, which
means both the limiter and the tier pricing have to land first.

## Done when

- [ ] The public API docs state the per-account ceiling for each tier
- [ ] The 429 response body links to that page
EOF

cat > tasks/blocked/015-load-test-the-limiter.md <<'EOF'
---
created: 2026-07-29
updated: 2026-07-29
completed: ""
status: blocked
owner: rey
blocked-by: tasks/wip/012-add-rate-limiting.md
---

# Nothing proves the limiter holds under real concurrency

## Context

The unit tests exercise the counter, not the middleware under load. Needs a soak run
against a deployed build once the limiter exists.

## Done when

- [ ] A soak run drives 500 concurrent accounts past their ceiling
- [ ] p99 latency for compliant accounts is unchanged versus the pre-limiter baseline
EOF

cat > tasks/wip/019-settle-the-pricing-tiers.md <<'EOF'
---
created: 2026-07-22
updated: 2026-08-02
completed: ""
status: wip
owner: sam
blocked-by: ""
---

# The tier names in billing and in the docs disagree

## Context

Billing calls them starter/growth/scale; the marketing site says free/pro/enterprise.
Nothing can quote a per-tier number until one naming wins.

## Done when

- [ ] One set of tier names is chosen and recorded
- [ ] Billing and the marketing site both use it
EOF

git init -q .
git config user.email "eval@example.invalid"
git config user.name "Eval Scaffold"
git add -A
git commit -q -m "tasks: rate limiting in flight, docs and load test waiting on it"
