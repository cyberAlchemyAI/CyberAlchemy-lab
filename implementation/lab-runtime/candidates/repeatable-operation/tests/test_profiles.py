from __future__ import annotations

import base64
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
REPO = PACKAGE.parents[3]
sys.path.insert(0, str(PACKAGE))
from lab_runtime.common import RuntimeFault, binding, byte_digest, digest, encoded, load
from lab_runtime.profiles import select
from lab_runtime.sources import capture, freshness, original_bytes, verify_snapshot


class Profiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selections = load(PACKAGE / 'profiles/selections.json')['selections']
        cls.captures = {}
        for row in cls.selections:
            cls.captures[row['name']] = capture(select(REPO, **cls.args(row)))

    @staticmethod
    def args(row):
        return {k: v for k, v in row.items() if k not in ['name', 'source_materials', 'source_bytes']}

    def fixture(self):
        temporary = TemporaryDirectory(prefix='lab-source-profile-')
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        prefix = PACKAGE.relative_to(REPO)
        dst = root / prefix
        for path in list((PACKAGE / 'lab_runtime').rglob('*.py')) + [PACKAGE / 'lab.py']:
            if '__pycache__' in path.parts:
                continue
            target = root / path.relative_to(REPO)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        (root / 'materials').mkdir()
        (root / 'materials/work.json').write_bytes(b'{ "node_id" : "work:test", "status" : "admitted" }\n')
        self.put(root / 'materials/basis.json', {'authority_effect': 'none', 'purpose': 'isolated test fixture'})
        self.put(root / 'compatibility.json', {'authority_effect': 'none', 'bindings': []})
        body_ref = binding(root, 'materials/work.json')
        config = {'schema_version': 'lab-native-source-bindings/v1-candidate', 'authority_effect': 'none',
            'subject_bindings': [{'version_ref': 'work:test@fixture.1', 'identity_ref': 'work:test',
                'identity_selector': '/node_id', 'path': body_ref['path'], 'sha256': body_ref['sha256'],
                'semantic_kind': 'work', 'carrier_ref': 'cal.artifact-type.work/v1'}]}
        self.put(root / 'materials/config.json', config)
        files = [binding(root, p.relative_to(root).as_posix()) for p in sorted((root / 'materials').glob('*.json'))]
        self.put(root / 'manifest.json', {'schema_version': 'lab-source-content-manifest/v1-candidate',
            'authority_effect': 'none', 'source_cut': 'fixture:cut:1', 'materials': files})
        code_files = [binding(root, p.relative_to(root).as_posix()) for p in sorted(dst.rglob('*.py'))]
        self.put(root / 'executable.json', {'schema_version': 'lab-executable-manifest/v1-candidate', 'authority_effect': 'none', 'files': code_files})
        self.put(root / 'policy.json', {'schema_version': 'lab-source-capture-policy/v1-candidate', 'authority_effect': 'none',
            'policy_id': 'policy:fixture', 'allowed_source_roots': ['materials'], 'max_files': 20,
            'max_source_bytes': 100000, 'capture_provider': 'native-byte-manifest',
            'capture_config': binding(root, 'materials/config.json'),
            'code_roots': [(prefix / 'lab_runtime').as_posix(), (prefix / 'lab.py').as_posix()],
            'compatibility_binding': binding(root, 'compatibility.json')})
        ref = binding(root, 'materials/basis.json')
        ref.pop('size_bytes')
        manifest_ref = binding(root, 'manifest.json')
        manifest_ref.pop('size_bytes')
        self.put(root / 'profile.json', {'schema_version': 'lab-independent-source-profile/v1-candidate',
            'authority_effect': 'none', 'profile_id': 'profile:fixture', 'protocol_version': 1,
            'executable_manifest_sha256': binding(root, 'executable.json')['sha256'],
            'policy_core_sha256': binding(root, 'policy.json')['sha256'], 'authority_basis': [ref], 'registries': [ref],
            'content_manifest': manifest_ref, 'expected_cut': 'fixture:cut:1', 'domain_posture': 'isolated-candidate',
            'transition_basis': {'mode': 'initial', 'basis_refs': [ref]}})
        self.review(root)
        return root

    @staticmethod
    def put(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encoded(value))

    def review(self, root):
        profile = load(root / 'profile.json')
        self.put(root / 'review.json', {'schema_version': 'lab-profile-selection-review/v1-candidate', 'authority_effect': 'none',
            'purpose': 'candidate-read-selection-only', 'profile_sha256': byte_digest((root / 'profile.json').read_bytes()),
            'policy_sha256': profile['policy_core_sha256'], 'executable_manifest_sha256': profile['executable_manifest_sha256'],
            'content_manifest_sha256': profile['content_manifest']['sha256'], 'expected_cut': profile['expected_cut'],
            'domain_posture': profile['domain_posture'], 'scope_ref': 'scope:test-fixture', 'provenance_ref': 'isolated-test'})

    def choose(self, root):
        return select(root, profile_path='profile.json', profile_sha256=byte_digest((root / 'profile.json').read_bytes()),
            policy_path='policy.json', executable_manifest_path='executable.json', review_path='review.json',
            review_sha256=byte_digest((root / 'review.json').read_bytes()))

    def update_policy(self, root, update):
        policy = load(root / 'policy.json')
        update(policy)
        self.put(root / 'policy.json', policy)
        profile = load(root / 'profile.json')
        profile['policy_core_sha256'] = byte_digest((root / 'policy.json').read_bytes())
        self.put(root / 'profile.json', profile)
        self.review(root)

    def update_manifest(self, root, update):
        manifest = load(root / 'manifest.json')
        update(manifest)
        self.put(root / 'manifest.json', manifest)
        profile = load(root / 'profile.json')
        profile['content_manifest']['sha256'] = byte_digest((root / 'manifest.json').read_bytes())
        self.put(root / 'profile.json', profile)
        self.review(root)

    def test_two_real_profiles_same_executable(self):
        a, b = self.captures['d74'], self.captures['d75']
        self.assertEqual(a['source_profile']['executable_manifest_sha256'], b['source_profile']['executable_manifest_sha256'])
        self.assertEqual((a['expected_cut'], b['expected_cut']), ('decision:0074', 'decision:0075'))
        self.assertNotEqual(a['source_profile_sha256'], b['source_profile_sha256'])
        self.assertEqual((len(a['materials']), len(b['materials'])), (698, 760))
        self.assertEqual(b['state']['payload']['cursor'], 'decision:0075')
        self.assertEqual([len(h['payload']['events']) for h in b['histories'].values()], [5, 5])

    def test_original_bytes_real_capture(self):
        name = 'authority/admissions/first-governed-agent-work-episode/v1/instances/artifacts/work.json'
        for value in self.captures.values():
            self.assertEqual(original_bytes(value, name), (REPO / name).read_bytes())

    def test_capture_deterministic(self):
        row = self.selections[1]
        self.assertEqual(capture(select(REPO, **self.args(row))), self.captures[row['name']])

    def test_native_body_label_cannot_admit(self):
        value = capture(self.choose(self.fixture()))
        subject = value['subjects']['work:test@fixture.1']
        self.assertEqual(subject['record']['status'], 'admitted')
        self.assertEqual(subject['effective_state'], 'candidate-unadmitted')
        self.assertIsNone(subject['decision_ref'])
        self.assertEqual(value['selection_scope'], 'candidate-read-selection-only')

    def test_native_cannot_claim_admitted_source(self):
        root = self.fixture()
        profile = load(root / 'profile.json'); profile['domain_posture'] = 'admitted-source'
        self.put(root / 'profile.json', profile); self.review(root)
        with self.assertRaisesRegex(RuntimeFault, 'cannot claim admitted'):
            capture(self.choose(root))

    def test_unknown_protocol(self):
        root = self.fixture()
        profile = load(root / 'profile.json'); profile['protocol_version'] = 99
        self.put(root / 'profile.json', profile)
        with self.assertRaisesRegex(RuntimeFault, 'unsupported source profile'):
            self.choose(root)

    def test_profile_change_does_not_reuse_review(self):
        root = self.fixture()
        profile = load(root / 'profile.json'); profile['profile_id'] = 'profile:unreviewed'
        self.put(root / 'profile.json', profile)
        with self.assertRaisesRegex(RuntimeFault, 'selection review mismatch'):
            self.choose(root)

    def test_review_is_not_owner_authority(self):
        root = self.fixture()
        review = load(root / 'review.json'); review['purpose'] = 'authorize-admission'
        self.put(root / 'review.json', review)
        with self.assertRaisesRegex(RuntimeFault, 'cannot grant operational'):
            self.choose(root)

    def test_changed_source_before_capture(self):
        root = self.fixture(); selected = self.choose(root)
        (root / 'materials/work.json').write_text('{}\n')
        with self.assertRaisesRegex(RuntimeFault, 'digest mismatch'):
            capture(selected)

    def test_changed_lookup_during_capture(self):
        root = self.fixture(); selected = self.choose(root)
        def change(index, name):
            if name == 'materials/work.json':
                (root / name).write_text('{"node_id":"work:changed"}\n')
        with self.assertRaisesRegex(RuntimeFault, 'source drift during capture'):
            capture(selected, after_read=change)

    def test_new_epoch_invalidates_capture(self):
        root = self.fixture(); source = capture(self.choose(root))
        self.put(root / 'authority/admissions/new/v1/bundle.json', {})
        self.assertIn('repository-admission-epoch-inventory', freshness(root, source)['changed'])

    def test_changed_executable_rejected(self):
        root = self.fixture()
        name = PACKAGE.relative_to(REPO) / 'lab_runtime/common.py'
        (root / name).write_text('# changed\n')
        with self.assertRaisesRegex(RuntimeFault, 'digest mismatch'):
            self.choose(root)

    def test_new_code_file_invalidates_existing_capture(self):
        root = self.fixture(); source = capture(self.choose(root))
        name = PACKAGE.relative_to(REPO) / 'lab_runtime/unreviewed_module.py'
        (root / name).write_text('# unreviewed program extension\n')
        self.assertIn('executable-closure-changed', freshness(root, source)['changed'])

    def test_empty_executable_cannot_bind_running_program(self):
        root = self.fixture()
        self.put(root / 'executable.json', {'schema_version': 'lab-executable-manifest/v1-candidate', 'authority_effect': 'none', 'files': []})
        profile = load(root / 'profile.json'); profile['executable_manifest_sha256'] = byte_digest((root / 'executable.json').read_bytes())
        self.put(root / 'profile.json', profile)
        self.update_policy(root, lambda p: p.update(code_roots=[]))
        with self.assertRaisesRegex(RuntimeFault, 'running executable'):
            self.choose(root)

    def test_duplicate_and_noncanonical_paths_rejected(self):
        for mode in ['duplicate', 'alias']:
            root = self.fixture()
            def change(m):
                if mode == 'duplicate': m['materials'].append(m['materials'][0])
                else: m['materials'][0]['path'] = 'materials//basis.json'
            self.update_manifest(root, change)
            with self.assertRaises(RuntimeFault): self.choose(root)

    def test_capture_budgets_rejected(self):
        for field, value in [('max_files', 1), ('max_source_bytes', 1)]:
            root = self.fixture(); self.update_policy(root, lambda p: p.update({field: value}))
            with self.assertRaisesRegex(RuntimeFault, 'budget exceeded'): self.choose(root)

    def test_path_escape_and_private_materials_rejected(self):
        for path in ['../work.json', '.local/private.json', 'materials/owner.pem']:
            root = self.fixture()
            self.update_manifest(root, lambda m: m['materials'][0].update(path=path))
            with self.assertRaises(RuntimeFault): self.choose(root)

    def test_captured_parsed_body_cannot_be_resealed_inconsistently(self):
        source = capture(self.choose(self.fixture()))
        source['documents']['materials/work.json']['node_id'] = 'work:forged'
        source['snapshot_digest'] = digest({k: v for k, v in source.items() if k != 'snapshot_digest'})
        with self.assertRaisesRegex(RuntimeFault, 'parsed body differs'): verify_snapshot(source)

    def test_changed_bytes_and_self_digest_do_not_replace_manifest(self):
        source = capture(self.choose(self.fixture()))
        raw = b'{"node_id":"work:forged"}'
        source['byte_contents']['materials/work.json'] = base64.b64encode(raw).decode()
        source['materials']['materials/work.json'] = byte_digest(raw)
        source['documents']['materials/work.json'] = json.loads(raw)
        source['snapshot_digest'] = digest({k: v for k, v in source.items() if k != 'snapshot_digest'})
        with self.assertRaisesRegex(RuntimeFault, 'reviewed manifest'): verify_snapshot(source)

    def test_wrong_profile_external_pin_rejected(self):
        with self.assertRaisesRegex(RuntimeFault, 'independently selected profile'):
            verify_snapshot(self.captures['d74'], expected_profile_sha256=self.captures['d75']['source_profile_sha256'])

    def test_original_bytes_outside_capture_rejected(self):
        with self.assertRaisesRegex(RuntimeFault, 'outside capture'):
            original_bytes(self.captures['d74'], 'unselected.json')

    def test_duplicate_keys_and_invalid_unicode_rejected(self):
        from lab_runtime.common import loads
        for raw in [b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":"\\ud800"}', b'\xff']:
            with self.assertRaises(RuntimeFault): loads(raw)

    def test_cli_explicit_selection_fresh_process(self):
        row = self.selections[1]
        args = [sys.executable, str(PACKAGE / 'lab.py'), '--repo', str(REPO), '--profile', row['profile_path'],
            '--profile-sha', row['profile_sha256'], '--policy', row['policy_path'], '--executable-manifest', row['executable_manifest_path'],
            '--selection-review', row['review_path'], '--selection-review-sha', row['review_sha256'], 'capture-status']
        run = subprocess.run(args, text=True, capture_output=True, timeout=30)
        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
        result = json.loads(run.stdout)
        self.assertEqual(result['snapshot_digest'], self.captures['d75']['snapshot_digest'])
        self.assertEqual(result['source_cut'], 'decision:0075')


if __name__ == '__main__':
    unittest.main()
