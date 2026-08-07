#!/usr/bin/env python3
"""Unit tests for the generated task board.

Renderer tests are pure — `Task` fixtures are hand-built and fed straight to the
renderers, so lane placement, edge rendering, WIP breach and `done/` collapsing are
asserted on generated output rather than eyeballed. Only `load_tasks` gets a real
tree (a tempdir), because "the directory IS the status" is exactly the behavior
under test. Run:
    python3 scripts/generate_task_board_test.py
"""

import contextlib
import importlib.util
import io
import pathlib
import re
import sys
import tempfile
import unittest

_spec = importlib.util.spec_from_file_location(
    "generate_task_board",
    pathlib.Path(__file__).with_name("generate-task-board.py"),
)
gen = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = gen  # dataclass + `from __future__ import annotations` resolves via sys.modules
_spec.loader.exec_module(gen)


def task(number=100, lane="new", title=None, owner="smiley", updated="2026-08-01",
         completed="", blockers=(), done_when_items=1):
    return gen.Task(
        number=number,
        slug=f"task-{number}",
        lane=lane,
        title=title if title is not None else f"Task {number}",
        owner=owner,
        updated=updated,
        completed=completed,
        blockers=list(blockers),
        path=f"tasks/{lane}/{number:03d}-task-{number}.md",
        done_when_items=done_when_items,
    )


def write_task(root, lane, name, body):
    d = pathlib.Path(root) / "tasks" / lane
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(body, encoding="utf-8")


class Frontmatter(unittest.TestCase):
    def test_scalar_blocked_by_parsed(self):
        fm, _ = gen.parse_task("---\nstatus: new\nblocked-by: \"tasks/new/080-x.md\"\n---\n\n# T\n")
        self.assertEqual(fm["blocked-by"], "tasks/new/080-x.md")

    def test_trailing_comment_stripped_from_scalar(self):
        # `blocked-by: ""   # cleared 2026-08-04` is a real shape in this tree.
        fm, _ = gen.parse_task("---\nblocked-by: \"\"   # cleared 2026-08-04\n---\n\n# T\n")
        self.assertEqual(fm["blocked-by"], "")

    def test_list_blocked_by_parsed(self):
        fm, _ = gen.parse_task(
            "---\nblocked-by:\n  - \"tasks/wip/353-a.md\"\n  - \"tasks/new/080-b.md\"\nlinks:\n  - docs/x.md\n---\n\n# T\n"
        )
        self.assertEqual(fm["blocked-by"], ["tasks/wip/353-a.md", "tasks/new/080-b.md"])

    def test_h1_title_extracted(self):
        _, title = gen.parse_task("---\nstatus: new\n---\n\n# Real title here\n\nbody\n")
        self.assertEqual(title, "Real title here")


class BlockerClassification(unittest.TestCase):
    def test_task_path_resolves_to_a_number(self):
        kind, value = gen.classify_blocker("tasks/done/099-reconcile-adr.md")
        self.assertEqual((kind, value), ("task", 99))

    def test_unquoted_task_path_resolves(self):
        kind, value = gen.classify_blocker("tasks/new/354-generate-task-board-view.md")
        self.assertEqual((kind, value), ("task", 354))

    def test_dotted_slug_path_resolves(self):
        kind, value = gen.classify_blocker("tasks/done/098-feature-1.1-workspace-ci.md")
        self.assertEqual((kind, value), ("task", 98))

    def test_prose_blocker_is_external(self):
        kind, value = gen.classify_blocker("approaching first external release — see task 006")
        self.assertEqual(kind, "external")
        self.assertIn("external release", value)

    def test_empty_is_not_a_blocker(self):
        self.assertIsNone(gen.classify_blocker(""))


class LanePlacement(unittest.TestCase):
    def test_directory_not_frontmatter_decides_the_lane(self):
        # "Its location IS its status" — a stale `status:` field must not move the card.
        with tempfile.TemporaryDirectory() as root:
            write_task(root, "wip", "042-a.md", "---\nstatus: new\nowner: smiley\n---\n\n# A\n")
            loaded = gen.load_tasks(pathlib.Path(root))
            self.assertEqual([t.lane for t in loaded], ["wip"])

    def test_non_task_files_ignored(self):
        with tempfile.TemporaryDirectory() as root:
            write_task(root, "new", "042-a.md", "---\nowner: smiley\n---\n\n# A\n")
            write_task(root, "new", "README.md", "# not a task\n")
            self.assertEqual([t.number for t in gen.load_tasks(pathlib.Path(root))], [42])

    def test_templates_directory_is_not_a_lane(self):
        with tempfile.TemporaryDirectory() as root:
            write_task(root, "templates", "001-ceremony.md", "---\nowner: smiley\n---\n\n# Tmpl\n")
            self.assertEqual(gen.load_tasks(pathlib.Path(root)), [])

    def test_slugs_with_dots_are_tasks(self):
        # Real trackers carry dotted identifiers in slugs; a kebab-only charset
        # drops them from the count and from the graph, and the board reads plausibly wrong.
        with tempfile.TemporaryDirectory() as root:
            write_task(root, "done", "098-feature-1.1-workspace-ci.md",
                       "---\nowner: smiley\ncompleted: 2026-06-01\n---\n\n# Feature 1.1\n")
            write_task(root, "done", "165-x25519-dalek-3-rand_core-unification.md",
                       "---\nowner: smiley\ncompleted: 2026-06-02\n---\n\n# Unification\n")
            self.assertEqual([t.number for t in gen.load_tasks(pathlib.Path(root))], [98, 165])

    def test_gitkeep_is_not_a_task(self):
        with tempfile.TemporaryDirectory() as root:
            write_task(root, "new", ".gitkeep", "")
            self.assertEqual(gen.load_tasks(pathlib.Path(root)), [])

    def test_fields_and_blockers_loaded(self):
        with tempfile.TemporaryDirectory() as root:
            write_task(root, "blocked", "005-liability.md",
                       "---\nowner: smiley\nupdated: 2026-07-02\nblocked-by: \"tasks/new/006-x.md\"\n---\n\n# Liability plan\n")
            t = gen.load_tasks(pathlib.Path(root))[0]
            self.assertEqual((t.number, t.title, t.owner, t.updated), (5, "Liability plan", "smiley", "2026-07-02"))
            self.assertEqual(t.blockers, ["tasks/new/006-x.md"])


def cells(md, row):
    """Cells of the Nth body row of a markdown table (0-indexed, header + rule skipped). Splits on
    UNESCAPED pipes only — a naive split lands inside an escaped pipe in a card title and reports a
    correctly-escaped renderer as broken."""
    body = [ln for ln in md.splitlines() if ln.startswith("|")][2:]
    return [c.strip() for c in re.split(r"(?<!\\)\|", body[row].strip().strip("|"))]


class BoardColumns(unittest.TestCase):
    """The live lanes render as ONE table whose columns ARE the lanes. Stacked per-lane tables
    answer 'what is in lane N?' one lane at a time — which is what `ls` already did."""

    def test_header_columns_are_the_lanes_in_flow_order(self):
        md = gen.render_board_columns([task(number=1, lane=l) for l in gen.LIVE_LANES])
        header = [c.strip() for c in md.splitlines()[0].strip().strip("|").split("|")]
        self.assertEqual([h.split(" (")[0] for h in header], ["new", "prioritized", "wip", "blocked"])

    def test_each_column_header_carries_its_count(self):
        md = gen.render_board_columns([task(number=i, lane="new") for i in range(3)])
        self.assertIn("new (3)", md.splitlines()[0])
        self.assertIn("wip (0)", md.splitlines()[0])

    def test_prioritized_column_keeps_file_order_top_to_bottom(self):
        # prioritized/ ordering is meaningful (triage-criteria.md) — never re-sorted.
        md = gen.render_board_columns(
            [task(number=n, lane="prioritized") for n in (300, 101, 205)]
        )
        col = [cells(md, r)[1] for r in range(3)]
        self.assertEqual([c[c.index("[") + 1:c.index("]")] for c in col], ["300", "101", "205"])

    def test_row_count_is_the_longest_lane(self):
        md = gen.render_board_columns(
            [task(number=i, lane="new") for i in range(5)] + [task(number=99, lane="blocked")]
        )
        self.assertEqual(len([ln for ln in md.splitlines() if ln.startswith("|")]) - 2, 5)

    def test_short_lanes_get_empty_cells_not_shifted_cards(self):
        # Ragged columns: a card must never slide up into another lane's row.
        md = gen.render_board_columns(
            [task(number=i, lane="new") for i in range(3)] + [task(number=99, lane="blocked")]
        )
        self.assertEqual(cells(md, 1)[3], "")
        self.assertEqual(cells(md, 2)[3], "")

    def test_empty_lane_says_so_in_its_first_cell_only(self):
        md = gen.render_board_columns([task(number=i, lane="new") for i in range(3)])
        self.assertIn("nothing pulled", cells(md, 0)[2])
        self.assertEqual(cells(md, 1)[2], "")

    def test_card_links_the_number_and_carries_owner_and_date(self):
        md = gen.render_board_columns([task(number=354, updated="2026-08-02")])
        cell = cells(md, 0)[0]
        self.assertIn("../tasks/new/354-task-354.md", cell)
        self.assertIn("354", cell)
        self.assertIn("smiley", cell)
        self.assertIn("2026-08-02", cell)

    def test_card_uses_a_line_break_not_a_newline(self):
        # A literal newline inside a cell ends the row and breaks the whole table.
        md = gen.render_board_columns([task(number=1)])
        self.assertIn("<br>", cells(md, 0)[0])

    def test_long_title_is_truncated_to_the_cap(self):
        long = "Integration — " + "x" * 200
        md = gen.render_board_columns([task(title=long)])
        cell = cells(md, 0)[0]
        self.assertIn("…", cell)
        self.assertNotIn("x" * 100, cell)

    def test_short_title_is_left_alone(self):
        md = gen.render_board_columns([task(title="Short one")])
        self.assertIn("Short one", cells(md, 0)[0])
        self.assertNotIn("…", cells(md, 0)[0])

    def test_pipe_in_title_is_escaped(self):
        # An unescaped pipe silently splits the cell and shifts every lane right.
        md = gen.render_board_columns([task(title="a | b")])
        self.assertIn("a \\| b", cells(md, 0)[0])

    def test_blocked_card_distinguishes_a_condition_from_a_task(self):
        md = gen.render_board_columns([
            task(number=5, lane="blocked", blockers=["approaching first external release"]),
            task(number=6, lane="blocked", blockers=["tasks/new/097-confirm.md"]),
        ])
        self.assertIn("condition", cells(md, 0)[3])
        self.assertIn("097", cells(md, 1)[3])
        self.assertNotIn("condition", cells(md, 1)[3])

    def test_card_carries_no_wall_clock_derived_value(self):
        # An "idle days" figure would rewrite this committed file every midnight and the
        # freshness gate would go red on a day nobody touched a task.
        md = gen.render_board_columns([task(updated="2026-08-02")])
        self.assertNotRegex(cells(md, 0)[0], r"\b\d+d\b")


class DoneCollapsing(unittest.TestCase):
    def _pile(self, n):
        return [task(number=i, lane="done", completed=f"2026-07-{i:02d}") for i in range(1, n + 1)]

    def test_full_count_surfaced_even_though_rows_are_capped(self):
        # Assert the heading and the window/total pair, not a bare "28" — the row for task 028
        # supplies that substring on its own, so the loose form passes with the count zeroed.
        md = gen.render_done(self._pile(28), recent=5)
        self.assertIn("## done (28)", md)
        self.assertIn("5 most recently completed of 28", md)

    def test_only_the_recent_window_is_listed(self):
        md = gen.render_done(self._pile(28), recent=5)
        self.assertEqual(len([ln for ln in md.splitlines() if ln.startswith("| [")]), 5)

    def test_window_holds_the_most_recently_completed(self):
        md = gen.render_done(self._pile(28), recent=3)
        self.assertIn("| [028", md)
        self.assertIn("| [026", md)
        self.assertNotIn("| [001", md)

    def test_most_recent_first(self):
        md = gen.render_done(self._pile(28), recent=3)
        rows = [ln.split("]")[0] for ln in md.splitlines() if ln.startswith("| [")]
        self.assertEqual(rows, ["| [028", "| [027", "| [026"])

    def test_undated_done_tasks_sort_last_not_first(self):
        # An empty `completed:` must not masquerade as the newest entry.
        pile = self._pile(4) + [task(number=99, lane="done", completed="")]
        md = gen.render_done(pile, recent=4)
        self.assertNotIn("| [099", md)


class BlockedByGraph(unittest.TestCase):
    def test_edge_points_from_blocker_to_dependent(self):
        tasks = [task(number=97), task(number=80, blockers=["tasks/new/097-confirm.md"])]
        mermaid = gen.render_blocked_graph(tasks)
        self.assertIn("T097 --> T080", mermaid)

    def test_done_blockers_are_marked_satisfied(self):
        # A live task still pointing at a closed blocker is a stale-board signal worth seeing.
        tasks = [task(number=99, lane="done", completed="2026-07-01"),
                 task(number=80, blockers=["tasks/done/099-x.md"])]
        mermaid = gen.render_blocked_graph(tasks)
        self.assertIn("T099 --> T080", mermaid)
        self.assertIn("class T099 satisfied", mermaid)

    def test_prose_blocker_becomes_an_external_node(self):
        tasks = [task(number=291, lane="blocked", blockers=["incorporation decision deferred 2026-07-29"])]
        mermaid = gen.render_blocked_graph(tasks)
        self.assertIn("--> T291", mermaid)
        self.assertIn("incorporation decision", mermaid)

    def test_quotes_in_prose_blocker_do_not_break_the_label(self):
        tasks = [task(number=291, lane="blocked", blockers=['waiting on the "big" thing'])]
        mermaid = gen.render_blocked_graph(tasks)
        label = next(ln for ln in mermaid.splitlines() if "big" in ln)
        self.assertEqual(label.count('"'), 2)

    def test_done_dependents_are_not_drawn(self):
        # 276 closed tasks' historical blockers would drown the live chain.
        tasks = [task(number=97), task(number=80, lane="done", completed="2026-07-01",
                                       blockers=["tasks/new/097-confirm.md"])]
        self.assertNotIn("T097 --> T080", gen.render_blocked_graph(tasks))

    def test_no_edges_renders_no_diagram(self):
        md = gen.render_blocked_graph([task(number=1), task(number=2)])
        self.assertNotIn("```mermaid", md)


class WipLimit(unittest.TestCase):
    def test_breach_is_flagged(self):
        tasks = [task(number=i, lane="wip") for i in range(4)]
        self.assertEqual(gen.wip_breaches(tasks), [("smiley", 4)])

    def test_at_the_limit_is_not_a_breach(self):
        tasks = [task(number=i, lane="wip") for i in range(3)]
        self.assertEqual(gen.wip_breaches(tasks), [])

    def test_only_wip_lane_counts(self):
        tasks = [task(number=i, lane="prioritized") for i in range(9)]
        self.assertEqual(gen.wip_breaches(tasks), [])

    def test_agent_owners_do_not_count_against_a_human_limit(self):
        # The limit is one concurrent session per human, not per task-runner identity.
        tasks = [task(number=i, lane="wip", owner="agent") for i in range(9)]
        self.assertEqual(gen.wip_breaches(tasks), [])

    def test_co_owned_task_counts_against_the_human(self):
        tasks = [task(number=i, lane="wip", owner="smiley + claude") for i in range(4)]
        self.assertEqual(gen.wip_breaches(tasks), [("smiley", 4)])

    def test_breach_renders_the_warning_marker(self):
        md = gen.render_wip_check([task(number=i, lane="wip") for i in range(4)])
        self.assertIn("⚠️", md)
        self.assertIn("smiley", md)

    def test_within_limit_renders_no_warning_marker(self):
        md = gen.render_wip_check([task(number=i, lane="wip") for i in range(2)])
        self.assertNotIn("⚠️", md)


class Board(unittest.TestCase):
    def test_live_lanes_render_as_columns_above_the_done_pile(self):
        md = gen.render_board([task(number=1, lane=lane) for lane in gen.LANES])
        header = next(ln for ln in md.splitlines() if ln.startswith("| new ("))
        self.assertLess(md.index(header), md.index("## done ("))

    def test_no_per_lane_section_headings_remain(self):
        # The wall this replaced: one `## lane` + full-width table per lane, stacked.
        md = gen.render_board([task(number=1, lane=lane) for lane in gen.LANES])
        for lane in gen.LIVE_LANES:
            self.assertNotIn(f"## {lane} (", md)

    def test_board_is_marked_generated(self):
        md = gen.render_board([task()])
        self.assertIn("GENERATED FILE", md)
        self.assertIn("scripts/generate-task-board.py", md)

    def test_totals_line_counts_every_task(self):
        md = gen.render_board([task(number=1), task(number=2, lane="done", completed="2026-07-01")])
        self.assertIn("**2 tasks**", md)

    def test_render_is_deterministic(self):
        # A freshness gate over a non-deterministic render is a permanently red build.
        tasks = [task(number=1), task(number=2, lane="done", completed="2026-07-01")]
        self.assertEqual(gen.render_board(tasks), gen.render_board(tasks))


VALID_FM = (
    "---\ncreated: 2026-08-07\nupdated: 2026-08-07\ncompleted:\n"
    "status: new\nowner: tester\nblocked-by: \"\"\n---\n"
)


class DoneWhenParsing(unittest.TestCase):
    """`## Done when` IS the acceptance criteria — the only part of a task a later session
    with none of the author's context is held to. Distinguish absent from empty: both are
    holes, but they are different mistakes and deserve different messages."""

    def test_absent_heading_returns_none(self):
        self.assertIsNone(gen.parse_done_when("# T\n\n## Fix\n\n- [ ] not under a criteria heading\n"))

    def test_counts_checklist_items(self):
        self.assertEqual(gen.parse_done_when("# T\n\n## Done when\n- [ ] one\n- [x] two\n"), 2)

    def test_heading_present_but_empty_returns_zero(self):
        # The vacuous case: the completion gate resolves every unchecked box, and zero boxes
        # is trivially resolved. A heading with nothing under it is the same hole wearing a hat.
        self.assertEqual(gen.parse_done_when("# T\n\n## Done when\n\nSoon.\n"), 0)

    def test_heading_match_is_case_insensitive(self):
        self.assertEqual(gen.parse_done_when("# T\n\n## Done When\n- [ ] one\n"), 1)

    def test_struck_through_item_counts(self):
        # A deliberately skipped criterion is resolved, not missing.
        self.assertEqual(gen.parse_done_when("# T\n\n## Done when\n- ~~one~~ (superseded)\n"), 1)

    def test_indented_continuation_item_counts(self):
        self.assertEqual(gen.parse_done_when("# T\n\n## Done when\n  - [ ] nested\n"), 1)

    def test_section_ends_at_the_next_heading(self):
        text = "# T\n\n## Done when\n- [ ] one\n\n## Notes\n- [ ] not a criterion\n"
        self.assertEqual(gen.parse_done_when(text), 1)


class StructuralGate(unittest.TestCase):
    def test_well_formed_task_has_no_problems(self):
        self.assertEqual(gen.structural_problems([task()]), [])

    def test_missing_h1_is_reported_with_its_path(self):
        problems = gen.structural_problems([task(number=7, title="")])
        self.assertEqual(len(problems), 1)
        self.assertIn("tasks/new/007-task-7.md", problems[0])
        self.assertIn("H1", problems[0])

    def test_missing_done_when_is_reported_with_its_path(self):
        problems = gen.structural_problems([task(number=7, done_when_items=None)])
        self.assertEqual(len(problems), 1)
        self.assertIn("tasks/new/007-task-7.md", problems[0])
        self.assertIn("Done when", problems[0])

    def test_empty_done_when_is_distinguished_from_a_missing_one(self):
        problems = gen.structural_problems([task(done_when_items=0)])
        self.assertEqual(len(problems), 1)
        self.assertIn("no criteria under it", problems[0])

    def test_every_violation_is_reported_not_just_the_first(self):
        # Fix one, re-run, discover the next is the failure mode worth designing out.
        problems = gen.structural_problems([task(title="", done_when_items=None)])
        self.assertEqual(len(problems), 2)

    def test_done_lane_is_held_to_the_same_contract(self):
        # The requirement is every lane, not a completion-time audit.
        self.assertEqual(len(gen.structural_problems([task(lane="done", title="")])), 1)

    def test_problems_name_every_offending_file(self):
        problems = gen.structural_problems([task(number=7, title=""), task(number=8, title="")])
        self.assertEqual(len(problems), 2)
        self.assertTrue(any("007" in p for p in problems))
        self.assertTrue(any("008" in p for p in problems))


class GateBlocksTheBoard(unittest.TestCase):
    """The gate is only real if it stops the artifact from being produced. A warning printed
    beside a freshly written board is a warning nobody reads."""

    def _run(self, body, argv):
        with tempfile.TemporaryDirectory() as root:
            write_task(root, "new", "007-x.md", body)
            out = pathlib.Path(root) / "docs" / "task-board.md"
            saved = (gen.REPO_ROOT, gen.OUTPUT, sys.argv)
            gen.REPO_ROOT, gen.OUTPUT, sys.argv = pathlib.Path(root), out, argv
            try:
                with contextlib.redirect_stderr(io.StringIO()) as err, \
                        contextlib.redirect_stdout(io.StringIO()):
                    code = gen.main()
            finally:
                gen.REPO_ROOT, gen.OUTPUT, sys.argv = saved
            return code, out.exists(), err.getvalue()

    def test_invalid_task_fails_and_writes_no_board(self):
        code, wrote, _ = self._run(VALID_FM + "\nNo heading anywhere.\n", ["gen"])
        self.assertEqual(code, 1)
        self.assertFalse(wrote)

    def test_invalid_task_fails_check_mode_too(self):
        code, _, _ = self._run(VALID_FM + "\nNo heading anywhere.\n", ["gen", "--check"])
        self.assertEqual(code, 1)

    def test_failure_names_the_file_and_says_how_to_fix_it(self):
        _, _, err = self._run(VALID_FM + "\nNo heading anywhere.\n", ["gen"])
        self.assertIn("tasks/new/007-x.md", err)
        self.assertIn("fix:", err)

    def test_valid_task_still_writes_the_board(self):
        body = VALID_FM + "\n# A real title\n\n## Done when\n- [ ] one\n"
        code, wrote, _ = self._run(body, ["gen"])
        self.assertEqual(code, 0)
        self.assertTrue(wrote)


class LoadsBodyContract(unittest.TestCase):
    def test_done_when_items_populated_from_disk(self):
        with tempfile.TemporaryDirectory() as root:
            write_task(root, "new", "007-x.md", VALID_FM + "\n# T\n\n## Done when\n- [ ] a\n- [ ] b\n")
            write_task(root, "new", "008-y.md", VALID_FM + "\n# T\n\n## Fix\n\nnothing\n")
            loaded = {t.number: t for t in gen.load_tasks(pathlib.Path(root))}
        self.assertEqual(loaded[7].done_when_items, 2)
        self.assertIsNone(loaded[8].done_when_items)


if __name__ == "__main__":
    unittest.main()
