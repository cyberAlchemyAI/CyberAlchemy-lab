import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cal_native_successor_under_test", HERE / "native_successor.py")
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


class NativeSuccessorPreflight(unittest.TestCase):
    def test_native_source_refuses_worktree_private_output(self):
        with tempfile.TemporaryDirectory(dir=HERE, prefix="test-native-stage-") as directory:
            home = Path(directory)
            instance = "legacy-local-0123456789abcdef"
            (home / "instances" / instance).mkdir(parents=True)
            with patch.object(native, "HERE", home):
                for phase in ("source", "cold", "reader", "mapped", "context"):
                    with self.subTest(phase=phase):
                        with self.assertRaisesRegex(ValueError, "PRIVATE_SELECTION_ORIGIN_REFUSED"):
                            native.phase(instance, phase)

    def test_stale_current_input_refuses_before_new_family(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "profile.json"
            profile.write_text(json.dumps({"current_selection": {"lookup": {
                "path": "authority/project-state-transitions/current.json", "sha256": "0" * 64}}}))
            before = list((native.HERE / "instances").glob("legacy-local-0123456789abcdef"))
            with patch.object(native, "ENGINE_PROFILE", profile):
                with self.assertRaisesRegex(ValueError, "PINNED_ENGINE_PROFILE_STALE"):
                    native.technical_preflight()
            self.assertEqual(before, list((native.HERE / "instances").glob("legacy-local-0123456789abcdef")))

    def test_current_engine_capture_and_changed_pin_refusal(self):
        actual = native.technical_preflight()
        self.assertEqual(actual["lookup"]["path"], "authority/project-state-transitions/current.json")
        rows = native.current_engine_bindings()
        self.assertGreater(len(rows), 40)
        self.assertEqual(len(rows), len({row["path"] for row in rows}))
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "profile.json"
            profile.write_text(json.dumps({"current_selection": {"lookup": {
                "path": actual["lookup"]["path"], "sha256": "0" * 64}}}))
            with patch.object(native, "ENGINE_PROFILE", profile):
                with self.assertRaisesRegex(ValueError, "PINNED_ENGINE_PROFILE_STALE"):
                    native.technical_preflight()


if __name__ == "__main__":
    unittest.main()
