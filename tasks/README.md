# Tasks

Lightweight directory-based task tracking. Each task is a single markdown file; its location IS its status.

```
tasks/
├── new/          # captured, not yet triaged
├── prioritized/  # triaged and ordered; pull from the top
├── wip/          # actively in progress (keep this small)
├── blocked/      # waiting on something — note the blocker in the file
└── done/         # completed; archive here for history
```

## Conventions

- **Filename:** `NNN-short-kebab-slug.md` — the numeric prefix orders the queue within a directory. Pad every number in a project to the same width: the directory *is* the tracker, read with `ls`, in an editor sidebar and in `git status`, all of which sort lexically, and only a uniform width makes lexical order equal numeric order. Pick the width once and keep it — the skill reads it off the highest number already in the tree rather than imposing one, so nothing here has to agree with any other project. Numbering restarts per project; the numbers carry no meaning beyond ordering, so yielding one is free.
- **Move, don't copy.** Status changes are `git mv` — git history preserves the journey. A task's whole life is `git log --follow` on one file, not a line that changed in a big shared file.
- **One task per file.** If a task spawns sub-tasks, link them; don't nest.
- **`prioritized/` ordering:** put at the top whatever unblocks the most other work, then whatever reduces the most risk, then the smallest useful batch. Order is expressed by position in the directory listing (hence the numeric prefix), not by a priority field — there is nothing to keep in sync.
- **WIP limit: 3 in `wip/` per human owner** — roughly one per concurrent session. Pull from the top of `prioritized/`. A task that stalls moves to `blocked/` *before* you pull the next one; that move is what keeps the limit honest rather than decorative.
- **Frontmatter is required** for status tracking, and so is a body — an H1 title and a
  `## Done when` checklist. Both are checked; see below.

## Frontmatter

```yaml
---
created: YYYY-MM-DD       # set on creation, never changed
updated: YYYY-MM-DD       # bumped on every status change or material edit
completed: YYYY-MM-DD     # set when moved to done/; empty otherwise
status: new               # must match the directory: new | prioritized | wip | blocked | done
owner: your-name
blocked-by: ""            # optional; the blocking task's path, or a prose condition
links:                    # optional
  - relative/path/to/related-doc.md
---
```

`blocked-by:` takes either a task path (`tasks/wip/012-thing.md`) or a plain-language condition
("waiting on the vendor contract"). Both are first-class — a task gated on something outside the
repo is still blocked, and rendering it as unblocked is a lie. For several blockers, use a YAML
block sequence.

Add your own fields if your project needs them. The board generator ignores what it doesn't know,
so extra frontmatter costs nothing — but if you want it *rendered*, add it to the generator
deliberately rather than hoping.

## The body

Two elements are required, in every lane, from the moment the file is created:

```markdown
# What outcome this task produces

## Context

Whatever carries the handoff — what is verifiably true in the code today, the fork you
considered, what you recommend. Free-form; use the headings that fit.

## Done when

- [ ] A criterion someone else can check without asking what you meant
- [ ] Another one
- [ ] Every document and open task this change makes wrong is updated, and anything the work
      turned up that nothing yet records is written down — or what was checked is named here,
      with why none of it needed changing
```

**The H1 is the title of record.** The board reads it for the card headline. There is no `title:`
frontmatter field on purpose — a title in two places is a title that disagrees with itself.

**`## Done when` is the acceptance criteria**, and it is the load-bearing half. It is the only
part of the file a later session with none of your context is held to, and "completing" a task is
*defined* as resolving every box in it — `- [x]` if met, `- ~~struck through~~ (reason)` if
deliberately skipped. A task with no criteria closes on nobody's authority but the closer's,
because "resolve every `- [ ]`" is trivially satisfied when there are none.

Write criteria a different person can evaluate. *"Works properly"* is not a criterion; *"the gate
exits non-zero on a task missing its H1"* is. If you can't state one yet, the task isn't understood
well enough to hand off — that's a useful signal, not a formality to skip.

**The third line in the template is the propagation criterion, and it is the one nobody would think
to write.** A closure leaves two things behind: a document that now says something false, and a
thing the closer learned that no document says at all. Only the session doing the work can name
either, and it is the session about to end. The wording is deliberately unsatisfiable in silence —
*"or what was checked is named here"* means a closer who ticks it without naming anything has
visibly not resolved it, and `- ~~struck through~~ (reason)` already covers the honest "nothing
applied" case. `- [ ] Docs updated` would be worse than no line at all: tickable without opening a
single file, and green forever.

This is a convention, **not** a gate. Nothing checks for the line, and that is deliberate — see the
note in `generate-task-board.py` where the gate deliberately stops. The skill enforces the
obligation at close instead, where the answer actually exists; the template line is for the task
that knows its blast radius when it's written.

If you have `generate-task-board.py` (see below — it is fetched separately), it **refuses to build
a board** when any task is missing either element, naming every offending file and what to do about
it. Both were silent failures before it did: a missing H1 rendered a blank card and exited 0, and a
missing checklist made the completion gate vacuous. Without the script these stay conventions; the
gate fires whenever the generator runs, so how often it fires is a consequence of how you answer the
CI trade below.

## Status hygiene

`status` and the file's directory must always agree. When moving a task:

- **Starting:** if the task has sat for more than one planning cycle, first check it hasn't been overtaken — `git log --oneline --all --grep="\bNNN\b"` (ignore hits where NNN is only a merge reference) and `grep -rn "task NNN" --exclude-dir=tasks .`. Read any hit before starting: a task's work can ship under a *different* task number while its file sits untouched. Then `git mv` to `wip/`, set `status: wip`, bump `updated`.
- **Completing:** resolve every `- [ ]` in the "Done when" checklist (`- [x]` if met, `- ~~strikethrough~~ (reason)` if deliberately skipped), set `status: done`, set `completed`, bump `updated`, `git mv` to `done/`.
- **Blocking:** `git mv` to `blocked/`, set `status: blocked`, bump `updated`, fill `blocked-by`.

Do this in the same commit as the work. Treat status moves and frontmatter updates as part of the
acceptance criteria, not as bookkeeping to catch up on later.

**On completion, sweep dependents.** Tasks reference each other by path in `blocked-by`, so a move
invalidates other files. When a task lands in `done/`, find what referenced it
(`grep -rl "blocked-by:" tasks/ | xargs grep -l <slug>`), rewrite the now-stale path to the new
`done/` location, and re-triage any task whose only remaining blocker just closed. Skipping this
leaves tasks sitting in `blocked/` behind something that finished weeks ago.

**On completion, also carry the content outward.** That sweep repairs *references* — it does not
notice that an open task or a document now describes behavior which just changed, and it never
visits the artifact that doesn't mention this task at all. So before reporting a task done, name
what this change made wrong and anything it turned up that nothing yet records. Bound it by what
already cites the task, the task's own `links:`, and the files you had to open to do the work —
that last one is where the unrecorded thing usually belongs. Naming an artifact and routing it to
the task that owns it is enough; you are not obliged to fix every site you find.

> The operational procedure for Claude Code is in the `task-lifecycle` skill this repo ships.
> This README is the human-readable summary; the skill governs the operations.

## Seeing the whole board

The generator is not installed with the skill and is not in this repository by default — fetch it
once, then it is yours to keep and edit:

```bash
mkdir -p scripts && curl -o scripts/generate-task-board.py \
  https://raw.githubusercontent.com/justmaniv/cannery-row/main/scripts/generate-task-board.py
```

```bash
python3 scripts/generate-task-board.py            # writes docs/task-board.md
python3 scripts/generate-task-board.py --check    # exits non-zero if the board is stale
```

`docs/task-board.md` is a generated view of this directory — every lane in flow order,
`prioritized/` in pull order, the `blocked-by:` graph as a Mermaid diagram, a WIP-limit check, and
`done/` collapsed to a count plus the most recent entries.

It is a **pure projection** — the files here stay the source of truth, and the board owns no state.
If it needs a field, add the field to the frontmatter above first.

**The board is regenerated by hand, on demand, and that is deliberate.** Nothing obliges you to
refresh it when you move a task, and a stale board is not an unfinished move. It is one file that
every lane change rewrites, so in a repo where several people or sessions work in parallel it is the
most contended file in the tree — and every one of those conflicts is ceremony, because the file is
derived. Nobody hand-merges two renderings of the same directory. Running the generator is nearly
free; it is the collisions that cost, and they land on whoever merges second. Refresh it when you
want to read it.

`--check` in CI is a genuine trade with two defensible answers:

| | |
|---|---|
| **Run `--check`** | The board can never be stale on a merged change, and the structural gate above fires on every proposed change. The price is that every task move must regenerate the board — the churn just described. Right if you want the freshness guarantee. |
| **Don't run it** | The board drifts between refreshes and someone regenerates it when it matters. The structural gate then fires only when the generator runs. Right if low churn is what you're optimising for. |

⚠️ **What doesn't work is `--check` in CI without regenerating on every move.** A staleness check
fails on a stale board, and a task move makes the board stale — so every task-move change goes red,
and the fix is to hand-run the generator anyway. That is the same work, discovered as a failed build
instead of prompted, and it is strictly worse than either row above. Pick a row; don't land between
them.

## Why one file per task

Two properties fall out of the layout, and they are the whole reason to prefer it over a single
shared list:

- **Parallel sessions don't collide.** Two agents working two tasks touch two files. A shared list
  is a merge conflict waiting for the second writer — which is a real incident, not a hypothetical,
  in the codebase this was extracted from.
- **Loading one task costs one task.** An agent pulling a task reads that file, not the whole board.
  The context saved is the difference between a page and the entire queue.
