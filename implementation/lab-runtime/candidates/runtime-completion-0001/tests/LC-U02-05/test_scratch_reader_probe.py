"""Pure refusal oracles for the disposable Reader phase boundary."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from t35_external_v1 import scratch_reader_probe as reader


SHA = 'a' * 64


def selected_manifests() -> tuple[bytes, bytes]:
    inputs = [{'path': f'input/{i:04d}.json', 'sha256': SHA} for i in range(1701)]
    inputs += [{'path': str(reader.FAMILY / f'role/{i:02d}.py'), 'sha256': SHA}
               for i in range(30)]
    members = [{'path': str(reader.FAMILY / f'source/packages/0001/member-{i:02d}.json'),
                'sha256': SHA} for i in range(36)]
    return (reader._json({'files': inputs, 'authority_effect': 'none',
                          'actual_owner_outcome': None}),
            reader._json({'files': members, 'authority_effect': 'none',
                          'actual_owner_outcome': None}))


class ScratchReaderPureTests(unittest.TestCase):
    def test_exact_source_stage_package_rows(self):
        source, package = selected_manifests()
        rows = reader._selected_reader_rows(source, package,
                                             reader.source._sha(source),
                                             reader.source._sha(package))
        self.assertEqual(len(rows), 1701 + 30 + 36 + 2)
        self.assertEqual(rows, sorted(rows, key=lambda row: row['path']))
        manifest = json.loads(reader._reader_manifest(source, package))
        self.assertEqual(manifest['files'], rows)
        self.assertEqual(manifest['producer_source_binding']['sha256'], reader.source._sha(source))
        self.assertEqual(manifest['producer_package_binding']['sha256'], reader.source._sha(package))
        self.assertFalse(manifest['original_Source8_permission_transferred'])

    def test_duplicate_and_escaped_output_refused(self):
        source, package = selected_manifests()
        value = json.loads(source)
        value['files'].append(value['files'][0])
        with self.assertRaises(ValueError):
            reader._selected_reader_rows(reader._json(value), package, 'b'*64, 'c'*64)
        value = json.loads(source)
        value['files'][0] = {'path': '/tmp/escaped.json', 'sha256': SHA}
        with self.assertRaises(ValueError):
            reader._selected_reader_rows(reader._json(value), package, 'b'*64, 'c'*64)
        value = json.loads(package)
        value['files'][0] = {'path': str(reader.FAMILY) + '2/alias.json', 'sha256': SHA}
        with self.assertRaises(ValueError):
            reader._selected_reader_rows(source, reader._json(value), 'b'*64, 'c'*64)

    def test_bridge_pins_compile_and_reader_mount_is_read_only(self):
        raw = reader._reader_bridge('1'*64, '2'*64, '3'*64, '4'*64)
        self.assertNotIn(b'__SOURCE_SHA__', raw)
        self.assertIn(b"SOURCE_SHA='" + b'1'*64 + b"'", raw)
        with self.assertRaises(ValueError):
            reader._reader_bridge('invalid', '2'*64, '3'*64, '4'*64)
        argv = reader._sandbox_argv(Path('/tmp/snapshot'), Path('/tmp/family'),
                                    '_t35_reader_runner.py')
        self.assertNotIn('--bind', argv)
        self.assertIn('--ro-bind', argv)
        self.assertIn('--clearenv', argv)
        self.assertIn('--die-with-parent', argv)
        self.assertEqual(argv[-1], '/work/snapshot/_t35_reader_runner.py')

    def test_closed_reader_result_and_wrong_pin_refusal(self):
        value = {
            'result': 'PASS-fixture-reader', 'reader_manifest_sha256': '1'*64,
            'source_manifest_sha256': '2'*64,
            'source_package_manifest_sha256': '3'*64,
            'actual_distinct_local_types': True, 'selected_record_count': 19,
            'accounted_subject_count': 21, 'scope_ref_sha256': '4'*64,
            'closure_report_sha256': '5'*64, 'wrong_independent_pin_refusals': 3,
            'sandbox_host_checkout_absent': True, 'sandbox_protected_roots_absent': True,
            'authority_effect': 'none', 'actual_owner_outcome': None,
        }
        raw = (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()
        self.assertEqual(reader._reader_output(raw, reader_sha='1'*64,
                                                source_sha='2'*64,
                                                package_sha='3'*64), value)
        for change in ({'wrong_independent_pin_refusals': 2},
                       {'selected_record_count': 513},
                       {'accounted_subject_count': 18},
                       {'authority_effect': 'host'},
                       {'closure_report_sha256': 'bad'}):
            invalid = {**value, **change}
            with self.assertRaises(ValueError):
                reader._reader_output((json.dumps(invalid, sort_keys=True,
                                    separators=(',', ':')) + '\n').encode(), reader_sha='1'*64,
                                      source_sha='2'*64, package_sha='3'*64)
        with self.assertRaises(ValueError):
            reader._reader_output(raw, reader_sha='0'*64, source_sha='2'*64,
                                  package_sha='3'*64)


if __name__ == '__main__':
    unittest.main()
