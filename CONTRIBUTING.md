# Contributing

## The problem this page solves

The skill is a plugin. A plugin you have installed runs from a **copy in the plugin cache**, not
from your checkout — so editing a clone changes nothing about the session you are editing in. You
would be testing the old copy while believing you were testing the new one.

Worse, the release path is pinned: `version` in `.claude-plugin/plugin.json` is what tells an
installed copy to update. Merging a fix without bumping it leaves every consumer on the old build
while `plugin update` reports *"already at the latest version."* That happened here — see
`tasks/done/003-pinned-version-silently-withheld-the-fix.md` — and CI now fails a shipped change
with no bump.

So there are two loops, and they are different: a **development** loop that runs your working tree
directly, and a **release** loop that moves a version.

## Development loop — run your edits, don't install them

A directory under a skills directory that contains `.claude-plugin/plugin.json` is loaded **in
place**, as `<name>@skills-dir`, with no marketplace and no install step. That is the whole trick:
clone the repo *into* your skills directory and your working tree is what runs.

```bash
git clone https://github.com/justmaniv/cannery-row ~/.claude/skills/cannery-row
claude plugin disable cannery-row@cannery-row    # see the warning below
# restart your session — it now loads as cannery-row@skills-dir, from your checkout
```

Edit, restart the session, and the change is live. No version bump, no cache, no install.

> ⚠️ **Disable the installed copy while developing.** Otherwise the marketplace install and the
> skills-dir checkout are both active and you have two copies of the same skill in one session —
> the exact duplication this project exists to argue against, reintroduced in your own environment.
> The symptom is subtle: you cannot tell which copy answered.

Re-enable it when you are done (`claude plugin enable cannery-row@cannery-row`), or keep working
from `skills-dir` permanently if you are a maintainer — that is a legitimate steady state, it just
has to be a choice rather than an accident.

## Testing before you commit

**Structure** is covered by CI, and all four gates run locally in about a second:

```bash
python3 scripts/check-portability.py          # no stack or methodology vocabulary in shipped files
python3 scripts/check-workflows.py            # GitHub-hosted runners only, no pull_request_target
python3 scripts/check-release.py              # manifests agree; version moved if shipped content did
python3 scripts/generate_task_board_test.py   # 51 unit tests
python3 scripts/generate-task-board.py --check
claude plugin validate . --strict             # manifests load; a broken one breaks install for everyone
```

**Behavior** — whether the skill actually makes Claude do the right thing — is not covered yet.
`claude plugin eval` runs scored cases against a plugin with a no-plugin baseline arm, so it can
measure whether the skill changed the outcome rather than just whether it loaded. Authoring that
suite is `tasks/new/004-author-eval-suite-for-the-skill.md`; until it exists, behavior is verified
by using the skill on this repo's own `tasks/` and reading what happened.

That gap is worth naming plainly: every automated check here proves the skill is *well-formed and
portable*. None of them proves it is *followed*.

## Release loop

1. PR the change. CI runs the gates above.
2. **Bump `version` in both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.**
   They must match — `plugin.json` wins at load time, so a stale marketplace entry is invisible
   until someone reads both files. `check-release.py` fails the build on either mistake.
   README-only and docs-only changes are exempt and need no bump.
3. Merge.
4. Consumers pick it up with:

   ```bash
   claude plugin marketplace update cannery-row
   claude plugin update cannery-row@cannery-row
   # restart the session to apply
   ```

   Both commands are needed. `plugin update` alone consults a marketplace cache that may still be
   pointing at the previous commit.

## What ships, and what does not

Only `skills/`, `scripts/`, `tasks/README.md`, and `.claude-plugin/` reach an installed copy. This
file, the README, and this repo's own `tasks/` are repository content — they inform, they do not
install. `check-release.py` uses exactly that boundary to decide whether a change needs a version
bump.
