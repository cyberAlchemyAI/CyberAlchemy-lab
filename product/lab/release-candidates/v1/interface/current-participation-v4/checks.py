"""Full new bounded source checks; not current Agent/Session qualification."""
import argparse
import base64
import copy
import importlib.util
import json
import sys
import unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
HERE=Path(__file__).resolve().parent
SOURCE_HERE=HERE

def guard_checks(pin):
    import hashlib
    root=HERE.parents[5];path=HERE/'source-manifest.json'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==pin,'independent checks source pin differs'
    for row in json.loads(path.read_bytes())['files']:
        assert hashlib.sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True);parser.add_argument('--package-sha256',required=True);parser.add_argument('--checks-source-sha256',required=True)
    args=parser.parse_args();guard_checks(args.checks_source_sha256);name='_cal_current_participation_checks_repair_0004'
    spec=importlib.util.spec_from_file_location(name,SOURCE_HERE/'__init__.py',submodule_search_locations=[str(SOURCE_HERE)])
    package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    B=__import__(name+'.base',fromlist=['*']);C=__import__(name+'.cold',fromlist=['*']);R=__import__(name+'.records',fromlist=['*'])
    B.verify_source(args.source_sha256)
    observations=[];cases=[]
    class Checks(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.old_period=HERE.parent/'custody-participation-v1/packages/0001/period.json';cls.old_raw=cls.old_period.read_bytes()
            cls.cm=C.open_source(args.source_sha256,args.package_sha256);cls.view=cls.cm.__enter__();cls.roots=[str(cls.view.root)]
        @classmethod
        def tearDownClass(cls):
            cls.cm.__exit__(None,None,None);assert cls.old_period.read_bytes()==cls.old_raw
        def test_00_signed_two_transaction_cold_replay(self):
            self.assertEqual(self.view.data['head']['sequence'],2)
            self.assertEqual(len(self.view.data['transactions']),3)
            self.assertEqual(self.view.handle.common.digest(self.view.data['projection']),self.view.expected['projection_sha256'])
        def test_01_complete23_actual_original_bodies(self):
            index=B.load(SOURCE_HERE/'packages/0001/record-index.json');self.assertEqual(len(index),21)
            for row in index:
                raw=B.original(row['original_binding']);subject=self.view.data['projection']['subjects'][row['version_ref']]
                self.assertEqual(subject['source']['sha256'],B.sha(raw));self.assertEqual(subject['record'],json.loads(raw))
                self.assertEqual(self.view.handle.custody.original_bytes(self.view.handle.store_module.Store(self.view.store,B.ROOT),row['version_ref'],self.view.data['head']['transaction_digest']),raw)
            self.assertEqual(B.load(SOURCE_HERE/'packages/0001/build-result.json')['setup_independent_cores'],2)
        def test_02_new_principal_key_and_assignment_identity(self):
            old=B.load(self.old_period);self.assertNotEqual(old['principal_ref'],R.PRINCIPAL);self.assertNotEqual(old['assignment_version_ref'],R.ASSIGNMENT+'@'+R.VERSION)
            principal=self.view.data['projection']['subjects'][R.PRINCIPAL+'@'+R.VERSION]['record']
            self.assertEqual(principal['payload']['stable_subject_ref'],'ed25519-public-key-sha256:'+B.sha(bytes.fromhex(self.view.data['config']['public_key'])))
            previous=B.load(HERE.parent/'custody-participation-v1/packages/0001/branch.snapshot')
            config=json.loads(base64.b64decode(previous['files']['config.json']['base64_original_bytes'],validate=True))
            self.assertNotEqual(config['public_key'],self.view.data['config']['public_key'])
        def test_03_exact_new_period_no_inherited_renewal(self):
            declared=B.episode();period=self.view.period
            self.assertEqual(period['not_before'],declared['not_before']);self.assertEqual(period['expires_at'],declared['expires_at'])
            self.assertEqual(datetime.fromisoformat(period['expires_at'])-datetime.fromisoformat(period['not_before']),timedelta(hours=24))
            self.assertFalse(declared['original_Assignment_renewed']);self.assertFalse(declared['original_signer_restored']);self.assertFalse(declared['Session_memory_rehydrated'])
            self.assertGreaterEqual(datetime.fromisoformat(period['not_before']),datetime.fromisoformat(B.load(self.old_period)['expires_at']))
        def test_04_new_assignment_profile_work_and_goal_closure(self):
            subjects=self.view.data['projection']['subjects'];assignment=subjects[R.ASSIGNMENT+'@'+R.VERSION]['record']['payload']
            self.assertEqual(assignment['eligible_agent_ref'],R.PROFILE+'@'+R.VERSION);self.assertEqual(assignment['period'],R.PERIOD)
            self.assertEqual(assignment['work_ref'],R.WORK+'@'+R.VERSION)
            self.assertEqual(subjects[R.WORK+'@'+R.VERSION]['record']['payload']['goal_refs'],[R.GOAL+'@'+R.VERSION])
        def test_05_all10_original_typed_connections_validate(self):
            index=B.load(SOURCE_HERE/'packages/0001/record-index.json');relations=[row for row in index if row['kind']=='typed-relation'];self.assertEqual(len(relations),10)
            for row in relations:self.view.handle.operations.validate_relation(self.view.data['projection']['subjects'][row['version_ref']]['record'],self.view.data['projection'])
        def test_06_same_current_project_state(self):
            state=self.view.data['projection']['state'];self.assertEqual(state['node_id'],self.view.expected['current_Project_State_ref'])
            self.assertEqual(state['payload']['project_ref'],self.view.data['config']['scope_ref'])
        def test_07_original_body_encoding_retained(self):
            for row in B.load(SOURCE_HERE/'packages/0001/record-index.json'):
                raw=B.original(row['original_binding']);self.assertNotEqual(raw,self.view.handle.common.encoded(json.loads(raw)));self.assertTrue(raw.startswith(b' \r\n'))
        def test_08_no_live_Agent_or_Session_created(self):
            result=B.load(SOURCE_HERE/'packages/0001/build-result.json');self.assertEqual(result['active_Agents_created'],0)
            self.assertFalse(result['Session_memory_rehydrated']);self.assertFalse(result['private_keys_exported']);self.assertEqual(result['public_API_operations_added'],0)
            selected=[r['kind'] for r in B.load(SOURCE_HERE/'packages/0001/record-index.json')];self.assertNotIn('agent-instance',selected);self.assertNotIn('agent-session',selected)
        def test_09_actual_exact_local_transaction_retry(self):
            applied=B.load(SOURCE_HERE/'packages/0001/application.json');retry=B.load(SOURCE_HERE/'packages/0001/retry.json')
            self.assertTrue(retry['idempotent']);self.assertEqual(applied['transaction_digest'],retry['transaction_digest'])
        def test_10_old_expired_period_preserved(self):
            self.assertEqual(self.old_period.read_bytes(),self.old_raw)
            self.assertLess(datetime.fromisoformat(B.load(self.old_period)['expires_at']),datetime.now(timezone.utc))
        def test_11_changed_new_period_refused(self):
            period=copy.deepcopy(self.view.period);period['expires_at']=(datetime.fromisoformat(period['expires_at'])+timedelta(seconds=1)).isoformat()
            with self.assertRaises(ValueError):C.validate_period(period,B.episode())
        def test_12_old_assignment_substitution_refused(self):
            period=copy.deepcopy(self.view.period);period['assignment_version_ref']=B.load(self.old_period)['assignment_version_ref']
            with self.assertRaises(ValueError):C.validate_period(period,B.episode())
        def test_13_independent_source_pin_refused(self):
            with self.assertRaises(ValueError):B.verify_source('0'*64)
        def test_14_independent_package_pin_refused(self):
            with self.assertRaises(ValueError):C.package(args.source_sha256,'0'*64)
        def test_15_new_owned_signer_disposed_and_zero_canonical_effects(self):
            result=B.load(SOURCE_HERE/'packages/0001/build-result.json');self.assertTrue(result['owned_store_and_key_removed']);self.assertFalse(Path(result['owned_root']).exists())
            self.assertEqual(result['canonical_effects_applied'],0);self.assertEqual(result['source_effects_applied'],0);self.assertIsNone(result['actual_owner_outcome'])
            observations.append({'new_episode_period':self.view.period,'source_cut_head':self.view.data['head'],'config_public_key_sha256':B.sha(bytes.fromhex(self.view.data['config']['public_key'])),'owned_signer_removed':True,'current_Agent_qualified':False,'authority_effect':'none'})
        def test_16_actual_declared_adapter_entrypoint(self):
            import ast
            implementation=self.view.data['projection']['subjects'][R.IMPLEMENTATION+'@'+R.VERSION]['record']
            expected='product/lab/release-candidates/v1/interface/current-source-adapter-v3/reader.py#SelectedReader.open_signed'
            self.assertEqual(implementation['payload']['execution_entrypoint_ref'],expected)
            path=B.ROOT/expected.split('#')[0]
            tree=ast.parse(path.read_bytes());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='SelectedReader')
            self.assertTrue(any(isinstance(n,ast.FunctionDef) and n.name=='open_signed' for n in cls.body))
            self.assertEqual(B.verify_source(args.source_sha256)['implementation_code_binding'],B.binding(path))
        def test_17_previous_candidate_episode_not_reused(self):
            previous=B.load(HERE.parent/'current-participation-v3/episode-contract.json')
            self.assertNotEqual(R.PRINCIPAL,previous['principal_ref'])
            self.assertNotEqual(R.ASSIGNMENT+'@'+R.VERSION,previous['assignment_version_ref'])
            self.assertNotEqual(R.PERIOD,previous['period_ref'])
            archive=B.load(HERE.parent/'current-participation-v3/packages/0001/branch.snapshot')
            config=json.loads(base64.b64decode(archive['files']['config.json']['base64_original_bytes'],validate=True))
            self.assertNotEqual(config['public_key'],self.view.data['config']['public_key'])
        def test_18_exact_three_independent_host_pins_declared(self):
            import ast
            path=HERE.parent/'current-source-adapter-v3/reader.py'
            tree=ast.parse(path.read_bytes());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='SelectedReader')
            constructor=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
            self.assertEqual([a.arg for a in constructor.args.args],['self','adapter_pin','source_pin','package_pin'])
            self.assertEqual(B.verify_source(args.source_sha256)['implementation_entrypoint_ref'],self.view.data['projection']['subjects'][R.IMPLEMENTATION+'@'+R.VERSION]['record']['payload']['execution_entrypoint_ref'])
        def test_19_both_previous_fixed_periods_preserved(self):
            for version in ('v2','v3'):
                path=HERE.parent/('current-participation-'+version)/'packages/0001/period.json'
                expected=next(row for row in B.verify_source(args.source_sha256)['files'] if row['path']==str(path.relative_to(B.ROOT)))
                self.assertEqual(B.binding(path),expected)
            self.assertEqual(B.episode()['max_session_seconds'],900)
    class Result(unittest.TextTestResult):
        def addSuccess(self,t):super().addSuccess(t);cases.append({'test':t.id(),'result':'PASS'})
        def addError(self,t,e):super().addError(t,e);cases.append({'test':t.id(),'result':'ERROR','detail':self._exc_info_to_string(e,t)})
        def addFailure(self,t,e):super().addFailure(t,e);cases.append({'test':t.id(),'result':'FAIL','detail':self._exc_info_to_string(e,t)})
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Checks);assert suite.countTestCases()==20
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite);B.verify_source(args.source_sha256)
    report={'schema_version':'lab-current-participation-source-checks/v4-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==20 else 'FAIL','tests_run':result.testsRun,'expected_tests':20,'cases':cases,'observations':observations,'source_sha256':args.source_sha256,'checks_source_sha256':args.checks_source_sha256,'retained_original16methods':True,'package_sha256':args.package_sha256,'current_Agent_qualified':False,'public_API_qualification':False,'original_Assignment_renewed':False,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False}
    guard_checks(args.checks_source_sha256);out=HERE/'receipts';out.mkdir(mode=0o700,exist_ok=True)
    with (out/'checks-0001.json').open('x') as stream:json.dump(report,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':report['result'],'tests_run':result.testsRun}),flush=True)
    raise SystemExit(0 if report['result']=='PASS' else 1)
if __name__=='__main__':main()
