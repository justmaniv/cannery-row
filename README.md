# Cannery Row

**One session writes the work. A different session does it. Every time, on purpose.**

The first session thinks the problem through and leaves a file: why the work exists, what's true in
the code today, and criteria someone else can check. The second session opens that file holding
nothing else, confirms it still matches the code, and executes.

Splitting those is the point. A session that reasons its way to a plan spends an hour on dead
ends, wrong turns, and decisions it reversed twice — and none of that reaches the session doing the
work, which starts with a clean window and one task in it. The session that didn't write the spec is
the only one that can catch what the spec got wrong — though that independence is *available*, not
automatic, and [it has a failure mode worth setting up against](#what-validating-the-spec-does-not-cover).
Surviving a restart is a side effect — a real one, but not the reason.

Task state as files, where the location is the status:

```
tasks/
├── new/          # captured, not yet triaged
├── prioritized/  # triaged and ordered; pull from the top
├── wip/          # actively in progress
├── blocked/      # waiting on something
└── done/         # completed
```

Moving a task to `wip/` is `git mv`. That's the whole idea. Everything else here — a skill that
governs the moves, a generated board, gates that fail loudly — exists to make that one idea hold
up under real use.

A Claude Code plugin. Nothing to run, nothing to host, no database.

## It's opinionated, and it's active

Worth knowing before you install it, because it changes how the first hour feels: this is a set of
opinions about how work gets handed off, not a neutral file convention. Once the skill is in play it
*does things* — moves files, rewrites other tasks' `blocked-by:` paths when a blocker closes,
refuses to close a task whose criteria didn't all come true, and stops to tell you when an invariant
can't hold. That activity is the product. A tracker that only stores state is a directory, and you
already have one of those.

The opinions, stated plainly so you can disagree with them on purpose:

- **Acceptance criteria are mandatory.** A task with no `## Done when` closes on nobody's authority
  but the closer's — so the board generator refuses to build from one, in every lane. First in this
  list on purpose: it is where most of the value is, and it is not what people come here for. The
  lanes are what gets noticed; the checklist is what stops a task being declared finished by whoever
  happens to be holding it.
- **Two is better than one.** The session that writes the spec should not be the session that
  executes it. Everything at the top of this page.
- **Validating a spec is not reviewing it.** The executing session checks the task's claims before
  it starts, which catches work that already shipped and premises that were false when written. It
  is not an independent audit — by the time it runs, the checker has read the task and inherited its
  framing. Set something up that hasn't; [see below](#what-validating-the-spec-does-not-cover).
- **The directory is the status.** No `status` field that can disagree with where the file actually
  is, and the journey lands in `git log` instead of being overwritten in place.
- **Unresolved beats tidy.** A criterion that didn't come true is struck with a reason, never
  ticked. A closed blocker's reference is rewritten, never deleted. Both shortcuts destroy the
  record to make the file look finished.
- **Surfacing beats auto-promoting.** When the last blocker closes, the skill tells you and waits.
  Re-triage is a judgment call and it isn't the tool's.
- **A host is a bonus, not a dependency.** The tracker is a directory tree, so the lanes and the
  board work on a filesystem alone. Git adds the history — per-task `git log`, and status changes
  that land as moves instead of edits in place. A shared remote adds backup and collaboration, and
  starts paying once a second person or machine is involved. Take as many of those layers as your
  project actually has; plenty of real use is local-only.

## Install

```
/plugin marketplace add justmaniv/cannery-row
/plugin install cannery-row@cannery-row
```

Then, in a repo you want tracked:

```bash
mkdir -p tasks/{new,prioritized,wip,blocked,done}
```

That's enough — ask Claude to create a task and it will use the skill.

**The plugin ships the skill; it does not put files in your repo.** Two things live in *this*
repository rather than in the plugin, and you fetch them if you want them:

```bash
# The conventions, written down for humans as well as for Claude.
curl -o tasks/README.md \
  https://raw.githubusercontent.com/justmaniv/cannery-row/main/tasks/README.md

# The board — and the gate.
mkdir -p scripts && curl -o scripts/generate-task-board.py \
  https://raw.githubusercontent.com/justmaniv/cannery-row/main/scripts/generate-task-board.py
python3 scripts/generate-task-board.py     # writes docs/task-board.md
```

The second one is worth doing. **That script is also the structural gate** — it is what refuses a
task with no H1 or no `## Done when`, described below. Without it those stay conventions that
Claude follows; with it they are checked every time you run it. No dependencies beyond Python 3.

**The board is refreshed by hand, on demand — deliberately.** The skill does *not* regenerate it as
part of a status move, and a stale board is not an unfinished move. It is one file that every lane
change rewrites, so in a repo with several people or sessions working in parallel it becomes the
most contended file in the tree, and each of those conflicts is ceremony: the file is derived, and
nobody needs to hand-merge two renderings of the same directory. In the project this was extracted
from, the board changed in 204 of 894 commits over 30 days. Regenerating costs a fraction of a
second — the cost was never compute, it is the collisions, and they land on whoever merges second.

**`--check` in CI is a real trade, and both answers are defensible:**

| | |
|---|---|
| **Run `--check`** | The board can never be stale on a merged change, and the structural gate fires on every proposed change. The price is that every task move has to regenerate the board — the churn above. Take this if you want the freshness guarantee. |
| **Don't run it** | The board drifts between refreshes and someone regenerates when it matters. The structural gate then fires only when the generator runs. Take this if low churn is what you're optimising for. |

⚠️ **One combination is strictly worse than either: `--check` in CI *without* regenerating on every
move.** A staleness check fails on a stale board, and a task move makes the board stale — so every
task-move change goes red, and the fix is to hand-run the generator anyway. Same work, discovered as
a failed build instead of prompted. Pick a row; the failure is landing between them.

### The layer the plugin can't ship: a second reader at pickup

The layers so far each catch one thing and are blind to the next. The lanes catch *where the work
is*. The skill catches *the transition going wrong* — a dropped criterion, a dependent left pointing
at a moved file. The gate catches *a task with no acceptance criteria*. None of them can tell you the
task's reasoning was **invented**, because a fabricated mechanism is well-formed, in the right lane,
and has a checklist.

That one needs a reader, and it is the only layer here that is a paste rather than an install. Put
it in your project instructions — `CLAUDE.md`, or whatever your host reads at session start:

````markdown
## Picking up a task you did not write

Run the skill's claim-validation step first. Then, before any work starts — and again before commit
when the deliverable is itself a spec other sessions will execute — hand the task to a subagent in a
fresh context with this instruction:

> At least one claim in this task file is wrong. For each load-bearing claim, open the code it
> refers to and try to prove it false. A cited file or test *existing* is not the claim — the claim
> is **how** it works, and that is the part that gets invented. Report every claim you could not
> confirm from the code, quoting what you read. You have not seen the reasoning that produced this
> task; you do not need it.

Correct the task file — and any sibling task that inherited the claim — before proceeding, with a
dated note saying what was wrong.
````

**The property that makes it work is the fresh context, not the seniority of the reader.** It reads
the claims and the code and none of the conversation that found them convincing. A subagent, a
second session, or a colleague all qualify; the session that just spent four minutes validating the
task does not, which is the whole point.

It costs one subagent run. Spend it where the task's output is a spec others get held to; skip it on
a task that changes one function and gets reviewed as a diff anyway.

## What a task looks like

One file — `tasks/new/007-short-kebab-slug.md`. The directory is the status, so there is no
`status` to change by hand and no `title:` field to disagree with the heading.

```markdown
---
created: 2026-08-07
updated: 2026-08-07
completed:
status: new
owner: your-name
blocked-by: ""
---

# The generated board carried two links back to the repo it came from

## What's wrong

What is verifiably true in the code *today* — paths, commands someone else can re-run without
asking you what you meant. Free-form; use whatever headings carry the handoff.

## Done when

- [ ] The board regenerates with no links to the upstream repo
- [ ] A test fails if they come back
- [ ] Every document and open task this change makes wrong is updated, and anything the work
      turned up that nothing yet records is written down — or what was checked is named here,
      with why none of it needed changing
```

That third line is in the template by default. It is the one nobody thinks to write, and only the
session doing the work can answer it — a closure leaves behind both a document that now says
something false and a thing the closer learned that no document says at all. It is worded so it
can't be ticked in silence: *"or what was checked is named here"* means a closer who names nothing
has visibly not resolved it. `- [ ] Docs updated` would be worse than no line — tickable without
opening a file, and green forever. **Nothing gates it**, deliberately; the skill enforces the
obligation at close, where the answer exists.

**`## Done when` is the acceptance criteria, and it is the load-bearing part.** It is the only
thing a later session is held to, and completing a task is *defined* as resolving every box —
`- [x]` if met, `- ~~struck through~~ (reason)` if deliberately skipped. Write criteria a
different person can evaluate: *"works properly"* isn't one, *"the gate exits non-zero on a task
missing its H1"* is.

**It is also the cheapest part of a task to review — and the gap between the two passes is where you
can do it.** Read the boxes when the spec lands, before execution starts. If they describe the wrong
work, finding that out costs you the time it takes to read a checklist instead of the time it takes
to read a diff. Approving criteria takes seconds; a page of reasoning takes minutes; the finished
work takes longer than both.

Nothing prompts you for that review and skipping it is fine — the criteria still do their job, just
later, as what the executing session gets held to at close. Either way they get checked. The only
question is whether the check lands before the work or after it, and one pass gives you no seam to
put it in.

The H1 and the checklist are **required in every lane**, and the board generator fails loudly
without them — naming the file and the fix, writing no board. Both used to be silent: a missing
H1 rendered a blank card and exited 0, and a missing checklist made the completion gate vacuous,
since "resolve every `- [ ]`" is trivially satisfied when there are none. A tracker that accepts a
task with no acceptance criteria isn't enforcing the one thing it exists to enforce.

## What it's for

Agent-driven, spec-driven development. The task file **is** the spec — and the beat people skip is
the third one, where a different session *validates* the spec before executing it. Validation
first: does this still describe reality? The skill puts the question in front of you and gives you
the commands; it can't make you run them. Nothing enforces it, and nothing can.

**A worked example, from the project this was extracted from** — not this repo, which has no
database of its own; see [Provenance](#provenance). A session wrote a well-formed task: scope
boundaries against two neighbouring pieces of work, a three-option design fork with effort
estimates and a recommendation, thresholds sourced to their owning documents. Its premise was that
a database table had never been populated. The session that picked it up checked before starting
and found seven migrations already seeding that table — the convention the task said had never
happened had worked for a year. The original grep had searched the wrong directory.

Nothing was wrong with the task as *writing*. It was wrong as a *claim*, and every automated check
in the world would have passed it. Caught in about four minutes, before a line of code was written,
because validating the spec is the executing session's first job and not an optional courtesy.

That is the loop this exists to support. Files in the repo are what make it possible: the handoff
has to carry everything, because there is nobody left to ask. A conversation log can't be pulled up
in a new session. A shared list can't hold a page of reasoning per item. Notes kept outside the
repository drift away from the code they describe. A file next to the code, in the same commit
history, does not.

### What validating the spec does not cover

The question that step asks is *"is this claim true?"*, and it is answered by a reader who has just
finished reading the task. That is enough for the two failures it was built for — work that already
shipped under a different number, and a premise that was false the day it was written. It is not an
independent audit, and passing it is not evidence that the task's description of *how* something
works is true.

**A citation checking out is weak evidence.** The task names a test; the test is there, at that path,
asserting that thing. But the load-bearing claim is rarely *"this test exists"* — it is *"this test
does X by doing Y"*, and Y is the part that gets invented. From the same project as the example
above: a task claimed a backend test injected a request header. Everything cited was real. No test
set any header — the fixture seeded a database column with a raw `INSERT`. Pickup validation passed
it in four minutes, because everything it went looking for was found. A second reader in a fresh
context, told to assume the task was wrong somewhere and go find it, falsified four of its claims
including that one.

Two things help, and neither of them is a feature:

- **Ask to falsify, not to confirm.** *"Try to prove this claim wrong"* reads different code than
  *"check this claim"* — it sends you to the fixture instead of to the assertion. Do this one first;
  it costs a rephrasing.
- **Escalate when the task's output is itself a spec.** Working agreements, decision records, and
  criteria other sessions will execute. A false mechanism in a task body flows into that task's own
  `## Done when` and into its siblings', and once it reaches the acceptance criteria it is
  self-enforcing: a later session executes the wrong instruction and the checklist confirms it did.
  In the case above it had already reached three sibling tasks, one as a criterion prescribing a
  change to a header that does not exist.

**So this project has an opinion about your setup and not only about its own: put a second reader at
pickup, one that was not in the conversation that accepted the task.** The rule is written out and
ready to paste in [Install](#the-layer-the-plugin-cant-ship-a-second-reader-at-pickup) — the plugin
deliberately ships no review mechanism, but it can hand you the paragraph. The four-minute check at
pickup is worth having and is not a substitute for it.

### The spec is the main shape, not the only one

Specs are what a task file is *best* at. They are not all it is used for. Four shapes seen in real
use — the list is open, and the point of writing it down is that you will find others:

| Shape | What the file is | Why a file and not something else |
|---|---|---|
| **Spec / handoff** | The loop above. Written to be executed later by someone with none of your context. | It has to survive the session that wrote it. |
| **Blocking gate** | A task whose only job is to hold other work until a human rules — an architecture decision to sign off, a design to approve. It carries *no* execution by design. | The dependency is visible on the board instead of living in someone's head, and `blocked/` is an honest answer to "why hasn't this moved?" |
| **Post-mortem / decision record** | Written *after* the work, to record what broke and why the fix is shaped the way it is. Spec-driven in reverse. | It lands next to the commit that caused it, and `git log` on one file reads as a narrative. |
| **The plan itself** | No single file — the `blocked-by:` graph *between* them. Sequencing is the edges, not the nodes. | A plan expressed as edges stays correct when one task changes; a plan written as a document goes stale on the first surprise. |

A blocking gate is worth calling out because it is the least obvious. A task that deliberately does
no work, exists only to stop other work, and closes when a person says "fine" sounds like overhead —
until you have three sessions running and no other way to express "not until they've looked at it."

## Why this instead of the alternatives

The ecosystem's nearest neighbours are good, and they solve different problems:

| | Where task state lives | What it optimizes |
|---|---|---|
| [`obra/superpowers`](https://github.com/obra/superpowers) | in-conversation | agent discipline — brainstorm → spec → test-first |
| BMAD | planning artifacts | requirements → architecture → work breakdown |
| Anthropic's `productivity` plugin | one markdown list plus memory, outside the repo | knowledge work — email, calendar, chat capture |
| **Cannery Row** | **one file per task, inside the repo, in git** | **two-pass execution — write it in one session, execute it cold in another** |

Several of these have phases: brainstorm, then spec, then build. The difference is where the phase
boundary falls. Theirs are steps *inside* one context, so the window that wrote the spec is the
window that executes it — no clean context, no independent read. Cannery Row puts the boundary
between sessions, and a boundary between sessions needs per-task state in the repository to cross.
That's the gap, and durability is what makes it crossable rather than being the point itself.

Concretely, four things follow from one-file-per-task:

- **Parallel sessions don't collide.** Two agents working two tasks touch two files. A single shared
  task list is a conflict magnet under exactly the parallel-agent load that makes it worth having —
  in the codebase this came from, a blanket `git add -A` once swept a sibling session's work into an
  unrelated commit. One file per task removes the shared write.
- **Status is a `git mv`,** so the journey is in history rather than overwritten in place. You get
  per-task `git log`, not "a line changed in a big file three weeks ago."
- **Loading one task costs one task.** The agent reads the file it needs, not the whole queue.
- **It outlives the conversation.** Context windows end. `tasks/wip/` doesn't.

The cost, stated plainly: it's files, so it's as good as your discipline about moving them. That's
what the skill is for.

## What's in the box

| | |
|---|---|
| `skills/task-lifecycle/SKILL.md` | The operational procedure — transitions, frontmatter invariants, the reverse `blocked-by` sweep, collision-safe numbering across worktrees, a claim-validation step before starting a task you didn't write, and a propagation gate at close that names the documents and open tasks the work made wrong — and routes them, rather than obliging you to fix every one. This is the substance. |
| `tasks/README.md` | The human-readable conventions. Copy it into your repo. |
| `scripts/generate-task-board.py` | Generates `docs/task-board.md` — lanes in flow order, the blocker graph as Mermaid, a WIP-limit check. Pure projection; the files stay the source of truth. `--check` for CI. Also the structural gate: it refuses to build a board from a task missing its H1 or its `## Done when`. |
| `scripts/check-portability.py` | Fails if any shipped file names a language, vendor, or planning cadence. See below. |
| `evals/` | Scored behavioral cases. Everything else here checks the skill is well-*formed*; these check it is *followed*. See below. |

Deliberately **not** shipped: sprint-ceremony templates from the upstream project. They were written
against a specific planning methodology and its generators, and porting them would smuggle that
methodology in through the side door. Each of the four was checked individually; all four stay.

## The portability gate

`check-portability.py` greps every shipped file for stack and methodology vocabulary — language
names, vendors, hosts, cadence words — and fails with a suggested neutral phrasing.

It exists because the failure it prevents already happened. Two days after a clean manual
portability audit, a new section was added to the skill that was *written* to be generic, *reads* as
generic, and still carried four occurrences of a cadence word. Nobody catches that by eye. Every
change to this repo runs the grep.

```bash
python3 scripts/check-portability.py          # what CI runs
python3 scripts/check-portability.py --list   # the vocabulary and why each term is out
```

False positives are the point. If a term is genuinely needed, the argument for it should be made
out loud rather than assumed.

## Does the skill actually change anything?

Fair question to ask of any prompt-shaped artifact, and `evals/` answers it with a number rather
than a claim. Each case scaffolds a throwaway repo mid-flight, gives Claude a realistic instruction
— *"Rate limiting is in. Wrap up task 012."* — and grades the state it leaves behind. Then it runs
the same case again with the plugin switched off.

That second arm is the whole point. Most of what a good skill asks for, a capable model does anyway,
and a suite that does not control for it is measuring the model.

| Case | Without the skill | With it |
|------|------------------|---------|
| Close a task whose dependents are waiting on it | **0.55** | **1.00** |
| Close a task whose criteria didn't all come true | **0.81** | **1.00** |

The gap is where the skill lives. Nobody infers *"go rewrite the `blocked-by:` paths in other
files"* from "wrap up task 012" — so in all three baseline runs the dependents were left pointing
at a path that no longer exists, which is exactly the silent rot the sweep exists to prevent. The
second case scores much closer, because striking a dropped criterion instead of ticking it is
ordinary good judgment and needs no teaching; what the baseline actually missed there was smaller
and duller — it left a criterion unresolved and never committed the move.

Writing the first two cases immediately found a contradiction in the skill — invariant 6 said a
closed blocker's reference could be *cleared*, the sweep procedure said *rewrite it* — and Claude
followed the wrong half, leaving a task in `blocked/` with an empty `blocked-by:`. Blocked by
nothing, and nothing would ever surface it again. That is the argument for evals in one paragraph:
both halves were shipped text, both read fine, and no amount of proofreading was going to catch it.

**What these numbers do not cover** — an honest note on **two is better than one**, the opinion
above most worth arguing with: it is an argument plus one worked example, not a measured result.
The evals score whether the skill is *followed*; nothing here measures two passes against one, and
proving it properly would cost more in run hours than the answer is worth. It's held on conviction
and about 380 tasks of use, and labelled that way rather than dressed up as data.
[`evals/README.md`](evals/README.md) records the decision not to chase it.

Running the suite takes twelve minutes, is not free, and needs Claude credentials, and so is deliberately
**not** in CI — this repo holds no secrets, which is the best security property a public repo can
have, and it is not worth trading for a check any contributor can run locally.
[`CONTRIBUTING.md`](CONTRIBUTING.md) has the command; [`evals/README.md`](evals/README.md) has the
design rules.

## Known limits

One rough edge, disclosed rather than discovered: if your repository *has* a remote, the skill
pushes on every lane move, and there is currently no way to say you'd rather it didn't. For some
projects that cadence is the point; for others it's chatty. A local-only repository is unaffected —
the commit is the whole step there, by design. Tracked in
[`tasks/blocked/019-user-cannot-opt-out-of-remote-operations.md`](tasks/blocked/019-user-cannot-opt-out-of-remote-operations.md).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). The short version: clone this repo into your skills
directory and it loads in place, so your working tree is what runs — no install, no cache, no
version bump while you iterate. Releasing is the separate loop, and it does need a bump.

## Provenance

Extracted from building [the kist](https://thekist.app) — a home-inventory app whose repo has run
this system for ~380 tasks across 15 months and many concurrent agent sessions. Everything here was
load-bearing before it was published; none of it was designed for an audience.

The name is Steinbeck's. Cannery Row is a working row of processing stations, each doing its own
stage, populated by people operating in parallel with their own agendas and somehow not wrecking
each other. That is the lane model, and it is the parallel-session story. "Cannery" also means
preservation, which is what git does with the history.

## License

Apache-2.0. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).

Apache rather than MIT for two reasons that matter once contributions arrive: §3's patent grant and
retaliation clause, and §5 making inbound contributions automatically inbound-equals-outbound, so
there is no CLA to sign.
