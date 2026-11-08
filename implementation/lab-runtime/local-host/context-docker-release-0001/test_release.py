"""Public, effect-disabled causal checks for the proposed finalization joins."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import finalization as F
import observer as O


HERE = Path(__file__).resolve().parent
STAGE = HERE.parent / 'context-stage-0001/selection.json'


class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = STAGE.read_bytes()
        cls.rows = F.baseline(cls.stage)
        assert len(cls.rows) == 1570

    def specimen(self):
        replacements = {p: hashlib.sha256(p.encode()).hexdigest() for p in F.REPLACEMENTS}
        rows = copy.deepcopy(self.rows)
        for row in rows:
            if row['path'] in replacements:
                row['sha256'] = replacements[row['path']]
        authorization = hashlib.sha256(b'fixture-authorization').hexdigest()
        rows.append({'path': F.AUTH, 'sha256': authorization})
        rows.sort(key=lambda row: row['path'])
        receipt = {
            'schema': 'context-finalization-receipt/v1',
            'root': F.ROOT, 'root_identity': [1, 2, 3, 4],
            'stage_sha256': F.STAGE_SHA, 'files': rows,
            'source_mode': '0700', 'auth_directory_mode': '0700',
            'auth_leaf_mode': '0600',
            'mounts': {'root': 'ro', 'output': 'ro', 'native': 'ro', 'private': 'unmounted'},
            'image': F.IMAGE, 'native_sha256': F.NATIVE_SHA,
            'constructor_review_sha256': 'a' * 64,
            'issuer_enrollment_sha256': 'b' * 64,
            'private_root': '/tmp/context-private-fixture-0001',
            'not_before': 1000, 'expires': 1100,
            'status': 'FINALIZATION_ONLY', 'retry_allowed': False,
        }
        selection = {
            'schema': 'context-finalization-selection/v1',
            'root': F.ROOT, 'root_identity': receipt['root_identity'],
            'stage_sha256': F.STAGE_SHA,
            'stage_review_sha256': F.STAGE_REVIEW_SHA,
            'receipt_sha256': F.sha(F.encode(receipt)),
            'authorization_sha256': authorization,
            'role_replacements': replacements,
            'constructor_review_sha256': receipt['constructor_review_sha256'],
            'issuer_enrollment_sha256': receipt['issuer_enrollment_sha256'],
            'private_root': receipt['private_root'],
            'not_before': receipt['not_before'], 'expires': receipt['expires'],
            'final_manifest_sha256': F.sha(F.encode(rows)),
        }
        return selection, receipt

    def validate(self, selection, receipt, now=1050):
        raw = F.encode(selection)
        return F.validate(self.stage, raw, F.sha(raw), F.encode(receipt), now)

    def test_exact_specimen_is_consistency_only(self):
        selection, receipt = self.specimen()
        result = self.validate(selection, receipt)
        self.assertEqual(result['status'], 'RECEIPT_CONSISTENT_ONLY')
        self.assertFalse(result['effect_enabled'])
        self.assertEqual(result['files'], 1571)

    def test_missing_authorization_and_surplus_file_refuse(self):
        selection, receipt = self.specimen()
        for changed in (receipt['files'][:-1], receipt['files'] + [
                {'path': 'surplus', 'sha256': 'f' * 64}]):
            copy_receipt = copy.deepcopy(receipt)
            copy_receipt['files'] = changed
            copy_selection = copy.deepcopy(selection)
            copy_selection['receipt_sha256'] = F.sha(F.encode(copy_receipt))
            with self.assertRaises(RuntimeError):
                self.validate(copy_selection, copy_receipt)

    def test_role_and_authorization_drift_refuse(self):
        selection, receipt = self.specimen()
        for key in ('role_replacements', 'authorization_sha256'):
            changed = copy.deepcopy(selection)
            if key == 'role_replacements':
                changed[key][F.REPLACEMENTS[0]] = 'c' * 64
            else:
                changed[key] = 'c' * 64
            with self.assertRaises(RuntimeError):
                self.validate(changed, receipt)

    def test_period_private_mount_and_receipt_pin_refuse(self):
        selection, receipt = self.specimen()
        for changed_time in (999, 1100):
            with self.assertRaises(RuntimeError):
                self.validate(selection, receipt, changed_time)
        changed = copy.deepcopy(selection)
        changed['private_root'] = F.ROOT + '/private'
        with self.assertRaises(RuntimeError):
            self.validate(changed, receipt)
        changed = copy.deepcopy(receipt)
        changed['mounts']['private'] = 'ro'
        with self.assertRaises(RuntimeError):
            self.validate(selection, changed)

    def test_noncanonical_json_and_duplicate_key_refuse(self):
        with self.assertRaises(RuntimeError):
            F.parse(b'{"a":1,"a":2}')
        with self.assertRaises(RuntimeError):
            F.parse(b'{"x":NaN}')

    def test_observer_terminal_join(self):
        expected = {'attempt': '/tmp/context-release-fixture-0001',
                    'selection_sha256': 'd' * 64,
                    'container_name': 'context-release-fixture-0001'}
        value = {'schema': 'context-release-terminal/v1',
                 'status': 'POSTCLOSE_COMPLETE', **expected,
                 'cid': 'c' * 64, 'container_os_exit': 0,
                 'cid_absent': True, 'name_absent': True,
                 'writer_closed': True, 'mediator_joined': True,
                 'postclose_readback': True, 'manifest_sha256': 'e' * 64}
        raw = F.encode(value)
        streams = {'stdout': F.encode({'status': 'POSTCLOSE_COMPLETE',
                                      'receipt_sha256': F.sha(raw)}) + b'\n',
                   'stderr': b''}
        self.assertEqual(O.join(raw, F.sha(raw), 0, streams, expected), value)
        with self.assertRaises(RuntimeError):
            O.join(raw, F.sha(raw), 1, streams, expected)
        with self.assertRaises(RuntimeError):
            O.join(raw, F.sha(raw), 0,
                   {'stdout': streams['stdout'], 'stderr': b'late'}, expected)
        bad = copy.deepcopy(value)
        bad['cid_absent'] = False
        with self.assertRaises(RuntimeError):
            O.join(F.encode(bad), F.sha(F.encode(bad)), 0, streams, expected)

    def test_effect_refuses(self):
        with self.assertRaisesRegex(RuntimeError, 'EFFECT_DISABLED'):
            O.execute()

    def test_public_fixture_observer_records_os_exit(self):
        expected = {'attempt': '/tmp/context-release-fixture-0001',
                    'selection_sha256': 'd' * 64,
                    'container_name': 'context-release-fixture-0001'}
        value = {'schema': 'context-release-terminal/v1',
                 'status': 'POSTCLOSE_COMPLETE', **expected,
                 'cid': 'c' * 64, 'container_os_exit': 0,
                 'cid_absent': True, 'name_absent': True,
                 'writer_closed': True, 'mediator_joined': True,
                 'postclose_readback': True, 'manifest_sha256': 'e' * 64}
        raw = F.encode(value)
        with tempfile.TemporaryDirectory(prefix='context-release-observer-fixture-',
                                         dir='/tmp') as base:
            receipt = Path(base) / 'terminal.json'
            script = ("import pathlib,sys\n"
                      + "p=pathlib.Path(sys.argv[1])\n"
                      + "p.write_bytes(" + repr(raw) + ")\n"
                      + "sys.stdout.buffer.write(" + repr(F.encode({
                          'status': 'POSTCLOSE_COMPLETE',
                          'receipt_sha256': F.sha(raw)}) + b'\n') + ")\n")
            command = ['/usr/bin/python3.14', '-I', '-B', '-S', '-c', script,
                       str(receipt)]
            try:
                result = O.observe_fixture(Path(base) / 'observation', command,
                                           command, receipt, expected)
            except BaseException:
                observed = Path(base) / 'observation/observation.json'
                stdout = Path(base) / 'observation/stdout'
                self.fail((observed.read_text() if observed.exists() else 'NO_OBSERVATION')
                          + ' stdout=' + repr(stdout.read_bytes() if stdout.exists() else None)
                          + ' receipt=' + repr(receipt.read_bytes() if receipt.exists() else None))
            self.assertEqual(result['status'], 'EXTERNAL_FIXTURE_OS_RECEIPT_MATCH')
            self.assertEqual(result['os_exit'], 0)
            observation = json.loads((Path(base) / 'observation/observation.json').read_bytes())
            self.assertEqual(observation['status'], 'PROVISIONAL_MATCH')


if __name__ == '__main__':
    unittest.main()
