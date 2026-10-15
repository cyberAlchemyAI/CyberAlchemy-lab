"""Complete typed scope profiles; actual scope refusal stays operationally blocked."""
import copy
import unittest
from . import adapter as A
from .test_predecessor_binding import PredecessorBindingTests


class ScopePreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): PredecessorBindingTests.setUpClass()

    def setUp(self):
        self.b = PredecessorBindingTests(); self.b.setUp(); self.f = self.b.f
        self.domain = self.f.config['scope_ref']
        self.storage = 'project:hypothetical-typed-scope-test-only'
        self.f.config['scope_ref'] = self.storage
        self.f.expected_config_digest = self.f.C.digest(self.f.config)
        self.f.proposal['scope_ref'] = self.storage
        for target in self.f.proposal['targets']:
            target['artifact']['scope_ref'] = self.storage
            if target['predecessor'] is not None: target['predecessor']['scope_ref'] = self.storage
        C = self.f.C
        self.profile = {
            'schema_version': 'lab-exact-typed-scope-preparation-profile/v1-candidate',
            'storage_scope_ref': self.storage, 'semantic_scope_ref': self.domain,
            'source_bindings': {
                'catalog_snapshot_digest': self.f.selection['snapshot_digest'],
                'catalog_profile_sha256': self.f.fixture.profile_sha,
                'runtime_baseline_digest': C.digest(self.b.b.baseline),
                'runtime_projection_digest': C.digest(self.f.projection),
                'runtime_config_digest': C.digest(self.f.config), 'runtime_head': self.f.head,
                'representation_profile_sha256': self.b.profile_pin},
            'proposal_structural_sha256': C.digest(self.f.proposal),
            'inspection_structural_sha256': C.digest(self.f.inspection),
            'impact_structural_sha256': C.digest(self.f.impact),
            'ordered_target_version_refs': [t['artifact']['version_ref'] for t in self.f.proposal['targets']],
            'ordered_decision_core_bindings': [t['decision_core_binding'] for t in self.f.proposal['targets']],
            'schema_bindings': copy.deepcopy(self.f.proposal['schema_bindings']),
            'runtime_admission_authorized': False, 'actual_owner_outcome': None, 'authority_effect': 'none'}

    def check(self, **changes):
        raw = self.f.C.encoded(self.profile)
        args = dict(independently_selected_scope_preparation_profile_bytes=raw,
                    expected_scope_preparation_profile_sha256=A.sha(raw))
        args.update(changes)
        return self.b.check(**args)

    def test_01_complete_coupled_hypothesis_preserves_all_actual_inputs(self):
        before = [self.f.C.encoded(x) for x in [self.f.projection, self.f.config, self.f.proposal]]
        result = self.check(); scope = result['scope_preparation']
        self.assertEqual(result['result'], 'PASS')
        self.assertEqual(scope['actual_preparation_result'], 'REFUSED')
        self.assertEqual(scope['actual_scope_refusal'], 'target outside authorized scope')
        self.assertEqual(scope['configuration_status'], 'hypothetical-unprovisioned')
        self.assertEqual(scope['complete_ordered_target_version_refs'], self.profile['ordered_target_version_refs'])
        self.assertFalse(scope['runtime_admission_authorized'])
        self.assertFalse(scope['operational_preparation_ready'])
        self.assertFalse(result['runtime_admission_authorized'])
        self.assertEqual(result['actual_transactions_written'], 0)
        self.assertEqual(before, [self.f.C.encoded(x) for x in [self.f.projection, self.f.config, self.f.proposal]])
        self.assertTrue(result['all_target_schema_and_core_checks'])
        self.assertTrue(result['all_affected_schema_and_ordered_roles_closed'])

    def test_02_default_actual_scope_refusal_remains(self):
        with self.assertRaisesRegex(self.f.C.RuntimeFault, 'target outside authorized scope'):
            self.b.check()

    def test_03_independent_profile_pin_required(self):
        with self.assertRaisesRegex(A.WireFault, 'scope profile pin'):
            self.check(expected_scope_preparation_profile_sha256='0' * 64)

    def test_04_partial_profile_inputs_refused(self):
        with self.assertRaisesRegex(A.WireFault, 'scope preparation inputs must be complete'):
            self.check(expected_scope_preparation_profile_sha256=None)

    def test_05_profile_cannot_grant_admission(self):
        self.profile['runtime_admission_authorized'] = True
        with self.assertRaisesRegex(A.WireFault, 'candidate-only typed scope profile'): self.check()

    def test_06_complete_wire_proposal_bound(self):
        self.profile['proposal_structural_sha256'] = '0' * 64
        with self.assertRaisesRegex(A.WireFault, 'wire proposal differs'): self.check()

    def test_07_complete_ordered_target_group_bound(self):
        self.profile['ordered_target_version_refs'].reverse()
        with self.assertRaisesRegex(A.WireFault, 'ordered typed scope target group'): self.check()

    def test_08_complete_schema_inventory_bound(self):
        self.profile['schema_bindings'].pop()
        with self.assertRaisesRegex(A.WireFault, 'schema/core binding inventory'): self.check()

    def test_09_complete_ordered_core_bindings_bound(self):
        self.profile['ordered_decision_core_bindings'][0] = {**self.profile['ordered_decision_core_bindings'][0], 'sha256': '0' * 64}
        with self.assertRaisesRegex(A.WireFault, 'schema/core binding inventory'): self.check()

    def test_10_independent_runtime_baseline_bound(self):
        self.profile['source_bindings']['runtime_baseline_digest'] = '0' * 64
        with self.assertRaisesRegex(A.WireFault, 'scope source/current/profile pins'): self.check()

    def test_11_actual_configuration_pin_bound(self):
        self.profile['source_bindings']['runtime_config_digest'] = '0' * 64
        with self.assertRaisesRegex(A.WireFault, 'scope source/current/profile pins'): self.check()

    def test_12_complete_inspection_bound(self):
        self.profile['inspection_structural_sha256'] = '0' * 64
        with self.assertRaisesRegex(A.WireFault, 'scope inspection/impact'): self.check()

    def test_13_complete_coupling_impact_bound(self):
        self.profile['impact_structural_sha256'] = '0' * 64
        with self.assertRaisesRegex(A.WireFault, 'scope inspection/impact'): self.check()

    def test_14_same_scope_needs_no_hypothesis(self):
        self.profile['semantic_scope_ref'] = self.storage
        with self.assertRaisesRegex(A.WireFault, 'distinct storage/domain scopes'): self.check()

    def test_15_closed_profile_cannot_add_category_authority(self):
        self.profile['permitted_categories'] = ['artifact-instance']
        with self.assertRaisesRegex(A.WireFault, 'candidate-only typed scope profile'): self.check()

    def test_16_declared_semantic_scope_matches_exact_original_bodies(self):
        self.profile['semantic_scope_ref'] = 'scope:hypothetical-other'
        with self.assertRaisesRegex(A.WireFault, 'semantic scope differs'): self.check()
