---
created: 2026-08-12
updated: 2026-08-12
completed:
status: new
owner: justmaniv
blocked-by: ""
links:
  - CLAUDE.md
  - README.md
  - tasks/done/032-same-commit-regeneration-rule-is-too-chatty.md
  - tasks/done/024-validation-is-not-independent-review.md
  - tasks/done/026-the-second-reader-is-advice-not-a-rule.md
---

# The mandated second reader runs with write access it does not need, and it corrupted a working tree

## What happened, because this is an incident report and not a hypothetical

`CLAUDE.md` § *"Picking up a task you did not write"* mandates handing the task to a subagent in a
fresh context. It specifies the **prompt** in full and says nothing about the subagent's **tools**.
Both readings of that silence are available, and the default one — a general-purpose agent with the
full tool set — is what task 032 used, twice, against the live working tree.

Two failures followed, on 2026-08-12:

1. **The first reader ran `git checkout` onto an unrelated branch and left it there.** Confirmed in
   the reflog: `checkout: moving from task/032-on-demand-board-regeneration to
   task-027-prior-coverage-sweep`. The parent session was mid-edit. Uncommitted changes rode along
   to a branch whose `tasks/` tree did not contain the task being worked on.
2. **Edits to `tasks/README.md` were silently reverted.** Two applied edits were gone from the
   working tree with no error and no `Edit` failure. The second reader reported the file as
   unmodified — while `CHANGELOG.md`, already written, asserted the correction had been made to
   that exact file. In the one file adopters copy into their own repositories.

The second failure was caught only by luck of ordering: the second validation pass happened to
grep for surviving statements of the deleted rule and found the live one. Nothing else would have.
No gate covers it — `check-release.py` *passed because* the file was unmodified.

**The eval harness was ruled out.** A monitor watching `git diff --quiet HEAD` across a full 913s
`plugin eval` run never fired. The mutation window belongs to the subagents.

## Why the tool grant is the wrong shape

The reader's job is stated in `CLAUDE.md` in one sentence: *open the code it refers to and try to
prove it false*. That is a read. Write access, `git` state access, and `Bash` buy the task nothing
and cost the parent session a silently corrupted tree — which is the worst available failure shape,
because the parent believes its own edits landed and keeps building on that belief.

`Explore` exists and is read-only. So the fix is a tool selection, not a new mechanism.

## The part that reaches further than this repo

`README.md` § *"The layer the plugin can't ship: a second reader at pickup"* ships this instruction
as a **paste block** for adopters to put in their own project instructions. It carries the same
silence about tools. Whatever this task decides, the paste block is where it has to land, or the
fix stays local to a repo that already knows.

⚠️ Do not widen this into re-litigating whether the second reader should exist. 024 and 026 settled
that. This is about what it is handed, not whether it runs.

## Two things to decide, not to discover

- **Is a read-only reader actually sufficient?** It is worth checking rather than assuming. The
  falsification prompt tells the reader to *"open the code"* — reads. But a reader that wants to
  run a test to disprove a claim about behavior needs execution. If that capability matters, the
  answer is "read-only plus a way to run the suite", not plain `Explore`, and the paste block
  should say which.
- **Whether to state a verification step regardless.** Even a correctly-scoped reader leaves the
  parent unable to tell whether its own edits survived. A one-line "confirm `git status` still
  shows the files you edited" costs nothing and catches the class, including causes nobody has
  identified yet — the `tasks/README.md` reversion still has no proven mechanism.

## Done when

- [ ] `CLAUDE.md` § *"Picking up a task you did not write"* states what the fresh-context reader is
      handed, not only what it is told — and the stated grant is sufficient for falsification work
      without carrying write or git-state access.
- [ ] `README.md`'s adopter paste block carries the same correction, since that is the copy that
      reaches other projects.
- [ ] The decision records *why* read-only is the grant, in one line a reader can disagree with —
      not merely that it is. A future session must be able to tell this was chosen.
- [ ] Whether an execution capability is needed for falsification is answered explicitly, either
      way, rather than left to the next session's default.
- [ ] Every document and open task this change makes wrong is updated, and anything the work
      turned up that nothing yet records is written down — or what was checked is named here,
      with why none of it needed changing
