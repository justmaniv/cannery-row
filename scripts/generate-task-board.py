#!/usr/bin/env python3
"""Generate docs/task-board.md — a readable view of the tasks/ directory tracker.

`tasks/<status>/NNN-slug.md` IS the tracker: a task's directory is its status. That's the
design's strength, but its only view is `ls` — there is no way to see what's in flight, what
blocks what, or how `prioritized/` is actually ordered without walking the tree by hand.

This is a pure projection of those files: frontmatter + H1 titles in, one committed markdown
board out, freshness CI-gated. The board owns no state — if it needs a field, the field goes in
the task spec first.

Deliberately markdown + Mermaid, not HTML: it renders in GitHub, in a terminal, and in an
editor, with no second artifact to keep fresh. It tracks task lanes only. If your project also
keeps a document tracking project phases, that answers a different question and stays separate.

Modes:
    generate-task-board.py            # writes docs/task-board.md
    generate-task-board.py --check    # exits non-zero if docs/task-board.md is stale
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = REPO_ROOT / "docs" / "task-board.md"

# Flow order. The two closed lanes are last: `done/` is recently closed and collapses to a
# window, `done-archived/` is shelved and renders in neither table.
LANES = ("new", "prioritized", "wip", "blocked", "done", "done-archived")
# ⚠️ Positional, and it will re-break when a seventh lane is appended — deliberately. A named
# tuple here would go quietly wrong instead; the slice reddens
# `test_header_columns_are_the_lanes_in_flow_order`, which is the property worth having.
LIVE_LANES = LANES[:-2]
# A blocker in either lane is closed work. Only the first is still listed on the board, and
# only the first is still structurally validated.
CLOSED_LANES = LANES[-2:]
ARCHIVE_LANE = LANES[-1]

# `done/` is 270+ entries and grows monotonically; listing it in full is noise that would also
# rewrite this file on every close. Count + a recent window is the signal.
DONE_RECENT = 12

# Card headlines, not full titles: four 100-character titles side by side is a horizontal
# scrollbar. The linked number is the route to the full text.
TITLE_CAP = 58

LANE_EMPTY = {
    "new": "_nothing captured_",
    "prioritized": "_nothing triaged_",
    "wip": "_nothing pulled_",
    "blocked": "_nothing waiting_",
}

# 3 per human owner, one per concurrent session. Agent identities aren't sessions of a human,
# so they don't count against the limit.
WIP_LIMIT = 3
AGENT_OWNERS = {"agent", "claude"}

# Slugs are kebab-case by convention but not in fact: real trackers carry dotted identifiers
# (`098-feature-1.1-workspace-ci.md`) and underscored package names (`rand_core`). A
# kebab-only charset drops those files with no error — a quietly wrong board.
NAME_RE = re.compile(r"^(\d{3,})-([A-Za-z0-9._-]+)\.md$")
# `done-archived` precedes `done` in the alternation so the match does not depend on the engine
# backtracking out of the shorter branch.
TASK_REF_RE = re.compile(
    r"tasks/(?:new|prioritized|wip|blocked|done-archived|done)/(\d{3,})-[A-Za-z0-9._-]+\.md"
)

# The body contract. Two elements, both load-bearing, neither previously checked:
#   H1        — the card headline. Without it the board renders a blank card and exits 0.
#   Done when — the acceptance criteria, and the only part of a task a later session with none
#               of the author's context is held to. The completion gate is "resolve every
#               unchecked box"; with no boxes that is trivially satisfied, so an unenforced
#               heading lets a task close on nobody's authority but the closer's.
# Tolerant on shape, strict on presence: any heading level, any case, and a struck-through
# item counts as a resolved criterion rather than a missing one.
DONE_WHEN_RE = re.compile(r"^#{2,6}\s*done when\b", re.IGNORECASE)
HEADING_RE = re.compile(r"^#{1,6}\s")
CRITERION_RE = re.compile(r"^\s*[-*]\s+(\[[ xX]\]|~~)")

EXTERNAL_LABEL_MAX = 60

MERMAID_CLASSDEFS = (
    "  classDef satisfied fill:#EAF2EA,stroke:#3A7D44,color:#1F3D24;\n"
    "  classDef external fill:#F4F1E8,stroke:#B58500,color:#5A4300;\n"
)


@dataclass
class Task:
    number: int
    prefix: str  # the number exactly as the filename spells it, padding and all
    slug: str
    lane: str  # = parent directory; the file's location IS its status
    title: str
    owner: str
    updated: str
    completed: str
    blockers: list[str]  # raw `blocked-by:` values — a task path or a prose condition
    path: str  # repo-relative
    done_when_items: int | None = 1  # None = no `## Done when` heading; 0 = heading, no criteria


def _scalar(raw: str) -> str:
    """One frontmatter scalar. Handles the shapes this tree actually uses: quoted, bare, and
    quoted-with-a-trailing-`# comment` (e.g. `blocked-by: ""   # cleared 2026-08-04`)."""
    raw = raw.strip()
    for quote in ('"', "'"):
        if raw.startswith(quote):
            m = re.match(rf"^{quote}([^{quote}]*){quote}", raw)
            if m:
                return m.group(1)
    return re.sub(r"\s+#.*$", "", raw).strip()


def parse_task(text: str) -> tuple[dict[str, str | list[str]], str]:
    """Return (frontmatter, H1 title). Tolerant line parse, no PyYAML — but list-valued keys
    are real here: `blocked-by:` takes a YAML block sequence when a task has several blockers,
    and flattening that to "" would silently drop edges from the graph."""
    lines = text.splitlines()
    fm: dict[str, str | list[str]] = {}
    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[i])
            if not m:
                i += 1
                continue
            key, raw = m.group(1), m.group(2)
            i += 1
            if raw.strip():
                fm[key] = _scalar(raw)
                continue
            items: list[str] = []
            while i < len(lines) and lines[i].strip() != "---" and re.match(r"^\s+-\s+", lines[i]):
                items.append(_scalar(re.sub(r"^\s+-\s+", "", lines[i])))
                i += 1
            fm[key] = items if items else ""
    title = next((ln[2:].strip() for ln in lines if ln.startswith("# ")), "")
    return fm, title


def parse_done_when(text: str) -> int | None:
    """Count the acceptance criteria under `## Done when`. None when the heading is absent —
    which is a different mistake from a heading with nothing under it, and gets its own message."""
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines) if DONE_WHEN_RE.match(ln)), None)
    if start is None:
        return None
    count = 0
    for ln in lines[start + 1:]:
        if HEADING_RE.match(ln):
            break
        if CRITERION_RE.match(ln):
            count += 1
    return count


def structural_problems(tasks: list[Task]) -> list[str]:
    """Every violation on every file. Reporting only the first turns a two-minute fix into
    fix-one, re-run, discover the next.

    Two properties, reported as three messages, and the list stops there on purpose. Adding a
    fourth for the propagation criterion the templates now carry — "every document and open task
    this change makes wrong is updated" — was considered and declined (task 020). A grep can see
    that a *line exists*; it cannot see that anything was read. Gating on the line teaches authors
    to keep the line, which manufactures exactly the always-green box the criterion is worded to
    prevent, and hands it a passing build as evidence. The checks below survive that test because
    presence *is* the property: an H1 that exists is an H1, and a criterion someone can read is a
    criterion.

    So the obligation lives in the skill's close procedure instead, where the session answering it
    has just done the work and knows what it changed. Declined deliberately — not overlooked."""
    problems: list[str] = []
    for t in tasks:
        # Shelved work leaves the sweep, and that is the point of the lane rather than a
        # concession. This check costs one pass over every closed file on every generation, so
        # its price grows monotonically with work already finished; bounding it is what the
        # archive is *for*. `done/` stays checked — it is the live record of what just shipped.
        if t.lane == ARCHIVE_LANE:
            continue
        if not t.title.strip():
            problems.append(
                f"{t.path}\n"
                "    no H1 title — the board renders this card with a blank headline\n"
                "    fix: add a line starting with '# ' saying what outcome this task produces"
            )
        if t.done_when_items is None:
            problems.append(
                f"{t.path}\n"
                "    no '## Done when' section — this task states no acceptance criteria, so\n"
                "    nothing gates its close and a later session has nothing to be held to\n"
                "    fix: add a '## Done when' heading followed by '- [ ] ' criteria"
            )
        elif t.done_when_items == 0:
            problems.append(
                f"{t.path}\n"
                "    '## Done when' is present with no criteria under it — the completion gate\n"
                "    resolves every unchecked box, and zero boxes is trivially resolved\n"
                "    fix: list the criteria as '- [ ] ' items, or delete the empty heading"
            )
    return problems


def classify_blocker(raw: str) -> tuple[str, int | str] | None:
    """('task', NNN) for a task-path blocker, ('external', text) for a prose condition, None for
    empty. Prose blockers are first-class — several live tasks are gated on a condition
    ("approaching first external release"), not on another task, and dropping them would render
    those tasks as unblocked."""
    raw = raw.strip()
    if not raw:
        return None
    m = TASK_REF_RE.search(raw)
    if m:
        return ("task", int(m.group(1)))
    return ("external", raw)


def load_tasks(root: Path) -> list[Task]:
    tasks: list[Task] = []
    for lane in LANES:
        lane_dir = root / "tasks" / lane
        if not lane_dir.is_dir():
            continue
        for path in sorted(lane_dir.iterdir()):
            m = NAME_RE.match(path.name)
            if not m:
                continue
            text = path.read_text(encoding="utf-8")
            fm, title = parse_task(text)
            raw_blocked = fm.get("blocked-by", "")
            values = raw_blocked if isinstance(raw_blocked, list) else [raw_blocked]
            tasks.append(
                Task(
                    number=int(m.group(1)),
                    prefix=m.group(1),
                    slug=m.group(2),
                    lane=lane,
                    title=title,
                    owner=str(fm.get("owner", "")),
                    updated=str(fm.get("updated", "")),
                    completed=str(fm.get("completed", "")),
                    blockers=[v for v in values if v.strip()],
                    path=f"tasks/{lane}/{path.name}",
                    done_when_items=parse_done_when(text),
                )
            )
    return tasks


def cell(text: str) -> str:
    return text.replace("|", "\\|").strip()


def card(t: Task) -> str:
    """One task as a board card. Everything in it comes from frontmatter — nothing derived from
    the wall clock, or this committed file would go stale at midnight and redden a build nobody
    caused."""
    title = cell(t.title)
    if len(title) > TITLE_CAP:
        title = title[:TITLE_CAP].rstrip() + "…"
    meta = [cell(t.owner) or "—", t.updated or "—"]
    for raw in t.blockers:
        classified = classify_blocker(raw)
        if classified is None:
            continue
        kind, value = classified
        meta.append(f"⛔ {value:0{len(t.prefix)}d}" if kind == "task" else "⛔ condition")
    return f"**[{t.prefix}](../{t.path})** {title}<br><sub>{' · '.join(meta)}</sub>"


def render_board_columns(tasks: list[Task]) -> str:
    """The live lanes as ONE table whose columns ARE the lanes. Stacked per-lane tables answer
    'what is in lane N?' one lane at a time — which is what `ls` already did."""
    by_lane = {lane: [t for t in tasks if t.lane == lane] for lane in LIVE_LANES}
    depth = max((len(by_lane[lane]) for lane in LIVE_LANES), default=0) or 1
    header = "| " + " | ".join(f"{lane} ({len(by_lane[lane])})" for lane in LIVE_LANES) + " |"
    lines = [header, "|" + "---|" * len(LIVE_LANES)]
    for row in range(depth):
        cells = []
        for lane in LIVE_LANES:
            items = by_lane[lane]
            if row < len(items):
                cells.append(card(items[row]))
            elif row == 0 and not items:
                cells.append(LANE_EMPTY[lane])
            else:
                cells.append("")
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def render_done(tasks: list[Task], recent: int = DONE_RECENT) -> str:
    ordered = sorted(tasks, key=lambda t: (t.completed, t.number), reverse=True)
    window = ordered[:recent]
    head = f"## done ({len(tasks)})"
    if not tasks:
        return f"{head}\n\n_Empty._\n"
    note = (
        f"Collapsed — the {len(window)} most recently completed of {len(tasks)}. "
        "The full pile is `tasks/done/`; git history is its journey."
    )
    rows = ["| # | Task | Completed |", "|---|---|---|"]
    for t in window:
        rows.append(f"| [{t.prefix}](../{t.path}) | {cell(t.title)} | {t.completed or '—'} |")
    return f"{head}\n\n{note}\n\n" + "\n".join(rows) + "\n"


def _mermaid_label(text: str) -> str:
    """Mermaid node labels are quote-delimited, so an embedded quote ends the label early and
    breaks the whole diagram. Prose blockers are free text — sanitize, don't trust."""
    flat = " ".join(text.split()).replace('"', "'")
    if len(flat) > EXTERNAL_LABEL_MAX:
        flat = flat[:EXTERNAL_LABEL_MAX].rstrip() + "…"
    return flat


def render_blocked_graph(tasks: list[Task]) -> str:
    """Dependency edges, blocker → dependent, for live dependents only. Closed tasks' historical
    blockers would bury the handful of edges that still gate work. A blocker already in `done/`
    is still drawn, marked satisfied — a live task pointing at a closed blocker is stale board
    state someone should clear."""
    by_number = {t.number: t for t in tasks}
    edges: list[tuple[str, str]] = []
    labels: dict[str, str] = {}
    satisfied: list[str] = []
    external: list[str] = []

    for t in tasks:
        if t.lane in CLOSED_LANES:
            continue
        # Node ids carry no width: they only have to be unique and to agree between the two
        # loops that emit them. Padding them would make the same task two nodes in a mixed tree.
        dependent = f"T{t.number}"
        for raw in t.blockers:
            classified = classify_blocker(raw)
            if classified is None:
                continue
            kind, value = classified
            if kind == "task":
                blocker = f"T{value}"
                known = by_number.get(int(value))
                labels[blocker] = f"{known.prefix if known else value} · {known.slug if known else 'missing'}"
                if known is not None and known.lane in CLOSED_LANES and blocker not in satisfied:
                    satisfied.append(blocker)
            else:
                blocker = f"X{len(external) + 1}"
                labels[blocker] = _mermaid_label(str(value))
                external.append(blocker)
            labels[dependent] = f"{t.prefix} · {t.slug}"
            edges.append((blocker, dependent))

    head = "## Blocked-by graph"
    if not edges:
        return f"{head}\n\n_No open dependencies._\n"

    lines = ["```mermaid", "graph LR"]
    for node in labels:
        lines.append(f'  {node}["{labels[node]}"]')
    for blocker, dependent in edges:
        lines.append(f"  {blocker} --> {dependent}")
    lines.append(MERMAID_CLASSDEFS.rstrip("\n"))
    for node in satisfied:
        lines.append(f"  class {node} satisfied")
    for node in external:
        lines.append(f"  class {node} external")
    lines.append("```")
    legend = "Edge reads *blocker → blocked*. Green = blocker already closed (stale reference). Amber = a condition, not a task."
    return f"{head}\n\n" + "\n".join(lines) + f"\n\n{legend}\n"


def human_owners(raw: str) -> list[str]:
    return [p for p in (part.strip() for part in raw.split("+")) if p and p not in AGENT_OWNERS]


def wip_breaches(tasks: list[Task]) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for t in tasks:
        if t.lane != "wip":
            continue
        for owner in human_owners(t.owner):
            counts[owner] = counts.get(owner, 0) + 1
    return sorted((owner, n) for owner, n in counts.items() if n > WIP_LIMIT)


def render_wip_check(tasks: list[Task]) -> str:
    breaches = wip_breaches(tasks)
    if not breaches:
        return f"WIP limit: within {WIP_LIMIT} per human owner.\n"
    lines = [f"⚠️ **WIP limit breached** (limit {WIP_LIMIT} per human owner):"]
    lines += [f"- {owner} — {n} in `wip/`" for owner, n in breaches]
    return "\n".join(lines) + "\n"


def render_board(tasks: list[Task]) -> str:
    by_lane = {lane: [t for t in tasks if t.lane == lane] for lane in LANES}
    tally = " · ".join(f"{len(by_lane[lane])} {lane}" for lane in LANES)
    parts = [
        "<!--\n"
        "  GENERATED FILE — do not hand-edit.\n"
        "  Source: tasks/<status>/NNN-*.md frontmatter + H1 titles.\n"
        "  Regenerate: scripts/generate-task-board.py  (--check reports staleness)\n"
        "-->\n",
        "# Task board\n",
        "Projection of `tasks/` — the directory is the tracker, this is its view. Columns are the\n"
        "lanes in flow order; `prioritized/` is in pull order. Regenerated on demand, not on every\n"
        "move — so this view can lag the tracker, and the tracker wins.\n"
        "Cards show `owner · last updated`, and `⛔` on a blocked task — a task number when another\n"
        "task gates it, `condition` when nothing but a judgement call does.\n",
        f"**{len(tasks)} tasks** — {tally}.\n",
        render_wip_check(tasks),
    ]
    parts.append(render_board_columns(tasks))
    parts.append(render_blocked_graph(tasks))
    parts.append(render_done(by_lane["done"]))
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit non-zero if the board is stale")
    args = parser.parse_args()

    tasks = load_tasks(REPO_ROOT)

    # Before anything is rendered. A board built from a broken task is the bug shipping —
    # a blank card looks like a styling glitch, and a task with no acceptance criteria looks
    # exactly like one that has them until someone tries to close it.
    problems = structural_problems(tasks)
    if problems:
        print(f"\n✗ {len(problems)} structural problem(s) in tasks/\n", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}\n", file=sys.stderr)
        print(
            "Every task needs an H1 title and a '## Done when' checklist. Both are required in\n"
            "every lane. The conventions are in tasks/README.md; no board was written.",
            file=sys.stderr,
        )
        return 1

    board = render_board(tasks)

    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != board:
            print(f"error: {OUTPUT} is stale — run scripts/generate-task-board.py and commit", file=sys.stderr)
            return 1
        print(f"ok: {len(tasks)} tasks, {OUTPUT} is fresh")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(board, encoding="utf-8")
    print(f"wrote {OUTPUT} ({len(tasks)} tasks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
