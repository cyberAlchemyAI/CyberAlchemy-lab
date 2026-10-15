"""Actual unchanged-source submit -> prepare -> retry -> inspect qualification."""
import copy,hashlib,importlib.util,json,sys,unittest
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4];API=ROOT/'product/lab/release-candidates/v1/interface/api-v71'
SOURCE='d393b0103680458664886bf39a6b1c5d277aab3408e26f60bde1a083fb5e9b40'
PROFILE='4fdd86fee7f932e86bac9109d97b14ca4bb294886c7fd6494b9c842d9ee02493'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def emit(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
    assert bind(API/'source-manifest.json')['sha256']==SOURCE and bind(API/'contract-profile.json')['sha256']==PROFILE
    name='_cal_API71_generated_preparation';spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    G=__import__(name+'.test_generated_candidate',fromlist=['*']);G.SOURCE=SOURCE;G.PROFILE=PROFILE
    P=__import__(name+'.protocol',fromlist=['*']);F=__import__(name+'.fixtures',fromlist=['*']);H=__import__(name+'.handlers',fromlist=['*']);guard=__import__(name+'.guard',fromlist=['*'])
    guard.verify(SOURCE)
    class Preparation(G.GeneratedWorkflow):
        def test_actual_generated_prepare_retry_and_inspection(self):
            service,proposal,_=self.submitted();manifest=copy.deepcopy(service.vault.manifest);inputs=copy.deepcopy(service.vault.inputs)
            call=F.call(service.channel.context,'lab.status',H.cut(self.view))
            call.update(operation='change.prepare',idempotency_key=proposal['idempotency_key'],deadline=service.channel.context['expires_at'],message=copy.deepcopy(proposal))
            reply=self.invoke(service,call);self.assertEqual(reply['kind'],'result',reply);review=reply['message']
            self.assertTrue(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:proposal-review:v1-candidate',review))
            self.assertEqual(review['source_cut'],H.cut(self.view));self.assertEqual(review['posture'],'blocked');self.assertTrue(review['gaps'])
            self.assertEqual(service.vault.object_read(review['proposal_binding']),P.compact(proposal))
            self.assertEqual(review['stable_core_bindings'],[t['decision_core_binding'] for t in proposal['targets']]);self.assertEqual(len(review['stable_core_bindings']),4)
            report=P.frame_parse(service.vault.object_read(review['validation_report_binding']));self.assertEqual(report['result'],'not-evaluable')
            self.assertEqual(len([c for c in report['checks'] if c['check_ref'].startswith('check:remaining-domain-reference-')]),2)
            for binding in review['declared_consequence_bindings']:
                consequences=P.frame_parse(service.vault.object_read(binding));self.assertEqual(consequences['canonical_admissions'],0);self.assertEqual(consequences['signed_transactions'],0);self.assertIsNone(consequences['owner_outcome'])
            privacy=P.frame_parse(service.vault.object_read(review['private_public_review_binding']))
            self.assertTrue(privacy['selected_inputs_checked']);self.assertFalse(privacy['session_memory_exported']);self.assertFalse(privacy['private_keys_exported']);self.assertFalse(privacy['public_export_permitted'])
            before=self.journal(service);retry=copy.deepcopy(call);retry['call_id']+=':retry'
            again=self.invoke(service,retry);self.assertEqual(again['kind'],'result',again);self.assertEqual(again['message'],review);self.assertEqual(self.journal(service),before)
            inspection=F.call(service.channel.context,'operation.inspect',H.cut(self.view));inspection['deadline']=service.channel.context['expires_at']
            inspection['message']['lookup']={'operation':'change.prepare','idempotency_key':proposal['idempotency_key']}
            observed=self.invoke(service,inspection);self.assertEqual(observed['kind'],'result',observed)
            self.assertFalse(observed['message']['retry_allowed']);self.assertEqual(observed['message']['operation'],'change.prepare')
            self.assertEqual(service.vault.manifest,manifest);self.assertEqual(service.vault.inputs,inputs);self.assertEqual(P.compact(self.view.data['projection']),self.projection)
    cases=[]
    class Result(unittest.TextTestResult):
        def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,error):super().addFailure(test,error);cases.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(error,test)})
        def addError(self,test,error):super().addError(test,error);cases.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(error,test)})
    suite=unittest.TestSuite([Preparation('test_actual_generated_prepare_retry_and_inspection')]);log=RUN/'API71-generated-preparation-0001.log'
    with log.open('x') as f:result=unittest.TextTestRunner(stream=f,verbosity=2,resultclass=Result).run(suite)
    guard.verify(SOURCE);complete=result.testsRun==1 and not any('setUpClass' in c['test'] or 'tearDownClass' in c['test'] for c in cases)
    observations=getattr(Preparation,'witnesses',[]);wire=RUN/'API71-generated-preparation-wire-0001.json';emit(wire,{'observations':observations,'actual_owner_outcome':None,'authority_effect':'none'})
    good=result.wasSuccessful() and complete and len(observations)==4
    report={'schema_version':'lab-actual-generated-preparation-checks/v1-candidate','result':'PASS' if good else 'FAIL',
        'source_sha256':SOURCE,'profile_sha256':PROFILE,'actual_cases':result.testsRun,'actual_public_calls':len(observations),'cases':cases,'failures':len(result.failures),'errors':len(result.errors),
        'source_guarded_exit_completed':True,'original_source_exit_completed':complete and not result.errors,'owned_fixture_cleanup_completed':complete and not result.errors,
        'source_callbacks_replaced':False,'clock_replaced':False,'time_bounds_extended':False,
        'files':[bind(API/'source-manifest.json'),bind(API/'contract-profile.json'),bind(Path(__file__).resolve()),bind(log),bind(wire)],
        'generic_challenge_review_workflow_qualified':False,'whole_API_qualified':False,'canonical_admissions_applied':0,'runtime_activations':0,
        'actual_owner_outcome':None,'authority_effect':'none','task_complete':False,'goal_complete':False,
        'claim_ceiling':'Selected actual original submit/preparation/retry/inspection only. Carrier semantic gaps retained; no proposal.review qualification, owner outcome or admission.'}
    path=RUN/'API71-generated-preparation-checks-0001.json';emit(path,report)
    print(json.dumps({'result':report['result'],'actual_cases':report['actual_cases'],'actual_public_calls':report['actual_public_calls'],'failures':report['failures'],'errors':report['errors'],'report_binding':bind(path)}),flush=True)
    return 0 if good else 1
if __name__=='__main__':raise SystemExit(main())
