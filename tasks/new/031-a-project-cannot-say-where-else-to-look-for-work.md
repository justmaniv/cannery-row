---
created: 2026-08-11
updated: 2026-08-11
completed:
status: new
owner: justmaniv
blocked-by: ""
links:
  - README.md
  - skills/task-lifecycle/SKILL.md
  - tasks/blocked/019-user-cannot-opt-out-of-remote-operations.md
  - tasks/new/022-task-root-is-hardcoded-to-repo-root.md
  - tasks/new/029-propagation-sweep-hardcodes-two-directories.md
---

# A project can tell this tool where else to look for its work

## The goal, in the words it was given

> The user should be able to tell this tool, on a per-project or per-repo basis — each with its own
> task home — where else it can look for work.

Stated 2026-08-11 by the owner, after two sessions argued the mechanism and lost the requirement.
This task exists to own the capability. **It is not a re-litigation of whether the capability is
wanted.** Read the constraints below as the shape the answer has to take, not as reasons to narrow
it further.

Two things in that sentence are load-bearing and both were being dropped:

1. **Per *project* or per *repo*.** Not only per repository. A project is not necessarily a git
   repository, and the front page already sells it that way — `README.md:62-66`: *"The tracker is a
   directory tree, so the lanes and the board work on a filesystem alone. Git adds the history… Take
   as many of those layers as your project actually has; plenty of real use is local-only."* A
   design that can only be found or read by way of git contradicts a shipped claim.
2. **Each with its own task home.** More than one home is in scope. The declaration says where the
   *other* places are, which presupposes the tool can hold more than one.

## What is in the way today

**Every search the skill hands out is written against one hardcoded layout**, and none of them can
be told otherwise. `029` has the verified inventory; the short version is that the prior-coverage
search names two directories from one upstream project, the propagation gate's bound names two more,
and one of the two prior-coverage commands has never worked at all. Those are defects to fix on
their own merits — but fixing them lands the searches on *a* default, not on *a project's answer*,
which is this task.

**There is no surface to put the answer on.** Three settings now want a per-project declaration and
none of them owns one:

| Wants a declaration | Task |
|---|---|
| Whether this project talks to a remote | `019` |
| Where this project's task home is | `022` |
| Where else to look for work | this task |

`019:66-76` has a fork table for the placement and recommends a field in `tasks/README.md`
frontmatter. `022:83-87` shows that placement cannot carry a task-home setting — finding
`tasks/README.md` requires already knowing where the task home is — and names a fixed-location
marker as the alternative it thinks wins. Neither task owns the decision, so it has not been made.
**This task owns it.** The other two become consumers.

## Constraints the answer has to satisfy

- **Absent a declaration, behavior is exactly today's.** No adopter has one; every one of them must
  be unaffected.
- **Findable without knowing the task home.** `022`'s objection applies to this setting with more
  force than to its own — a reader looking for "where else does this project keep work" cannot be
  required to already know where the first home is.
- **Findable without git.** Per point 1 above. A marker read by a filesystem path satisfies this; a
  mechanism that depends on being in a repository does not.
- **Scoped to the project, not the machine** — the part of `019:47-52` that is not in dispute. Two
  projects on one machine must be able to answer differently with no reconfiguration between them.
  Whether a user-level *default* may sit underneath a project's answer is `019`'s open question, not
  this task's; nothing here should foreclose it.
- **Portable prose.** The declaration is described in `SKILL.md` and `tasks/README.md`, both scanned
  by `check-portability.py`. Run `--list` rather than guessing.

## The open fork — this needs the owner's answer before the criteria below are final

**What "look for work" reaches.** Two readings, and they build differently:

| Reading | What it means |
|---|---|
| **A. Search scope** | The declared locations are added to the searches the skill runs — prior coverage before creating, the propagation bound at close, the reverse-dependency sweep. Work stays in one home; the tool reads more places when looking for what already covers a topic or what a change made wrong. |
| **B. Multiple task homes** | The declared locations may themselves hold lane trees. The board generator reads all of them, numbering has to stay unique across them, and `blocked-by:` has to resolve across them. |

B contains A. B is materially more work — the generator, the numbering scan, and the reference
format all move — and it is the reading the phrase *"each with its own task home"* most naturally
supports. Do not guess: the answer changes the criteria below, and this is exactly the fork whose
guessing wasted the exchange that produced this task.

## Done when

⚠️ Provisional until the fork above is answered; the last three assume nothing about it.

- [ ] A project can declare additional locations for its work, and the tool honors the declaration
      on a project that is not a git repository as well as on one that is
- [ ] The declaration is found without knowing where the project's first task home is, and without
      running a git command
- [ ] Absent a declaration, every behavior is byte-for-byte today's — demonstrated, not asserted
- [ ] Two projects on one machine answer differently with no reconfiguration between them
- [ ] `019` and `022` are reconciled against the placement this task lands: `019`'s fork table at
      `:66-76` and `022`'s "fixed, known location" criterion either resolve to this surface or state
      why they need their own
- [ ] `README.md:62-66`'s layer promise still reads true after the change, or is amended in the same
      change to say what it now promises
- [ ] `check-portability.py` passes on the changed shipped files
- [ ] `version` bumped in both manifests with a matching `CHANGELOG.md` heading, and the behavioral
      evals run before merge
- [ ] Every document and open task this change makes wrong is updated, and anything the work turned
      up that nothing yet records is written down — or what was checked is named here, with why none
      of it needed changing
