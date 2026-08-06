# Cannery Row

**Task state that lives in your repo, as files, where the location is the status.**

```
tasks/
├── new/          # captured, not yet triaged
├── prioritized/  # triaged and ordered; pull from the top
├── wip/          # actively in progress
├── blocked/      # waiting on something
└── done/         # completed
```

Moving a task to `wip/` is `git mv`. That's the whole idea. Everything else here — a skill that
governs the moves, a generated board, a portability gate — exists to make that one idea hold up
under real use.

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

Ask Claude to create a task and it will use the skill. Copy `tasks/README.md` from this repo into
yours if you want the conventions written down for humans too.

## What it's for

Agent-driven, spec-driven development. The task file **is** the spec, and it is a handoff between
sessions that share no context.

1. **One session writes the task.** Not a to-do line — a spec. Why this work exists, what is
   verifiably true in the code *today*, the design fork with its trade-offs and a recommendation,
   and a "Done when" list somebody else can check without asking you what you meant.
2. **Time passes.** Days. Other people's merges. The session that wrote it is gone; its context
   window ended and took every unwritten assumption with it.
3. **A different session picks it up, validates it, then executes it.** Validation first: does the
   spec still describe reality? The skill makes this a required step rather than a nice idea,
   because a task file is a claim about the past.

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
| `skills/task-lifecycle/SKILL.md` | The operational procedure — transitions, frontmatter invariants, the reverse `blocked-by` sweep, collision-safe numbering across worktrees, and a staleness check before starting an old task. This is the substance. |
| `tasks/README.md` | The human-readable conventions. Copy it into your repo. |
| `scripts/generate-task-board.py` | Generates `docs/task-board.md` — lanes in flow order, the blocker graph as Mermaid, a WIP-limit check. Pure projection; the files stay the source of truth. `--check` for CI. |
| `scripts/check-portability.py` | Fails if any shipped file names a language, vendor, or planning cadence. See below. |

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
