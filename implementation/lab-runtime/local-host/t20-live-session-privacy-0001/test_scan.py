import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t20_live_scan', HERE / 'scan.py')
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)


class LiveSessionPrivacyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scanner = scan.scanner_from_selected_bytes(scan.selected(scan.OLD))
        cls.value = cls.scanner.strict_json(scan.selected(scan.RECEIPT))

    def altered(self, transform):
        value = json.loads(json.dumps(self.value))
        transform(value)
        return json.dumps(value, sort_keys=True).encode()

    def test_selected_public_output(self):
        self.assertEqual(scan.assess(scan.selected(scan.RECEIPT), self.scanner)['api_replies_checked'], 4)

    def test_populated_credential_field_refuses(self):
        with self.assertRaisesRegex(ValueError, 'credential'):
            scan.assess(self.altered(lambda value: value['report'].update({'access_token': 'canary'})), self.scanner)

    def test_private_key_block_refuses(self):
        with self.assertRaisesRegex(ValueError, 'private key block'):
            scan.assess(self.altered(lambda value: value['report'].update({'text': '-----BEGIN PRIVATE KEY-----'})), self.scanner)

    def test_camel_case_private_key_material_refuses(self):
        with self.assertRaisesRegex(ValueError, 'extended credential'):
            scan.assess(self.altered(lambda value: value['report'].update({'privateKeyMaterial': 'canary'})), self.scanner)

    def test_bearer_authorization_refuses(self):
        with self.assertRaisesRegex(ValueError, 'credential'):
            scan.assess(self.altered(lambda value: value['report'].update({'authorization': 'Bearer CANARY-CREDENTIAL'})), self.scanner)

    def test_basic_authorization_refuses(self):
        with self.assertRaisesRegex(ValueError, 'credential'):
            scan.assess(self.altered(lambda value: value['report'].update({'authorization': 'Basic Y2FuYXJ5'})), self.scanner)

    def test_session_cookie_refuses(self):
        with self.assertRaisesRegex(ValueError, 'credential'):
            scan.assess(self.altered(lambda value: value['report'].update({'sessionCookie': 'sid=CANARY'})), self.scanner)

    def test_private_runtime_locator_refuses(self):
        with self.assertRaisesRegex(ValueError, 'private runtime locator'):
            scan.assess(self.altered(lambda value: value['report'].update({'text': '/tmp/cal-private-owner/root'})), self.scanner)

    def test_changed_selected_receipt_refuses(self):
        original = scan.PINS[scan.RECEIPT]
        try:
            scan.PINS[scan.RECEIPT] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'selected public file changed'):
                scan.selected(scan.RECEIPT)
        finally:
            scan.PINS[scan.RECEIPT] = original


if __name__ == '__main__':
    unittest.main()
