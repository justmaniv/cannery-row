---
created: 2026-08-11
updated: 2026-08-12
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

`019:89-103` has a fork table for the placement and recommends a field in `tasks/README.md`
frontmatter. `022:88-93` shows that placement cannot carry a task-home setting — finding
`tasks/README.md` requires already knowing where the task home is — and names a fixed-location
marker as the alternative it thinks wins. Neither task owns the decision, so it has not been made.
**This task owns it.** The other two become consumers.

⚠️ **Citations corrected 2026-08-12.** The three line references above and at §Constraints read
`019:66-76`, `022:83-87` and `019:47-52` when this file was written. All three were already stale
that day: commit `54e1325` — the commit that created this task — shifted `019` by ~23 lines, so the
references pointed at unrelated prose from the moment they landed. `027` copied two of them forward
without reopening the file, and they were caught by its pickup validation. **Re-open a cited file
before quoting a line range from a sibling task**; a line number is the one kind of citation that
rots without anything failing.

## Constraints the answer has to satisfy

- **Absent a declaration, behavior is exactly today's.** No adopter has one; every one of them must
  be unaffected.
- **Findable without knowing the task home.** `022`'s objection applies to this setting with more
  force than to its own — a reader looking for "where else does this project keep work" cannot be
  required to already know where the first home is.
- **Findable without git.** Per point 1 above. A marker read by a filesystem path satisfies this; a
  mechanism that depends on being in a repository does not.
- **Scoped to the project, not the machine** — the part of `019:74-80` that is not in dispute. Two
  projects on one machine must be able to answer differently with no reconfiguration between them.
  Whether a user-level *default* may sit underneath a project's answer is `019`'s open question, not
  this task's; nothing here should foreclose it.
- **Portable prose.** The declaration is described in `SKILL.md` and `tasks/README.md`, both scanned
  by `check-portability.py`. Run `--list` rather than guessing.

## Scope — settled 2026-08-11

**What "look for work" reaches: the searches, not the tracker.** Decided by the owner the day this
task was written, after the alternative was put to them explicitly.

Work still lives in **one task home per project**. That is what *"each with its own task home"*
means — one home each, not many homes each. What a declaration adds is **where the skill's searches
read**, and nothing else:

```
project-a/tasks/{new,prioritized,wip,blocked,done}/   <- the one home
shared-docs/                                          <- declared
sibling-project/docs/                                 <- declared

board   -> unchanged, reads the one home
numbers -> unchanged, unique within the one home
search  -> reads the home *and* every declared location
```

**Explicit non-goals**, so an implementer does not drift into them:

- The board generator does not gain a second root. It reads the project's home, as today.
- The numbering scan does not widen. Numbers stay unique within one home.
- `blocked-by:` does not have to resolve across locations, so the reference format does not move.

A declared location holding its own lane tree is a **later** question. It is strictly larger — the
generator, the numbering scan, and the reference format all move together — and nothing about this
task's design should foreclose it. If it is ever wanted it gets its own task, and the first thing
that task will ask is whether the declaration format chosen here can carry more than a path.

**Which searches are in scope** — every one the skill hands out, which is the same list `029` is
repairing: prior coverage before creating, the propagation gate's bound at close, and the
reverse-dependency sweep. If `029` has already landed, this extends a working search; if not, this
task inherits the defects and must not paper over them.

## Done when

- [ ] A project can declare additional locations, and every search the skill hands out reads them in
      addition to the project's own task home — demonstrated on a location that holds no lane tree
      and contains only prose
- [ ] The declaration works on a project that is **not** a git repository as well as on one that is,
      per `README.md:62-66`'s layer promise
- [ ] The declaration is found without already knowing where the project's task home is
- [ ] Absent a declaration, every behavior is today's — demonstrated on a project with no
      declaration, not asserted
- [ ] Two projects on one machine answer differently with no reconfiguration between them
- [ ] A declared location that does not exist, or has become unreadable, degrades to a stated
      behavior rather than an error that stops a lifecycle operation — the searches it feeds are
      mandatory steps, so a broken declaration must not be able to block a close
- [ ] The non-goals are recorded in the change itself: the board reads one home, numbering stays
      within one home, `blocked-by:` does not resolve across locations. A later task may widen them;
      this one does not, and a reader must see that as a decision rather than an omission
- [ ] `019`'s placement fork at `:66-76` and `022`'s "fixed, known location" criterion are
      reconciled against the surface this task lands — both consume it or state why they need their
      own
- [ ] `check-portability.py` passes on the changed shipped files
- [ ] `version` bumped in both manifests with a matching `CHANGELOG.md` heading, and the behavioral
      evals run before merge
- [ ] Every document and open task this change makes wrong is updated, and anything the work turned
      up that nothing yet records is written down — or what was checked is named here, with why none
      of it needed changing. At minimum: `tasks/README.md`, and `029` if it has not yet landed
