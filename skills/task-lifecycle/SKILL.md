---
name: task-lifecycle
description: Move tasks between status directories (new/prioritized/wip/blocked/done) with full frontmatter sync, "Done when" reconciliation, reverse blocked-by sweep, a propagation gate that carries a closure's changes and findings out to the documents and open tasks they affect, claim validation before starting a task you did not write, and collision-safe task numbering. Use whenever creating, starting, blocking, unblocking, or completing a task in a repository's `tasks/` directory.
allowed-tools: Bash, Read, Edit
---

## Premise

`tasks/<status>/NNN-slug.md` IS the task tracker. The directory the file lives in is its status. Frontmatter must agree with the directory. Other tasks reference this one by path in their `blocked-by:` field, so a move has cross-task consequences.

This skill is the source of truth for the lifecycle procedure. Project `tasks/README.md` files document layout and frontmatter for humans; this skill governs the *operations*.

---

## Invariants (always true after this skill runs)

1. `status:` frontmatter value === directory the file is in.
2. `updated:` is today's date on every transition or material edit.
3. `created:` is set at file creation and **never** changes.
4. `completed:` is set if and only if the file is in `done/`.
5. Every `- [ ]` in the "Done when" checklist is resolved (`- [x]` or `- ~~strikethrough~~ (reason)`) before a task moves to `done/`.
6. No task sits in `blocked/` with every one of its blockers closed. A `blocked-by:` entry whose task has moved is **rewritten to the new path**, never deleted — the entry is the audit trail, and `status: blocked` over an empty `blocked-by:` is a task blocked by nothing. When the last blocker closes, surface the task for re-triage (see the sweep); it does not sit there.
7. **The campsite is clean** before any task is reported `done` to the human — see the Clean-campsite gate in the `wip → done` procedure. "Done" is never claimed over a littered workspace.
8. **Every task file carries an H1 title and a `## Done when` checklist with at least one criterion** — in every lane, from the moment it is created. See "The shape of a task file" below.
9. **What the closure made wrong has been corrected, and what the closure turned up has been written down somewhere it will be read again** — see the Propagation gate in the `wip → done` procedure. Naming the artifact and routing it satisfies this; fixing every site does not have to.

If you can't satisfy an invariant, stop and surface the conflict — don't move the file.

---

## Transitions

All transitions are: (a) update frontmatter in place, (b) `git mv` the file, (c) for `→ done`, run the three closing gates — the reverse-dependency sweep, the propagation gate, and the campsite check. Do this in the same turn as the work that triggered the transition. Don't ask "should I move it?" as a separate question.

### `new → prioritized`
- Set `status: prioritized`
- Bump `updated:` to today
- `git mv tasks/new/X.md tasks/prioritized/X.md`

### `prioritized → wip` (or `new → wip`, `blocked → wip`)
- **First validate the task's claims** (see below) — unless you wrote it yourself, in which case there is nothing to re-check.
- Set `status: wip`
- Bump `updated:`
- `git mv` to `tasks/wip/`

### `* → blocked`
- Set `status: blocked`
- Bump `updated:`
- Fill `blocked-by:` with the blocking task's path (e.g. `tasks/wip/010-create-prd.md`). Multi-line YAML block scalar is fine for multiple blockers.
- `git mv` to `tasks/blocked/`

### `wip → done` (full procedure)

1. **Reconcile "Done when" checklist.** Every `- [ ]` must become either:
   - `- [x]` (or `- ✅`) — criterion actually met
   - `- ~~strikethrough~~ (reason)` — deliberately skipped, reason stated
   
   Never pre-fill `- ✅` on something that wasn't accomplished. ✅ means done; pre-filling erodes the signal.
2. Set `status: done`
3. Set `completed:` to today
4. Bump `updated:` to today
5. `git mv` to `tasks/done/`
6. **Run reverse-dependency sweep** (below).
7. **Run the propagation gate** (next section) — carry outward what this closure made wrong and what it turned up.
8. **Clean the campsite** (below) — the last thing before you report `done` to the human.

---

## Propagation gate (before claiming `done`)

**A closure changes what is true, and nothing else in this skill carries that outward.** Every other
propagation step here walks a path: the reverse-dependency sweep walks the tasks that name this one,
and the phase check walks a document the project has already identified. Content has no path to
walk. The session holding the answer is the one about to end, so what does not go out now does not
go out.

**This gate holds on every closure, whether or not the task file says so** (invariant 9). The
template carries a matching line because most tasks benefit from stating their blast radius up
front — but an author who drops it changes nothing about the obligation, exactly as with the
campsite gate one section down.

Two things go outward, and the second is the one that gets missed:

- **What the change left wrong.** Something asserts the old behavior and is now false.
- **What the change turned up that nothing yet says.** No sentence is wrong; a sentence is
  *missing*, and only you know it. There is no query behind this half — the artifact that needs the
  note may never mention this task at all.

⚠️ **This is not the reverse-dependency sweep, and it will be mistaken for it.** That sweep finds
tasks that *name* this one and rewrites a stale path — a bookkeeping fix to a reference. This gate
reads for *content that just stopped being true*, and its most valuable hits are artifacts that
never named this task and never will.

### The bound

*"Everything relevant"* is not a criterion. It is satisfied by finding nothing and refuted by
nothing — the shape of check §"The shape of a task file" tells you not to write. Three sources, and
it is the third that reaches the second half:

1. **What already cites this work**, by number or by slug:

   ```bash
   grep -rl "NNN-slug" tasks/ docs/
   ```

2. **The task's own `links:` frontmatter.**
3. **The artifacts you had to read to do the work.** No query returns this list; you have it because
   you just opened them. It is usually where the missing sentence belongs, and neither of the other
   two sources can see it.

### The stopping rule — name and route, don't fix everything

A four-line change can open into dozens of sites, and an unbounded sweep at closure is how this step
gets ticked blind to escape it. **Name the artifact and route it to the task that owns it — you are
not obliged to fix every site you find.** Correct what this change itself made wrong; for anything
further out, name it in the closing task and either open a task for it or add it to the one that
already owns that ground. This is the same call the reverse-dependency sweep makes one step over: it
*surfaces* newly-unblocked tasks for the user to triage rather than moving them itself.

Then, in the done report, say what you carried and what you routed elsewhere.

---

## Clean-campsite gate (before claiming `done`)

**"Done" is not "the change merged" — it is "the change merged *and* the workspace is as clean
as you found it."** Never come back to the human claiming a task is done while temporary
scaffolding you created is still lying around. This is a required completion step, not a
courtesy: leftover worktrees, merged branches, and orphaned background jobs are the litter
the *next* session (or the human) trips over. Every task carries an implicit clean-campsite
acceptance criterion — you do not need to restate it per file, but you must satisfy it every
time (invariant 7).

Walk this checklist and act on each — don't just eyeball it:

```bash
git worktree list          # any temp worktree you added for this task → remove it
git branch -vv             # merged/`: gone` local branches you created → delete (-d, or -D for squash-merges)
git status -sb             # working tree clean, on a known branch (usually main), no stray files
jobs                       # background polls/servers you started → stop them
```

- **Temp worktrees:** reset the branch to its merge target (usually `main`) first if it holds merged work (avoids a
  "discard permanently?" prompt), then `git worktree remove`. Never leave a task's worktree behind.

  ⚠️ **Run the removal from outside the tree you are removing.** `git worktree remove` deletes the
  directory, so if your shell is sitting in it, the cwd is pulled out from under you mid-command and
  everything chained after it dies with `fatal: Unable to read current working directory` — including
  the rest of this checklist. The failure looks like a git problem and is not one. `cd` to the main
  tree first:

  ```bash
  cd /path/to/main-tree && git worktree remove ../<temp-tree>
  ```

  Then finish the checklist from there. This is the single most-reported stumble in this section.
- **Local branches:** delete the ones *you* created that are now merged or whose upstream is `gone`.
  **Leave** branches still under review or carrying an active sibling task — say which you left and why.
- **Remote branches / anything outward-facing:** do not delete without asking — surface it instead.
- **Background jobs:** stop any poll/watch/server you spawned for the task.
- **Scratchpad temp files** are session-scoped and auto-cleaned — no action needed; never put task
  deliverables there.

Then, in the done report, state the campsite is clean and note anything deliberately left standing.

---

## Before starting: validate the task's claims

**A task file is a claim about the past. Before acting on it, confirm the claim is true.** Note
what that does *not* say: not "still true." A task can be false the day it was written.

**The trigger is authorship, not age.** Validate the load-bearing claims of any task you did not
write yourself, however fresh it is. A task you wrote in this session needs nothing — you already
read the code. Everything else does, because two different failures land in the same place:

- **Overtaken.** Work converges under whatever task its author happened to be in, so a task's own
  work can ship under a *different* number while its file sits untouched. Age makes this likelier.
- **Wrong when written.** The author searched the wrong directory, read a stale document, or
  assumed a convention had lapsed. Age has nothing to do with it, and nobody reviewed the file
  before it landed.

The second is the more likely failure for a task written to be handed off, and the more expensive:
a stale task wastes a pickup, a false premise sends you building the wrong thing with a
well-argued spec telling you it's right. Real case: a task claimed a table had never been seeded
and specified work to seed it. Seven migrations were already doing exactly that — the author's grep
had searched one directory while the writes lived in another. Four minutes of checking; the task
was one day old, and every "is it stale?" heuristic would have waved it through.

Read the code before you trust the task, and read it to **break** the claim rather than to confirm
it. The two questions send you to different files: *"check this claim"* finds the thing the task
cited and stops there; *"try to prove this wrong"* opens what that thing actually does. Start with
the claims the work depends on — the ones where being wrong changes what you build, not every
sentence.

Then, for task number `NNN`, check whether the work already shipped elsewhere:

```bash
git log --oneline --all --grep="\bNNN\b"     # discard hits where NNN is only a merge reference, (#NNN)
grep -rn "task NNN" --include='*.rs' --include='*.md' --exclude-dir=tasks .
```

Read any hit before proceeding. Note the second command excludes `tasks/` deliberately: hits
*inside* `tasks/` are just cross-references, and the naive `| grep -v '^./tasks/'` filter silently
matches nothing, because paths come back without the `./` prefix.

Then act on what you find:

- **Work already shipped →** the task is done, not startable. Close it per `wip → done` with the
  evidence (the commit and the file that implements it), and spawn a follow-up for any real
  remainder rather than folding the remainder into the closure.
- **Partially shipped →** rewrite the task to the *actual* remaining scope before starting, so the
  "Done when" list describes work that still exists.
- **A load-bearing claim is false →** rewrite the task against what the code actually says, *then*
  start. Say what was wrong and how you found it; the next reader needs to know the file was
  corrected rather than drafted that way. If the correction changes the shape of the work rather
  than its details, hand it back instead of quietly redesigning it under the old number.
- **Nothing found →** proceed. The check cost two greps and a few minutes of reading.

**Why this matters most for decision tasks and spikes.** Their chosen option characteristically
ships inside the very piece of work that needed it. A decision task picked up cold reads as an
instruction to *go implement option A* — so the failure mode is not a stale board entry, it is
rebuilding something that already has callers. Real case: a coverage-standard decision task sat in
`new/` for ten days while the harness it recommended was built and merged the very next day under a
different task number — the implementing file named the decision task in its own module doc. It was
caught only because the pickup happened to read the code first. That is luck, not procedure.

If you also run a periodic grooming sweep, this is its per-pickup complement: grooming bounds
staleness to at most one cycle; this catches it at zero latency, at the moment it would cost work.

**Where this check stops.** It is answered by a reader who has just absorbed the task's argument, so
it is validation and not an independent read. It is built for the two failures above and is weak
against a third: a claim about *how* something works, where everything cited is real and the
mechanism is invented. A citation that checks out is not evidence for the sentence around it — the
load-bearing claim is rarely *"this artifact exists"*, it is *"it does X by doing Y"*, and Y is the
part that gets made up. When the task's own output is a spec later sessions are held to, a false
mechanism does not stop at this file: it flows into its `## Done when` list and its siblings', and
once it is a criterion it is self-enforcing. That case wants a second reader that was not in the
conversation which accepted the task, told to assume something is wrong and go find it. This skill
does not ship one and does not prescribe one — it tells you where its own check stops.

---

## Before creating: check for prior coverage

**Before drafting a new task, search for existing coverage of its topic.** A new task
that duplicates or *contradicts* an existing task, ADR, README, or runbook is worse than
no task: two artifacts answering the same question differently silently diverge, and a
blind draft can merge to `main` before anyone notices the conflict. This is a real failure
mode, not a hypothetical — it has happened (a runner-cache task drafted and merged before
finding an existing task + README already governed that ground, with a *different* stance).

The check is cheap and mandatory. Before writing the file:

```bash
# TOPIC = a couple of distinctive keywords for the task (e.g. "runner cache", "otp signup")
grep -ril "TOPIC" tasks/ docs/decisions/ docs/working-agreement/ 2>/dev/null
grep -ril "TOPIC" -- '*README*' 'ci/**' 2>/dev/null   # topic's runbook/README home, if any
```

Then act on the hits:

- **Prior coverage exists →** extend or reopen against it (add a task that *references* the
  governing doc/ADR, or reopen the owning task) rather than creating a parallel artifact.
  If the existing coverage is a decision you'd be changing, that's an ADR/supersession
  conversation, not a fresh task.
- **A governing doc exists but is stale/wrong →** fix it in place; don't route around it
  with a contradicting new task.
- **Nothing found →** proceed to numbering below.

Fold anything you *do* find into the new task's `links:` frontmatter so the next person
inherits the trail. When in doubt, widen the keywords — a false "nothing found" is the
expensive outcome.

---

## The shape of a task file (on creation)

Frontmatter is not the whole contract. Two things in the **body** are required, in every lane,
from creation — not added later when the task is closed:

```markdown
---
created: YYYY-MM-DD
updated: YYYY-MM-DD
completed:
status: new
owner: name
blocked-by: ""
---

# What outcome this task produces

## <whatever carries the handoff>

Context, the verifiable state of the code today, the fork you considered and what you recommend.

## Done when

- [ ] A criterion someone else can check without asking what you meant
- [ ] Another one
- [ ] Every document and open task this change makes wrong is updated, and anything the work
      turned up that nothing yet records is written down — or what was checked is named here,
      with why none of it needed changing
```

- **The H1 is the title of record.** Any projection of `tasks/` reads it for the card headline;
  without it the card renders blank and nothing reports the omission.
- **`## Done when` is the acceptance criteria.** It is the only part of the file a later session
  is held to, and the `wip → done` transition is *defined* as reconciling it (invariant 5). A task
  with no criteria — or with the heading and nothing under it — closes on nobody's authority but
  the closer's, because "resolve every `- [ ]`" is trivially true when there are none.

- **The third line is the propagation criterion.** It is worded so it cannot be resolved silently:
  a closer who ticks it having named nothing has visibly not done it. It is in the template as a
  default, not as a requirement — invariant 9 holds whether or not the file carries the line, so
  dropping it costs nothing but the reminder. Keep it when the task can already guess what its
  change will make wrong.

Write criteria a different person can evaluate. "Works properly" is not a criterion; "the gate
fails with a non-zero exit on a task missing its H1" is. If you cannot state one, the task is not
yet understood well enough to hand off — that is information, not a formality to skip.

Everything between the H1 and `## Done when` is free-form. Use whatever headings carry the
handoff.

---

## Assigning the next task number (on creation)

Task numbers must be unique across the **entire repo — every branch and every
worktree** — not just the tree you happen to be sitting in. Numbering off a plain
`ls tasks/` in the current worktree is the **#1 collision source**: two parallel
branches each read the same stale max, both grab the same "next" number, and they
clash at merge. This is not hypothetical — it happens whenever work is split across
worktrees (routine wherever parallel sessions each take a branch).

**Always compute the next number with this scan** — it covers committed task files
on every local + remote ref, *plus* working-tree files (including staged/untracked
new ones) in every worktree:

```bash
# If other machines/sessions share task branches via a remote, fetch first so their numbers count:
#   git fetch --all -q
next=$( {
  git for-each-ref --format='%(refname)' refs/heads refs/remotes 2>/dev/null \
    | while read -r ref; do git ls-tree -r --name-only "$ref" -- tasks/ 2>/dev/null; done
  git worktree list --porcelain 2>/dev/null | awk '/^worktree /{print $2}' \
    | while read -r wt; do find "$wt/tasks" -type f -name '*.md' 2>/dev/null; done
} | sed -E 's#.*/##' | grep -oE '^[0-9]{3}' | sort -n | tail -1 )
printf 'next task number: %03d\n' $(( 10#${next:-0} + 1 ))
```

- Run it from anywhere in the repo — it scans **all** worktrees and refs, not the cwd.
- `git ls-tree` reads each ref's committed tree; the `find` over `git worktree list`
  paths catches numbers created-but-not-yet-committed in a sibling worktree.
- Creating several tasks at once? Increment locally from that base; don't re-scan between them.
- Collide anyway (a branch landed after you scanned)? The loser **renumbers via
  `git mv` before merge** — task numbers carry no meaning, so yielding a number is free.
- Never reach into another session's worktree to renumber *its* task; renumber *yours*.

---

## Commit (closes every transition)

Every status move and every new task file is committed in the same session the change happens. Provenance — *why* this task moved, *why* this task exists — lives in conversation context until it's in git history. If the session ends before the commit, that reasoning is lost.

Git is assumed throughout this skill — history is what makes the provenance claim true. A remote is not: a local commit satisfies provenance completely, and a repository tracked only on a filesystem is an ordinary way to use this skill, not a degraded one.

The atomic unit is *"what would I want to revert in one move."*

- **Status moves** (one or two files): commit immediately after the lifecycle ops land. Use the `commit-push` skill.
- **Singleton task creation** (a one-off task drafted with its own rationale, e.g. a single new spec): commit immediately, like a move.
- **Bulk creation** (generating many cross-referencing task files at once): commit per **coherent batch** — one commit per group whose members reference each other and don't independently revert. Per-file commits in this case are ceremony without provenance benefit and drown the signal at bisect time.

`git mv` is preferred for moves *of tracked files*. If the file is untracked (just created this session), a plain `mv` + commit is equivalent — the commit captures the destination path.

### Push, when a remote exists

Sharing and backup are what a remote adds — a bonus, not a dependency. If `git remote` prints anything, push in the same session as the commit, at the same cadence: status moves and singleton creations push immediately after their commit; bulk creation pushes when the batch is internally consistent (every internal cross-reference resolves). If `git remote` prints nothing, the commit is the whole step — there is nothing to push to, and no part of this skill should exit non-zero because of that.

### Projections of `tasks/` are refreshed on demand — not as part of the move

A directory-as-tracker attracts generated views: a board, an index, a status roll-up, a diagram.
Each one goes stale the moment a task is added, moved, or has its frontmatter edited. **That is
accepted.** Do not regenerate a view as part of a status move, and do not treat a stale one as an
incomplete move. Refresh it when someone wants to read it, using whatever command the project
documents.

This obligation used to run the other way — regenerate in the same commit, so the tracker and its
view could never disagree at any commit. That argument was reasoned about one session moving one
task, and it does not survive concurrency. A view is a single file that *every* lane change
rewrites, so where parallel sessions are normal it becomes the most contended file in the tree,
and the conflict it produces is pure ceremony: the file is derived, and nobody has ever needed to
hand-merge two renderings of the same directory. Cheap to run was never the problem — running it
costs a fraction of a second. The cost is the collision, and one merged change can make every
sibling change touching the view pay a re-merge, a regenerate, and a fresh round of automated
checks.

⚠️ **If the project fails a build on a stale view, the two halves are coupled.** A staleness check
that runs on every proposed change will fail every task move once this rule is gone, and the fix is
to hand-run the generator anyway — the same work, now discovered as a failed build instead of
prompted. That combination is worse than either alternative. A project that wants the freshness
guarantee should keep regenerating as part of the move; a project optimising for low churn should
drop the check. Follow whichever the project has chosen; don't add a gate on its behalf.

If the project has no generated view, this is a no-op — don't invent one.

---

## Reverse-dependency sweep (on `→ done` only)

When a task closes, other tasks may have been waiting on it. Find them and update.

```bash
# Replace NNN with the closing task's number prefix, or use the slug
grep -rl "blocked-by:" tasks/ | xargs grep -l "NNN-slug"
```

For each hit:

1. **Update the path — don't delete the entry.** The reference probably points to the old location (e.g. `tasks/wip/NNN-slug.md`). Rewrite it to the new path (`tasks/done/NNN-slug.md`). Deleting the line instead is the tempting shortcut and it is wrong twice over: it destroys the record of *what* this task was waiting on, and it leaves a task in `blocked/` whose `blocked-by:` is empty — blocked by nothing, which nothing will ever surface. Rewrite; never clear.
2. **Check if this was the last blocker.** Read the dependent's `blocked-by:` field. If every entry now points into `done/`, the dependent is no longer blocked and must not be left sitting in `blocked/` (invariant 6) — surface it per step 3.
3. **Surface, don't auto-move.** List the now-unblocked tasks back to the user with a recommendation:
   > Task 005 was blocked only by 016 (just closed). Recommend moving to `prioritized/`. Confirm?
   
   The user decides whether the dependent goes to `prioritized/`, `wip/`, or stays put. Auto-moving risks promoting work the user hasn't re-triaged.

---

## When `blocked-by:` paths drift

Task paths change every time the blocker transitions. Two ways to handle:

- **At sweep time** (preferred): when sweeping for `→ done`, also rewrite stale paths in any matched task.
- **Defensively**: if you notice a `blocked-by:` pointing to a path that doesn't exist, find the file by slug and rewrite.

Don't leave stale paths — they break the dependency graph silently.

---

## Phase-tipping tasks

Some projects keep a document that tracks *what phase the project is in* — requirements locked, architecture decided, first end-to-end slice in production, launch criterion met. If yours does, it is the doc most likely to go quietly stale, because nothing fails when it does.

**On every `→ done` transition, explicitly evaluate whether this closure moves the project across a phase boundary.** Do this every time, as part of the same completion step — not as a separate judgment call you might skip. Most task closures are routine and the answer is no; a phase doc tracks boundaries, not throughput. But the check itself is not optional, because a missed phase tip compounds silently until someone notices the doc is wrong.

If the answer is yes:

- Update the phase doc — status, any "you are here" marker, any summary table.
- **Check for a companion rendered visual** (SVG, diagram, image) alongside it. If one exists, regenerate it in the same pass, not as an optional afterthought. A stale visual next to a freshly-updated source doc is worse than no visual at all: it silently contradicts the doc it summarizes, and nobody re-checks a rendered image against its source once it exists.

If you discover the phase doc (or its visual) is *already* stale from a tip that happened in a prior session — even though the task you're closing right now isn't itself the trigger — fix it now rather than deferring further. Staleness compounds; the moment you notice is the cheapest moment to fix it.

If your project has no such document, this section is a no-op. Don't invent one to satisfy it.

---

## What this skill does NOT do

- **Doesn't decide what to work on.** Prioritization is a judgment call; this skill executes transitions.
- **Doesn't write task content.** "Done when" updates reflect work the user/Claude already did.
- **Doesn't auto-promote unblocked tasks.** It surfaces them; the user triages.
- **Doesn't write the commit message.** It mandates the commit — and the push, where a remote exists (see above) — but defers message authorship to the `commit-push` skill.
