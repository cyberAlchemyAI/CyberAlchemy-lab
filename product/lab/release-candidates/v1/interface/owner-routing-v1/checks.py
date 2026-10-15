"""Actual schema construction and rejection checks; no owner impersonation."""
import argparse
import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import prepare as P


class Checks(unittest.TestCase):
    def setUp(self):
        self.registry, self.decision = P.inputs()
        self.bodies, self.plan = P.propose(self.registry, self.decision, '2026-10-10T01:00:00Z')

    def test_all_41_exact_existing_schemas(self):
        P.validate(self.bodies, self.plan)
        self.assertEqual([sum(kind == k for _, kind, _ in self.bodies) for k in ['principal', 'role', 'role-assignment']], [1, 20, 20])

    def test_all_20_original_scopes_and_separate_roles(self):
        by_file = {name: body for name, _, body in self.bodies}
        for original, mapped, scope in zip(self.registry['role_assignments'], self.plan['mappings'], self.plan['protocol_scopes']):
            self.assertEqual(original, mapped['original_row'])
            self.assertEqual(original['scope'], scope['original_scope_prose'])
            role, assignment = by_file[mapped['role_file']], by_file[mapped['assignment_file']]
            self.assertEqual(role['purpose'], original['scope'])
            self.assertEqual(role['node_id'], mapped['role_identity_mapping']['to'])
            self.assertEqual(assignment['role_ref'], role['node_id'])
            self.assertEqual(role['scope_ref'], assignment['scope_ref'])
            self.assertEqual(mapped['decision_separation'], 'required')

    def test_principal_stable_identity_without_aliases(self):
        principal = self.bodies[0][2]
        self.assertEqual(principal['payload']['stable_subject_ref'], 'person:<vrondelli>')
        self.assertNotEqual(principal['node_id'], 'principal:repository-owner')
        self.assertFalse(self.plan['automatic_principal_aliases'])
        self.assertFalse(self.plan['principal_identity_mapping']['authentication_verified'])

    def test_period_is_proposed_not_historical_or_runtime(self):
        for _, kind, body in self.bodies:
            if kind == 'role-assignment':
                self.assertEqual(body['assignment_state'], 'proposed')
                self.assertEqual(body['period'], {'start': self.plan['proposed_at'], 'end': None})
                self.assertFalse(body['authority_claim_refs'])
        self.assertTrue(all(not m['legacy_period_present'] and m['legacy_period'] is None for m in self.plan['mappings']))

    def test_owned_disk_roundtrip_exact_bytes(self):
        with tempfile.TemporaryDirectory(prefix='cal-owner-representation-') as temp:
            root = Path(temp) / 'package'
            proposal = P.write_package(root, self.bodies, self.plan)
            self.assertEqual(len(list(root.iterdir())), 42)
            for target in proposal['exact_targets']:
                raw = (root / target['filename']).read_bytes()
                self.assertEqual(P.sha(raw), target['byte_sha256'])
                self.assertEqual(json.loads(raw)['node_id'], target['identity_ref'])
                self.assertFalse(target['independent_decision_core_prepared'])
        self.assertFalse(Path(temp).exists())

    def test_duplicate_role_rejected(self):
        r = copy.deepcopy(self.registry)
        r['role_assignments'][1]['role_id'] = r['role_assignments'][0]['role_id']
        with self.assertRaises(AssertionError):
            P.propose(r, self.decision, self.plan['proposed_at'])

    def test_duplicate_assignment_rejected(self):
        r = copy.deepcopy(self.registry)
        r['role_assignments'][1]['assignment_id'] = r['role_assignments'][0]['assignment_id']
        with self.assertRaises(AssertionError):
            P.propose(r, self.decision, self.plan['proposed_at'])

    def test_principal_alias_rejected(self):
        r = copy.deepcopy(self.registry)
        r['role_assignments'][0]['principal_id'] = 'person-reference:repository-owner'
        with self.assertRaises(AssertionError):
            P.propose(r, self.decision, self.plan['proposed_at'])

    def test_merged_decision_voice_rejected(self):
        r = copy.deepcopy(self.registry)
        r['role_assignments'][0]['decision_separation'] = 'optional'
        with self.assertRaises(AssertionError):
            P.propose(r, self.decision, self.plan['proposed_at'])

    def test_unknown_legacy_period_not_invented(self):
        r = copy.deepcopy(self.registry)
        r['role_assignments'][0]['period'] = {'start': '2020-01-01'}
        with self.assertRaises(AssertionError):
            P.propose(r, self.decision, self.plan['proposed_at'])

    def test_proposed_role_cannot_claim_dispatch(self):
        self.assertFalse(self.plan['required_governing_role_coverage_verified'])
        self.assertFalse(self.plan['public_review_adapter_implemented'])
        self.assertIsNone(self.plan['actual_owner_outcome'])
        for _, kind, body in self.bodies:
            self.assertEqual(body['authority_effect'], 'none')
            if kind == 'role':
                self.assertEqual(body['lifecycle_state'], 'draft')
                self.assertFalse(body['eligible_authority_relation_kinds'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    P.guard(args.source_sha256)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    P.guard(args.source_sha256)
    if not result.wasSuccessful():
        raise SystemExit(1)
    registry, decision = P.inputs()
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    bodies, plan = P.propose(registry, decision, timestamp)
    proposal = P.write_package(P.HERE / 'artifacts', bodies, plan)
    P.guard(args.source_sha256)
    receipt = {'schema_version': 'lab-owner-representation-checks/v1-candidate', 'result': 'PASS',
               'tests_run': result.testsRun, 'source_sha256': args.source_sha256, 'schema_valid_targets': 41,
               'separate_legacy_assignments': 20, 'proposal_binding': P.binding(P.HERE / 'artifacts/proposal.json'),
               'public_api_operations': 12, 'remaining_public_api_operations': 22,
               'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False}
    with (P.HERE / 'checks.json').open('xb') as f:
        f.write(P.encoded(receipt))
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
