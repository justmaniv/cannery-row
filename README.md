# Cannery Row

**Your agent's work survives the session that wrote it.**

One session writes a task as a spec. Days pass; that context window ends and takes every unwritten
assumption with it. A *different* session picks the task up, checks the spec still describes
reality, and executes it — because the handoff is a file in your repo, not a conversation nobody
can reopen.

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
Claude follows; with it they are checked, and `--check` in CI makes them enforced. No dependencies
beyond Python 3.

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
```

**`## Done when` is the acceptance criteria, and it is the load-bearing part.** It is the only
thing a later session is held to, and completing a task is *defined* as resolving every box —
`- [x]` if met, `- ~~struck through~~ (reason)` if deliberately skipped. Write criteria a
different person can evaluate: *"works properly"* isn't one, *"the gate exits non-zero on a task
missing its H1"* is.

The H1 and the checklist are **required in every lane**, and the board generator fails loudly
without them — naming the file and the fix, writing no board. Both used to be silent: a missing
H1 rendered a blank card and exited 0, and a missing checklist made the completion gate vacuous,
since "resolve every `- [ ]`" is trivially satisfied when there are none. A tracker that accepts a
task with no acceptance criteria isn't enforcing the one thing it exists to enforce.

## What it's for

Agent-driven, spec-driven development. The task file **is** the spec, and only one of the three
beats is about writing it:

1. **One session writes the task as a spec** — why the work exists, what is verifiably true in the
   code *today*, the design fork with its trade-offs and a recommendation, and criteria somebody
   else can check without asking what you meant.
2. **Time passes.** Days, and other people's merges.
3. **A different session picks it up, validates it, then executes it.** Validation first: does the
   spec still describe reality? The skill puts this in front of you and gives you the commands; it
   can't make you run them. Nothing enforces it, and nothing can. Avoiding context rot is the
   operator's job — the tool's job is to make sure the question gets asked.

Beat 3 is the one people skip, and it is the one that makes the other two safe.

**A worked example, from this project's own use.** A session wrote a well-formed task: scope
boundaries against two neighbouring pieces of work, a three-option design fork with effort
estimates and a recommendation, thresholds sourced to their owning documents. Its premise was that
a database table had never been populated. The session that picked it up checked before starting
and found seven migrations already seeding that table — the convention the task said had never
happened had worked for a year. The original grep had searched the wrong directory.

Nothing was wrong with the task as *writing*. It was wrong as a *claim*, and every automated check
in the world would have passed it. Caught in about four minutes, before a line of code was written,
because validating the spec is beat 3 and not an optional courtesy.

That is the loop this exists to support. Files in the repo are what make it possible: the handoff
has to carry everything, because there is nobody left to ask. A conversation log can't be pulled up
in a new session. A shared list can't hold a page of reasoning per item. Notes kept outside the
repository drift away from the code they describe. A file next to the code, in the same commit
history, does not.

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
| **Cannery Row** | **one file per task, inside the repo, in git** | **durable state that survives the session** |

None of the others put durable, per-task, versioned state *inside the repository it describes*.
That's the gap this fills, and it's the only claim it makes.

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
| `skills/task-lifecycle/SKILL.md` | The operational procedure — transitions, frontmatter invariants, the reverse `blocked-by` sweep, collision-safe numbering across worktrees, and a claim-validation step before starting a task you didn't write. This is the substance. |
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
| Close a task whose dependents are waiting on it | **0.50** | **1.00** |
| Close a task whose criteria didn't all come true | **0.88** | **1.00** |

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

Running the suite costs about $5 and twelve minutes, needs Claude credentials, and so is deliberately
**not** in CI — this repo holds no secrets, which is the best security property a public repo can
have, and it is not worth trading for a check any contributor can run locally.
[`CONTRIBUTING.md`](CONTRIBUTING.md) has the command; [`evals/README.md`](evals/README.md) has the
design rules.

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
