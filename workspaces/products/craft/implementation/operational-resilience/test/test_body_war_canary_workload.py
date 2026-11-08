import unittest

from src.body_war_canary_contracts import WorkloadSummary
from src.body_war_canary_workload import build_schedule, validate_workload


class WorkloadTests(unittest.TestCase):
    def test_exact_ten_hz_and_900_ceiling(self):
        schedule = build_schedule(100.0, 90)
        self.assertEqual(len(schedule), 900)
        self.assertAlmostEqual(schedule[1] - schedule[0], 0.1)
        with self.assertRaisesRegex(ValueError, "CEILING"):
            build_schedule(100.0, 91)

    def test_valid_and_hostile_generator_summaries(self):
        valid, reasons = validate_workload(WorkloadSummary(450, 446, 446, 10, 100))
        self.assertTrue(valid)
        self.assertEqual(reasons, ())
        cases = [
            WorkloadSummary(450, 445, 445, 10, 0),
            WorkloadSummary(450, 450, 449, 10, 0),
            WorkloadSummary(450, 450, 450, 11, 0),
            WorkloadSummary(450, 450, 450, 21, 0),
            WorkloadSummary(450, 450, 450, 10, 101),
            WorkloadSummary(450, 450, 450, 10, 0, True),
        ]
        for summary in cases:
            with self.subTest(summary=summary):
                self.assertFalse(validate_workload(summary)[0])


if __name__ == "__main__":
    unittest.main()
