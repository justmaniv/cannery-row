---
created: 2026-08-09
updated: 2026-08-09
completed: ""
status: new
owner: justmaniv
blocked-by: ""
links:
  - tasks/new/00013-adopters-copy-of-the-generator-drifts.md
  - tasks/done/00017-skill-assumes-a-remote-exists.md
  - README.md
  - scripts/check-portability.py
---

# Nobody can say what Cannery Row's feature set is, including us

## What's wrong

`README.md`'s **What's in the box** table lists five artifacts. The repository ships more than that,
and several of the unlisted ones are capabilities an adopter would want — including host-specific
ones that are never named, so nobody evaluating the project learns they exist.

There is no document that answers *"what can this do, and which parts are optional?"* The README
answers "what is the idea" (well) and "what is in the box" (partially). The gap is the middle: the
capability surface.

## Verified today

**The box table lists 5 of these.** Present in the repository:

| Artifact | In the box table? | Note |
|---|---|---|
| `skills/task-lifecycle/SKILL.md` | ✅ | 12 documented procedures |
| `tasks/README.md` | ✅ | |
| `scripts/generate-task-board.py` | ✅ | 2 modes: generate, `--check` |
| `scripts/check-portability.py` | ✅ | |
| `evals/` | ✅ | 2 cases |
| `scripts/check-workflows.py` | ❌ | **rejects `self-hosted` runner labels and `pull_request_target`** — host-specific, reusable, unmentioned |
| `scripts/check-release.py` | ❌ | manifest agreement + version-moved-if-content-moved |
| `scripts/check-evals.py` | ❌ | asserts the suite is well-formed without paying for a run |
| `.github/workflows/ci.yml` | ❌ | 7 gates wired up; a copyable reference for an adopter |
| `scripts/*_test.py` (5 files) | ❌ | unit tests, 85% branch floor |
| `docs/task-board.md` | ❌ | the generated artifact itself |
| `CHANGELOG.md` | ❌ | added by task 011 |

**The host-specific capabilities that exist and go unnamed.** This is the part that prompted the
task. `check-workflows.py` is a CI-safety gate for one host's workflow format. The board is emitted
as markdown + Mermaid *specifically* so it renders in a hosted repository view as well as a terminal
(`generate-task-board.py`'s own module docstring says so). `--check` exists to be a CI gate. None of
that appears in the README as a capability, so the reasonable assumption from reading it is that the
project is a skill plus one script.

**Naming a host in the README is allowed by design, so this does not fight the portability gate.**
`check-portability.py` scans exactly four files — `SKILL.md`, `tasks/README.md`,
`generate-task-board.py`, `docs/task-board.md` — and its source comment states the rule out loud:
*"README.md is the storefront, not cargo. It has to name the neighbours it is compared to and credit
where it came from; forbidding that vocabulary would forbid the positioning."* The executor does not
need to invent a neutral phrasing for the README. The shipped four still may not name a host.

**"Shipped" means two different things, and that is worth resolving while here.** The portability
gate's scanned set is those four files. The version-bump boundary in `CLAUDE.md` is
`skills/ scripts/ tasks/README.md .claude-plugin/` — all of `scripts/`. So `check-workflows.py` is
inside the bump boundary and outside the portability scan. Both are defensible individually and the
pair is confusing to explain, which is a symptom of there being no capability map.

## Scope — what this task is not

- **Not how adopters obtain files.** `tasks/new/00013-*` owns that, and its fork already weighs the
  plugin-cache path against the `curl`. Do not re-decide it here; if the inventory changes the
  inputs to that decision, say so in 013 rather than answering it in this task.
- **Not the skill's remote coupling.** `tasks/new/00017-*` owns that.
- **Not "document everything."** The README just gained an opinions section and is long. Deciding
  what does *not* earn a mention is half the work.

⚠️ One thing to verify rather than assume: an installed plugin's cache directory currently contains
the whole repository, not just `skills/` — so an adopter already has every script on disk before any
`curl`. That was checked by listing the cache on one machine on 2026-08-09 and **it is an
observation, not a documented contract**. Do not build an instruction on it without confirming it is
intended behaviour; that path is version-pinned and internal, which is precisely why
`tasks/done/00009-*` rejected it as an acquisition route.

## The fork — where the inventory lives

| Option | Trade-off |
|--------|-----------|
| **A column on the existing box table** | Smallest change; one table stays the single place to look. The table is already wide, and "optional/required" does not capture "needs a host" versus "needs git" versus "needs nothing". |
| **A `docs/capabilities.md`, linked from the README** | Room for the required/optional/host-dependent distinction without lengthening the storefront. One more file to keep fresh, and nothing gates its freshness — the failure mode this repo keeps rediscovering. |
| **A short "Optional extras" section in the README** | Keeps it in the one file people read, sells the host-specific pieces where they are visible. Grows the README again, right after a section was added to it. |
| **Inventory only, no new prose** | Produce the map as the task's own record, fix the box table's omissions, and stop. Cheapest, and defensible if the answer turns out to be "most of these are repo-internal and rightly unadvertised." |

Recommendation: **produce the inventory first, then decide — and expect option D or A.** The
capability list is short once "repo-internal gate" is separated from "adopter capability", and the
honest answer may be that only `check-workflows.py`, `ci.yml` and `--check` belong in front of a
reader. Writing the map is what makes that decision possible; picking the presentation before the
list is what produces a marketing section nobody can maintain.

## Done when

- [ ] An inventory exists that names every artifact in the repository and classifies each as: ships
      in the plugin, fetched by the adopter, or repo-internal — and separately, what it depends on
      (nothing / git / a remote / a specific host)
- [ ] The README's **What's in the box** table has no unexplained omissions — every artifact is
      either listed or deliberately excluded with the reason recorded in this task
- [ ] The host-specific capabilities are either named somewhere a reader will find them, or the
      decision to leave them out is recorded with the reason
- [ ] The two meanings of "shipped" — the portability gate's four files versus the version-bump
      boundary — are stated in one place so the next person does not have to derive the difference
- [ ] Whatever is added is either freshness-gated or small enough that staleness is visible; no new
      hand-maintained list that nothing checks
