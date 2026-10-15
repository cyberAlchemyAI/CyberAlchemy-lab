"""Real D75 catalog resolution and complete declared generic carrier impacts."""
import copy
import importlib
import json
import sys
import unittest

from . import adapter as A
from . import source_selection as S

sys.path.insert(0, str(A.KERNEL))
sys.path.insert(0, str(A.KERNEL / 'tests'))
import test_bound_extensions


class SourceSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_bound_extensions.BoundExtensionTests.setUpClass()
        cls.original = test_bound_extensions.BoundExtensionTests

    def setUp(self):
        fixture = self.original()
        fixture.setUp()
        self.fixture = fixture
        self.snapshot = fixture.snapshot
        self.inspection = copy.deepcopy(fixture.p)
        self.evidence = dict(fixture.evidence)

    def select(self, **changes):
        args = dict(expected_profile_sha256=self.fixture.profile_sha,
                    expected_snapshot_digest=self.fixture.snapshot_digest,
                    evidence_bytes=self.evidence)
        args.update(changes)
        return S.select_bound_catalog(self.snapshot, **args)

    def changed_pair(self):
        pair = copy.deepcopy(self.inspection['allowed_endpoint_pairs'][0])
        for suffix in ['kind', 'contract_ref', 'role']:
            pair['source_' + suffix], pair['target_' + suffix] = (
                pair['target_' + suffix], pair['source_' + suffix])
        self.inspection['allowed_endpoint_pairs'].append(pair)

    def test_01_complete_real_relation_inventory(self):
        selected = self.select()
        self.assertEqual(set(selected['relations']), set(self.snapshot['relation_contracts']))
        self.assertEqual(len(selected['relations']), 41)
        self.assertFalse(selected['live_currentness_established'])

    def test_02_exact_predecessor_signature_bytes(self):
        selected = self.select()
        old = selected['relations']['relation.acts-for']
        b = old['signature_binding']
        self.assertEqual(A.sha(selected['materials'][b['ref']]), b['sha256'])
        self.assertEqual(A.parse(selected['materials'][b['ref']])['payload']['unique_question'],
                         old['unique_question'])

    def test_03_resealed_effective_labels_do_not_replace_independent_pin(self):
        self.snapshot = copy.deepcopy(self.snapshot)
        entry = next(s for s in self.snapshot['subjects'].values()
                     if s['category'] == 'relation-kind' and s['effective_state'] == 'admitted-current')
        entry['effective_state'] = 'candidate-unadmitted'
        kernel = A.kernel()
        self.snapshot['snapshot_digest'] = kernel.digest({k: v for k, v in self.snapshot.items()
                                                         if k != 'snapshot_digest'})
        with self.assertRaisesRegex(A.WireFault, 'independent semantic snapshot pin'):
            self.select()

    def test_04_candidate_cannot_shadow_current_schema(self):
        ref = next(iter(self.snapshot['byte_contents']))
        self.evidence[ref] = b'{}'
        with self.assertRaisesRegex(A.WireFault, 'shadow canonical bytes'):
            self.select()

    def test_05_retained_real_pair_requires_no_carrier_rewrite(self):
        impact = S.assess_carrier_impacts(self.select(), self.inspection)
        self.assertEqual(impact['required_current_carrier_refs'], [])
        self.assertEqual(impact['globally_available_pairs_added'], 0)

    def test_06_new_direction_requires_both_roles_and_generic_schema(self):
        self.changed_pair()
        impact = S.assess_carrier_impacts(self.select(), self.inspection)
        self.assertEqual(impact['required_current_carrier_refs'], [
            'cal.artifact-type.agent-instance/v1', 'cal.artifact-type.principal/v1',
            'cal.artifact-type.typed-relation/v3'])

    def test_07_replacing_old_direction_is_refused(self):
        self.changed_pair()
        self.inspection['allowed_endpoint_pairs'].pop(0)
        with self.assertRaisesRegex(A.WireFault, 'remove predecessor ordered pairs'):
            S.assess_carrier_impacts(self.select(), self.inspection)

    def test_08_missing_affected_successors_is_refused(self):
        self.changed_pair()
        impact = S.assess_carrier_impacts(self.select(), self.inspection)
        with self.assertRaisesRegex(A.WireFault, 'successor missing or ambiguous'):
            S.resolve_impacted_successors(impact, {'targets': []}, lambda b: b'{}')

    def test_09_unselected_endpoint_is_not_assumed_admitted(self):
        self.inspection['allowed_endpoint_pairs'][0]['source_contract_ref'] = 'fixture:unselected'
        with self.assertRaisesRegex(A.WireFault, 'prospective carrier resolver'):
            S.assess_carrier_impacts(self.select(), self.inspection)

    def test_10_endpoint_carrier_kind_mismatch_is_refused(self):
        self.inspection['allowed_endpoint_pairs'][0]['source_kind'] = 'principal'
        # Keep the retained pair so the failure specifically identifies the carrier mismatch.
        self.inspection['allowed_endpoint_pairs'].append(copy.deepcopy(self.fixture.p['allowed_endpoint_pairs'][0]))
        with self.assertRaisesRegex(A.WireFault, 'endpoint carrier kind differs'):
            S.assess_carrier_impacts(self.select(), self.inspection)

    def test_11_specialized_authority_requires_declared_resolver(self):
        self.inspection['allowed_endpoint_pairs'][0]['canonical_authority'] = 'specialized-carrier'
        with self.assertRaisesRegex(A.WireFault, 'own independently bound impact resolver'):
            S.assess_carrier_impacts(self.select(), self.inspection)

    def test_12_source_profile_pin_is_independent(self):
        with self.assertRaises(ValueError):
            self.select(expected_profile_sha256='0' * 64)

    def test_13_resolution_preserves_entire_original_snapshot(self):
        before = json.dumps(self.snapshot, sort_keys=True)
        S.assess_carrier_impacts(self.select(), self.inspection)
        self.assertEqual(json.dumps(self.snapshot, sort_keys=True), before)

    def test_14_wildcard_pair_is_refused(self):
        pair = copy.deepcopy(self.inspection['allowed_endpoint_pairs'][0])
        pair['source_kind'] = '*'
        self.inspection['allowed_endpoint_pairs'].append(pair)
        with self.assertRaisesRegex(A.WireFault, 'exact unique ordered pairs'):
            S.assess_carrier_impacts(self.select(), self.inspection)

    def test_15_no_impact_does_not_invent_successor_targets(self):
        selected = self.select()
        impact = S.assess_carrier_impacts(selected, self.inspection)
        self.assertEqual(S.resolve_impacted_successors(impact, {'targets': []}, lambda b: b'{}'), [])
        self.assertEqual(impact['complete_current_carrier_inventory_count'], len(selected['endpoints']))
        self.assertEqual(impact['authority_effect'], 'none')
