import copy
import json
from pathlib import Path
import unittest
from unittest import mock

import probe as P


class StatusDependencyProbeTests(unittest.TestCase):
    def test_cold_result(self):
        result = P.run()
        self.assertEqual(result, json.loads((Path(__file__).parent / "RESULT.json").read_bytes()))
        self.assertEqual(result["clean_root_guard_subset_verified"], 7)
        self.assertFalse(result["current_service_operation_executed"])
        self.assertFalse(result["portable_closure_complete"])
        self.assertEqual(result["full_source_guard_coverage_counts"],
                         {"archive-byte-selected": 1, "unresolved": 147,
                          "not-in-profile": 59})

    def test_missing_and_changed_byte_refuse(self):
        rows, payload = P.inputs()
        self.assertEqual(P.exercise(rows, payload, "missing"), "REFUSED")
        self.assertEqual(P.exercise(rows, payload, "changed"), "REFUSED")
        self.assertEqual(P.exercise(rows, payload), "PASS")

    def test_altered_selected_dependency_refused(self):
        rows, payload = P.inputs()
        bad = dict(payload)
        bad[P.NAMES[-1]] = b"wrong\n"
        with self.assertRaisesRegex(ValueError, "source changed"):
            P.exercise(rows, bad)
        with self.assertRaisesRegex(ValueError, "selected bytes changed"):
            P.selected(P.NAMES[-1], "0" * 64)

    def test_archive_disposition_upgrade_cannot_be_assumed(self):
        actual = P.selected
        def forged(name, expected):
            raw = actual(name, expected)
            if name == P.DISPOSITIONS:
                document = json.loads(raw)
                target = next(row for row in document["rows"] if row["path"] == P.NAMES[-1])
                target["disposition"] = "archive-byte-selected"
                return json.dumps(document).encode()
            return raw
        with mock.patch.object(P, "selected", side_effect=forged):
            with self.assertRaisesRegex(ValueError, "disposition differs"):
                P.inputs()

    def test_unrelated_guard_error_does_not_pass_negatives(self):
        rows, payload = P.inputs()
        class BrokenGuard:
            @staticmethod
            def _verify_files(*_):
                raise ValueError("unrelated guard failure")
        with mock.patch.object(P, "guard_module", return_value=BrokenGuard()):
            for mutation in ("missing", "changed"):
                with self.subTest(mutation=mutation):
                    with self.assertRaisesRegex(ValueError, "unrelated guard failure"):
                        P.exercise(rows, payload, mutation)


if __name__ == "__main__":
    unittest.main()
