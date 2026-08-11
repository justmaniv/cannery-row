---
created: 2026-08-09
updated: 2026-08-11
completed:
status: new
owner: justmaniv
blocked-by: ""
links:
  - scripts/generate-task-board.py
  - skills/task-lifecycle/SKILL.md
  - tasks/blocked/019-user-cannot-opt-out-of-remote-operations.md
---

# The task tree can only live at `<repo>/tasks/`, which some repos cannot offer

## What's wanted

Adoption currently requires creating `tasks/` at the root of the repository. Plenty of repositories
cannot give that up cheaply:

- The name is taken and means something else — build-tool task definitions are a common collision,
  and a lane tree landing beside them is confusing in both directions.
- The root is owned. Monorepos, generated trees, and repositories where a top-level addition needs
  sign-off from a platform team all make "add a directory at root" the expensive step.
- House layout says otherwise. A project that keeps every non-source artifact under `docs/` or
  `ops/` has a rule this violates for no reason the rule's author would accept.

The ask: let a project say where its lane tree lives, rather than assuming one path.

## Verified cost — where the path is baked in

| File | Literal `tasks/` | Notes |
|---|---|---|
| `skills/task-lifecycle/SKILL.md` | 22 | mostly prose and example commands |
| `scripts/generate-task-board.py` | 9 | including the two structural seams below |
| `README.md` | 9 | prose, install instructions, the lane tree diagram |
| `scripts/check-portability.py` | 4 | |
| `tasks/README.md` | 3 | |

Three structural seams in the generator, not 47 edits:

```python
REPO_ROOT = Path(__file__).resolve().parent.parent      # :29  script must sit in <repo>/scripts/
OUTPUT    = REPO_ROOT / "docs" / "task-board.md"        # :30  output path also fixed
TASK_REF_RE = re.compile(r"tasks/(?:new|prioritized|wip|blocked|done)/(\d{3,})-…")  # :60
```

`load_tasks(root)` already takes a root and derives `root / "tasks" / lane` (`:196`), so the
loader is nearly parameterized already. The two that actually bite are `REPO_ROOT` being inferred
from the *script's own location*, and `TASK_REF_RE` hardcoding the literal `tasks/` prefix that
every `blocked-by:` value is written and parsed with. Change the root and every existing
`blocked-by:` in the project stops matching.

## The fork — and only one branch is really "someday"

**A. Relocatable, still inside the repo.** `docs/tasks/`, `.tasks/`, `ops/tasks/`. Every property
the project argues for survives untouched: the task and the code change land in one commit, one
history, one review. This is the branch that answers the legacy-repo complaint as actually stated.

**B. A sidecar repository.** Tasks tracked in git, in a *different* repo. Provenance survives —
it is still git — but the coupling to the code's history does not: no single commit holds the task
move and the change it describes, and `git log` on the code no longer reaches the reasoning.
`README.md`'s own argument runs against this: *"Notes kept outside the repository drift away from
the code they describe. A file next to the code, in the same commit history, does not."* The
comparison table sells the differentiator as **"one file per task, inside the repo, in git."**
Option B keeps the last two and gives up the first.

**C. Outside git entirely** — a directory on the filesystem, not tracked anywhere. **Struck before
it is proposed.** Ruling 1 on task 019 settled that git is not optional: moving lanes any other way
forfeits the per-task history that makes provenance real. This task must not become the side door
that reopens it, and the reason is recorded here so a future reader sees a decision rather than an
omission.

⚠️ **The strike above rests on a ruling that is no longer settled — corrected 2026-08-11.** 019 was
moved to `blocked/` that day precisely because ruling 1 assumes every project is a git repository
while `README.md:62-66` promises *"the lanes and the board work on a filesystem alone… Take as many
of those layers as your project actually has."* Do not treat option C as struck on 019's authority
until 019 is re-decided. This entry is left standing rather than rewritten because the *reasoning*
in it — that moving lanes outside git forfeits per-task history — is a real cost that survives
whichever way the ruling lands; what does not survive is citing 019 as having settled it.

Recommendation: **A, scoped tightly, and B only behind an explicit statement of what it costs.**
"Head task directory" should mean *a path within the repository*, defaulting to `tasks/`. That
covers the legacy-repo cases above at a fraction of B's blast radius, and it does not require the
project to soften a front-page claim. If B is ever wanted, it needs its own decision — the honest
framing is a supported downgrade, not a configuration value.

## This changes the fork in 019 — chicken-and-egg

019 is choosing where per-project configuration lives, and currently recommends **a frontmatter
field in `tasks/README.md`**. That placement cannot also carry a *task-root* setting: finding
`tasks/README.md` requires already knowing where the task tree is. A reader looking for the config
would have to search for the thing the config exists to locate.

So this task is evidence for 019's second option — a dedicated marker at a fixed, known location
(`.lifecycle` or similar at the repo root). Whoever picks up 019 should read this before choosing,
because picking the `tasks/README.md` field first and discovering this later means a second config
surface, or a migration off the first.

⚠️ **Updated 2026-08-11: the placement decision has an owner now, and it is neither this task nor
019.** A third setting wants the same surface — `031`, a project's declaration of where else to look
for its work — and `031` owns the placement for all three. This section stands as the argument that
sent it there; make the decision in `031` and consume it here.

A task root is a property of one project, and a user-global setting that *overrode* a project would
be actively wrong — that much of 019's scope ruling holds. Whether a user-level **default** may sit
underneath a project's own answer was not argued either way in 019 and is open; see the note added
to that task on 2026-08-11.

## Done when

- [ ] A project can declare its lane-tree root, and the board generator, the gate, and the skill
      all honor it; absent a declaration the behavior is today's `tasks/` and nothing changes for
      existing adopters
- [ ] The declaration is read from a fixed, known location that does **not** require knowing the
      task root to find — and 019's placement decision is either made consistently with this or
      explicitly reconciled with it
- [ ] `blocked-by:` values keep resolving after a relocation — the reference format and
      `TASK_REF_RE` are decided together, and an existing project's references either keep working
      or have a stated migration
- [ ] `REPO_ROOT` no longer depends on the generator script sitting in `<repo>/scripts/`, or that
      dependency is documented as a supported constraint rather than left implicit
- [ ] Scope is recorded: whether a root outside the repository (option B) is supported, and if it
      is, what it costs stated where the user chooses it. Option C is decided on its own merits
      against `README.md:62-66`'s layer promise — 019 ruling 1 is no longer available as the reason,
      per the note in §"The fork"
- [ ] `check-portability.py` passes on the changed shipped files
- [ ] `version` bumped in both manifests with a matching `CHANGELOG.md` heading, and the
      behavioral evals run before merge
- [ ] Every doc describing the changed behavior is updated in the same change — at minimum
      `README.md`'s lane-tree diagram and install instructions, and `tasks/README.md` — or the docs
      checked are named here, with why none needed it
