import importlib.util
import copy
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("_cal_t20_seven_machine", HERE / "scan.py")
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)


class MachinePublicPrivacy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = scan.scanner()

    def test_exact_seven_retained_replies(self):
        result = scan.run()
        self.assertEqual(result["status"], "PASS-BOUNDED")
        self.assertEqual([row["operation"] for row in result["replies"]], list(scan.OPERATIONS))

    def test_changed_selected_bytes_refuse(self):
        with self.assertRaisesRegex(ValueError, "selected output bytes changed"):
            scan.selected(scan.T05_PATH, "0" * 64)

    def test_populated_alternate_credential_key_refuses(self):
        raw = json.dumps({"authorization": {"client-secret": "fictional-value"}}).encode()
        with self.assertRaisesRegex(ValueError, "credential"):
            scan.inspect_public(raw, self.old)

    def test_private_key_block_refuses(self):
        raw = json.dumps({"body": "-----BEGIN PRIVATE KEY-----\nfictional\n"}).encode()
        with self.assertRaisesRegex(ValueError, "private key block"):
            scan.inspect_public(raw, self.old)

    def test_private_owned_locator_refuses(self):
        raw = json.dumps({"body": "/tmp/cal-owned-private/issuer"}).encode()
        with self.assertRaisesRegex(ValueError, "private locator"):
            scan.inspect_public(raw, self.old)

    def test_authorization_scheme_refuses(self):
        raw = json.dumps({"body": "Bearer fictional-token"}).encode()
        with self.assertRaisesRegex(ValueError, "credential scheme"):
            scan.inspect_public(raw, self.old)

    def test_rebound_request_digest_refuses(self):
        receipt = self.old.strict_json(scan.selected(scan.T05_PATH, scan.T05_SHA))
        row = receipt["seven_actual_read_result_receipts"][0]
        body = self.old.strict_json(scan.selected(scan.ROOT / row["path"], row["sha256"]))
        changed = copy.deepcopy(body)
        changed["request_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "request/profile join"):
            scan.verify_observation(changed, row["operation"], receipt["profile_sha256"])

    def test_rebound_profile_digest_refuses(self):
        receipt = self.old.strict_json(scan.selected(scan.T05_PATH, scan.T05_SHA))
        row = receipt["seven_actual_read_result_receipts"][0]
        body = self.old.strict_json(scan.selected(scan.ROOT / row["path"], row["sha256"]))
        changed = copy.deepcopy(body)
        changed["actual_public_reply"]["contract_profile_binding"]["sha256"] = "1" * 64
        with self.assertRaisesRegex(ValueError, "request/profile join"):
            scan.verify_observation(changed, row["operation"], receipt["profile_sha256"])


if __name__ == "__main__":
    unittest.main()
