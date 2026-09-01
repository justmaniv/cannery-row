#!/usr/bin/env python3
"""Shelve completed tasks that have been closed long enough to stop being interesting.

`done/` grows monotonically and nothing ever leaves it. That is fine for a while and then it is
not: every structural check that validates the whole tracker pays for every file in it, so the
cost of closing work grows with the amount of work already closed. Archiving bounds that.

The archive is a **lane, not a shelf**. A file moved here gets `status: done-archived` in a
directory of the same name, so "the directory is the status" holds unamended — no exception
clause on the invariant, and every consumer that enumerates lanes gains one correct entry
instead of a special case.

Age is read from `completed:` frontmatter, never from mtime. mtime does not survive a clone and
a move does not set it meaningfully, so an mtime rule archives the entire tracker on a fresh
checkout. A file in `done/` with no usable `completed:` is refused and reported rather than
guessed at: that is an invariant breach upstream of this script, and moving it would bury the
evidence.

Renaming is not this script's business. Filenames cross unchanged, because number width is a
property of the repository and reconstructing a name from its number is how a tracker ends up
mixed-width.

    archive-done-tasks.py                 # shelve anything closed more than 14 days ago
    archive-done-tasks.py --days 30       # a different threshold
    archive-done-tasks.py --dry-run       # list what would move, move nothing

Exits non-zero if any file was refused. Moves are plain filesystem renames — commit them with
the rest of the change.
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

DONE_LANE = "done"
ARCHIVE_LANE = "done-archived"

# The window before a closed task stops being interesting. Not a deep number — long enough that
# a task closed at the start of a fortnight's work is still in `done/` at the end of it.
DEFAULT_DAYS = 14

# Same shape the rest of the tracker uses: three or more digits, and a slug that tolerates the
# dots and underscores real identifiers carry. Anything else in the lane is not a task file.
NAME_RE = re.compile(r"^\d{3,}-[A-Za-z0-9._-]+\.md$")

FRONTMATTER_RE = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)
COMPLETED_RE = re.compile(r"^completed:(.*)$", re.MULTILINE)
STATUS_RE = re.compile(r"^status:.*$", re.MULTILINE)
UPDATED_RE = re.compile(r"^updated:.*$", re.MULTILINE)


@dataclass
class Result:
    moved: list[Path] = field(default_factory=list)
    refused: list[Path] = field(default_factory=list)


def frontmatter(text: str) -> str:
    """The frontmatter block, or "" if the file has none. Deliberately not a YAML parse — the
    two fields this script reads are flat scalars, and a parser is a dependency."""
    m = FRONTMATTER_RE.match(text)
    return m.group(1) if m else ""


def completed_date(text: str) -> datetime.date | None:
    """The `completed:` value as a date, or None if it is absent, empty or not a date.

    None is the refusal signal, and the three causes are deliberately not distinguished: the
    caller's response is the same for all of them, and reporting the file is what matters."""
    m = COMPLETED_RE.search(frontmatter(text))
    if not m:
        return None
    raw = m.group(1).split("#")[0].strip().strip("\"'")
    if not raw:
        return None
    try:
        return datetime.date.fromisoformat(raw)
    except ValueError:
        return None


def to_archive_lane(text: str, today: datetime.date) -> str:
    """Rewrite the frontmatter for the new lane. `completed:` is left alone — invariant 4 admits
    the archive lane rather than dropping the date, and the date is what a later run reads."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return text
    head, rest = text[: m.end()], text[m.end() :]
    head = STATUS_RE.sub(f"status: {ARCHIVE_LANE}", head, count=1)
    head = UPDATED_RE.sub(f"updated: {today.isoformat()}", head, count=1)
    return head + rest


def candidates(root: Path) -> list[Path]:
    lane = root / "tasks" / DONE_LANE
    if not lane.is_dir():
        return []
    return sorted(p for p in lane.iterdir() if p.is_file() and NAME_RE.match(p.name))


def archive(
    root: Path,
    today: datetime.date,
    days: int = DEFAULT_DAYS,
    dry_run: bool = False,
) -> Result:
    """Move every `done/` task closed more than `days` ago into the archive lane.

    Strictly *more* than `days`: at exactly the threshold the file stays. A refusal is per-file
    and never aborts the run — one breached file must not turn a bulk move into a no-op."""
    result = Result()
    destination = root / "tasks" / ARCHIVE_LANE
    for path in candidates(root):
        text = path.read_text(encoding="utf-8")
        closed = completed_date(text)
        if closed is None:
            result.refused.append(path)
            continue
        if (today - closed).days <= days:
            continue
        result.moved.append(path)
        if dry_run:
            continue
        destination.mkdir(parents=True, exist_ok=True)
        (destination / path.name).write_text(to_archive_lane(text, today), encoding="utf-8")
        path.unlink()
    return result


def report(result: Result, days: int, dry_run: bool) -> None:
    verb = "would shelve" if dry_run else "shelved"
    if result.moved:
        print(f"{verb} {len(result.moved)} task(s) closed more than {days} days ago:")
        for path in result.moved:
            print(f"  {path.name}")
    else:
        print(f"nothing closed more than {days} days ago")
    if result.refused:
        print(f"\nrefused {len(result.refused)} task(s) in {DONE_LANE}/ with no usable `completed:`:")
        for path in result.refused:
            print(f"  {path.name}")
        print("  fix: set `completed:` to the closure date (invariant 4), then re-run")


def positive(raw: str) -> int:
    value = int(raw)
    if value < 0:
        raise argparse.ArgumentTypeError("must be zero or more")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="repository root holding tasks/")
    parser.add_argument("--days", type=positive, default=DEFAULT_DAYS)
    parser.add_argument("--today", help="override the date, for testing (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    today = datetime.date.fromisoformat(args.today) if args.today else datetime.date.today()
    result = archive(Path(args.root), today, args.days, args.dry_run)
    report(result, args.days, args.dry_run)
    return 1 if result.refused else 0


if __name__ == "__main__":
    sys.exit(main())
