import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("local_t25_account", HERE / "account.py")
account = importlib.util.module_from_spec(spec)
spec.loader.exec_module(account)


class OriginalPackageAccountingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = json.loads(account.INPUTS.read_bytes())
        cls.inventory = json.loads(account.INVENTORY.read_bytes())

    def test_all_original_members_and_files(self):
        result = account.run()
        self.assertEqual((result["original_members"], result["selected_public_files_rehashed"]), (363, 681))
        self.assertFalse(result["original_package_materialized"])

    def test_duplicate_member_refuses(self):
        changed = copy.deepcopy(self.inventory)
        changed["members"][1]["member_id"] = changed["members"][0]["member_id"]
        with self.assertRaisesRegex(ValueError, "identity changed"):
            account.account(self.inputs, changed)

    def test_changed_selected_file_refuses(self):
        changed = copy.deepcopy(self.inputs)
        changed["files"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "selected bytes changed"):
            account.account(changed, self.inventory)

    def test_changed_inventory_selector_refuses(self):
        changed = copy.deepcopy(self.inputs)
        changed["original_final_inventory_binding"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "selector changed"):
            account.account(changed, self.inventory)


if __name__ == "__main__":
    unittest.main()
