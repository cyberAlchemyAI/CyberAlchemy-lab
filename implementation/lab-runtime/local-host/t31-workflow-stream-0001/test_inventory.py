import copy
import hashlib
import json
import unittest
from pathlib import Path

from inventory import inventory, check_output_set
from verify import check_report


class InventoryTests(unittest.TestCase):
    def test_all_original_templates_and_api30_registry_agree(self):
        result = inventory()
        self.assertEqual((result["workflow_count"], result["transition_count"]), (10, 28))
        self.assertEqual(len({row["workflow"] for row in result["transitions"]}), 10)
        self.assertTrue(all(row["required_output_carriers"] for row in result["transitions"]))

    def test_zero_wrong_and_changed_output_refuse(self):
        transition = next(row for row in inventory()["transitions"] if row["transition_ref"] == "transition:engineering:assessed")
        raw = b'{"fixture":"actual original bytes"}'
        header = {"carrier_ref": transition["required_output_carriers"][0], "identity_ref": "assessment:local",
                  "version_ref": "assessment:local@1", "scope_ref": "project:fixture", "byte_sha256": hashlib.sha256(raw).hexdigest()}
        self.assertEqual(check_output_set(transition, [(header, raw)]), [header])
        with self.assertRaisesRegex(ValueError, "nonempty"):
            check_output_set(transition, [])
        wrong = copy.deepcopy(header); wrong["carrier_ref"] = "cal.artifact-type.generated-output/v2"
        with self.assertRaisesRegex(ValueError, "wrong"):
            check_output_set(transition, [(wrong, raw)])
        with self.assertRaisesRegex(ValueError, "bytes"):
            check_output_set(transition, [(header, raw + b"!")])

    def test_cold_report_refuses_false_qualification_claims(self):
        path = Path(__file__).resolve().parent / "run-0001/RESULT.json"
        report = json.loads(path.read_bytes())
        rows = report["observed_terminal_output_transitions"]
        check_report(report, rows)
        for field, false_value in (("native_output_journal_or_all28_qualified", True),
                                   ("zero_output_substitute_accepted", True),
                                   ("source_or_authority_effect", "present")):
            changed = copy.deepcopy(report)
            changed[field] = false_value
            with self.assertRaisesRegex(ValueError, "claim"):
                check_report(changed, rows)


if __name__ == "__main__":
    unittest.main()
