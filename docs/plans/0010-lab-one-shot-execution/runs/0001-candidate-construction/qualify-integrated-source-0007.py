"""Actual signed cold replay, original-body and controlled gate qualification."""
import argparse
import base64
import copy
from datetime import datetime,timezone,timedelta
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
SOURCE=BASE/'current-participation-v7'
PIN='b5ea33d7d0d64211f886221010dbf352183e93374e8f69bb536f15fdb7417dbd'


def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())
def package(name,path):
    spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return name


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--selection-sha256',required=True);args=parser.parse_args()
    selected=RUN/'integrated-source-selection-0007.json'
    assert bind(selected)['sha256']==args.selection_sha256
    selection=load(selected)
    assert selection['source_binding']==bind(SOURCE/'source-manifest.json') and selection['source_binding']['sha256']==PIN
    assert selection['package_binding']==bind(SOURCE/'packages/0001/manifest.json')
    assert selection['driver_binding']==bind(Path(__file__).resolve())
    report=RUN/'integrated-source-qualification-0007.json';assert not report.exists()
    name=package('_cal_integrated_source_0007',SOURCE)
    B=__import__(name+'.base',fromlist=['*']);C=__import__(name+'.cold',fromlist=['*'])
    R=__import__(name+'.records',fromlist=['*']);I=__import__(name+'.integration',fromlist=['*'])
    gate_name=package('_cal_integrated_source_resolution_v2',BASE/'challenge-resolution-v2')
    G=__import__(gate_name+'.gate',fromlist=['*']);O=__import__(gate_name+'.obligations',fromlist=['*'])
    from cryptography.exceptions import InvalidSignature
    manifest=B.verify_source(PIN);cases=[]
    class NativeSource(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.cm=C.open_source(PIN,selection['package_binding']['sha256']);cls.view=cls.cm.__enter__()
            cls.store=cls.view.handle.store_module.Store(cls.view.store,ROOT)
            cls.data=cls.view.data;cls.subjects=cls.data['projection']['subjects']
            cls.index=load(SOURCE/'packages/0001/integrated-record-index.json')
            cls.plan=load(SOURCE/'packages/0001/resolution-qualification-plan.json')
            cls.workspace=SOURCE/'packages/0001/qualification-workspace'
            cls.workspace_manifest=load(cls.workspace/'workspace.json')
            cls.routing=cls.object(cls.plan['routing_binding'])
            cls.gate=cls.object(cls.routing['owner_gate_binding'])
            cls.cold_root=cls.view.root
        @classmethod
        def tearDownClass(cls):cls.cm.__exit__(None,None,None);assert not cls.cold_root.exists()
        @classmethod
        def object(cls,binding):
            assert binding['ref']=='workspace-object:'+cls.workspace_manifest['workspace_ref']+':'+binding['sha256']
            path=cls.workspace/'objects'/(binding['sha256']+'.json')
            assert hashlib.sha256(path.read_bytes()).hexdigest()==binding['sha256']
            return load(path)
        @classmethod
        def material(cls,binding):
            rows=[row for row in cls.workspace_manifest['materials'] if row['ref']==binding['ref'] and row['sha256']==binding['sha256']]
            assert len(rows)==1
            path=cls.workspace/rows[0]['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==binding['sha256']
            return load(path)
        def test_01_four_actual_signed_transactions_and_exact_cold_projection(self):
            self.assertEqual(self.data['head']['sequence'],4);self.assertEqual(len(self.data['transactions']),5)
            self.assertEqual(self.view.handle.common.digest(self.data['projection']),self.view.expected['projection_sha256'])
        def test_02_all73_native_original_records_retrievable(self):
            self.assertEqual(len(self.index),73)
            for row in self.index:
                original=self.view.handle.custody.original_bytes(self.store,row['version_ref'],self.data['head']['transaction_digest'])
                self.assertEqual(hashlib.sha256(original).hexdigest(),row['original_byte_sha256'])
                self.assertEqual(json.loads(original),self.subjects[row['version_ref']]['record'])
        def test_03_all23_Source5_originals_preserved(self):
            old=BASE/'current-participation-v5/packages/0001'
            rows=load(old/'record-index.json');self.assertEqual(len(rows),21)
            for row in rows:
                original=B.original(row['original_binding'])
                self.assertEqual(self.view.handle.custody.original_bytes(self.store,row['version_ref'],self.data['head']['transaction_digest']),original)
            for target in load(old/'project-setup-proposal.json')['targets']:
                original=self.view.handle.custody.original_bytes(self.store,target['version_ref'],self.data['head']['transaction_digest'])
                kind='project' if target['carrier_ref']=='cal.artifact-type.project-identity/v1' else 'product'
                self.assertEqual(original,(old/('setup-artifacts/'+kind+'.json')).read_bytes())
        def test_04_all7_learning_originals_and_attribution_preserved(self):
            index=load(RUN/'Machine-policy-custody-lesson-0001/index.json');self.assertEqual(len(index['records']),7)
            for row in index['records']:
                actual=self.view.handle.custody.original_bytes(self.store,row['version_ref'],self.data['head']['transaction_digest'])
                self.assertEqual(actual,B.original(row['binding']))
            action=self.subjects['agent-action:R03-Machine-policy-custody@1.0.0-candidate.1']['record']
            self.assertEqual(action['owner_ref'],'principal:R03-current-episode-0004')
            self.assertTrue(action['payload']['agent_instance_ref'].startswith('agent-instance:R03-live:'))
        def test_05_distinct_source_and_gate_signers_recognized_by_exact_Principals(self):
            principal=self.subjects[R.PRINCIPAL+'@'+R.VERSION]['record']
            public=self.data['config']['public_key']
            self.assertEqual(principal['payload']['stable_subject_ref'],'ed25519-public-key-sha256:'+B.sha(bytes.fromhex(public)))
            owner=self.subjects[I.OWNER+'@'+R.VERSION]['record']
            self.assertEqual(owner['payload']['stable_subject_ref'],'ed25519-public-key-sha256:'+B.sha(bytes.fromhex(self.plan['gate_public_key_hex'])))
            self.assertNotEqual(public,self.plan['gate_public_key_hex'])
        def test_06_fixed_period_and_original_Source5_period_preserved(self):
            episode=B.episode();self.assertEqual(self.view.period['expires_at'],episode['expires_at'])
            self.assertEqual(datetime.fromisoformat(episode['expires_at'])-datetime.fromisoformat(episode['not_before']),timedelta(hours=24))
            self.assertEqual(episode['max_session_seconds'],900)
            self.assertFalse(episode['original_Assignment_renewed']);self.assertFalse(episode['original_signer_restored'])
            old=BASE/'current-participation-v5/packages/0001/period.json'
            row=next(row for row in manifest['files'] if row['path']==old.relative_to(ROOT).as_posix())
            self.assertEqual(bind(old),row)
        def test_07_fresh_Profile_Assignment_Work_Goal_closure(self):
            assignment=self.subjects[R.ASSIGNMENT+'@'+R.VERSION]['record']['payload']
            self.assertEqual(assignment['eligible_agent_ref'],R.PROFILE+'@'+R.VERSION)
            self.assertEqual(assignment['work_ref'],R.WORK+'@'+R.VERSION)
            self.assertEqual(self.subjects[R.WORK+'@'+R.VERSION]['record']['payload']['goal_refs'],[R.GOAL+'@'+R.VERSION])
        def test_08_all32_explicit_native_typed_relations_validate(self):
            relations=[row for row in self.index if row['kind']=='typed-relation'];self.assertEqual(len(relations),32)
            for row in relations:self.view.handle.operations.validate_relation(self.subjects[row['version_ref']]['record'],self.data['projection'])
        def test_09_current_Policy_v2_and_all_new_carriers_validate(self):
            for row in self.index:
                if row['phase']!='fresh-participation-and-contest':continue
                self.assertIn(self.data['projection']['contracts'][row['carrier_ref']]['lifecycle_state'],('admitted-current','local-admitted-current'))
                self.view.handle.operations.validate_record(self.subjects[row['version_ref']]['record'],row['carrier_ref'],self.data['projection'])
            self.assertEqual(self.subjects[I.POLICY+'@'+R.VERSION]['carrier_ref'],'cal.artifact-type.policy/v2')
        def test_10_Work_and_challenged_source_not_resolved_by_preparation(self):
            self.assertEqual(self.subjects[R.WORK+'@'+R.VERSION]['record']['payload']['completion_state'],'pending')
            self.assertEqual(self.subjects[I.CHALLENGE+'@'+R.VERSION]['record']['payload']['resolution_decision_ref'],'none')
            for ref in I.NEXT.values():self.assertNotIn(ref,self.subjects)
        def test_11_actual_native_prospective_axis_cores_match_materials(self):
            for axis in I.EFFECTS:
                proposal=load(SOURCE/('packages/0001/resolution-native-'+axis+'.json'))
                post,cores=self.view.handle.operations.prepare(self.data['projection'],proposal,self.data['head']['transaction_digest'],self.data['config'])
                branch=self.object(self.routing[axis+'_proposal_binding'])
                self.assertEqual(cores,[self.material(branch['targets'][0]['decision_core_binding'])])
                self.assertIn(I.NEXT[axis],post['subjects']);self.assertNotIn(I.NEXT[axis],self.subjects)
        def verify_gate(self,envelope=None,**changes):
            payload=self.gate['payload'];selected=dict(selected_public_key_hex=self.plan['gate_public_key_hex'],recognized_principal=I.OWNER,
                selected_gate_ref=I.ROUTES['resolution_gate_ref'],owner_route=I.ROUTES['owner_route'],scope_ref=self.data['config']['scope_ref'],
                source_cut=self.plan['source_cut'],challenge=payload['challenge'],resolution_decision=payload['resolution_decision'],
                challenge_contract=payload['challenge_contract'],subject=payload['subject'],selected_outcome=I.OUTCOME,
                semantic_proposal_binding=payload['semantic_proposal_binding'],governance_proposal_binding=payload['governance_proposal_binding'],
                evidence_bindings=payload['evidence_bindings'],consequence_routes=self.routing['consequence_routes'],response_obligations=self.routing['response_obligations'],
                principal_record=self.subjects[I.OWNER+'@'+R.VERSION]['record'],policy_expires_at=self.view.period['expires_at'],now=datetime.now(timezone.utc))
            return G.verify(self.gate if envelope is None else envelope,**{**selected,**changes})
        def test_12_actual_independent_signature_and_exact_source_gate(self):self.assertEqual(self.verify_gate(),self.gate['payload'])
        def test_13_altered_signed_source_gate_refused(self):
            gate=copy.deepcopy(self.gate);gate['payload']['selected_outcome']='substitution'
            with self.assertRaises(InvalidSignature):self.verify_gate(gate)
        def test_14_foreign_Principal_and_expired_gate_refused(self):
            with self.assertRaises(ValueError):self.verify_gate(recognized_principal=R.PRINCIPAL)
            with self.assertRaises(ValueError):self.verify_gate(now=datetime.fromisoformat(self.view.period['expires_at']))
        def test_15_response_Contract_obligations_and_original_evidence(self):
            control=self.routing['response_obligations'];payload=self.gate['payload']
            response=self.material(control['response_binding'])
            O.verify(control,rules=self.subjects[I.CONTRACT+'@'+R.VERSION]['record']['payload'],
                challenge=self.subjects[I.CHALLENGE+'@'+R.VERSION]['record']['payload'],challenge_header=payload['challenge'],
                contract_header=payload['challenge_contract'],subject_header=payload['subject'],owner_header=self.routing['owner_principal'],
                challenger=self.subjects[I.OWNER+'@'+R.VERSION]['record'],response=response,evidence_bindings=payload['evidence_bindings'],now=datetime.now(timezone.utc))
        def test_16_acyclic_exact_workspace_manifest_and_complete_axis_composition(self):
            self.assertEqual(self.plan['workspace_binding']['sha256'],B.sha((self.workspace/'workspace.json').read_bytes()))
            self.assertNotIn(self.routing['owner_gate_binding']['ref'],[row['ref'] for row in self.workspace_manifest['materials']])
            branches={axis:self.object(self.routing[axis+'_proposal_binding']) for axis in I.EFFECTS}
            result=self.object(self.routing['result_proposal_binding'])
            O.composition(result,branches,subject_header=self.gate['payload']['subject'])
            for body in branches.values():self.assertEqual(body['workspace_binding'],self.plan['workspace_binding'])
        def test_17_source_and_package_independent_pin_refusals(self):
            with self.assertRaises(ValueError):B.verify_source('0'*64)
            with self.assertRaises(ValueError):C.package(PIN,'0'*64)
        def test_18_actual_signed_transaction_corruption_refused(self):
            path=self.view.store/'transactions/0000000004.json';original=path.read_bytes()
            try:
                path.write_bytes(original+b' ')
                with self.assertRaises(Exception):self.view.handle.replay_owned(self.view.store,self.view.expected['config_sha256'],self.view.expected['baseline_snapshot_digest'],self.view.expected['expected_head'])
            finally:path.write_bytes(original)
        def test_19_actual_signer_cleanup_no_Agent_memory_or_canonical_effects(self):
            result=load(SOURCE/'packages/0001/build-result.json')
            self.assertTrue(result['owned_store_and_key_removed']);self.assertFalse(Path(result['owned_root']).exists())
            self.assertFalse(result['private_keys_exported']);self.assertFalse(result['Session_memory_rehydrated'])
            self.assertEqual(result['active_Agents_created'],0);self.assertEqual(result['canonical_effects_applied'],0)
            self.assertIsNone(result['actual_owner_outcome']);self.assertFalse(list((SOURCE/'packages/0001').rglob('*.pem')))
        def test_20_all_four_exact_retries_and_complete_current_Project_State(self):
            result=load(SOURCE/'packages/0001/build-result.json');self.assertEqual(len(result['phases']),4)
            for row in result['phases']:
                self.assertTrue(row['exact_retry'])
                application=load(SOURCE/('packages/0001/'+row['phase']+'-application.json'))
                retry=load(SOURCE/('packages/0001/'+row['phase']+'-retry.json'))
                self.assertTrue(retry['idempotent']);self.assertEqual(application['transaction_digest'],retry['transaction_digest'])
            self.assertEqual(self.data['projection']['state']['node_id'],self.view.expected['current_Project_State_ref'])
    class Result(unittest.TextTestResult):
        def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,error):super().addFailure(test,error);cases.append({'test':test.id(),'result':'FAIL','error_class':error[0].__name__})
        def addError(self,test,error):super().addError(test,error);cases.append({'test':test.id(),'result':'ERROR','error_class':error[0].__name__})
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(NativeSource);assert suite.countTestCases()==20
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite);B.verify_source(PIN)
    value={'schema_version':'lab-integrated-cold-source-qualification/v1-candidate',
        'result':'PASS' if result.wasSuccessful() and result.testsRun==20 else 'FAIL','actual_cases':result.testsRun,
        'failures':len(result.failures),'errors':len(result.errors),'cases':cases,'files':[*manifest['files'],
            bind(SOURCE/'source-manifest.json'),bind(SOURCE/'packages/0001/manifest.json'),bind(selected),bind(Path(__file__).resolve())],
        'source_binding':selection['source_binding'],'package_binding':selection['package_binding'],
        'native_original_targets':73,'source_guarded_exit_completed':True,
        'Reader6_qualified':False,'public_resolution_qualified':False,'learning_context_qualified':False,
        'whole_API_qualified':False,'task_complete':False,'goal_complete':False,'authority_effect':'none','actual_owner_outcome':None,
        'claim_ceiling':'Actual20 signed cold replay, original body, native prospective core, isolated exact gate/response and cleanup cases only. Reader6, public transport/journal and learning delivery/application remain unqualified.'}
    with report.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':value['result'],'actual_cases':result.testsRun,'report_binding':bind(report)}),flush=True)
    return 0 if value['result']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
