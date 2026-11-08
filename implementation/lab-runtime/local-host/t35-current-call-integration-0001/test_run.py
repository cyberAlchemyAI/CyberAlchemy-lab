from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t35_current_call", HERE / "run.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
builder_path = runner.ROOT / 'implementation/lab-runtime/local-host/t35-api33-reader-rebind-0001/build.py'
builder_spec = importlib.util.spec_from_file_location('t35_reader_rebind_test', builder_path)
builder = importlib.util.module_from_spec(builder_spec)
builder_spec.loader.exec_module(builder)


class CurrentCallReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads((HERE / "RESULT.json").read_bytes())

    def test_actual_receipt_and_source_period(self):
        runner.verify_result(self.result)
        self.assertEqual(self.result["operation"], "lab.status")
        self.assertEqual(self.result["observation"]["callback_count"], 1)

    def test_false_callback_and_clock_refuse(self):
        changed = deepcopy(self.result)
        changed["observation"]["callback_count"] = 2
        with self.assertRaisesRegex(ValueError, "boundary count"):
            runner.verify_result(changed)
        changed = deepcopy(self.result)
        changed["observation"]["events"][0]["monotonic_elapsed_seconds"] += 10
        with self.assertRaisesRegex(ValueError, "clock"):
            runner.verify_result(changed)
        changed = deepcopy(self.result)
        changed["monotonic_elapsed_seconds"] += 10
        with self.assertRaisesRegex(ValueError, "clock"):
            runner.verify_result(changed)

    def test_false_lease_origin_and_effect_refuse(self):
        changed = deepcopy(self.result)
        changed["reader_lease_origin"]["authenticated_context"] = False
        with self.assertRaisesRegex(ValueError, "lease"):
            runner.verify_result(changed)
        changed = deepcopy(self.result)
        changed["authority_effect"] = "admitted"
        with self.assertRaisesRegex(ValueError, "selection or claim"):
            runner.verify_result(changed)

    def test_changed_source_period_bytes_refuse(self):
        with patch.object(runner, "SOURCE_PERIOD", (runner.SOURCE_PERIOD[0], "0" * 64)):
            with self.assertRaisesRegex(ValueError, "selected file changed"):
                runner.verify_result(self.result)

    def test_wrong_reader_class_and_changed_api_source_refuse(self):
        old = (builder.OLD / 'source_bridge.py').read_bytes()
        new = (builder.NEW / 'source_bridge.py').read_bytes()
        builder.verify_bridge_edit(old, new)
        with self.assertRaisesRegex(ValueError, 'sole source change'):
            builder.verify_bridge_edit(old, old)
        with self.assertRaisesRegex(ValueError, 'sole source change'):
            builder.verify_bridge_edit(old, new + b'\n# unselected mutation\n')
        with patch.object(runner, 'API_MANIFEST', (runner.API_MANIFEST[0], '0' * 64)):
            with self.assertRaisesRegex(ValueError, 'selected file changed'):
                runner.verify_result(self.result)


if __name__ == "__main__":
    unittest.main()
