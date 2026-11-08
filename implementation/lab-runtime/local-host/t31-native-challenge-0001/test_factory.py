"""Historical evidence is retained data; current permissions are independent."""
import copy
from datetime import datetime,timedelta,timezone
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'),str(HERE)]
import factory as F

class Factory(unittest.TestCase):
    def setUp(self):
        self.originals=F.selected_originals();_,request,_,_=F.historical(self.originals)
        self.contract=(F.ROOT/'implementation/lab-runtime/local-host/t15-integrated-fixture-0001/instances/legacy-local-4636eca980a5d94d/source/packages/0001/artifacts/05.json').read_bytes()
        now=datetime.now(timezone.utc)
        self.grant={'principal_ref':'principal:independent-fixture-metadata-owner','run_ref':'workflow-run:factory-test','scope_ref':request['subject']['scope_ref'],
         'source_cut':request['source_cut'],'not_before':(now-timedelta(seconds=1)).isoformat(),'expires_at':(now+timedelta(minutes=1)).isoformat(),
         'actor_role_refs':['role:accountable-owner'],'permitted_effects':['candidate-workflow-transition'],'revoked':False,'actual_owner_outcome':None,'authority_effect':'none'}
        self.calls=0
    def guard(self):self.calls+=1
    def derive(self):return F.derive(originals=self.originals,contract_raw=self.contract,grant=self.grant,host_guard=self.guard,run_ref=self.grant['run_ref'])
    def test_actual_signed_history_produces_new_typed_snapshots_and_distinct_v2(self):
        headers,raws,receipt=self.derive();self.assertEqual(self.calls,2);self.assertEqual(len(raws),5)
        self.assertEqual(receipt['old_native_decision_schema'],'cyberalchemy-lab-decision/v1');self.assertEqual(receipt['new_decision_schema'],'cyberalchemy-lab-decision/v2')
        self.assertTrue(receipt['new_decision_is_distinct_record']);self.assertTrue(receipt['historical_capsule_period_is_not_current_permission'])
        self.assertIsNone(receipt['actual_owner_outcome']);self.assertEqual(receipt['selected_fixture_outcome'],'defer')
        states=[__import__('json').loads(raws[headers[k]['version_ref']])['payload']['response_state'] for k in ('eligible','responded','resolved')]
        self.assertEqual(states,['eligible','responded','deferred'])
    def test_old_signed_capsule_does_not_authorize_expired_or_revoked_current_grant(self):
        before=copy.deepcopy(self.grant)
        self.grant['expires_at']=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()
        with self.assertRaisesRegex(ValueError,'fresh independently'):self.derive()
        self.grant=before;self.grant['revoked']=True
        with self.assertRaisesRegex(ValueError,'fresh independently'):self.derive()
    def test_original_body_and_contract_substitution_refused(self):
        self.originals['native-candidate']+=b' '
        with self.assertRaisesRegex(ValueError,'actual original changed'):self.derive()
        self.originals=F.selected_originals();self.contract+=b' '
        with self.assertRaisesRegex(ValueError,'Contract original differs'):self.derive()
    def test_no_real_owner_outcome_or_foreign_cut_can_be_injected(self):
        self.grant['actual_owner_outcome']='accepted'
        with self.assertRaisesRegex(ValueError,'fresh independently'):self.derive()
        self.grant['actual_owner_outcome']=None;self.grant['source_cut']['commit_sequence']+=1
        with self.assertRaisesRegex(ValueError,'fresh independently'):self.derive()
    def test_effect_boundary_guard_failure_refuses_production(self):
        def ended():raise ValueError('actual current Source/permission ended')
        with self.assertRaisesRegex(ValueError,'permission ended'):
            F.derive(originals=self.originals,contract_raw=self.contract,grant=self.grant,host_guard=ended,run_ref=self.grant['run_ref'])

if __name__=='__main__':unittest.main()
