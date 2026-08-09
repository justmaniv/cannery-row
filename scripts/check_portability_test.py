#!/usr/bin/env python3
"""Unit tests for the portability gate.

`scan()` takes a repo root, so every case is a small tree in a tempdir rather than an
assertion about this repository — which would test the content, not the gate. Run:
    python3 scripts/check_portability_test.py
"""

import contextlib
import importlib.util
import io
import pathlib
import sys
import tempfile
import unittest

_spec = importlib.util.spec_from_file_location(
    "check_portability", pathlib.Path(__file__).with_name("check-portability.py")
)
gate = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = gate
_spec.loader.exec_module(gate)


def tree(root, **overrides):
    """Write every scanned path so `scan()` reports findings, not missing-file errors."""
    for rel in gate.SCANNED:
        path = pathlib.Path(root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(overrides.get(rel, "# Clean\n\nNothing coupled here.\n"), encoding="utf-8")
    return pathlib.Path(root)


SKILL = "skills/task-lifecycle/SKILL.md"
BOARD = "docs/task-board.md"


class CleanTree(unittest.TestCase):
    def test_no_findings_and_no_errors(self):
        with tempfile.TemporaryDirectory() as root:
            findings, errors = gate.scan(tree(root))
        self.assertEqual(findings, [])
        self.assertEqual(errors, [])


class ForbiddenVocabulary(unittest.TestCase):
    def _scan(self, text, rel=SKILL):
        with tempfile.TemporaryDirectory() as root:
            return gate.scan(tree(root, **{rel: text}))

    def test_forbidden_term_is_reported_with_file_and_line(self):
        findings, _ = self._scan("# T\n\nline two\nPlan the sprint carefully.\n")
        self.assertEqual(len(findings), 1)
        self.assertIn(f"{SKILL}:4", findings[0])

    def test_finding_explains_why_and_suggests_a_replacement(self):
        findings, _ = self._scan("Run this each sprint.\n")
        self.assertIn("a cadence not every team runs", findings[0])
        self.assertIn("planning cycle", findings[0])

    def test_finding_quotes_the_offending_line(self):
        findings, _ = self._scan("Ship it with cargo build.\n")
        self.assertIn("Ship it with cargo build.", findings[0])

    def test_match_is_case_insensitive(self):
        # The real incident was prose that read as generic; capitalisation is not a defence.
        findings, _ = self._scan("Sprint planning happens here.\n")
        self.assertEqual(len(findings), 1)

    def test_suffixed_form_is_caught(self):
        # "sprints"/"backlogged" are the same coupling wearing a plural.
        findings, _ = self._scan("Several sprints later.\n")
        self.assertEqual(len(findings), 1)

    def test_term_embedded_mid_word_is_not_a_hit(self):
        # The gate is dumb on purpose, but not so dumb it cries at every substring.
        findings, _ = self._scan("The offspringed nonsense word.\n")
        self.assertEqual(findings, [])

    def test_upstream_project_names_are_caught(self):
        findings, _ = self._scan("Deploy with flyctl to the kist backend.\n")
        self.assertEqual(len(findings), 2)

    def test_every_scanned_file_is_actually_scanned(self):
        # A file silently dropped from the list is the failure this gate cannot self-report.
        for rel in gate.SCANNED:
            with self.subTest(rel=rel):
                findings, _ = self._scan("A supabase reference.\n", rel=rel)
                self.assertTrue(any(rel in f for f in findings))


class HostWorkflowVocabulary(unittest.TestCase):
    """Remote names and host review mechanics are collaboration topology, not git primitives.
    This class of coupling shipped seven times over while the gate looked only for languages,
    vendors, and cadence words — task 017 is the incident report."""

    def _scan(self, text):
        with tempfile.TemporaryDirectory() as root:
            return gate.scan(tree(root, **{SKILL: text}))[0]

    def test_remote_and_host_review_vocabulary_is_caught(self):
        for line in [
            "reset the branch to origin/main first\n",
            "leave branches with an open PR\n",
            "close stale PRs weekly\n",
            "now that main is PR-protected\n",
            "open a pull request for review\n",
            "requires branch protection on main\n",
        ]:
            with self.subTest(line=line):
                self.assertEqual(len(self._scan(line)), 1)

    def test_abbreviation_does_not_swallow_ordinary_words(self):
        # 'PR' must match as an exact, case-sensitive word: the suffix wildcard the other
        # terms use would flag 'provenance', 'procedure', and every 'Press'.
        self.assertEqual(self._scan("Provenance is the point of the procedure. Press on.\n"), [])

    def test_push_is_deliberately_not_forbidden(self):
        # The skill legitimately instructs a *conditional* push ("if `git remote` prints
        # anything") — the word is the fix, not the coupling. Guard the decision so a future
        # sweep doesn't add it and break the skill's own gate.
        self.assertNotIn("push", gate.FORBIDDEN)
        self.assertEqual(self._scan("commit always; push when a remote exists\n"), [])


class StructuralErrors(unittest.TestCase):
    def test_missing_scanned_file_is_an_error_not_a_finding(self):
        with tempfile.TemporaryDirectory() as root:
            tree(root)
            (pathlib.Path(root) / SKILL).unlink()
            findings, errors = gate.scan(pathlib.Path(root))
        self.assertEqual(findings, [])
        self.assertEqual(len(errors), 1)
        self.assertIn(SKILL, errors[0])


class GeneratedArtifactLinks(unittest.TestCase):
    """A generated board ships into somebody else's repo. A relative link that resolved here
    404s there — and unlike vocabulary, a 404 cannot be argued for."""

    def _scan_board(self, text):
        with tempfile.TemporaryDirectory() as root:
            return gate.scan(tree(root, **{BOARD: text}))[0]

    def test_link_outside_the_repo_is_flagged(self):
        findings = self._scan_board("See [the log](../docs/decisions/0038-thing.md).\n")
        self.assertEqual(len(findings), 1)
        self.assertIn("404s downstream", findings[0])

    def test_task_links_are_portable(self):
        self.assertEqual(self._scan_board("[007](../tasks/done/007-x.md)\n"), [])

    def test_absolute_urls_are_ignored(self):
        self.assertEqual(self._scan_board("[home](https://example.com/x)\n"), [])

    def test_anchor_links_are_ignored(self):
        self.assertEqual(self._scan_board("[section](#done-when)\n"), [])

    def test_link_rule_applies_only_to_generated_files(self):
        # SKILL.md is authored, not emitted; its links are a human's problem, not the gate's.
        with tempfile.TemporaryDirectory() as root:
            findings, _ = gate.scan(tree(root, **{SKILL: "[x](../elsewhere/y.md)\n"}))
        self.assertEqual(findings, [])


class Cli(unittest.TestCase):
    def _main(self, argv, root=None):
        saved = (gate.REPO_ROOT, sys.argv)
        gate.REPO_ROOT, sys.argv = (root or gate.REPO_ROOT), argv
        try:
            with contextlib.redirect_stderr(io.StringIO()) as err, \
                    contextlib.redirect_stdout(io.StringIO()) as out:
                code = gate.main()
        finally:
            gate.REPO_ROOT, sys.argv = saved
        return code, out.getvalue(), err.getvalue()

    def test_list_prints_the_vocabulary_and_exits_zero(self):
        code, out, _ = self._main(["check-portability.py", "--list"])
        self.assertEqual(code, 0)
        self.assertIn("sprint", out)
        self.assertEqual(len(out.strip().splitlines()), len(gate.FORBIDDEN))

    def test_clean_tree_exits_zero(self):
        with tempfile.TemporaryDirectory() as root:
            code, out, _ = self._main(["check-portability.py"], tree(root))
        self.assertEqual(code, 0)
        self.assertIn("no stack-coupled vocabulary", out)

    def test_coupled_tree_exits_one_and_says_why_on_stderr(self):
        with tempfile.TemporaryDirectory() as root:
            code, _, err = self._main(["check-portability.py"], tree(root, **{SKILL: "a sprint\n"}))
        self.assertEqual(code, 1)
        self.assertIn("not portable", err)
        self.assertIn("FAIL", err)

    def test_missing_file_exits_one(self):
        with tempfile.TemporaryDirectory() as root:
            tree(root)
            (pathlib.Path(root) / BOARD).unlink()
            code, _, err = self._main(["check-portability.py"], pathlib.Path(root))
        self.assertEqual(code, 1)
        self.assertIn("error:", err)


if __name__ == "__main__":
    unittest.main()
