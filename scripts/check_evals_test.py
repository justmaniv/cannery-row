#!/usr/bin/env python3
"""Unit tests for the eval suite's structural gate.

This gate exists because the behavioral suite is expensive and runs on a human's machine:
every breakage it catches is one a contributor would otherwise discover after paying for a
run. So the gate's own failure modes are the ones worth pinning — particularly the
all-`with-only` case, where a suite built entirely around a with/without delta quietly
stops being able to produce one. Run:
    python3 scripts/check_evals_test.py
"""

import contextlib
import importlib.util
import io
import pathlib
import sys
import tempfile
import textwrap
import unittest

_spec = importlib.util.spec_from_file_location(
    "check_evals", pathlib.Path(__file__).with_name("check-evals.py")
)
gate = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = gate
_spec.loader.exec_module(gate)

VALID = """\
schema_version: "1.1"
name: sweep
context:
  scaffold_script: scaffold.sh
graders:
  - type: file_exists
    name: landed
    path: tasks/done/012.md
  - type: tool_used
    name: used-skill
    tool: Skill
    arm: with-only
"""


@contextlib.contextmanager
def suite(cases, with_scaffold=True):
    """A repo root holding an evals/ tree. `check_case` renders paths relative to REPO_ROOT,
    so both module globals have to move with the tempdir or the report names a path that
    does not exist."""
    with tempfile.TemporaryDirectory() as root:
        evals = pathlib.Path(root) / "evals"
        for name, text in cases.items():
            case_dir = evals / name
            case_dir.mkdir(parents=True)
            if text is not None:
                (case_dir / "case.yaml").write_text(textwrap.dedent(text), encoding="utf-8")
            if with_scaffold:
                (case_dir / "scaffold.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
        saved = (gate.REPO_ROOT, gate.EVALS_DIR)
        gate.REPO_ROOT, gate.EVALS_DIR = pathlib.Path(root), evals
        try:
            yield evals
        finally:
            gate.REPO_ROOT, gate.EVALS_DIR = saved


def run_main():
    err, out = io.StringIO(), io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
        code = gate.main()
    return code, err.getvalue() + out.getvalue()


class WellFormedSuite(unittest.TestCase):
    def test_valid_case_passes(self):
        with suite({"sweep": VALID}):
            code, text = run_main()
        self.assertEqual(code, 0)
        self.assertIn("1 eval case(s) well-formed", text)

    def test_missing_evals_dir_is_not_a_failure(self):
        """A repo that has not written any evals yet is not broken."""
        with tempfile.TemporaryDirectory() as root:
            saved = (gate.REPO_ROOT, gate.EVALS_DIR)
            gate.REPO_ROOT = pathlib.Path(root)
            gate.EVALS_DIR = pathlib.Path(root) / "evals"
            try:
                code, text = run_main()
            finally:
                gate.REPO_ROOT, gate.EVALS_DIR = saved
        self.assertEqual(code, 0)
        self.assertIn("nothing to check", text)

    def test_results_dir_is_not_treated_as_a_case(self):
        """`--output-dir` defaults to evals/results/<timestamp>/, which is not a case."""
        with suite({"sweep": VALID, "results": None}, with_scaffold=False) as evals:
            (evals / "sweep" / "scaffold.sh").write_text("#!/bin/sh\n", encoding="utf-8")
            code, text = run_main()
        self.assertEqual(code, 0)
        self.assertIn("1 eval case(s)", text)


class Breakages(unittest.TestCase):
    def test_case_dir_without_case_yaml(self):
        with suite({"sweep": None}):
            code, text = run_main()
        self.assertEqual(code, 1)
        self.assertIn("has no case.yaml", text)

    def test_missing_required_keys(self):
        with suite({"sweep": 'name: sweep\n'}):
            code, text = run_main()
        self.assertEqual(code, 1)
        self.assertIn("missing 'schema_version'", text)
        self.assertIn("missing 'graders'", text)

    def test_name_disagreeing_with_directory(self):
        """--case filters on the declared name, so the case you ask for is not the one that runs."""
        with suite({"sweep": VALID.replace("name: sweep", "name: something-else", 1)}):
            code, text = run_main()
        self.assertEqual(code, 1)
        self.assertIn("--case filters on the declared name", text)

    def test_missing_scaffold_script(self):
        with suite({"sweep": VALID}, with_scaffold=False):
            code, text = run_main()
        self.assertEqual(code, 1)
        self.assertIn("does not exist", text)

    def test_every_grader_with_only(self):
        """The failure this gate exists for: a delta computed against a baseline that scores nothing."""
        with suite({"sweep": """\
            schema_version: "1.1"
            name: sweep
            graders:
              - type: tool_used
                name: used-skill
                tool: Skill
                arm: with-only
            """}):
            code, text = run_main()
        self.assertEqual(code, 1)
        self.assertIn("the reported delta is meaningless", text)

    def test_empty_grader_list(self):
        with suite({"sweep": 'schema_version: "1.1"\nname: sweep\ngraders: []\n'}):
            code, text = run_main()
        self.assertEqual(code, 1)
        self.assertIn("at least one grader", text)

    def test_graders_key_with_no_entries(self):
        with suite({"sweep": 'schema_version: "1.1"\nname: sweep\ngraders: nope\n'}):
            code, text = run_main()
        self.assertEqual(code, 1)
        self.assertIn("at least one grader", text)

    def test_a_graders_name_does_not_masquerade_as_the_cases_name(self):
        """Graders carry their own `name:`, indented. Only column zero is the case's."""
        with suite({"sweep": """\
            schema_version: "1.1"
            name: sweep
            graders:
              - type: file_exists
                name: some-grader-called-something-else
                path: tasks/done/012.md
            """}, with_scaffold=False):
            code, text = run_main()
        self.assertEqual(code, 0, text)

    def test_quoted_name_is_compared_unquoted(self):
        with suite({"sweep": 'schema_version: "1.1"\nname: "sweep"\ngraders:\n  - type: file_exists\n'},
                   with_scaffold=False):
            code, text = run_main()
        self.assertEqual(code, 0, text)

    def test_reports_every_broken_case_not_just_the_first(self):
        with suite({"one": None, "two": None}):
            code, text = run_main()
        self.assertEqual(code, 1)
        self.assertIn("2 eval suite problem(s)", text)


if __name__ == "__main__":
    unittest.main()
