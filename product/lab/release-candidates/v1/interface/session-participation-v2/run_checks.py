"""Real cold signed branch checks; no fabricated view delivery or Agent permission."""
import argparse
import copy
from datetime import datetime, timezone
import json
import sys
import unittest
from base import *
import records
import reader

class RealBranchChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manager = reader.open_signed(SOURCE_PIN, PACKAGE_PIN)
        cls.adapter = cls.manager.__enter__()
        cls.sources = cls.adapter.sources
        cls.selected = {row.artifact['identity_ref']: row for row in cls.adapter.records}
        cls.projection = cls.adapter.view.data['projection']
    @classmethod
    def tearDownClass(cls): cls.manager.__exit__(None, None, None)
    def get(self, identity):
        return self.sources.get(self.selected[identity].artifact)[0]
    def test_01_actual_eleven_current_bodies(self):
        for identity in [records.PRINCIPAL,records.PRINCIPAL_REFERENCE,records.GOAL,records.WORK,records.INTENT,
            records.PROFILE,records.ASSIGNMENT,records.COORDINATION,records.CONTEXT,records.CAPABILITY,records.IMPLEMENTATION]:
            self.assertEqual(self.get(identity).posture,'local-admitted-current')
    def test_02_actual_original_byte_parity(self):
        for row in load(HERE/'packages/0001/record-index.json'):
            subject=self.projection['subjects'][row['version_ref']]
            self.assertEqual(subject['source']['sha256'],row['original_binding']['sha256'])
            self.assertEqual(encoded(subject['record']),original(row['original_binding']))
    def test_03_actual_ten_closed_typed_relations(self):
        rows=[s for s in self.projection['subjects'].values() if s['identity'].startswith('typed-relation:'+records.PREFIX+':')]
        self.assertEqual(len(rows),10)
        for row in rows: self.adapter.view.handle.operations.validate_relation(row['record'],self.projection)
    def test_04_actual_public_key_correspondence(self):
        p=reader.adapter.eligibility.parse(self.get(records.PRINCIPAL).original)
        ref=reader.adapter.eligibility.parse(self.get(records.PRINCIPAL_REFERENCE).original)
        expected='ed25519-public-key-sha256:'+sha(bytes.fromhex(self.adapter.view.data['config']['public_key']))
        self.assertEqual(p['payload']['stable_subject_ref'],expected)
        self.assertEqual(ref['payload']['integrity_digest'],expected)
        self.assertEqual(ref['payload']['principal_ref'],records.PRINCIPAL)
    def test_05_Profile_assignment_never_old_instance(self):
        a=reader.adapter.eligibility.parse(self.get(records.ASSIGNMENT).original)
        self.assertEqual(a['payload']['eligible_agent_ref'],records.PROFILE+'@'+records.VERSION)
    def test_06_one_Goal_coordination(self):
        c=reader.adapter.eligibility.parse(self.get(records.COORDINATION).original)
        self.assertEqual(c['goal_ref'],records.GOAL+'@'+records.VERSION)
        self.assertEqual(c['project_ref'],self.sources.scope_ref)
    def test_07_goal_context(self):
        c=reader.adapter.eligibility.parse(self.get(records.CONTEXT).original)
        self.assertEqual(c['context_kind'],'goal');self.assertEqual(c['goal_ref'],records.GOAL+'@'+records.VERSION)
    def test_08_reciprocal_capability_metadata(self):
        p=reader.adapter.eligibility.parse(self.get(records.PROFILE).original)
        c=reader.adapter.eligibility.parse(self.get(records.CAPABILITY).original)
        self.assertEqual(p['relation_refs'][0]['direction'],'source')
        self.assertEqual(c['relation_refs'][0]['direction'],'target')
        self.assertEqual(c['relation_refs'][0]['counterpart_ref'],records.PROFILE+'@'+records.VERSION)
    def test_09_current_Project_State(self):
        state=self.projection['state'];self.assertEqual(state['payload']['project_ref'],self.sources.scope_ref)
        self.assertIn(state['node_id'],self.selected)
    def test_10_Product_revision_retains_body_version(self):
        s=self.get('product:cyberalchemy-lab');body=reader.adapter.eligibility.parse(s.original)
        self.assertNotEqual(s.artifact['version_ref'].split('@',1)[1],body['version'])
        self.assertIsNotNone(s.revision_witness)
    def test_11_wrong_body_hash_denied(self):
        ref=copy.deepcopy(self.selected[records.ASSIGNMENT].artifact);ref['byte_sha256']='0'*64
        with self.assertRaises(ValueError):self.sources.get(ref)
    def test_12_wrong_scope_denied(self):
        ref=copy.deepcopy(self.selected[records.ASSIGNMENT].artifact);ref['scope_ref']='project:foreign'
        with self.assertRaises(ValueError):self.sources.get(ref)
    def test_13_package_pin_denied(self):
        with self.assertRaises(ValueError):reader.package(SOURCE_PIN,'0'*64)
    def test_14_source_pin_denied(self):
        with self.assertRaises(ValueError):reader.package('0'*64,PACKAGE_PIN)
    def test_15_nickname_closed(self):
        with self.assertRaises(ValueError):reader.selection(SOURCE_PIN,PACKAGE_PIN,'other')
    def test_16_owned_store_and_key_removed(self):
        result=load(HERE/'packages/0001/build-result.json')
        self.assertTrue(result['owned_store_and_key_removed']);self.assertFalse(result['private_keys_exported'])
    def test_17_exact_retry(self):
        result=load(HERE/'packages/0001/retry.json');self.assertTrue(result['idempotent'])
        self.assertEqual(result['transaction_digest'],load(HERE/'packages/0001/application.json')['transaction_digest'])
    def test_18_no_api_Agent_or_authority_claim(self):
        result=load(HERE/'packages/0001/build-result.json')
        for k in ['active_Agents_created','public_API_operations_added','canonical_effects_applied','source_effects_applied']:self.assertEqual(result[k],0)
        self.assertIsNone(result['actual_owner_outcome']);self.assertEqual(result['authority_effect'],'none')
    def test_19_no_private_memory_context(self):
        for row in self.adapter.records:reader.adapter.eligibility.no_private_memory(reader.adapter.eligibility.parse(row.original),blank_session_policy=row.artifact['carrier_ref']=='cal.artifact-type.agent-session/v1')
    def test_20_absolute_period_never_restarted(self):
        p=load(HERE/'packages/0001/period.json');start=datetime.fromisoformat(p['not_before']);end=datetime.fromisoformat(p['expires_at'])
        self.assertEqual((end-start).total_seconds(),86400)
        self.assertEqual(p['assignment_version_ref'],records.ASSIGNMENT+'@'+records.VERSION)
    def test_21_complete_subject_accounting(self):
        self.assertEqual(len(self.adapter.dispositions),len(self.adapter.view.subjects))
    def test_22_current_Project_version_binding(self):
        project=self.get(self.sources.scope_ref);body=reader.adapter.eligibility.parse(project.original)
        self.assertEqual(project.artifact['version_ref'],self.sources.scope_ref+'@'+body['version'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);p.add_argument('--package-sha256',required=True);a=p.parse_args()
    SOURCE_PIN=a.source_sha256;PACKAGE_PIN=a.package_sha256
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RealBranchChecks))
    emit(HERE/'receipts/checks.json',{'result':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,
        'failures':len(result.failures),'errors':len(result.errors),'source_sha256':SOURCE_PIN,'package_sha256':PACKAGE_PIN,
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False})
    sys.exit(0 if result.wasSuccessful() else 1)
