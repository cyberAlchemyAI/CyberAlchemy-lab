import json
from pathlib import Path
import unittest

import scan


class CandidatePrivacyTests(unittest.TestCase):
    def test_exact_archive_scans(self):
        result = scan.run()
        self.assertEqual((result["original_public_files_scanned"], result["additions_scanned"]),
                         (681, 799))
        self.assertEqual(result["archive_sha256"], scan.ARCHIVE_SHA)
        self.assertFalse(result["full_privacy_qualified"])
        self.assertEqual((json.dumps(result, sort_keys=True, indent=2) + "\n").encode(),
                         (Path(scan.__file__).parent / "RESULT.json").read_bytes())

    def test_sensitive_content_and_private_path_refuse(self):
        privacy = scan.load_selected(scan.PRIVACY, scan.PRIVACY_SHA, "test_selected_privacy")
        with self.assertRaisesRegex(ValueError, "credential field populated"):
            scan.scan_public("fixture/public.json", b'{"clientSecret":"fixture-value"}', privacy)
        with self.assertRaisesRegex(ValueError, "private-state package path"):
            scan.scan_public("fixture/private/session.json", b"{}", privacy)
        for body in (b"password=example-secret", b"api_key = 'example-secret'",
                     b"clientSecret: example-secret", b'password = None or "example-secret"',
                     b'password = "" or "example-secret"',
                     b'password = False or "example-secret"',
                     b'password = None, "example-secret"',
                     b'password=None) or "example-secret"',
                     b'password += "example-secret"',
                     b'password %= "example-secret"',
                     b'password //= "example-secret"',
                     b'password **= "example-secret"',
                     b'password <<= "example-secret"',
                     b'password >>= "example-secret"',
                     b'password @= "example-secret"'):
            with self.subTest(body=body):
                with self.assertRaisesRegex(ValueError, "text credential assignment"):
                    scan.scan_public("fixture/public.txt", body, privacy)
        scan.scan_public("fixture/public.py", b"load_pem_private_key(data, password=None)", privacy)
        for body in (b"password: # description\n  value: example-secret",
                     b"password:\n  example-secret", b"api_key =\n  example-secret"):
            with self.subTest(multiline=body):
                with self.assertRaisesRegex(ValueError, "empty or multiline"):
                    scan.scan_public("fixture/public.yaml", body, privacy)

    def test_public_policy_exception_requires_exact_bytes(self):
        privacy = scan.load_selected(scan.PRIVACY, scan.PRIVACY_SHA, "test_selected_privacy")
        with self.assertRaisesRegex(ValueError, "exception bytes changed"):
            scan.scan_public(scan.PUBLIC_POLICY_PATH, b"{}", privacy)

    def test_changed_selected_scanner_refuses_before_execution(self):
        with self.assertRaisesRegex(ValueError, "selected code changed"):
            scan.load_selected(scan.PRIVACY, "0" * 64, "wrong_privacy")


if __name__ == "__main__":
    unittest.main()
