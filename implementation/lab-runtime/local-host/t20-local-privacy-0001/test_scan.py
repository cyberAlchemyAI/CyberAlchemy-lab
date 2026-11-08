import json
import unittest
from unittest import mock
import scan

class LocalPrivacyTests(unittest.TestCase):
    def refused_without_leak(self, callback, marker=None):
        with self.assertRaises(ValueError) as caught:
            callback()
        if marker:
            self.assertNotIn(marker, str(caught.exception))

    def test_actual_selected_t07_context_and_outputs(self):
        result = scan.run()
        self.assertEqual(result['status'], 'PASS-LOCAL-TECHNICAL')
        self.assertEqual((result['material_count'], result['runtime_code_count'],
                          result['build_input_count'], result['name_only_count']), (698, 3, 4, 78))
        self.assertFalse(result['final_family_privacy_qualified'])

    def test_selected_manifest_change_refuses(self):
        path = scan.T07 / 'source-manifest.json'
        with mock.patch.dict(scan.PINS, {path: '0'*64}):
            self.refused_without_leak(scan.run)

    def test_private_path_refuses(self):
        self.refused_without_leak(lambda: scan.scan_member('fixture/owner.pem', b'public'))
        self.refused_without_leak(lambda: scan.scan_member('state/private-key.json', b'{}'))
        self.refused_without_leak(lambda: scan.scan_member('private/state.json', b'{}'))

    def test_private_key_block_refuses_without_body(self):
        body = b'-----BEGIN PRIVATE KEY-----\nSYNTHETIC-TEST-ONLY\n'
        self.refused_without_leak(lambda: scan.scan_member('public.txt', body), 'SYNTHETIC-TEST-ONLY')

    def test_populated_credential_refuses_without_value(self):
        marker = 'synthetic-marker-only'
        raw = json.dumps({'password': marker}).encode()
        self.refused_without_leak(lambda: scan.scan_member('public.json', raw, json_body=True), marker)
        self.refused_without_leak(lambda: scan.scan_member('public.json', b'{"password":0}', json_body=True))
        self.refused_without_leak(lambda: scan.scan_member('public.json', b'{"private-key":"test"}', json_body=True))
        self.refused_without_leak(lambda: scan.scan_member('public.json', b'{"privateKey":"test"}', json_body=True))
        scan.scan_member('public.json', b'{"privateKey":false}', json_body=True)

    def test_private_runtime_locator_refuses(self):
        raw = b'fixture key: removed\n/tmp/cal-fixture-123/state.json\n'
        self.refused_without_leak(lambda: scan.scan_runtime_log(raw), 'state.json')

    def test_container_mount_or_network_refuses(self):
        raw = scan.pinned(scan.EVIDENCE / 'INSPECT-v3-chain.json')
        value = scan.strict_json(raw)
        value['mounts'] = [{'source':'synthetic'}]
        self.refused_without_leak(lambda: scan.inspect_boundary(json.dumps(value).encode()))
        value['mounts'] = []
        value['network_mode'] = 'bridge'
        self.refused_without_leak(lambda: scan.inspect_boundary(json.dumps(value).encode()))

if __name__ == '__main__':
    unittest.main()
