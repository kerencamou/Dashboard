import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from studio import BriefError, build_pack, calendar_csv, render


class StudioTests(unittest.TestCase):
    def setUp(self):
        self.brief = json.loads((Path(__file__).parents[1]/"examples/brief.json").read_text())

    def test_seven_formats_and_calendar(self):
        pack = build_pack(self.brief)
        self.assertEqual(len(pack["assets"]), 7)
        self.assertEqual(len({a["format"] for a in pack["assets"]}), 7)
        self.assertEqual(pack["assets"][-1]["suggested_date"], "2027-01-24")
        self.assertIn("Source ledger", render(pack))
        self.assertEqual(len(calendar_csv(pack).splitlines()), 8)

    def test_unverified_claim_quote_rejected(self):
        self.brief["claims"][0]["quote"] = "An invented statistic"
        with self.assertRaises(BriefError):
            build_pack(self.brief)

    def test_duplicate_hooks_and_options_rejected(self):
        for field in ("hooks", "poll_options"):
            with self.subTest(field=field):
                brief = copy.deepcopy(self.brief)
                brief[field][1] = brief[field][0]
                with self.assertRaises(BriefError):
                    build_pack(brief)

    def test_claimed_approval_never_enables_publishing(self):
        self.brief["approved"] = True
        pack = build_pack(self.brief)
        self.assertFalse(pack["publishing_connected"])
        self.assertTrue(all(a["status"] == "draft" and not a["publish_allowed"] for a in pack["assets"]))

    def test_voice_and_numeric_flags(self):
        self.brief["hooks"][0] = "Guaranteed results: 50% better"
        asset = build_pack(self.brief)["assets"][0]
        self.assertTrue(any("Banned phrase" in x for x in asset["review_flags"]))
        self.assertTrue(any("percentage" in x for x in asset["review_flags"]))

    def test_csv_formula_prefix_escaped(self):
        self.brief["hooks"][0] = '=HYPERLINK("example")'
        self.assertIn("'=HYPERLINK", calendar_csv(build_pack(self.brief)))

    def test_non_synthetic_and_bad_date_rejected(self):
        for field, value in (("synthetic", False), ("start_date", "2027-02-30")):
            with self.subTest(field=field):
                brief = copy.deepcopy(self.brief)
                brief[field] = value
                with self.assertRaises(BriefError):
                    build_pack(brief)


if __name__ == "__main__":
    unittest.main()
