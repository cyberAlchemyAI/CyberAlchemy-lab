"""Actual backend owner target preparation and explicit negative scope cases."""
import argparse,copy,json,unittest
import prepare as C
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);a=p.parse_args();C.guard(a.source_sha256);cases=[];prepared=[]
    class Checks(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.cm=C.P.source.replay_source('custody-participation');cls.view=cls.cm.__enter__();cls.groups=C.inputs(cls.view)
        @classmethod
        def tearDownClass(cls):cls.cm.__exit__(None,None,None)
        def test_00_all42_actual_backend_cores(self):
            for scope,members in self.groups.items():prepared.append(C.prepare_group(self.view,scope,members))
            self.assertEqual(sum(len(x['cores']) for x in prepared),42);self.assertEqual(len(prepared),21)
            self.assertEqual(len({c['decision_ref'] for x in prepared for c in x['cores']}),42)
            self.assertEqual(len({c['version_ref'] for x in prepared for c in x['cores']}),42)
            self.assertTrue(all(x['source_projection_unchanged'] and not x['current_runtime_grant'] and x['configuration_status']=='hypothetical-unprovisioned' for x in prepared))
        def example(self):
            scope=next(iter(self.groups));members=copy.deepcopy(self.groups[scope]);return scope,members
        def test_01_scope_cannot_collapse_to_source_Project(self):
            scope,m=self.example()
            with self.assertRaisesRegex(ValueError,'owner scope differs'):C.prepare_group(self.view,self.view.data['config']['scope_ref'],m)
        def test_02_cross_scope_member_refused(self):
            scope,m=self.example();m[0]['target']['record']['scope_ref']='protocol:undeclared-scope'
            with self.assertRaisesRegex(ValueError,'owner scope differs'):C.prepare_group(self.view,scope,m)
        def test_03_stale_head_refused(self):
            scope,m=self.example();config,p=C.proposal_for(self.view,scope,m);p['expected_head']='0'*64
            with self.assertRaises(Exception):self.view.handle.operations.prepare(self.view.data['projection'],p,self.view.data['head']['transaction_digest'],config)
        def test_04_wrong_config_scope_refused(self):
            scope,m=self.example();config,p=C.proposal_for(self.view,scope,m);config['scope_ref']='protocol:wrong-scope'
            with self.assertRaises(Exception):self.view.handle.operations.prepare(self.view.data['projection'],p,self.view.data['head']['transaction_digest'],config)
        def test_05_changed_original_bytes_refused(self):
            scope,m=self.example();m[0]['original_bytes']+=b' '
            with self.assertRaises(Exception):C.prepare_group(self.view,scope,m)
        def test_06_wrong_carrier_refused(self):
            scope,m=self.example();m[0]['target']['carrier_ref']='cal.artifact-type.work/v1'
            with self.assertRaises(Exception):C.prepare_group(self.view,scope,m)
        def test_07_duplicate_identity_refused(self):
            scope,m=self.example();m.append(copy.deepcopy(m[0]))
            with self.assertRaises(Exception):C.prepare_group(self.view,scope,m)
        def test_08_noncanonical_serializer_changes_exact_core(self):
            scope,m=self.example();t=m[0]['target'];raw=json.dumps(t['record'],separators=(',',':')).encode();self.assertNotEqual(raw,m[0]['original_bytes']);other=copy.deepcopy(t);other['content']=self.view.handle.custody.content_entry(raw);self.assertNotEqual(self.view.handle.common.digest(t),self.view.handle.common.digest(other))
        def test_09_body_scope_retained_in_complete_core_target(self):
            for members in self.groups.values():
                for m in members:
                    t=m['target'];other=copy.deepcopy(t);other['record']['scope_ref']='protocol:wrong-scope';other['content']=self.view.handle.custody.content_entry(C.encoded(other['record']));self.assertNotEqual(self.view.handle.common.digest(t),self.view.handle.common.digest(other))
        def test_10_original_projection_retains_no_owner_proposals(self):
            for members in self.groups.values():
                for m in members:self.assertNotIn(m['target']['version_ref'],self.view.subjects)
    class Result(unittest.TextTestResult):
        def addSuccess(self,t):super().addSuccess(t);cases.append({'test':t.id(),'result':'PASS'})
        def addFailure(self,t,e):super().addFailure(t,e);cases.append({'test':t.id(),'result':'FAIL','detail':self._exc_info_to_string(e,t)})
        def addError(self,t,e):super().addError(t,e);cases.append({'test':t.id(),'result':'ERROR','detail':self._exc_info_to_string(e,t)})
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks));C.guard(a.source_sha256)
    out=C.HERE/'receipts';out.mkdir(exist_ok=False,mode=0o700)
    report={'schema_version':'lab-owner-core-preparation-checks/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==11 else 'FAIL','tests_run':result.testsRun,'expected_tests':11,'cases':cases,'source_sha256':a.source_sha256,'authority_effect':'none','actual_owner_outcome':None,'current_runtime_grant':False,'public_review_adapter_implemented':False,'task_complete':False}
    (out/'checks.json').open('xb').write(C.encoded(report))
    if report['result']=='PASS':
        artifacts=C.HERE/'artifacts';artifacts.mkdir(mode=0o700);members=[];proposals=[]
        for group in prepared:
            name=C.sha(group['scope_ref'].encode());p=artifacts/(name+'-proposal.json');p.open('xb').write(C.encoded(group['runtime_proposal']));cp=artifacts/(name+'-configuration-hypothesis.json');cp.open('xb').write(C.encoded(group['configuration']));proposals.append({'scope_ref':group['scope_ref'],'runtime_proposal_binding':C.bind(p),'configuration_hypothesis_binding':C.bind(cp),'configuration_status':group['configuration_status'],'actual_runtime_authority_verified':False,'source_projection_unchanged':True})
            for t,core in zip(group['runtime_proposal']['targets'],group['cores']):
                path=artifacts/(C.sha(core['decision_ref'].encode())+'-core.json');path.open('xb').write(C.encoded(core));members.append({'identity_ref':t['record']['node_id'],'version_ref':t['version_ref'],'scope_ref':t['record']['scope_ref'],'carrier_ref':t['carrier_ref'],'original_body_sha256':t['content']['byte_sha256'],'complete_target_sha256':C.sha(C.encoded(t)),'decision_ref':core['decision_ref'],'independent_core_binding':C.bind(path),'authority_effect':'none','current_owner_authority_verified':False})
        manifest={'schema_version':'lab-owner-core-preparation/v1-candidate','source_binding':C.bind(C.HERE/'source-manifest.json'),'source_owner_proof_binding':C.bind(C.OWNER/'proof-0001.json'),'members':members,'scope_proposals':proposals,'independent_core_count':42,'separate_scope_count':21,'source_projection_unchanged':True,'configuration_status':'hypothetical-unprovisioned','public_API_preparation_verified':False,'required_governing_role_coverage_verified':False,'actual_owner_outcome':None,'repository_admissions_applied':0,'authority_effect':'none','task_complete':False,'claim_ceiling':'Exact independent core bytes and original backend hypothetical-scope construction only. Actual source scope/profile/grants, public review integration and final owner outcomes remain pending.'}
        (artifacts/'manifest.json').open('xb').write(C.encoded(manifest))
    print(json.dumps({'result':report['result'],'tests_run':result.testsRun,'expected_tests':11,'prepared_scope_groups':len(prepared)}),flush=True);raise SystemExit(0 if report['result']=='PASS' else 1)
if __name__=='__main__':main()
