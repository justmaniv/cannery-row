#!/usr/bin/env python3
"""Unit tests for the workflow safety gate.

This is the gate whose failure causes harm rather than mess: it is the only thing between a
public repository and a fork's pull request executing on a self-hosted runner that holds deploy
credentials. It was verified once by hand, by injecting violations. These tests are that
verification, kept. Run:
    python3 scripts/check_workflows_test.py
"""

import contextlib
import importlib.util
import io
import pathlib
import sys
import tempfile
import unittest

_spec = importlib.util.spec_from_file_location(
    "check_workflows", pathlib.Path(__file__).with_name("check-workflows.py")
)
gate = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = gate
_spec.loader.exec_module(gate)

CLEAN = """\
name: CI
on:
  pull_request:
  push:
    branches: [main]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
"""


@contextlib.contextmanager
def workflow(text, name="ci.yml"):
    """A repo root holding one workflow. `check_file` renders paths relative to REPO_ROOT, so
    that global has to move with the tempdir or the report names the wrong file."""
    with tempfile.TemporaryDirectory() as root:
        wf_dir = pathlib.Path(root) / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        path = wf_dir / name
        path.write_text(text, encoding="utf-8")
        saved = (gate.REPO_ROOT, gate.WORKFLOW_DIR)
        gate.REPO_ROOT, gate.WORKFLOW_DIR = pathlib.Path(root), wf_dir
        try:
            yield path
        finally:
            gate.REPO_ROOT, gate.WORKFLOW_DIR = saved


class SafeWorkflow(unittest.TestCase):
    def test_clean_workflow_has_no_problems(self):
        with workflow(CLEAN) as path:
            self.assertEqual(gate.check_file(path), [])

    def test_every_allowed_runner_passes(self):
        for runner in sorted(gate.ALLOWED_RUNNERS):
            with self.subTest(runner=runner):
                with workflow(CLEAN.replace("ubuntu-latest", runner)) as path:
                    self.assertEqual(gate.check_file(path), [])


class SelfHostedRunner(unittest.TestCase):
    def test_bare_self_hosted_label_is_caught(self):
        with workflow(CLEAN.replace("ubuntu-latest", "self-hosted")) as path:
            problems = gate.check_file(path)
        self.assertEqual(len(problems), 1)
        self.assertIn("self-hosted", problems[0])
        self.assertIn("fork PR would execute on that machine", problems[0])

    def test_label_list_form_is_caught(self):
        # The realistic shape: a job copy-pasted from the upstream project brings its labels.
        with workflow(CLEAN.replace("ubuntu-latest", "[self-hosted, linux, ehap]")) as path:
            problems = gate.check_file(path)
        self.assertEqual(len(problems), 1)
        self.assertIn("self-hosted", problems[0])

    def test_problem_names_the_file_and_line(self):
        with workflow(CLEAN.replace("ubuntu-latest", "self-hosted")) as path:
            problems = gate.check_file(path)
        self.assertIn(".github/workflows/ci.yml:8", problems[0])


class NonStandardRunner(unittest.TestCase):
    def test_larger_runner_is_rejected_because_it_bills(self):
        with workflow(CLEAN.replace("ubuntu-latest", "ubuntu-latest-8-core")) as path:
            problems = gate.check_file(path)
        self.assertEqual(len(problems), 1)
        self.assertIn("Larger runners bill even on public repos", problems[0])

    def test_other_hosted_platforms_are_rejected(self):
        with workflow(CLEAN.replace("ubuntu-latest", "macos-14")) as path:
            self.assertEqual(len(gate.check_file(path)), 1)


class PullRequestTargetTrigger(unittest.TestCase):
    def test_block_form_is_caught(self):
        with workflow(CLEAN.replace("  pull_request:", "  pull_request_target:")) as path:
            problems = gate.check_file(path)
        self.assertEqual(len(problems), 1)
        self.assertIn("write-scoped token", problems[0])

    def test_inline_list_form_is_caught(self):
        text = "name: CI\non: [pull_request_target]\njobs:\n  c:\n    runs-on: ubuntu-latest\n"
        with workflow(text) as path:
            problems = gate.check_file(path)
        self.assertEqual(len(problems), 1)
        self.assertIn("Use pull_request", problems[0])

    def test_inline_scalar_form_is_caught(self):
        text = "name: CI\non: pull_request_target\njobs:\n  c:\n    runs-on: ubuntu-latest\n"
        with workflow(text) as path:
            self.assertEqual(len(gate.check_file(path)), 1)

    def test_plain_pull_request_is_not_flagged(self):
        text = "name: CI\non: [pull_request]\njobs:\n  c:\n    runs-on: ubuntu-latest\n"
        with workflow(text) as path:
            self.assertEqual(gate.check_file(path), [])


class CommentsAreNotCode(unittest.TestCase):
    """The gate is structural precisely so it can describe itself. A textual grep would match
    the comments explaining why these settings are forbidden — and a gate that fails on its own
    documentation gets deleted the first time it is inconvenient."""

    def test_forbidden_terms_in_comments_are_ignored(self):
        text = CLEAN.replace(
            "jobs:",
            "# Never self-hosted, and never pull_request_target: a fork would run here.\njobs:",
        )
        with workflow(text) as path:
            self.assertEqual(gate.check_file(path), [])

    def test_trailing_comment_after_a_valid_runner_is_ignored(self):
        text = CLEAN.replace("ubuntu-latest", "ubuntu-latest  # never self-hosted")
        with workflow(text) as path:
            self.assertEqual(gate.check_file(path), [])


class Cli(unittest.TestCase):
    def _main(self):
        with contextlib.redirect_stderr(io.StringIO()) as err, \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = gate.main()
        return code, out.getvalue(), err.getvalue()

    def test_safe_workflow_exits_zero(self):
        with workflow(CLEAN):
            code, out, _ = self._main()
        self.assertEqual(code, 0)
        self.assertIn("GitHub-hosted runners only", out)

    def test_unsafe_workflow_exits_one(self):
        with workflow(CLEAN.replace("ubuntu-latest", "self-hosted")):
            code, _, err = self._main()
        self.assertEqual(code, 1)
        self.assertIn("unsafe:", err)

    def test_yaml_extension_is_scanned_too(self):
        with workflow(CLEAN.replace("ubuntu-latest", "self-hosted"), name="other.yaml"):
            code, _, _ = self._main()
        self.assertEqual(code, 1)

    def test_missing_workflow_directory_fails(self):
        with tempfile.TemporaryDirectory() as root:
            saved = gate.WORKFLOW_DIR
            gate.WORKFLOW_DIR = pathlib.Path(root) / "nope"
            try:
                code, _, err = self._main()
            finally:
                gate.WORKFLOW_DIR = saved
        self.assertEqual(code, 1)
        self.assertIn("no workflow directory", err)

    def test_empty_workflow_directory_fails(self):
        # A repo with CI deleted should not report "ok: 0 workflows".
        with tempfile.TemporaryDirectory() as root:
            wf_dir = pathlib.Path(root) / ".github" / "workflows"
            wf_dir.mkdir(parents=True)
            saved = gate.WORKFLOW_DIR
            gate.WORKFLOW_DIR = wf_dir
            try:
                code, _, err = self._main()
            finally:
                gate.WORKFLOW_DIR = saved
        self.assertEqual(code, 1)
        self.assertIn("no workflows found", err)


if __name__ == "__main__":
    unittest.main()
