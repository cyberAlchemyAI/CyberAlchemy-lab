import copy
import json
import unittest
from unittest.mock import patch

from consume_15 import (CONTROL, CONTROL_SHA256, RECEIPT, RECEIPT_SHA256,
                        SELECTION, SELECTION_SHA256, consume, pinned,
                        strict_json, validate_control, verify_witness)


class W07SignedSelectionConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.control = strict_json(pinned({"path": CONTROL, "sha256": CONTROL_SHA256}))
        cls.selection = strict_json(pinned({"path": SELECTION, "sha256": SELECTION_SHA256}))
        cls.receipt = strict_json(pinned({"path": RECEIPT, "sha256": RECEIPT_SHA256}))
        cls.witness = cls.selection["signed_coupling_witnesses"][0]
        cls.approval = strict_json(pinned(cls.witness["approval_binding"]))
        cls.result = strict_json(pinned(cls.witness["result_binding"]))

    def test_four_cases_and_two_real_signatures_pass(self):
        output = consume()
        self.assertEqual(output["result"], "PASS")
        self.assertEqual(output["case_count"], 4)
        self.assertEqual([w["domain"] for w in output["signature_verified_witnesses"]],
                         ["engineering", "research"])

    def test_wrong_control_member_refuses(self):
        control = copy.deepcopy(self.control)
        control["member_ref"] = "review:W07:other"
        with self.assertRaisesRegex(ValueError, "wrong W07 control"):
            validate_control(control, self.selection, self.receipt)

    def test_changed_parent_proof_refuses(self):
        selection = copy.deepcopy(self.selection)
        selection["parent_workflow_proof_binding"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "bound bytes differ"):
            validate_control(self.control, selection, self.receipt)

    def test_changed_signed_approval_refuses(self):
        approval = copy.deepcopy(self.approval)
        approval["signature"] = "00" * 64
        with self.assertRaisesRegex(ValueError, "signed approval"):
            verify_witness(self.witness, approval=approval)

    def test_changed_witness_result_refuses(self):
        result = copy.deepcopy(self.result)
        result["result"] = "PASS" if result["result"] != "PASS" else "FAIL"
        with self.assertRaisesRegex(ValueError, "signed witness result"):
            verify_witness(self.witness, result=result)

    def test_duplicate_json_key_refuses(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            strict_json(b'{"a":1,"a":2}')

    def test_overflowed_json_number_refuses(self):
        with self.assertRaisesRegex(ValueError, "nonfinite JSON"):
            strict_json(b'{"elapsed":1e10000}')

    def test_archive_config_crossbinding_refuses(self):
        original_pinned = pinned
        binding = self.witness["archive_binding"]
        archive = strict_json(original_pinned(binding))
        archive["config_sha256"] = "0" * 64

        def supplied(row):
            if row == binding:
                return json.dumps(archive, sort_keys=True).encode()
            return original_pinned(row)

        with patch("consume_15.pinned", side_effect=supplied):
            with self.assertRaisesRegex(ValueError, "config/baseline lineage"):
                verify_witness(self.witness)

    def test_archive_baseline_crossbinding_refuses(self):
        original_pinned = pinned
        binding = self.witness["archive_binding"]
        archive = strict_json(original_pinned(binding))
        archive["baseline_snapshot_digest"] = "0" * 64

        def supplied(row):
            if row == binding:
                return json.dumps(archive, sort_keys=True).encode()
            return original_pinned(row)

        with patch("consume_15.pinned", side_effect=supplied):
            with self.assertRaisesRegex(ValueError, "config/baseline lineage"):
                verify_witness(self.witness)

    def test_expected_projection_crossbinding_refuses(self):
        original_pinned = pinned
        binding = self.witness["expected_replay_binding"]
        expected = strict_json(original_pinned(binding))
        expected["projection_sha256"] = "0" * 64

        def supplied(row):
            if row == binding:
                return json.dumps(expected, sort_keys=True).encode()
            return original_pinned(row)

        with patch("consume_15.pinned", side_effect=supplied):
            with self.assertRaisesRegex(ValueError, "head lineage"):
                verify_witness(self.witness)

    def test_expected_target_crossbinding_refuses(self):
        original_pinned = pinned
        binding = self.witness["expected_replay_binding"]
        expected = strict_json(original_pinned(binding))
        expected["actual_targets"][0]["record_structural_sha256"] = "0" * 64

        def supplied(row):
            if row == binding:
                return json.dumps(expected, sort_keys=True).encode()
            return original_pinned(row)

        with patch("consume_15.pinned", side_effect=supplied):
            with self.assertRaisesRegex(ValueError, "expected targets"):
                verify_witness(self.witness)


if __name__ == "__main__":
    unittest.main()
