import copy
import json
from pathlib import Path
import unittest

import inventory


HERE = Path(__file__).resolve().parent


class InventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = inventory.read_binding(inventory.SOURCE)
        cls.profile = inventory.read_binding(inventory.PROFILE)
        cls.selection = inventory.read_binding(inventory.SELECTION)

    def test_cold_inventory_matches_saved_artifact(self):
        actual = inventory.build()
        self.assertEqual(inventory.canonical(actual), (HERE / "INVENTORY.json").read_bytes())
        self.assertEqual((actual["source_manifest_rows"], actual["schema_execution_rows"],
                          actual["overlap_rows"], actual["union_rows"], actual["guard_rows"]),
                         (207, 5043, 0, 5250, 5045))
        self.assertEqual(actual["byte_status_counts"], {"matching": 5250})
        self.assertEqual(actual["top_level_startup_read_count_outside_selected_rows"], 15)
        self.assertTrue(all(row["current_byte_status"] == "matching"
                            for row in actual["top_level_startup_read_rows"]))

    def test_changed_source_pin_refuses(self):
        with self.assertRaisesRegex(ValueError, "selected binding changed"):
            inventory.read_binding({**inventory.SOURCE, "sha256": "0" * 64})

    def test_changed_execution_row_refuses(self):
        selection = copy.deepcopy(self.selection)
        selection["files"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "outside selected profile"):
            inventory.select(self.source, self.profile, selection)

    def test_unexplained_execution_row_refuses(self):
        selection = copy.deepcopy(self.selection)
        selection["selection_reasons"].pop(selection["files"][0]["path"])
        with self.assertRaisesRegex(ValueError, "selection reasons"):
            inventory.select(self.source, self.profile, selection)

    def test_wrong_profile_selection_refuses(self):
        profile = dict(self.profile)
        profile["schema_execution_dependency_binding"] = {**inventory.SELECTION, "sha256": "0" * 64}
        with self.assertRaisesRegex(ValueError, "different execution closure"):
            inventory.select(self.source, profile, self.selection)

    def test_code_filename_private_is_not_secret_class(self):
        self.assertEqual(inventory.classify("product/lab/release-candidates/v1/private_content.py"),
                         "repository_code_or_contract")
        self.assertEqual(inventory.classify("authority/current.json"), "live_authority_state")
        self.assertEqual(inventory.classify("/usr/lib/python3.14/json/__init__.py"),
                         "absolute_host_dependency")
        self.assertEqual(inventory.classify("secrets/issuer.key"), "explicit_private_path")
        self.assertEqual(inventory.classify("docs/private/issuer.key"), "explicit_private_path")
        self.assertEqual(inventory.classify("authority/secrets/issuer.key"), "explicit_private_path")
        self.assertEqual(inventory.classify(".local/private/issuer.key"), "explicit_private_path")

    def test_changed_extra_guard_binding_refuses(self):
        _, _, guard, _ = inventory.select(self.source, self.profile, self.selection)
        path = self.profile["original_schema_inputs_binding"]["path"]
        self.assertIn(path, guard)
        changed = {**guard[path], "sha256": "0" * 64}
        with self.assertRaisesRegex(ValueError, "extra guard binding changed"):
            inventory.check_guard_extras([changed])

    def test_changed_startup_parent_refuses(self):
        selection = copy.deepcopy(self.selection)
        selection["parent_profile_binding"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "startup binding changed"):
            inventory.startup_reads(self.source, self.profile, selection)


if __name__ == "__main__":
    unittest.main()
