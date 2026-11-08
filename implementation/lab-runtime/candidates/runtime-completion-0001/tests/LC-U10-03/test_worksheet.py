"""Meaningful refusal tests for the inert LC-U10-03 worksheet."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

import worksheet


class WorksheetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = worksheet.load_sources()
        cls.saved = json.loads(worksheet.OUTPUT.read_bytes())

    def test_complete_pinned_public_selection(self):
        worksheet.check_worksheet(self.saved, self.inputs)
        self.assertEqual(len(self.saved["members"]), 365)
        self.assertEqual(sum(x["selection_membership"] == "original363-and-composed365" for x in self.saved["members"]), 363)
        self.assertEqual(sum(x["selection_membership"] == "composed365-addition-only" for x in self.saved["members"]), 2)

    def test_missing_or_duplicate_member_refused(self):
        missing = copy.deepcopy(self.inputs)
        missing["composed"]["members"].pop()
        with self.assertRaisesRegex(ValueError, "member count changed"):
            worksheet.construct(missing)
        duplicate = copy.deepcopy(self.inputs)
        duplicate["composed"]["members"][0]["member_ref"] = duplicate["composed"]["members"][1]["member_ref"]
        with self.assertRaisesRegex(ValueError, "duplicate member"):
            worksheet.construct(duplicate)

    def test_selection_role_and_predecessor_drift_refused(self):
        forged = copy.deepcopy(self.inputs)
        forged["composed"]["members"][0]["proposed_owner_roles"] = ["role:repository-owner"]
        with self.assertRaisesRegex(ValueError, "role drift"):
            worksheet.construct(forged)
        predecessor = copy.deepcopy(self.inputs)
        predecessor["composed"]["original_selection_binding"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "composed predecessor mismatch"):
            worksheet.construct(predecessor)

    def test_forged_authority_refused(self):
        forged = copy.deepcopy(self.saved)
        forged["members"][0]["governing_current_authority"]["authorized_for_this_effect"] = True
        with self.assertRaisesRegex(ValueError, "worksheet drift or forged authority"):
            worksheet.check_worksheet(forged, self.inputs)
        forged_readpoint = copy.deepcopy(self.inputs)
        forged_readpoint["public_readpoint"]["public_admitted_role_assignment_instance_count"] = 1
        with self.assertRaisesRegex(ValueError, "public authority readpoint changed"):
            worksheet.construct(forged_readpoint)

    def test_source_byte_drift_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            relative = worksheet.SOURCES["original"][0]
            path = root / relative
            path.parent.mkdir(parents=True)
            path.write_bytes(b"{}\n")
            with self.assertRaisesRegex(ValueError, "source drift: original"):
                worksheet.load_sources(root)


if __name__ == "__main__":
    unittest.main()
