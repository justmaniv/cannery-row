#!/usr/bin/env python3
"""Executable tests for the numbering scan the skill tells a reader to run.

Unlike the gate tests next door, these assert on *this repository's shipped content*, and
deliberately so. The scan is a shell pipeline embedded in prose: nothing compiles it, nothing
imports it, and every other check in `scripts/` reads it only as text. A reduction that returns
a wrong number is still well-formed prose, so the only way to catch it is to run it.

The pipeline is extracted from `SKILL.md` and executed over synthetic filenames. Run:
    python3 scripts/skill_numbering_scan_test.py
"""

import pathlib
import re
import subprocess
import unittest

SKILL = pathlib.Path(__file__).resolve().parents[1] / "skills" / "task-lifecycle" / "SKILL.md"

REDUCTION_RE = re.compile(r"(sed -E .*\bgrep -oE\b.*\bsort -n\b.*\btail -1)")
SUCCESSOR_RE = re.compile(r"^(printf .*next task number.*)$", re.MULTILINE)


def reduction() -> str:
    """The `sed | grep | sort | tail` tail of the scan — the part that turns filenames into a max."""
    found = REDUCTION_RE.findall(SKILL.read_text(encoding="utf-8"))
    assert len(found) == 1, f"expected exactly one reduction pipeline in SKILL.md, found {len(found)}"
    return found[0]


def successor() -> str:
    """The line that prints the next number, given `next` holding the scanned max."""
    found = SUCCESSOR_RE.findall(SKILL.read_text(encoding="utf-8"))
    assert len(found) == 1, f"expected exactly one successor line in SKILL.md, found {len(found)}"
    return found[0]


def run(script: str) -> str:
    done = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


def next_number(maximum: str) -> int:
    """The number the successor line hands back, read independently of its print width so these
    cases survive a change to the padding without being rewritten to match it."""
    return int(next_token(maximum), 10)


def next_token(maximum: str) -> str:
    """The successor exactly as printed, padding included."""
    return run(f"next={maximum}; {successor()}").split()[-1]


def scan(*names: str) -> str:
    listing = "".join(f"tasks/new/{n}\\n" for n in names)
    return run(f"printf '{listing}' | {reduction()}")


class TheScanReportsTheRealMaximum(unittest.TestCase):
    """A wrong maximum is worse than a crash: the caller takes max+1, which is already in use."""

    def test_three_digit_numbers_still_scan(self):
        self.assertEqual(scan("007-a.md", "042-b.md", "036-c.md"), "042")

    def test_a_four_digit_number_is_not_truncated_to_its_first_three(self):
        # The regression this test exists for: an exact `{3}` quantifier plus `grep -o` matches a
        # *prefix*, so 1000-b.md reduces to 100 and the caller is handed 101 -- a number in use.
        self.assertEqual(scan("0999-a.md", "1000-b.md", "1001-c.md"), "1001")

    def test_a_zero_padded_number_is_not_truncated_to_its_padding(self):
        # Under five-digit padding an exact `{3}` reduces 00035-slug.md to 000, so the scan reports
        # a maximum of zero and hands back 1 -- every number colliding, forever.
        self.assertEqual(scan("00007-a.md", "00035-b.md", "00036-c.md"), "00036")

    def test_the_maximum_is_numeric_not_lexical(self):
        # 200 sorts after 1000 lexically. Under an exact `{3}` the four-digit entry reduces to 100
        # and this passes for the wrong reason, so it is a live case both before and after the fix.
        self.assertEqual(scan("1000-a.md", "200-b.md"), "1000")


class TheSuccessorSurvivesLeadingZeros(unittest.TestCase):
    """`10#` forces base ten; without it a padded maximum is read as octal and 00008 is an error."""

    def test_an_unpadded_maximum_increments(self):
        self.assertEqual(next_number("1000"), 1001)

    def test_a_padded_maximum_increments_in_base_ten_not_octal(self):
        self.assertEqual(next_number("01000"), 1001)

    def test_a_padded_eight_is_not_an_invalid_octal_digit(self):
        self.assertEqual(next_number("00008"), 9)

    def test_an_empty_scan_starts_at_one(self):
        self.assertEqual(next_number(""), 1)


class TheSuccessorKeepsTheWidthTheRepositoryAlreadyUses(unittest.TestCase):
    """The skill ships to repositories this one has never seen, and they have not all chosen the
    same width. A hardcoded width mints a number of the wrong shape in every repository that chose
    a different one -- which is the mixed-width state the padding rule exists to prevent, shipped
    by the thing meant to prevent it. The scan already returns the maximum with its padding intact,
    so the width is free."""

    def test_a_five_digit_repository_gets_a_five_digit_number(self):
        self.assertEqual(next_token("00739"), "00740")

    def test_a_three_digit_repository_still_gets_three(self):
        self.assertEqual(next_token("739"), "740")

    def test_a_four_digit_repository_gets_four(self):
        self.assertEqual(next_token("0035"), "0036")

    def test_padding_is_never_truncated_when_the_number_outgrows_it(self):
        self.assertEqual(next_token("999"), "1000")

    def test_an_empty_repository_starts_at_the_three_digit_floor(self):
        # No files, so no width to read. Three is the floor every earlier version of this line used.
        self.assertEqual(next_token(""), "001")


if __name__ == "__main__":
    unittest.main()
