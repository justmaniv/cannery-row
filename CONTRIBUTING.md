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

Use a **git worktree**, not a clone, so switching which branch you are testing is one command:

```bash
git worktree add ~/.claude/skills/cannery-row-dev <your-branch>
claude plugin uninstall cannery-row@cannery-row   # required — see below
# restart your session
claude plugin list                                 # cannery-row@skills-dir · Status: ✔ loaded
```

Edit, restart the session, and the change is live. No version bump, no cache, no install. To test a
different branch, `git -C ~/.claude/skills/cannery-row-dev checkout <other-branch>` and restart.

> ⚠️ **Uninstall the marketplace copy — disabling it is not enough.** An installed plugin holds its
> name whether or not it is enabled, and the installed copy wins. `claude plugin disable` leaves the
> skills-dir copy silently unloaded, and `plugin list` says so explicitly:
>
> ```
> cannery-row-dev@skills-dir: ✘ Not loaded — the name "cannery-row" is already taken by an
> installed plugin (cannery-row@cannery-row), which takes precedence.
> ```
>
> Read that line before trusting a test result. If you skip it, you are editing one copy and running
> another — the failure this whole page exists to prevent, wearing a different hat. (An earlier
> revision of this page recommended `disable`. It does not work; verified.)

**Uninstalling is cheap — do it without ceremony.** It removes a cache directory, not your work. The
canonical copy is this public repository, restoring it is the two commands below, and if a test
build turns out to be bad you are one `plugin install` away from the released one. Nothing here is
worth protecting with a workaround; reach for `uninstall` first rather than trying to run both
copies at once.

Restore the installed copy when you are done:

```bash
git worktree remove ~/.claude/skills/cannery-row-dev   # run this from your main tree, not from inside it
claude plugin marketplace update cannery-row
claude plugin install cannery-row@cannery-row
```

Working permanently from `skills-dir` is a legitimate steady state for a maintainer — it just has to
be a choice rather than an accident.

### Installing from a branch through the real marketplace path

The loop above bypasses the marketplace entirely, which is the point for fast iteration — but it
also means the install machinery goes untested. When you need to exercise that path (a manifest
change, a `source` change, anything about how the plugin is *fetched*), a marketplace source accepts
a `ref`:

- **Local worktree as a marketplace** — `claude plugin marketplace add ~/.claude/skills/cannery-row-dev`
  installs from whatever branch that worktree has checked out, through the real fetch path.
  ⚠️ The marketplace `name` is `cannery-row` either way, and adding a second marketplace with the
  same name **replaces** the first — so you will need to re-add the GitHub one afterwards.
- **A published branch** — marketplace sources support `ref` (branch or tag), and plugin sources
  support `ref` and `sha`. There is no CLI flag for it, so it goes in `extraKnownMarketplaces` in
  settings rather than on the `marketplace add` command line.

For ordinary skill edits, neither is worth the ceremony. Use the worktree loop.

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
