---
created: 2026-08-08
updated: 2026-08-08
completed: ""
status: prioritized
owner: justmaniv
blocked-by: tasks/done/017-skill-assumes-a-remote-exists.md
links:
  - skills/task-lifecycle/SKILL.md
  - tasks/done/017-skill-assumes-a-remote-exists.md
---

# A user can turn off git and host operations even when a remote exists

## What's wanted

Task 017 makes the push conditional on a remote *existing* — and deliberately holds everything
else constant. Its own "Done when" pins it: on a repository that has a remote, every transition
still ends with an immediate push. That leaves no room for the user who *has* a remote and still
doesn't want the cadence: a commit and push on every lane move, plus host-side operations (PR
checks, `gh` calls) riding along. For some projects that is the point; for others it is noise —
too chatty, and there is currently no way to say so.

This task adds the missing layer: an explicit, per-project opt-out that the skill honors even
when `git remote` returns something. 017 answers "can this project push?"; this answers "does
this project want to?"

## The fork

Two decisions, roughly independent:

**Where the opt-out lives.**

| Option | Trade-off |
|--------|-----------|
| A marker the skill checks — e.g. a field in `tasks/README.md` frontmatter | Travels with the repo, discoverable, one place to look. Adds a config surface to a skill that has none today. |
| A sentence in the skill deferring to "project instructions" | Near-zero mechanism, but vague — an agent has to notice it, and "project instructions" means different things in different harnesses. |

**What "disabled" covers.**

| Tier | Trade-off |
|------|-----------|
| Push + host operations only; local commits stay | Preserves the skill's own provenance argument (history survives locally). Likely the right default meaning. |
| Everything, including commits | A pure directory tracker. Sacrifices provenance — the skill's stated reason for the commit — so if offered, the trade-off must be stated where the user makes the choice. |

Recommendation: marker in `tasks/README.md` frontmatter, covering push + host operations, with
commits kept. Offer the full-off tier only if it costs nothing extra to specify.

**Portability constraint:** the shipped skill cannot say `gh`, GitHub, or PR — and if 017 lands
its option 3, the gate will also flag host-workflow vocabulary like `push` outside allowed
phrasing. Whatever prose this task adds must be written as "host operations" / "sharing" from the
start, not retrofitted after the gate fires. (This task file can name names; `tasks/*.md` task
files are not shipped.)

## Done when

- [ ] A documented per-project mechanism exists to disable push and host operations on lifecycle
      transitions, and the skill honors it even when `git remote` returns a remote
- [ ] The mechanism states what it covers; whether local commits can also be disabled is decided
      and recorded, with the provenance trade-off stated at the point of choice
- [ ] With no opt-out present, behavior is identical to post-017 behavior — this is an opt-out,
      not a new default
- [ ] `check-portability.py` passes on the changed shipped files, including any terms 017 adds
- [ ] `version` bumped in both manifests with a matching `CHANGELOG.md` heading, and the
      behavioral evals run before merge
