import copy
from dataclasses import asdict, replace
import json
from pathlib import Path
import subprocess
import sys
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE))
from provision import *


class ProvisionTests(unittest.TestCase):
    observed = None
    @classmethod
    def setUpClass(cls):
        cls.branch = CandidateBranch(CandidateScope('c11-provisioning-rehearsal', 'role:candidate-c11-operator', 'scope:lab-runtime-local:c11-provisioning-rehearsal'))
        cls.addClassCleanup(cls.branch.close)
        cls.catalog = cls.branch.bootstrap_catalog()
        cls.exported, cls.export_digests = cls.branch.export_project()
        cls.controls = cls.branch.root / 'cold-controls.json'
        cls.controls.write_bytes(encoded({'path': str(cls.exported), 'pins': asdict(cls.branch.pins),
            'catalog_path': str(cls.branch.catalog_path), 'catalog_pins': asdict(cls.branch.catalog_pins),
            'catalog_policy': cls.branch.catalog_policy.core()}))

    def test_explicit_public_store_boundary(self):
        branch = self.branch; config = branch.initial['config']
        self.assertEqual(config['store_id'], branch.scope.store_id)
        self.assertEqual(config['owner_ref'], branch.scope.operator_ref)
        self.assertEqual(config['scope_ref'], branch.scope.scope_ref)
        self.assertEqual(config['allowed_categories'], ['artifact-instance'])
        self.assertEqual(config['allowed_effects'], ['admit'])
        self.assertEqual(config['repository_admission_effect'], 'none')
        self.assertEqual(branch.initial['head']['sequence'], 0)
        self.assertEqual(branch.initial['freshness']['status'], 'current')
        ProvisionTests.observed = {'fixture_only': True, 'actual_owner_outcome': None,
            'public_configuration': copy.deepcopy(config), 'independent_project_pins': asdict(branch.pins),
            'signed_catalog_pins': asdict(branch.catalog_pins), 'catalog_contracts': len(self.catalog['catalog']['contracts']),
            'catalog_candidates': len(self.catalog['catalog']['candidate_subjects']),
            'private_key_inside_repository': False, 'private_key_inside_store': False, 'private_key_mode': '0600',
            'exported_original_byte_digests': self.export_digests,
            'permanent_store_provisioned': False, 'service_started': False, 'Work_only_authority_adapter': False}

    def test_signed_catalog_retains_candidate_posture(self):
        self.assertEqual(len(self.catalog['catalog']['contracts']), 144)
        self.assertEqual(len(self.catalog['catalog']['candidate_subjects']), 6)
        self.assertIsNone(self.catalog['actual_owner_outcome'])
        self.assertEqual(self.catalog['authority_effect'], 'none')
        response = load(self.branch.catalog_path / 'rehearsal-response.json')
        self.assertTrue(response['fixture_only']); self.assertIsNone(response['human_outcome'])
        self.assertTrue(all(r['effective_state'] == 'candidate-unadmitted' for r in self.catalog['catalog']['candidate_subjects'].values()))

    def test_private_key_outside_repository_and_stores(self):
        key = self.branch.key_path
        self.assertFalse(key.is_relative_to(ROOT)); self.assertFalse(key.is_relative_to(self.branch.store_path))
        self.assertFalse(key.is_relative_to(self.branch.catalog_path))
        self.assertEqual(key.stat().st_mode & 0o777, 0o600)
        for directory in (self.branch.store_path, self.branch.catalog_path, self.exported):
            for path in directory.rglob('*'):
                if path.is_file(): self.assertNotIn(b'PRIVATE KEY', path.read_bytes())

    def test_existing_project_store_never_overwritten(self):
        branch = self.branch; before = (branch.store_path / 'HEAD.json').read_bytes()
        profile = load(Path(branch.stage.name) / 'profile.json')
        with self.assertRaisesRegex(branch.engine.RuntimeFault, 'store already exists'):
            branch.store.initialize(profile, 'overwrite-attempt', branch.scope.operator_ref, branch.public_key)
        self.assertEqual(before, (branch.store_path / 'HEAD.json').read_bytes())

    def test_incompatible_profile_refused_before_creation(self):
        path = self.branch.root / 'incompatible'; store = self.branch.engine.Store(path, ROOT)
        wrong = load(ROOT / 'implementation/lab-runtime/v1/profile.json')
        with self.assertRaisesRegex(self.branch.engine.RuntimeFault, 'exact source profile'):
            store.initialize(wrong, 'bad-profile', self.branch.scope.operator_ref, self.branch.public_key)
        self.assertFalse(path.exists())

    def test_missing_scope_and_graph_role_are_not_authority(self):
        for scope in [replace(self.branch.scope, scope_ref=''), replace(self.branch.scope, operator_ref='role:graph-inferred-owner'), replace(self.branch.scope, candidate_only=False)]:
            with self.assertRaises(RuntimeFault): CandidateBranch(scope)

    def test_unknown_categories_or_effects_refused(self):
        for scope in [replace(self.branch.scope, allowed_categories=('work',)), replace(self.branch.scope, allowed_effects=('withdraw',))]:
            with self.assertRaises(RuntimeFault): CandidateBranch(scope)

    def test_independent_head_and_config_pins_required(self):
        for pins in [replace(self.branch.pins, config_sha256='0' * 64), replace(self.branch.pins, expected_head='0' * 64)]:
            with self.assertRaises(RuntimeFault): full_replay(self.branch.store_path, ROOT, ROOT, pins)

    def test_export_preserves_original_committed_bytes(self):
        self.assertEqual(self.export_digests, {p: byte_digest((self.exported / p).read_bytes()) for p in self.export_digests})
        self.assertEqual(full_replay(self.exported, ROOT, ROOT, self.branch.pins)['head'], self.branch.initial['head'])
        with self.assertRaisesRegex(RuntimeFault, 'export destination already exists'): self.branch.export_project()

    def test_cold_fresh_process_replays_project_and_catalog(self):
        code = 'import json,sys;from provision import *;x=load(sys.argv[1]);r=full_replay(x["path"],ROOT,ROOT,ReplayPins(**x["pins"]),require_current=True);c=bootstrap.replay(x["catalog_path"],bootstrap.CatalogPins(**x["catalog_pins"]),bootstrap.RehearsalPolicy(**x["catalog_policy"]));print(json.dumps({"head":r["head"]["transaction_digest"],"catalog":c["catalog"]["digest"],"human":c["actual_owner_outcome"]}))'
        result = subprocess.run([sys.executable, '-c', code, str(self.controls)], cwd=PACKAGE, capture_output=True, text=True, timeout=90)
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertEqual(value['head'], self.branch.pins.expected_head)
        self.assertEqual(value['catalog'], self.branch.catalog_pins.catalog_digest)
        self.assertIsNone(value['human'])

    def test_verified_genesis_recovery_is_noop(self):
        before = (self.branch.store_path / 'HEAD.json').read_bytes()
        self.branch.store.recover(self.branch.pins.expected_head)
        self.assertEqual(before, (self.branch.store_path / 'HEAD.json').read_bytes())
        full_replay(self.branch.store_path, ROOT, ROOT, self.branch.pins)

    def test_close_removes_fixture_key_and_rejects_use(self):
        branch = CandidateBranch(CandidateScope('c11-cleanup', 'role:candidate-cleanup', 'scope:lab-runtime-local:c11-cleanup'))
        root = branch.root; branch.close(); branch.close()
        self.assertFalse(root.exists())
        with self.assertRaisesRegex(RuntimeFault, 'closed'): branch.export_project()

    def test_repository_local_state_is_git_ignored(self):
        result = subprocess.run(['git', 'check-ignore', '.local/lab-runtime/c11-uncreated/config.json'], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('.local/', result.stdout)
