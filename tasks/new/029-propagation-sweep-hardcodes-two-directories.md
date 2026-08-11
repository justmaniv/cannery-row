---
created: 2026-08-11
updated: 2026-08-11
completed:
status: new
owner: justmaniv
blocked-by: ""
links:
  - skills/task-lifecycle/SKILL.md
  - tasks/done/020-task-template-has-no-docs-criterion.md
  - tasks/new/022-task-root-is-hardcoded-to-repo-root.md
  - tasks/blocked/019-user-cannot-opt-out-of-remote-operations.md
---

# The searches the skill hands out look in two named directories, and one of them may not exist

## The gap

Two of the skill's three mandatory searches are written against a layout the skill is not allowed
to assume. Both were verified by reading `SKILL.md` at v0.6.0 on 2026-08-11.

**1. The propagation gate's bound (`SKILL.md:100-104`)** — shipped in v0.6.0 as source 1 of three:

```bash
grep -rl "NNN-slug" tasks/ docs/
```

`docs/` is a house-layout guess. In a project that keeps prose anywhere else the search reads only
`tasks/`, which is the half the reverse-dependency sweep already covers — so the new gate silently
degrades to the step it was written to be different from. Worse, in a project with no `docs/` at
all the command *fails*: verified in a scratch tree with `tasks/` and no `docs/`, it printed
`No such file or directory` and exited **2** — and it exits 2 *even when `tasks/` matched*, so the
failure is not confined to the no-hit case. The prior-coverage search three sections down carries
`2>/dev/null` for exactly this reason (`:257`); the propagation bound does not.

**2. The prior-coverage search (`SKILL.md:257-258`)** — two commands, and the second one has never
worked:

```bash
grep -ril "TOPIC" tasks/ docs/decisions/ docs/working-agreement/ 2>/dev/null
grep -ril "TOPIC" -- '*README*' 'ci/**' 2>/dev/null   # topic's runbook/README home, if any
```

On the first line, `docs/decisions/` and `docs/working-agreement/` are one upstream project's
directory names. They are not forbidden vocabulary and `check-portability.py` cannot see them — the
gate matches terms, not paths — so this is house layout that reached a portable file through the one
door the gate does not watch. Here the `2>/dev/null` keeps it from failing, which is worse than
failing: an adopter with neither directory gets a clean exit and no hits, and "nothing found" is the
expensive outcome the same section warns about in its closing line.

⚠️ **The second line is not merely unportable — it is dead.** `'*README*'` and `'ci/**'` are
`git grep` pathspecs pasted into plain `grep`. They are quoted, so the shell never expands them and
`grep` receives them as literal filenames that do not exist. Verified 2026-08-11: run in a directory
containing a matching `README.md`, it prints `grep: *README*: No such file or directory` and exits
**2** with no hits. It has been silenced by its own `2>/dev/null` since it was written, so one of
the skill's two mandatory prior-coverage searches has been returning nothing, indistinguishably from
finding nothing.

## Why the whole-repo search is the fix, not a declared list of directories

The obvious repair is to let each project declare where its prose lives. It is the wrong trade for
source 1, because the search does not need to know:

```bash
git grep -l --untracked "NNN-slug" -- :/
```

Every part of that earns its place, and the naked `git grep -l "NNN-slug"` does not work — verified
2026-08-11 in a scratch repository:

- **`-- :/`** — `git grep` searches from the **current directory downward**, not the repository
  root. Run from inside `tasks/`, the bare form misses a match in a sibling directory entirely. The
  `:/` pathspec re-roots it, so the command is correct from anywhere.
- **`--untracked`** — without it the search cannot see files that are not yet committed, and
  `SKILL.md:374` explicitly blesses **bulk creation** of many cross-referencing task files before a
  commit. That is precisely when a propagation search that skips untracked files goes blind to the
  siblings it most needs to find. This task was itself invisible to the bare form while being
  written.

With both, it reads the repository at any layout, still skips ignored trees such as dependency and
build output, and exits 1 with no output rather than 2 with an error when there are no hits. The
skill already uses `git grep` at `:390` (the projection check), so it is established idiom here
rather than a new dependency — and `SKILL.md:368` already states *"Git is assumed throughout this
skill."* Outside a repository it exits 128, which is the one behavior a replacement has to decide
about deliberately rather than inherit.

The same applies to the prior-coverage search: `git grep -il --untracked "TOPIC" -- :/` covers every
named directory above plus the ones nobody named, replaces the dead second command outright, and
cannot be defeated by a project that files its decisions somewhere else.

**A third site the same fix reaches.** `SKILL.md:200`, in claim validation:

```bash
grep -rn "task NNN" --include='*.rs' --include='*.md' --exclude-dir=tasks .
```

`--include='*.rs'` is a source-file extension for one language, hardcoded into a portability-gated
shipped file. `check-portability.py` cannot see it either — its pattern for that language is a word
regex, and the extension contains no word to match. Same class of leak as the directory names above,
found by the independent read rather than by any gate.

## What this task is not — the declaration belongs to `031`

An earlier draft of this file argued at length that a project-level declaration of extra locations
was the wrong trade, on the grounds that a whole-repository search reaches everything in-repo for
free. **That framing is superseded and should not be revived.** Ruled 2026-08-11 by the owner: a
project must be able to say where else this tool looks for its work, on a per-project or per-repo
basis. `031` owns that capability.

The two do not compete, and the boundary between them is worth stating precisely so neither absorbs
the other:

- **This task fixes the default.** The searches above are broken and layout-coupled *whatever* a
  project declares. A project that declares nothing — every adopter today — gets a correct search
  only if this lands.
- **`031` makes the default configurable.** Where the search looks beyond the project's own tree is
  a question no search syntax can answer, because the answer is not derivable from the tree.

Sequencing follows from that: this task is not blocked by `031`, and `031` should not wait on it.
If this lands first, `031` extends a working search instead of a broken one.

One in-repo consequence for `031` to inherit rather than rediscover: **a project that is not a git
repository cannot use the replacement command at all** — `git grep` exits 128 outside a repository,
and `README.md:62-66` promises the lanes work on a filesystem alone. Whatever this task does about
that (see the criterion below) is the same seam `031` has to work through.

Also out of scope: half (b) of the propagation gate — the finding nothing yet records — is not
helped by any search fix. Nothing cites the task, so no search of any breadth returns the artifact.
The gate already answers that with source 3, *the artifacts you had to read to do the work*; the one
cheap improvement is to say out loud there that the list includes artifacts outside this project's
tree, which no search here can reach.

## Done when

- [ ] The propagation gate's source 1 searches the whole repository rather than two named
      directories, and does not exit non-zero in a project that lacks either one
- [ ] The replacement finds a match in a **task file created but not yet committed**, and finds one
      when run from a subdirectory — the two ways the obvious `git grep -l "NNN-slug"` is wrong.
      Bulk creation before a commit is blessed at `SKILL.md:374`, so the uncommitted case is normal
      operation, not an edge
- [ ] The prior-coverage search names no project-specific directory, and finds a topic filed
      anywhere in the repository
- [ ] The dead second prior-coverage command is gone, not repaired in place — verified by running
      the replacement in a directory holding a matching file and confirming it reports the hit
- [ ] The `2>/dev/null` on the prior-coverage search is either unnecessary after the change or its
      remaining purpose is stated — a silenced error that returns no hits reads identically to a
      clean search that found nothing, and that section's own closing line says which of those is
      expensive
- [ ] Behavior outside a repository is decided rather than inherited: `git grep` exits 128 there,
      and `SKILL.md:368`'s "git is assumed" is the sentence that governs whether that is acceptable
- [ ] Any search the skill hands out is checked for the same defect, so this lands once rather than
      per site — at minimum every `grep -r` in `SKILL.md`, including `:200`'s hardcoded
      single-language file extension and the `--exclude-dir` note that follows it
- [ ] Source 3 says out loud that the artifacts you read may sit outside this project's tree, where
      no search here can reach them — the one-line half of what `031` owns in full
- [ ] A project that is not a git repository is not left worse off: `README.md:62-66` promises the
      lanes work on a filesystem alone, and `git grep` exits 128 there. Either the replacement
      degrades to a portable search or the skill states plainly which of its steps need a
      repository — decided here, not left for `031` to discover
- [ ] `check-portability.py` passes on the changed shipped files
- [ ] `version` bumped in both manifests with a matching `CHANGELOG.md` heading, and the
      behavioral evals run before merge
- [ ] Every document and open task this change makes wrong is updated, and anything the work turned
      up that nothing yet records is written down — or what was checked is named here, with why
      none of it needed changing. At minimum: 020's §"The bounding problem", which quotes the
      two-directory search as the bound it recommends
