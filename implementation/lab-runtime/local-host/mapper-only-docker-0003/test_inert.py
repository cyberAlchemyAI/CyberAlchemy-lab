"""Causal inert Mapper selector checks; no Reader, Mapper, native or Docker effect."""
import json
import datetime as dt
import subprocess
import unittest
from pathlib import Path

import construct


class InertSelector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = {name: (construct.REPO / construct.OLD / name).read_bytes()
                        for name in construct.PREIMAGES}

    def refuses(self, call):
        with self.assertRaises(ValueError):
            call()

    def test_exact_four_roles_and_five_pins(self):
        counts = []
        for name, raw in self.original.items():
            projected, ledger = construct.role_projection(name, raw)
            self.assertEqual(ledger['inverse_recovered_sha256'], ledger['preimage_sha256'])
            self.assertEqual(ledger['projection_sha256'], construct.digest(projected))
            counts.append(sum(ledger['predecessor_occurrences'].values()))
        self.assertEqual(counts, [0, 3, 2, 0])

    def test_changed_preimage(self):
        self.refuses(lambda: construct.role_projection('base.py', self.original['base.py'] + b' '))

    def test_wrong_or_missing_pin(self):
        bad = dict(construct.NEW_PINS, source='f' * 63)
        self.refuses(lambda: construct.role_projection('base.py', self.original['base.py'], bad))
        bad = dict(construct.NEW_PINS)
        bad.pop('reader')
        self.refuses(lambda: construct.role_projection('base.py', self.original['base.py'], bad))

    def test_duplicate_old_pin_is_refused(self):
        raw = self.original['base.py'] + construct.OLD_PINS['reader'].encode()
        self.refuses(lambda: construct.role_projection('base.py', raw))

    def test_public_closure_excludes_protected_history(self):
        state, generated = construct.build()
        rows = state['manifest']['files']
        self.assertEqual(len(rows), 953)
        self.assertEqual(len({r['path'] for r in rows}), 953)
        self.assertFalse(any(r['path'].endswith('/branch.snapshot') or
                             'legacy-session-fixture-' in r['path'] for r in rows))
        self.assertEqual(len(generated), 4)
        self.assertFalse(Path(state['fresh_attempt']).exists())
        self.assertNotEqual(Path(state['copy_from']), Path(state['copy_to']))
        self.assertEqual(state['reader_predecessor']['reader_unified3_overall'], 'UNKNOWN')
        self.assertIsNone(state['reader_predecessor']['reader_cold_open_pass_receipt'])

    def test_frozen_projection_matches_generator(self):
        state, generated = construct.build()
        saved = json.loads((construct.HERE / 'selection.json').read_bytes())
        self.assertEqual(saved['manifest'], state['manifest'])
        self.assertEqual(saved['ledger'], state['ledger'])
        for name, raw in generated.items():
            self.assertEqual((construct.HERE / 'generated' / construct.NEW / name).read_bytes(), raw)
        manifest = construct.canonical(state['manifest'])
        self.assertEqual((construct.HERE / 'generated' / construct.NEW / 'source-manifest.json').read_bytes(), manifest)
        self.assertEqual(saved['mapper_manifest_sha256'], construct.digest(manifest))

    def test_reader_gate_refuses_unknown_stage_only_forgery_and_expiry(self):
        receipt = {'schema_version': 'lab-disposable-reader-receipt/v1-private',
                   'reader_manifest_sha256': construct.NEW_PINS['reader'],
                   'source_manifest_sha256': construct.NEW_PINS['source'],
                   'source_package_manifest_sha256': construct.NEW_PINS['package'],
                   'authority_effect': 'none', 'actual_owner_outcome': None}
        terminal = {'overall': 'PASS', 'operation': 'PASS', 'cleanup': 'PASS',
                    'reader_effect': 'DISPOSABLE_READER_DIAGNOSTIC',
                    'client_exit': 0, 'daemon_exit': 0,
                    'daemon_exit_consistent': True, 'absent': True,
                    'forced_cleanup': False, 'postclose_inputs': 'PASS',
                    'output_attachment': 'PASS', 'stream_or_deadline_failure': False,
                    'receipt_sha256': construct.digest(construct.canonical(receipt))}
        raw = construct.canonical(terminal)
        period = {'not_before': '2026-10-20T08:20:00+00:00',
                  'expires_at': '2026-10-21T08:20:00+00:00'}
        now = dt.datetime(2026, 10, 20, 12, tzinfo=dt.timezone.utc)
        def check(t=terminal, r=receipt, exit_code=0, reviewed_sha=None,
                  selected_period=period, selected_now=now):
            construct.reader_gate(t, r, exit_code, reviewed_sha or construct.digest(raw),
                                  raw, selected_period, selected_now)
        check()
        self.refuses(lambda: check(exit_code=2))
        self.refuses(lambda: check(t=dict(terminal, overall='UNKNOWN')))
        self.refuses(lambda: check(t=dict(terminal, reader_effect='NOT_RUN')))
        self.refuses(lambda: check(r=dict(receipt, source_manifest_sha256='0' * 64)))
        self.refuses(lambda: check(reviewed_sha='1' * 64))
        self.refuses(lambda: check(selected_now=dt.datetime(2026, 10, 21, 9,
                                                            tzinfo=dt.timezone.utc)))

    def test_native_hash_mode_abi_and_library_negatives(self):
        path = construct.REPO / construct.NATIVE
        raw = path.read_bytes()
        ph = subprocess.run(['readelf', '-l', str(path)], check=True,
                            capture_output=True, text=True).stdout
        dh = subprocess.run(['readelf', '-d', str(path)], check=True,
                            capture_output=True, text=True).stdout
        def check(data=raw, mode=0o755, program=ph, dynamic=dh):
            construct.native_abi_gate(data, mode, program, dynamic)
        check()
        self.refuses(lambda: check(data=raw[:-1] + bytes([raw[-1] ^ 1])))
        self.refuses(lambda: check(mode=0o644))
        self.refuses(lambda: check(program=ph.replace('/lib64/ld-linux-x86-64.so.2', '/wrong')))
        self.refuses(lambda: check(dynamic=dh.replace('libgcc_s.so.1', 'wrong.so')))

    def test_resource_and_attempt_negatives(self):
        check = construct.resource_gate
        check(1024, 512 * 1024 * 1024, 2200, False)
        self.refuses(lambda: check(1023, 512 * 1024 * 1024, 2200, False))
        self.refuses(lambda: check(1024, 512 * 1024 * 1024 - 1, 2200, False))
        self.refuses(lambda: check(1024, 512 * 1024 * 1024, 2199, False))
        self.refuses(lambda: check(1024, 512 * 1024 * 1024, 2200, True))

    def test_exact_output_and_scratch_path_graph(self):
        state, generated = construct.build()
        plan = state['copy_and_mount_plan']
        build = generated['build.py']
        construct.path_graph_gate(plan, build, packages_empty=True)
        self.assertEqual(len(plan['expected_package_members']), 55)
        self.assertEqual(plan['expected_package_members'][0], 'semantic/00000001.json')
        self.assertEqual(plan['expected_package_members'][25], 'governance/00000001.json')
        self.assertEqual(plan['expected_package_members'][-1], 'manifest.json')
        self.assertEqual(plan['container_mounts'][0]['mode'], 'ro')
        self.assertEqual(plan['container_mounts'][1]['mode'], 'rw')
        self.assertEqual(plan['container_mounts'][1]['target'],
                         '/workspace/' + construct.NEW + '/packages')
        self.assertIn("dir='/attempt/scratch'", build.decode())
        self.assertNotIn("HERE/'receipts'", build.decode())
        self.assertEqual(plan['container_env'], {'TMPDIR': '/attempt/scratch'})
        self.assertEqual(plan['container_mounts'][3]['size_bytes'], 536870912)

    def test_path_graph_refuses_unmapped_output_and_temp(self):
        state, generated = construct.build()
        plan = state['copy_and_mount_plan']
        build = generated['build.py']
        def changed(key, value):
            clone = json.loads(json.dumps(plan))
            clone[key] = value
            return clone
        self.refuses(lambda: construct.path_graph_gate(plan, build, packages_empty=False))
        self.refuses(lambda: construct.path_graph_gate(
            changed('container_env', {}), build, packages_empty=True))
        self.refuses(lambda: construct.path_graph_gate(
            changed('output_package_container', '/attempt/output/0001'), build,
            packages_empty=True))
        bad = json.loads(json.dumps(plan))
        bad['container_mounts'][1]['mode'] = 'ro'
        self.refuses(lambda: construct.path_graph_gate(bad, build, packages_empty=True))
        bad = json.loads(json.dumps(plan))
        bad['container_mounts'].pop()
        self.refuses(lambda: construct.path_graph_gate(bad, build, packages_empty=True))
        bad = json.loads(json.dumps(plan))
        bad['expected_package_members'].pop()
        self.refuses(lambda: construct.path_graph_gate(bad, build, packages_empty=True))
        self.refuses(lambda: construct.path_graph_gate(
            plan, build.replace(b"dir='/attempt/scratch'", b"dir='/tmp'"), packages_empty=True))

    def test_exact_effective_user_archive_output_and_scratch(self):
        state, _ = construct.build()
        identity = state['container_identity']
        archive, traversed = construct.selected_stage_permissions()
        self.assertEqual(archive, (1000, 1000, 0o600))
        self.assertGreater(len(traversed), 5)
        self.assertEqual(identity['runtime_user'], '1000:1000')
        self.assertEqual(identity['image_default_user'], '20001:20001')
        self.assertEqual(state['copy_and_mount_plan']['container_mounts'][3]['uid'], 1000)
        self.assertEqual(state['copy_and_mount_plan']['container_mounts'][3]['gid'], 1000)
        construct.permission_gate(identity, archive_owner=archive,
                                  package_owner=(1000, 1000, 0o700),
                                  scratch_owner=(1000, 1000, 0o700),
                                  traversed=traversed)

    def test_permission_negatives(self):
        state, _ = construct.build()
        identity = state['container_identity']
        archive, traversed = construct.selected_stage_permissions()
        def check(selected_identity=identity, selected_archive=archive,
                  package=(1000, 1000, 0o700), scratch=(1000, 1000, 0o700),
                  path=traversed):
            construct.permission_gate(selected_identity,
                                      archive_owner=selected_archive,
                                      package_owner=package,
                                      scratch_owner=scratch,
                                      traversed=path)
        self.refuses(lambda: check(selected_identity=dict(identity, runtime_user='20001:20001')))
        self.refuses(lambda: check(selected_identity=dict(identity, runtime_userns='private')))
        self.refuses(lambda: check(selected_archive=(1000, 1000, 0o000)))
        self.refuses(lambda: check(selected_archive=(20001, 20001, 0o600)))
        self.refuses(lambda: check(package=(20001, 20001, 0o700)))
        self.refuses(lambda: check(package=(1000, 1000, 0o500)))
        self.refuses(lambda: check(scratch=(0, 0, 0o700)))
        self.refuses(lambda: check(scratch=(1000, 1000, 0o500)))
        self.refuses(lambda: check(path=traversed[:-1] + [(1000, 1000, 0o600)]))

    def test_synthetic_access_probe_binding_and_negatives(self):
        raw = construct.PROBE.read_bytes()
        self.assertEqual(construct.digest(raw), construct.PROBE_SHA)
        receipt = json.loads(raw)
        construct.synthetic_probe_gate(receipt)
        self.refuses(lambda: construct.synthetic_probe_gate(dict(receipt, docker_exit=2)))
        self.refuses(lambda: construct.synthetic_probe_gate(dict(receipt, effective_user='20001:20001')))
        self.refuses(lambda: construct.synthetic_probe_gate(dict(receipt, container_absent=False)))
        bad = json.loads(json.dumps(receipt))
        bad['observed']['scratch_write'] = False
        self.refuses(lambda: construct.synthetic_probe_gate(bad))


if __name__ == '__main__':
    unittest.main()
