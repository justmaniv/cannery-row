#!/usr/bin/env python3
"""Unit tests for the argument-substitution gate.

`scan()` takes a repo root, so every case is a small tree in a tempdir rather than an
assertion about this repository — which would test the content, not the gate. Run:
    python3 scripts/check_skill_args_test.py
"""

import importlib.util
import pathlib
import sys
import tempfile
import unittest

_spec = importlib.util.spec_from_file_location(
    "check_skill_args", pathlib.Path(__file__).with_name("check-skill-args.py")
)
gate = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = gate
_spec.loader.exec_module(gate)


def tree(root, **overrides):
    for rel in gate.SCANNED:
        path = pathlib.Path(root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(overrides.get(rel, "# Clean\n\nNothing positional here.\n"), encoding="utf-8")
    return pathlib.Path(root)


SKILL = "skills/task-lifecycle/SKILL.md"


def scan(text, rel=SKILL):
    with tempfile.TemporaryDirectory() as root:
        return gate.scan(tree(root, **{rel: text}))


class CleanTree(unittest.TestCase):
    def test_no_findings_and_no_errors(self):
        with tempfile.TemporaryDirectory() as root:
            findings, errors = gate.scan(tree(root))
        self.assertEqual(findings, [])
        self.assertEqual(errors, [])


class PositionalTokensAreRejected(unittest.TestCase):
    """The case with teeth. This is the exact line that shipped broken for weeks."""

    def test_awk_field_reference_is_caught(self):
        findings, _ = scan("    git worktree list | awk '/^worktree /{print $2}'\n")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].line, 1)
        self.assertIn("$2", findings[0].token)

    def test_every_digit_zero_through_nine_is_caught(self):
        for digit in range(10):
            with self.subTest(digit=digit):
                findings, _ = scan(f"run `echo ${digit}` please\n")
                self.assertEqual(len(findings), 1, f"${digit} was not caught")

    def test_shell_positional_in_a_function_body_is_caught(self):
        findings, _ = scan('bump() { printf "%s" "$1"; }\n')
        self.assertEqual(len(findings), 1)

    def test_every_occurrence_is_reported_not_just_the_first(self):
        findings, _ = scan("$1 and $2 on one line\nand $3 on the next\n")
        self.assertEqual(len(findings), 3)
        self.assertEqual([f.line for f in findings], [1, 1, 2])

    def test_findings_carry_the_line_text_so_the_report_is_actionable(self):
        findings, _ = scan("awk '{print $7}'\n")
        self.assertIn("awk", findings[0].text)


class NonPositionalDollarsSurvive(unittest.TestCase):
    """Verified 2026-08-30: these arrive byte-identical, so flagging them is a false alarm."""

    def test_braced_name_with_a_digit_in_its_default_is_allowed(self):
        findings, _ = scan("printf '%03d' $(( 10#${next:-0} + 1 ))\n")
        self.assertEqual(findings, [])

    def test_quoted_variable_is_allowed(self):
        findings, _ = scan('git ls-tree -r --name-only "$ref" -- tasks/\n')
        self.assertEqual(findings, [])

    def test_command_substitution_is_allowed(self):
        findings, _ = scan("next=$( git for-each-ref )\n")
        self.assertEqual(findings, [])

    def test_a_currency_amount_is_allowed(self):
        findings, _ = scan("The suite costs about $4.52 per run.\n")
        self.assertEqual(findings, [])

    def test_a_bare_dollar_is_allowed(self):
        findings, _ = scan("A `$` on its own means nothing to the substituter.\n")
        self.assertEqual(findings, [])


class Reporting(unittest.TestCase):
    def test_a_missing_scanned_file_is_an_error_not_a_silent_pass(self):
        with tempfile.TemporaryDirectory() as root:
            findings, errors = gate.scan(pathlib.Path(root))
        self.assertEqual(findings, [])
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
