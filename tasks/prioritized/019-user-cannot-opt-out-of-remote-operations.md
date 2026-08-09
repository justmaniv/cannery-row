---
created: 2026-08-08
updated: 2026-08-09
completed: ""
status: prioritized
owner: justmaniv
blocked-by: tasks/done/017-skill-assumes-a-remote-exists.md
links:
  - skills/task-lifecycle/SKILL.md
  - tasks/done/017-skill-assumes-a-remote-exists.md
---

# A user can turn off remote and host operations even when a remote exists

## What's wanted

Task 017 makes the push conditional on a remote *existing* — and deliberately holds everything
else constant. Its own "Done when" pins it: on a repository that has a remote, every transition
still ends with an immediate push. That leaves no room for the user who *has* a remote and still
doesn't want the cadence: a push on every lane move, plus host-side operations (review checks,
`gh` calls) riding along. For some projects that is the point; for others it is noise — too chatty,
and there is currently no way to say so.

This task adds the missing layer: an explicit, per-project opt-out that the skill honors even
when `git remote` returns something. 017 answers "can this project push?"; this answers "does
this project want to?"

## Scope ruling — the opt-out covers the remote, never git

**Settled 2026-08-09. Not to be re-proposed.** An earlier version of this task offered a second
tier that also disabled local commits, leaving a plain directory of files moved with `mv`. That
tier is struck.

`git mv` and the commit are the mechanism, not an implementation detail riding along with it.
Moving a task between lanes any other way forfeits the history that makes a task's provenance
real — per-task `git log`, and status changes that land as moves instead of edits in place — which
is the thing this tracker trades on. `SKILL.md` already states the rule: *"Git is assumed
throughout this skill — history is what makes the provenance claim true. A remote is not."* This
task must not open a hole in it.

Nothing is lost by striking it. The complaint that motivates this work is *"the tool is too
noisy"*, and noise is entirely a property of talking to the remote. A repository that commits
locally on every lane move and pushes when the user says so is silent from the team's point of
view. Making the **remote** the option satisfies the complaint in full; making **git** the option
would trade the product's core claim for nothing anyone asked for.

## Scope ruling — the opt-out is repo-level, never global

**Settled 2026-08-09.** The setting lives in the tracked repository and applies to that repository
only. A user-level or harness-level setting that silences pushes across every project the operator
touches is not what this is for: chattiness is a property of *a* project's cadence and *its* team,
so a second project on the same machine must be unaffected and must need no reconfiguration.

This is straightforwardly achievable — the tracker is already a directory in the repo, so the
marker can be too, and it lands in the same commit history as the tasks it governs.

It also rules out one of the two placements below. "Project instructions" is not reliably a repo
file: in most harnesses the same instruction surface resolves to a *user-global* file as well, so
an opt-out written there can leak to every repository on the machine — the exact failure this
ruling exists to prevent.

## The fork

One decision remains — the other two were settled above.

**Where in the repo the marker lives.**

| Option | Trade-off |
|--------|-----------|
| A field in `tasks/README.md` frontmatter | No new file, and it sits with the conventions it modifies — a reader who wants to know how this project behaves already opens that file. `tasks/README.md` is a copied-in doc, though, so an operator who never fetched it has nowhere to put the field. |
| A dedicated repo file the skill checks — e.g. `tasks/.lifecycle` | Independent of whether the operator copied `tasks/README.md`, and unambiguous to parse. Adds a file whose only job is config, in a project whose pitch is that it has none. |
| ~~A sentence in the skill deferring to "project instructions"~~ | Struck by the repo-level ruling above — that surface can resolve to a user-global file. |

Recommendation: the `tasks/README.md` frontmatter field. The missing-file case is real but cheap —
absent the file, there is no marker, and absent a marker the behavior is today's, which is the
correct default anyway. Adding a config-only file to buy that edge case is the worse trade.

**What "disabled" covers — settled.** Push and host operations only. `git mv` and the local commit
sit outside the mechanism's reach in every configuration; there is no tier that suppresses them.

**Portability constraint:** the shipped skill cannot say `gh`, GitHub, `origin`, `PR`, `pull
request`, or `branch protection` — 017 landed all six in the gate's vocabulary, each with a
suggested neutral phrasing (`origin` → *"the remote", or gate the step on `git remote` output*).
`push` itself is not banned and needs no circumlocution. Write this task's prose as "host
operations" / "sharing" from the start rather than retrofitting after the gate fires. This task
file may name names; `tasks/*.md` are not shipped and the gate does not scan them.

## Done when

- [ ] A documented per-project mechanism exists to disable push and host operations on lifecycle
      transitions, and the skill honors it even when `git remote` returns a remote
- [ ] The mechanism is read from a file inside the tracked repository, and only from there — no
      user-level or harness-level setting can turn it on, so two repositories on one machine can
      disagree about the cadence with no reconfiguration between them
- [ ] `git mv` and the local commit happen regardless of the mechanism's state — no configuration
      reachable through it can suppress either, and the skill says so where the option is described
- [ ] The mechanism's documentation states what it covers, and gives the one-line reason git is
      not on the list
- [ ] With no opt-out present, behavior is identical to post-017 behavior — this is an opt-out,
      not a new default
- [ ] `check-portability.py` passes on the changed shipped files
- [ ] `version` bumped in both manifests with a matching `CHANGELOG.md` heading, and the
      behavioral evals run before merge
- [ ] Every doc describing the changed behavior is updated in the same change — or the docs
      checked are named here, with why none needed it. At minimum: `README.md`'s
      *"A host is a bonus, not a dependency"* bullet, which currently offers a rung where
      *"the lanes and the board work on a filesystem alone"* — the git-less mode ruling 1 strikes —
      and `tasks/README.md`, which documents the conventions this option changes
