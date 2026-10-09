import unittest
from datetime import date

from matching import match_opportunities, parse_opportunity


def record(**changes):
    base = {"Name":"Sample", "Subjects":["Math"], "Grade":9, "Type":"Competition",
            "Format":"Online", "Location":"Online", "Cost":100, "Deadline":"2026-10-08",
            "Description":"Sample description", "Link":"https://example.org/"}
    return {**base, **changes}


class MatchingTests(unittest.TestCase):
    def test_exact_grade_budget_and_deadline_are_eligible(self):
        result = match_opportunities([record()], 9, 100, "Math", "Online", "Any", date(2026,10,8))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["score"], 5)

    def test_grade_budget_expiry_and_type_are_hard_filters(self):
        candidates = [record(), record(Name="Grade", Grade=10), record(Name="Cost", Cost=101),
                      record(Name="Expired", Deadline="2026-10-07"), record(Name="Type", Type="Research")]
        result = match_opportunities(candidates, 9, 100, "Math", "Online", "Competition", date(2026,10,8))
        self.assertEqual([x["name"] for x in result], ["Sample"])

    def test_any_type_does_not_add_score_and_paid_is_not_penalized(self):
        paid = record(Cost=100)
        free = record(Name="Free", Cost=0)
        results = match_opportunities([paid, free], 9, 100, "Math", "Online", "Any", date(2026,10,1))
        self.assertEqual([x["score"] for x in results], [5, 5])

    def test_both_means_no_format_preference(self):
        results = match_opportunities([record()], 9, 100, "Math", "Both", "Any", date(2026,10,1))
        self.assertEqual(results[0]["score"], 3)
        self.assertFalse(any("format preference" in reason.lower() for reason in results[0]["reasons"]))

    def test_legacy_subject_is_supported_without_mutating_record(self):
        item = record(Subjects=["Science"], Subject="Math")
        old_subjects = list(item["Subjects"])
        result = match_opportunities([item], 9, 100, "Math", "Onsite", "Any", date(2026,10,1))
        self.assertEqual(result[0]["score"], 3)
        self.assertEqual(item["Subjects"], old_subjects)

    def test_malformed_record_is_skipped(self):
        self.assertIsNone(parse_opportunity(record(Deadline="not-a-date")))
        self.assertEqual(match_opportunities([None, record(Cost="free")], 9, 500, "Math", "Both", "Any", date(2026,10,1)), [])

    def test_sorting_and_no_match(self):
        records = [record(Name="No preference", Subjects=["Science"], Format="Onsite"), record(Name="Subject", Format="Onsite"), record(Name="Top")]
        results = match_opportunities(records, 9, 500, "Math", "Online", "Any", date(2026,10,1))
        self.assertEqual([r["name"] for r in results], ["Top", "Subject", "No preference"])
        self.assertEqual(match_opportunities([record(Grade=12)], 9, 500, "Math", "Online", "Any", date(2026,10,1)), [])


if __name__ == "__main__":
    unittest.main()
