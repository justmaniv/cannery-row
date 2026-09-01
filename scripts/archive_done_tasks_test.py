#!/usr/bin/env python3
"""Unit tests for the archive operation the skill ships.

The script under test lives beside `SKILL.md`, not in this directory — it is skill cargo, not
gate tooling, so it travels with the skill and is replaced by a plugin update. Its tests live
here because this is where the runner looks (`unittest discover -s scripts`).

Every test pins a *moved set* or a *refusal*, never merely that the code ran. `today` is injected
rather than read from the clock: a threshold test that depends on the day it runs is a test that
starts failing for the wrong reason. Run:
    python3 scripts/archive_done_tasks_test.py
"""

import contextlib
import datetime
import importlib.util
import io
import pathlib
import sys
import tempfile
import unittest

_spec = importlib.util.spec_from_file_location(
    "archive_done_tasks",
    pathlib.Path(__file__).resolve().parents[1]
    / "skills"
    / "task-lifecycle"
    / "scripts"
    / "archive-done-tasks.py",
)
arch = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = arch
_spec.loader.exec_module(arch)

TODAY = datetime.date(2026, 9, 1)


def write_task(root, lane, name, completed="2026-01-01", status=None, updated="2026-01-01"):
    """A minimally valid task file in `lane`. `completed` of None omits the value, not the key —
    an absent value is the invariant-4 breach the guard exists for, and it is not the same file
    as one with no `completed:` line at all."""
    lane_dir = root / "tasks" / lane
    lane_dir.mkdir(parents=True, exist_ok=True)
    path = lane_dir / name
    path.write_text(
        "---\n"
        "created: 2026-01-01\n"
        f"updated: {updated}\n"
        f"completed: {completed if completed is not None else ''}\n"
        f"status: {status if status is not None else lane}\n"
        "owner: smiley\n"
        'blocked-by: ""\n'
        "---\n"
        "\n"
        "# A task\n"
        "\n"
        "## Done when\n"
        "\n"
        "- [x] it happened\n",
        encoding="utf-8",
    )
    return path


@contextlib.contextmanager
def tree():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "tasks" / "done").mkdir(parents=True)
        yield root


def moved_names(root):
    lane = root / "tasks" / arch.ARCHIVE_LANE
    return sorted(p.name for p in lane.iterdir()) if lane.is_dir() else []


def done_names(root):
    return sorted(p.name for p in (root / "tasks" / "done").iterdir())


class Threshold(unittest.TestCase):
    def test_default_is_fourteen_days(self):
        self.assertEqual(arch.DEFAULT_DAYS, 14)

    def test_older_than_default_moves(self):
        with tree() as root:
            write_task(root, "done", "00001-old.md", completed="2026-08-01")
            arch.archive(root, today=TODAY, days=arch.DEFAULT_DAYS)
            self.assertEqual(moved_names(root), ["00001-old.md"])
            self.assertEqual(done_names(root), [])

    def test_younger_than_default_stays(self):
        with tree() as root:
            write_task(root, "done", "00001-fresh.md", completed="2026-08-30")
            arch.archive(root, today=TODAY, days=arch.DEFAULT_DAYS)
            self.assertEqual(moved_names(root), [])
            self.assertEqual(done_names(root), ["00001-fresh.md"])

    def test_exactly_n_days_old_stays(self):
        """The boundary. "More than N" must not drift to "at least N" — at exactly 14 days the
        file is not yet stale, and nothing but this test says so."""
        with tree() as root:
            write_task(root, "done", "00001-boundary.md", completed="2026-08-18")  # 14 days
            arch.archive(root, today=TODAY, days=14)
            self.assertEqual(moved_names(root), [])
            self.assertEqual(done_names(root), ["00001-boundary.md"])

    def test_one_day_past_n_moves(self):
        with tree() as root:
            write_task(root, "done", "00001-past.md", completed="2026-08-17")  # 15 days
            arch.archive(root, today=TODAY, days=14)
            self.assertEqual(moved_names(root), ["00001-past.md"])

    def test_days_is_overridable_per_call(self):
        with tree() as root:
            write_task(root, "done", "00001-a.md", completed="2026-08-25")  # 7 days
            arch.archive(root, today=TODAY, days=3)
            self.assertEqual(moved_names(root), ["00001-a.md"])

    def test_zero_days_archives_everything_dated_before_today(self):
        with tree() as root:
            write_task(root, "done", "00001-a.md", completed="2026-08-31")
            write_task(root, "done", "00002-b.md", completed="2026-09-01")
            arch.archive(root, today=TODAY, days=0)
            self.assertEqual(moved_names(root), ["00001-a.md"])
            self.assertEqual(done_names(root), ["00002-b.md"])


class Refusals(unittest.TestCase):
    def test_empty_completed_is_reported_and_not_moved(self):
        with tree() as root:
            write_task(root, "done", "00001-nodate.md", completed=None)
            result = arch.archive(root, today=TODAY, days=14)
            self.assertEqual(moved_names(root), [])
            self.assertEqual(done_names(root), ["00001-nodate.md"])
            self.assertEqual([p.name for p in result.refused], ["00001-nodate.md"])

    def test_unparseable_completed_is_reported_and_not_moved(self):
        with tree() as root:
            write_task(root, "done", "00001-junk.md", completed="last tuesday")
            result = arch.archive(root, today=TODAY, days=14)
            self.assertEqual(moved_names(root), [])
            self.assertEqual(done_names(root), ["00001-junk.md"])
            self.assertEqual([p.name for p in result.refused], ["00001-junk.md"])

    def test_a_refusal_does_not_block_its_neighbours(self):
        """One bad file must not turn a bulk move into a no-op — that would make the guard a
        denial of service on the whole operation."""
        with tree() as root:
            write_task(root, "done", "00001-junk.md", completed="")
            write_task(root, "done", "00002-old.md", completed="2026-01-01")
            arch.archive(root, today=TODAY, days=14)
            self.assertEqual(moved_names(root), ["00002-old.md"])
            self.assertEqual(done_names(root), ["00001-junk.md"])

    def test_refusal_is_reported_on_stdout(self):
        with tree() as root:
            write_task(root, "done", "00001-junk.md", completed="")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                arch.main(["--root", str(root), "--today", "2026-09-01"])
            self.assertIn("00001-junk.md", buf.getvalue())


class Scope(unittest.TestCase):
    def test_other_lanes_are_untouched(self):
        with tree() as root:
            for lane in ("new", "prioritized", "wip", "blocked"):
                write_task(root, lane, "00009-live.md", completed="2026-01-01")
            arch.archive(root, today=TODAY, days=14)
            self.assertEqual(moved_names(root), [])
            for lane in ("new", "prioritized", "wip", "blocked"):
                self.assertTrue((root / "tasks" / lane / "00009-live.md").is_file())

    def test_non_task_files_in_done_are_ignored(self):
        with tree() as root:
            (root / "tasks" / "done" / "README.md").write_text("not a task\n", encoding="utf-8")
            write_task(root, "done", "00001-old.md", completed="2026-01-01")
            arch.archive(root, today=TODAY, days=14)
            self.assertEqual(moved_names(root), ["00001-old.md"])
            self.assertTrue((root / "tasks" / "done" / "README.md").is_file())

    def test_already_archived_files_are_left_alone(self):
        with tree() as root:
            write_task(root, arch.ARCHIVE_LANE, "00001-old.md", completed="2026-01-01")
            result = arch.archive(root, today=TODAY, days=14)
            self.assertEqual(result.moved, [])
            self.assertEqual(moved_names(root), ["00001-old.md"])


class Frontmatter(unittest.TestCase):
    def test_status_becomes_the_archive_lane(self):
        with tree() as root:
            write_task(root, "done", "00001-old.md", completed="2026-01-01")
            arch.archive(root, today=TODAY, days=14)
            text = (root / "tasks" / arch.ARCHIVE_LANE / "00001-old.md").read_text(encoding="utf-8")
            self.assertIn(f"status: {arch.ARCHIVE_LANE}\n", text)
            self.assertNotIn("status: done\n", text)

    def test_updated_is_bumped_to_today(self):
        with tree() as root:
            write_task(root, "done", "00001-old.md", completed="2026-01-01", updated="2026-01-01")
            arch.archive(root, today=TODAY, days=14)
            text = (root / "tasks" / arch.ARCHIVE_LANE / "00001-old.md").read_text(encoding="utf-8")
            self.assertIn("updated: 2026-09-01\n", text)

    def test_completed_is_preserved(self):
        """Invariant 4 is amended to "set iff in `done/` or the archive lane" — not dropped. The
        date is what a later archive run, and any audit of when work closed, reads."""
        with tree() as root:
            write_task(root, "done", "00001-old.md", completed="2026-01-01")
            arch.archive(root, today=TODAY, days=14)
            text = (root / "tasks" / arch.ARCHIVE_LANE / "00001-old.md").read_text(encoding="utf-8")
            self.assertIn("completed: 2026-01-01\n", text)

    def test_body_is_not_rewritten(self):
        with tree() as root:
            write_task(root, "done", "00001-old.md", completed="2026-01-01")
            arch.archive(root, today=TODAY, days=14)
            text = (root / "tasks" / arch.ARCHIVE_LANE / "00001-old.md").read_text(encoding="utf-8")
            self.assertIn("# A task\n", text)
            self.assertIn("- [x] it happened\n", text)


class Naming(unittest.TestCase):
    def test_filename_is_carried_across_unchanged(self):
        """Archiving renames nothing. A three-digit adopter must not come back to a five-digit
        file — that is the mixed-width state task 035 exists to prevent."""
        with tree() as root:
            write_task(root, "done", "042-three-digit.md", completed="2026-01-01")
            arch.archive(root, today=TODAY, days=14)
            self.assertEqual(moved_names(root), ["042-three-digit.md"])

    def test_dotted_and_underscored_slugs_survive(self):
        with tree() as root:
            write_task(root, "done", "00098-feature-1.1_ws.md", completed="2026-01-01")
            arch.archive(root, today=TODAY, days=14)
            self.assertEqual(moved_names(root), ["00098-feature-1.1_ws.md"])


class DryRun(unittest.TestCase):
    def test_dry_run_moves_nothing(self):
        with tree() as root:
            write_task(root, "done", "00001-old.md", completed="2026-01-01")
            arch.archive(root, today=TODAY, days=14, dry_run=True)
            self.assertEqual(moved_names(root), [])
            self.assertEqual(done_names(root), ["00001-old.md"])

    def test_dry_run_still_reports_what_would_move(self):
        with tree() as root:
            write_task(root, "done", "00001-old.md", completed="2026-01-01")
            result = arch.archive(root, today=TODAY, days=14, dry_run=True)
            self.assertEqual([p.name for p in result.moved], ["00001-old.md"])

    def test_dry_run_does_not_create_the_lane_directory(self):
        with tree() as root:
            write_task(root, "done", "00001-old.md", completed="2026-01-01")
            arch.archive(root, today=TODAY, days=14, dry_run=True)
            self.assertFalse((root / "tasks" / arch.ARCHIVE_LANE).exists())

    def test_dry_run_names_every_file_on_stdout(self):
        with tree() as root:
            write_task(root, "done", "00001-old.md", completed="2026-01-01")
            write_task(root, "done", "00002-also.md", completed="2026-01-02")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                arch.main(["--root", str(root), "--today", "2026-09-01", "--dry-run"])
            out = buf.getvalue()
            self.assertIn("00001-old.md", out)
            self.assertIn("00002-also.md", out)


class Cli(unittest.TestCase):
    def test_days_flag_overrides_the_default(self):
        with tree() as root:
            write_task(root, "done", "00001-a.md", completed="2026-08-25")  # 7 days
            arch.main(["--root", str(root), "--today", "2026-09-01", "--days", "3"])
            self.assertEqual(moved_names(root), ["00001-a.md"])

    def test_exit_zero_when_nothing_to_do(self):
        with tree() as root:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = arch.main(["--root", str(root), "--today", "2026-09-01"])
            self.assertEqual(rc, 0)

    def test_exit_zero_on_a_clean_move(self):
        with tree() as root:
            write_task(root, "done", "00001-old.md", completed="2026-01-01")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = arch.main(["--root", str(root), "--today", "2026-09-01"])
            self.assertEqual(rc, 0)

    def test_exit_nonzero_when_a_file_was_refused(self):
        """A refusal is an invariant-4 breach upstream of this script. Exiting 0 would let it
        pass unnoticed in exactly the automated context that would catch it."""
        with tree() as root:
            write_task(root, "done", "00001-junk.md", completed="")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = arch.main(["--root", str(root), "--today", "2026-09-01"])
            self.assertEqual(rc, 1)

    def test_today_defaults_to_the_clock(self):
        with tree() as root:
            write_task(root, "done", "00001-old.md", completed="2020-01-01")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                arch.main(["--root", str(root)])
            self.assertEqual(moved_names(root), ["00001-old.md"])

    def test_negative_days_is_rejected(self):
        with tree() as root:
            with self.assertRaises(SystemExit):
                with contextlib.redirect_stderr(io.StringIO()):
                    arch.main(["--root", str(root), "--days", "-1"])

    def test_missing_done_lane_is_not_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = arch.main(["--root", str(root), "--today", "2026-09-01"])
            self.assertEqual(rc, 0)


class Portability(unittest.TestCase):
    def test_the_script_hardcodes_no_number_width(self):
        """035's obligation: nothing in shipped code may reconstruct a name from its number. A
        `%05d`, `:05d` or `{:0N}` here would hand a three-digit adopter a five-digit file."""
        src = pathlib.Path(_spec.origin).read_text(encoding="utf-8")
        for forbidden in ("%05d", "%03d", ":05d", ":03d", "zfill"):
            self.assertNotIn(forbidden, src)


if __name__ == "__main__":
    unittest.main()
