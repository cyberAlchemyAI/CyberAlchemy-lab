"""Exact preparation guards; no canonical mutations or owner outcomes."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE))
from review import *


class ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.environ['C10_PREPARATION_PATH']
        cls.pin = os.environ['C10_PREPARATION_SHA256']
        cls.value = validate_preparation(cls.path, cls.pin)
        cls.canonical_binding = binding(REGISTRY)

    def setUp(self):
        self.value = copy.deepcopy(self.__class__.value)

    def test_exact_preparation_and_thirteen_targets(self):
        self.assertEqual(len(validate_preparation(self.path, self.pin)['members']), 13)
        self.assertTrue(validate_members(self.value))

    def test_no_actual_owner_or_outcome(self):
        self.assertIsNone(self.value['actual_owner_outcome'])
        for row in self.value['members']:
            self.assertIsNone(row['selected_outcome'])
            self.assertIsNone(row['actual_answering_principal_ref'])
            self.assertFalse(row['current_owner_authority_verified'])

    def test_false_external_pin_rejected(self):
        with self.assertRaisesRegex(ValueError, 'independent preparation pin'):
            validate_preparation(self.path, '0' * 64)

    def test_missing_member_rejected(self):
        self.value['members'].pop()
        with self.assertRaisesRegex(ValueError, 'missing or duplicate'):
            validate_members(self.value)

    def test_duplicate_member_identity_rejected(self):
        self.value['members'][1]['member_id'] = self.value['members'][0]['member_id']
        with self.assertRaisesRegex(ValueError, 'missing or duplicate'):
            validate_members(self.value)

    def test_changed_target_hash_rejected(self):
        self.value['members'][0]['targets'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'changed exact file binding'):
            validate_members(self.value)

    def test_changed_evidence_hash_rejected(self):
        self.value['members'][0]['evidence'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'changed exact file binding'):
            validate_members(self.value)

    def test_owner_claim_rejected(self):
        for key, val in [('selected_outcome', 'admit'), ('actual_answering_principal_ref', 'owner:fake'), ('current_owner_authority_verified', True)]:
            value = copy.deepcopy(self.value); value['members'][0][key] = val
            with self.assertRaisesRegex(ValueError, 'fabricated owner'):
                validate_members(value)

    def test_envelope_authority_rejected(self):
        self.value['actual_owner_outcome'] = 'admit'
        with self.assertRaisesRegex(ValueError, 'actual authority'):
            validate_members(self.value)

    def test_effect_exclusion_cannot_disappear(self):
        self.value['members'][0]['exclusions'] = []
        with self.assertRaisesRegex(ValueError, 'missing effect exclusion'):
            validate_members(self.value)

    def test_missing_dependency_rejected(self):
        self.value['members'][0]['dependencies'] = ['protocol:C10:unknown']
        with self.assertRaisesRegex(ValueError, 'unresolved member'):
            validate_members(self.value)

    def test_cyclic_dependency_rejected(self):
        row = self.value['members'][0]; row['dependencies'] = [row['member_id']]
        with self.assertRaisesRegex(ValueError, 'cyclic member'):
            validate_members(self.value)

    def test_registry_schema_and_admitted_records_preserved(self):
        original = load(REGISTRY); candidate = registry_candidate()
        self.assertEqual(original['admitted_contracts'], candidate['admitted_contracts'])
        self.assertEqual(original['current_by_identity'], candidate['current_by_identity'])
        self.assertEqual(original['descriptors'], candidate['descriptors'][:-1])
        self.assertEqual(candidate['inventory']['admitted_contract_count'], 143)
        self.assertEqual(candidate['inventory']['descriptor_count'], 146)
        self.assertEqual(candidate['descriptors'][-1]['effective_decision_refs'], [])
        self.assertEqual(candidate['descriptors'][-1]['effective_state'], 'candidate-unadmitted')
        self.assertEqual(candidate['descriptors'][-1]['activation_state'], 'not-activated')
        self.assertEqual(binding(REGISTRY), self.canonical_binding)

    def test_runtime_artifact_is_schema_valid_candidate(self):
        artifact = runtime_artifact()
        self.assertEqual(artifact['lifecycle_state'], 'candidate')
        self.assertEqual(artifact['authority_effect'], 'none')
        self.assertNotIn('v1/lab.py', artifact['payload']['execution_entrypoint_ref'])

    def test_connections_and_endpoint_meaning_are_independent(self):
        rows = self.value['members']
        self.assertEqual(len([m for m in rows if m['member_class'] == 'typed-connections']), 4)
        self.assertEqual(len([m for m in rows if m['member_class'] == 'semantic-mappings']), 3)
        self.assertTrue(all('new Relation Kind or pair' in m['exclusions'] for m in rows))
        mappings = {m['selected_record']['endpoint_kind']: m for m in rows if m['member_class'] == 'semantic-mappings'}
        self.assertEqual(mappings['project']['selected_record']['identity_selector'], '/project_id')
        self.assertEqual(mappings['product']['selected_record']['identity_selector'], '/product_id')
        self.assertEqual(mappings['method']['selected_record']['identity_selector'], '/method_id')

    def test_candidate_drift_with_new_self_pin_still_rejected(self):
        # Model changed bytes without mutating any real reviewed file.
        value = copy.deepcopy(self.value); value['members'][0]['requested_effect'] = 'Activate a service'
        changed = encoded(value); original_read = read
        with patch('review.read', side_effect=lambda p: changed if p == self.path else original_read(p)):
            with self.assertRaisesRegex(ValueError, 'changed or incomplete exact preparation'):
                validate_preparation(self.path, sha(changed))

    def test_repository_traversal_rejected(self):
        for name in ['/etc/passwd', '../README.md', 'docs/../README.md']:
            with self.assertRaisesRegex(ValueError, 'repository-relative'):
                read(name)

    def test_fresh_process_rechecks_exact_preparation(self):
        script = 'import json,sys; from review import validate_preparation; d=validate_preparation(sys.argv[1],sys.argv[2]); print(json.dumps({"members":len(d["members"]),"outcome":d["actual_owner_outcome"]}))'
        result = subprocess.run([sys.executable, '-c', script, self.path, self.pin], cwd=PACKAGE, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'members': 13, 'outcome': None})
