#!/usr/bin/env python3
"""Unit tests for the release gate.

The failure this gate exists to catch is silent by nature: a fix merges, `version` does not
move, installed copies keep the old build, and `plugin update` reports "already at the latest
version" — every surface reporting health while nothing shipped. It happened once (task 003).

`git` is stubbed rather than driven against a real repository: the behavior under test is the
decision, not the plumbing, and a real repo would make these cases slow and fiddly to arrange.
Run:
    python3 scripts/check_release_test.py
"""

import contextlib
import importlib.util
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

_spec = importlib.util.spec_from_file_location(
    "check_release", pathlib.Path(__file__).with_name("check-release.py")
)
gate = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = gate
_spec.loader.exec_module(gate)

NAME = "cannery-row"


def fake_git(changed=None, old_version=None, base="deadbeef"):
    """Stand in for the three calls main() makes. `base=None` models a shallow clone or a first
    commit, where there is no baseline and the bump check must be skipped rather than guessed."""
    def _git(*args):
        if args[0] == "merge-base":
            return base
        if args[0] == "diff":
            return "\n".join(changed or [])
        if args[0] == "show":
            return json.dumps({"version": old_version}) if old_version else None
        return None
    return _git


@contextlib.contextmanager
def manifests(plugin_version="0.4.0", marketplace_version=None, entry_name=NAME, git=None):
    with tempfile.TemporaryDirectory() as root:
        plugin = pathlib.Path(root) / "plugin.json"
        marketplace = pathlib.Path(root) / "marketplace.json"
        plugin.write_text(json.dumps({"name": NAME, "version": plugin_version}), encoding="utf-8")
        marketplace.write_text(
            json.dumps({"plugins": [{
                "name": entry_name,
                "version": marketplace_version if marketplace_version is not None else plugin_version,
            }]}),
            encoding="utf-8",
        )
        saved = (gate.PLUGIN, gate.MARKETPLACE, gate.git)
        gate.PLUGIN, gate.MARKETPLACE = plugin, marketplace
        gate.git = git if git is not None else fake_git(base=None)
        try:
            yield
        finally:
            gate.PLUGIN, gate.MARKETPLACE, gate.git = saved


def run():
    with contextlib.redirect_stderr(io.StringIO()) as err, \
            contextlib.redirect_stdout(io.StringIO()) as out:
        code = gate.main()
    return code, out.getvalue(), err.getvalue()


class ManifestsAgree(unittest.TestCase):
    def test_matching_versions_pass(self):
        with manifests():
            code, out, _ = run()
        self.assertEqual(code, 0)
        self.assertIn("0.4.0", out)

    def test_version_mismatch_fails(self):
        with manifests(plugin_version="0.4.0", marketplace_version="0.3.0"):
            code, _, err = run()
        self.assertEqual(code, 1)
        self.assertIn("version mismatch", err)

    def test_mismatch_message_names_both_values(self):
        with manifests(plugin_version="0.4.0", marketplace_version="0.3.0"):
            _, _, err = run()
        self.assertIn("'0.4.0'", err)
        self.assertIn("'0.3.0'", err)

    def test_mismatch_explains_that_plugin_json_wins(self):
        # Why this is worth a build break: the divergence is invisible from either file alone.
        with manifests(plugin_version="0.4.0", marketplace_version="0.3.0"):
            _, _, err = run()
        self.assertIn("plugin.json wins at load time", err)

    def test_marketplace_entry_missing_fails(self):
        with manifests(entry_name="something-else"):
            code, _, err = run()
        self.assertEqual(code, 1)
        self.assertIn("would not be installable", err)


class VersionMovedWhenShippedContentDid(unittest.TestCase):
    def test_shipped_change_without_a_bump_fails(self):
        git = fake_git(changed=["skills/task-lifecycle/SKILL.md"], old_version="0.4.0")
        with manifests(plugin_version="0.4.0", git=git):
            code, _, err = run()
        self.assertEqual(code, 1)
        self.assertIn("installed content changed", err)
        self.assertIn("skills/task-lifecycle/SKILL.md", err)

    def test_failure_explains_the_silent_consequence(self):
        git = fake_git(changed=["scripts/generate-task-board.py"], old_version="0.4.0")
        with manifests(plugin_version="0.4.0", git=git):
            _, _, err = run()
        self.assertIn("already at the latest version", err)

    def test_shipped_change_with_a_bump_passes(self):
        git = fake_git(changed=["skills/task-lifecycle/SKILL.md"], old_version="0.3.0")
        with manifests(plugin_version="0.4.0", git=git):
            code, _, _ = run()
        self.assertEqual(code, 0)

    def test_every_shipped_prefix_requires_a_bump(self):
        for path in ("skills/x.md", "scripts/x.py", "tasks/README.md", ".claude-plugin/plugin.json"):
            with self.subTest(path=path):
                git = fake_git(changed=[path], old_version="0.4.0")
                with manifests(plugin_version="0.4.0", git=git):
                    code, _, _ = run()
                self.assertEqual(code, 1)

    def test_documentation_only_change_is_exempt(self):
        # README and this repo's own tasks/ inform; they do not install.
        git = fake_git(changed=["README.md", "CONTRIBUTING.md", "tasks/done/007-x.md"],
                       old_version="0.4.0")
        with manifests(plugin_version="0.4.0", git=git):
            code, _, _ = run()
        self.assertEqual(code, 0)

    def test_tasks_readme_is_shipped_but_other_task_files_are_not(self):
        # The boundary is exact: tasks/README.md installs, tasks/done/*.md does not.
        git = fake_git(changed=["tasks/wip/008-x.md"], old_version="0.4.0")
        with manifests(plugin_version="0.4.0", git=git):
            self.assertEqual(run()[0], 0)

    def test_no_baseline_skips_the_bump_check(self):
        # First commit, or a shallow clone. Absence of a baseline is not evidence of a problem.
        git = fake_git(changed=["skills/x.md"], old_version="0.4.0", base=None)
        with manifests(plugin_version="0.4.0", git=git):
            self.assertEqual(run()[0], 0)

    def test_unreadable_baseline_manifest_does_not_crash(self):
        git = fake_git(changed=["skills/x.md"], old_version=None)
        with manifests(plugin_version="0.4.0", git=git):
            self.assertEqual(run()[0], 0)


class GitHelper(unittest.TestCase):
    """The decisions above stub `git`, which would leave the one piece of real plumbing in this
    file untested. These two drive the actual subprocess against a throwaway repository."""

    @contextlib.contextmanager
    def _repo(self):
        with tempfile.TemporaryDirectory() as root:
            path = pathlib.Path(root)
            env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@e",
                   "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@e", "PATH": os.environ["PATH"]}
            subprocess.run(["git", "init", "-q", str(path)], check=True, env=env)
            (path / "f.txt").write_text("x", encoding="utf-8")
            subprocess.run(["git", "-C", str(path), "add", "f.txt"], check=True, env=env)
            subprocess.run(["git", "-C", str(path), "commit", "-qm", "c"], check=True, env=env)
            saved = gate.REPO_ROOT
            gate.REPO_ROOT = path
            try:
                yield
            finally:
                gate.REPO_ROOT = saved

    def test_successful_command_returns_stripped_output(self):
        with self._repo():
            head = gate.git("rev-parse", "HEAD")
        self.assertRegex(head or "", r"^[0-9a-f]{40}$")

    def test_failing_command_returns_none_rather_than_raising(self):
        # A missing baseline must degrade to "skip the check", never to a crashed build.
        with self._repo():
            self.assertIsNone(gate.git("rev-parse", "refs/heads/does-not-exist"))


class ProblemsAreReportedTogether(unittest.TestCase):
    def test_both_failures_reported_in_one_run(self):
        git = fake_git(changed=["skills/x.md"], old_version="0.4.0")
        with manifests(plugin_version="0.4.0", marketplace_version="0.1.0", git=git):
            code, _, err = run()
        self.assertEqual(code, 1)
        self.assertIn("2 release problem(s)", err)


if __name__ == "__main__":
    unittest.main()
