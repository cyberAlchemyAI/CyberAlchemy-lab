"""Synthetic mount/visibility evidence; no Docker or output creation."""
import datetime as dt
import importlib.util
import unittest
from pathlib import Path
from unittest import mock

SOURCE = Path(__file__).with_name('mount_vector.py')
spec = importlib.util.spec_from_file_location('mount_vector_tested',SOURCE)
mount = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mount)


class MountVectorTests(unittest.TestCase):
    def fixture(self):
        selected = mount.vector()
        digest = '1'*64
        return {'mounts':selected['mounts'],
                'mountinfo_raw':b'121 10 0:44 / /workspace ro,relatime - ext4 /dev/root rw\n',
                'ready':{'schema':'context-child-ready/v1',
                         'attempt':'a'*32,'out':selected['logical_output_root'],
                         'original_guard_sha256':mount.GUARD_SHA,
                         'output_absent':True},
                'selected_token':'a'*32,'parent_absent_at_ready':True,
                'sentinel':{'path':'/workspace/'+selected['context_role']+
                           '/.readonly-sentinel',
                           'attempted_create':True,'errno':30,'created':False},
                'ack':{'leaf':'request.json','ordinal':1,'sha256':digest,
                       'parent_fsync_readback_sha256':digest,
                       'ack_received':True,
                       'child_post_ack_readback_sha256':digest}}

    def test_exact_five_ro_mounts_parent_writer_child_ro(self):
        selected = mount.vector()
        self.assertEqual(selected['status'],'INERT_PARENT_WRITER_CHILD_RO_MOUNT_VECTOR')
        self.assertEqual([r['target'] for r in selected['mounts']],
                         ['/workspace','/control','/runner','/cache-disabled',
                          '/attempt/input/lab-context-native-reader'])
        self.assertTrue(all(r['read_only'] for r in selected['mounts']))
        self.assertEqual(selected['child_nested_output_bind'],'ABSENT')
        self.assertEqual(selected['parent_writer_access'],'RW_HELD_DESCRIPTOR')
        self.assertEqual(selected['child_workspace_access'],'RO_BIND')
        self.assertEqual(selected['authorization'],'UNMINTED')

    def test_synthetic_mountinfo_erofs_and_post_ack_visibility(self):
        result = mount.check_synthetic_probe(**self.fixture())
        self.assertEqual(result['status'],'SYNTHETIC_MOUNT_VECTOR_OBSERVATIONS_ONLY')
        self.assertFalse(result['actual_namespace_observed'])
        self.assertFalse(result['nested_child_writable_output_bind'])

    def test_rw_or_nested_mount_refuses(self):
        for mutation in ('rw','nested','extra_bind'):
            case = self.fixture()
            if mutation == 'rw':
                case['mountinfo_raw'] = case['mountinfo_raw'].replace(b'ro,relatime',
                                                                       b'rw,relatime')
            elif mutation == 'nested':
                case['mountinfo_raw'] += (b'122 121 0:44 / /workspace/product '
                                          b'rw,relatime - ext4 /dev/root rw\n')
            else:
                case['mounts'] = case['mounts'] + [{
                    'source':'/fixture/output','target':'/workspace/product',
                    'read_only':False}]
            with self.subTest(mutation=mutation),self.assertRaises(mount.Refused):
                mount.check_synthetic_probe(**case)

    def test_ready_parent_absence_and_erofs_refuse_when_forged(self):
        for mutation in ('ready','parent','errno'):
            case = self.fixture()
            if mutation == 'ready': case['ready']['output_absent'] = False
            elif mutation == 'parent': case['parent_absent_at_ready'] = False
            else: case['sentinel']['errno'] = 13
            with self.subTest(mutation=mutation),self.assertRaises(mount.Refused):
                mount.check_synthetic_probe(**case)

    def test_ack_requires_parent_and_child_exact_digest(self):
        for field in ('parent_fsync_readback_sha256','child_post_ack_readback_sha256',
                      'ack_received'):
            case = self.fixture()
            case['ack'][field] = False if field == 'ack_received' else '0'*64
            with self.subTest(field=field),self.assertRaisesRegex(
                    mount.Refused,'PARENT_WRITE_ACK_CHILD_READBACK_JOIN'):
                mount.check_synthetic_probe(**case)

    def test_predecessor_drift_and_period_expiry_refuse(self):
        wrong = dict(mount.PINS)
        wrong[mount.PREVIOUS_REVIEW] = '0'*64
        with mock.patch.object(mount,'PINS',wrong),self.assertRaisesRegex(
                mount.Refused,'PREDECESSOR_DRIFT'):
            mount.vector()
        with self.assertRaises(ValueError):
            mount.vector(dt.datetime(2026,10,21,15,0,tzinfo=dt.timezone.utc))

    def test_all_effect_entrypoints_refuse(self):
        for entry in (mount.stage_or_mount_effect,mount.run_public_namespace_probe,
                      mount.issue_auth_key_policy_or_cleanup):
            with self.subTest(entry=entry.__name__),self.assertRaises(mount.Refused):
                entry()


if __name__ == '__main__':
    unittest.main()
