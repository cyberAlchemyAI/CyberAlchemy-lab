import sys
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import entrypoint


SOURCE = "ceae2efe1a93e7041b83a5f7d3efa32085383beb061459e0568ebb5536e168aa"
PROFILE = "62cf46ffc5a01cc0009a4675ce265a45037104b3e64da0f022aaf2b2d3e75ec9"


class CurrentCompositePrerequisiteTests(unittest.TestCase):
    def test_real_current_selection_identifies_historical_sdk(self):
        selected = entrypoint.inspect_current(SOURCE, PROFILE)
        self.assertEqual(selected["api_operation_count"], 34)
        self.assertTrue(selected["historical_sdk_binds_api17"])
        self.assertTrue(selected["historical_preparer_binds_api17"])
        self.assertEqual(selected["historical_sdk_profile_rows"], 17)

    def test_wrong_current_source_and_profile_pins_refuse(self):
        with self.assertRaisesRegex(ValueError, "PIN_CHANGED"):
            entrypoint.inspect_current("0" * 64, PROFILE)
        with self.assertRaisesRegex(ValueError, "PIN_CHANGED"):
            entrypoint.inspect_current(SOURCE, "0" * 64)

    def test_changed_historical_sdk_and_preparer_bytes_refuse(self):
        original = Path.read_bytes
        for selected, refusal in ((entrypoint.SDK / "composite.py", "HISTORICAL_SDK_BYTES_CHANGED"),
                                  (entrypoint.PREPARER, "HISTORICAL_PREPARER_BYTES_CHANGED")):
            with self.subTest(selected=selected.name):
                def changed(path):
                    return b"changed-selected-bytes\n" if path == selected else original(path)
                with patch.object(Path, "read_bytes", changed):
                    with self.assertRaisesRegex(ValueError, refusal):
                        entrypoint.inspect_current(SOURCE, PROFILE)

    def test_changed_bridge_freeze_refuses(self):
        original = Path.read_bytes
        selected = entrypoint.BRIDGE / "FREEZE.json"
        def changed(path):
            return b"changed-freeze\n" if path == selected else original(path)
        with patch.object(Path, "read_bytes", changed):
            with self.assertRaisesRegex(ValueError, "PIN_CHANGED"):
                entrypoint.craft_build()

    def test_selected_symlink_origin_refuses_even_when_bytes_match(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target.json"
            target.write_text("{}\n")
            link = root / "selected.json"
            link.symlink_to(target)
            with patch.object(entrypoint, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "PINNED_ORIGIN_CHANGED"):
                    entrypoint.pinned_json(link, entrypoint.sha(target.read_bytes()))
                with self.assertRaisesRegex(ValueError, "SELECTED_ORIGIN_CHANGED"):
                    entrypoint.selected_bytes({"path": link.name, "sha256": entrypoint.sha(target.read_bytes())},
                                              "SELECTED_ORIGIN_CHANGED")

    def test_actual_revision3_software_guard_refuses_api33_directory(self):
        sys.path.insert(0, str(entrypoint.SDK))
        self.addCleanup(lambda: sys.path.remove(str(entrypoint.SDK)))
        spec = importlib.util.spec_from_file_location("_cal_t06_historical_sdk_negative", entrypoint.SDK / "composite.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        config = {"source": {"directory": str(entrypoint.API), "source_sha256": SOURCE,
                             "profile_sha256": PROFILE, "members_sha256": "0" * 64,
                             "bootstrap_bindings": [{"path": "irrelevant", "sha256": "0" * 64}]}}
        with self.assertRaisesRegex(ValueError, "exact maintained API17 successor required"):
            module.software_guard(config)

    def test_craft_positive_cannot_be_reported_as_composite_ready(self):
        craft = {"status": "technical_candidate_validation_passed", "native_eligibility": False}
        with patch.object(entrypoint, "craft_build", return_value=craft) as selected:
            value = entrypoint.run(SOURCE, PROFILE, True)
        selected.assert_called_once_with()
        self.assertEqual(value["craft"], craft)
        self.assertEqual(value["status"], "BLOCKED_CURRENT_COMPOSITE_INTEGRATION")
        self.assertFalse(value["actual_base_action_governance_started"])
        self.assertFalse(value["actual_full34_ready"])
        self.assertEqual(value["dispatch_operations_executed"], 0)


if __name__ == "__main__":
    unittest.main()
