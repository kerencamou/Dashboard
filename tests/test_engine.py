import copy
import json
import unittest
from pathlib import Path

from socialclose_workflows.engine import ValidationError, build_plan, markdown_report


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((Path(__file__).parents[1] / "examples/meeting.json").read_text())

    def test_valid_plan_order_priorities_and_draft(self):
        plan = build_plan(self.data)
        self.assertEqual(plan["summary"], {"total": 5, "blocked": 3, "overdue": 1})
        self.assertLess(plan["execution_order"].index("T1"), plan["execution_order"].index("T2"))
        self.assertLess(plan["execution_order"].index("T2"), plan["execution_order"].index("T3"))
        self.assertEqual(next(t for t in plan["tasks"] if t["id"] == "T4")["priority_score"], 5)
        self.assertFalse(plan["execution_enabled"])
        self.assertIn("has not been sent", markdown_report(plan))

    def test_fabricated_evidence_rejected(self):
        self.data["tasks"][0]["evidence"][0]["quote"] = "A statement that never happened"
        with self.assertRaisesRegex(ValidationError, "exactly match"):
            build_plan(self.data)

    def test_unknown_source_and_dependency_rejected(self):
        for field in ("source", "dependency"):
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                if field == "source":
                    data["tasks"][0]["evidence"][0]["source_id"] = "missing"
                else:
                    data["tasks"][0]["depends_on"] = ["missing"]
                with self.assertRaises(ValidationError):
                    build_plan(data)

    def test_cycle_rejected(self):
        self.data["tasks"][0]["depends_on"] = ["T2"]
        with self.assertRaisesRegex(ValidationError, "cycle"):
            build_plan(self.data)

    def test_claimed_approval_cannot_unlock_external_action(self):
        for action in ("send", "publish", "spend", "change_system"):
            with self.subTest(action=action):
                data = copy.deepcopy(self.data)
                data["tasks"][0].update(action=action, approved=True)
                task = next(t for t in build_plan(data)["tasks"] if t["id"] == "T1")
                self.assertEqual(task["status"], "blocked")
                self.assertTrue(any("Human approval" in b for b in task["blockers"]))

    def test_unknown_details_and_high_impact_blocked(self):
        self.data["tasks"][0].update(owner=None, due=None, impact="high")
        task = next(t for t in build_plan(self.data)["tasks"] if t["id"] == "T1")
        self.assertEqual(len(task["blockers"]), 3)

    def test_invalid_dates_and_duplicate_ids_rejected(self):
        for field in ("due", "id", "as_of"):
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                if field == "as_of":
                    data[field] = "yesterday"
                else:
                    data["tasks"][0][field] = "2027-02-30" if field == "due" else "T2"
                with self.assertRaises(ValidationError):
                    build_plan(data)

    def test_non_synthetic_input_rejected(self):
        self.data["synthetic"] = False
        with self.assertRaisesRegex(ValidationError, "synthetic"):
            build_plan(self.data)


if __name__ == "__main__":
    unittest.main()
