import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("local_t15_inventory", HERE / "inventory.py")
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


class InventoryTests(unittest.TestCase):
    def test_original_323_and_current_345_preserved(self):
        report = inventory.build()
        self.assertEqual((report["original_count"], report["current_count"]), (323, 345))
        self.assertEqual(report["missing_original_methods"], [])
        self.assertEqual(len(report["added_method_ids"]), 22)

    def test_selected_report_rebuilds_byte_identically(self):
        expected = (HERE / "INVENTORY.json").read_bytes()
        actual = (json.dumps(inventory.build(), sort_keys=True, indent=2) + "\n").encode()
        self.assertEqual(actual, expected)

    def test_changed_method_ast_changes_its_digest(self):
        original = ast.parse("class T:\n def test_one(self):\n  return 1\n").body[0].body[0]
        changed = ast.parse("class T:\n def test_one(self):\n  return 2\n").body[0].body[0]
        self.assertNotEqual(inventory.method_ast_sha(original), inventory.method_ast_sha(changed))

    def test_selected_file_bytes_remain_pinned(self):
        report = json.loads((HERE / "INVENTORY.json").read_bytes())
        for path, expected in {**report["original_file_sha256"], **report["current_file_sha256"]}.items():
            self.assertEqual(hashlib.sha256((inventory.ROOT / path).read_bytes()).hexdigest(), expected)


if __name__ == "__main__":
    unittest.main()
