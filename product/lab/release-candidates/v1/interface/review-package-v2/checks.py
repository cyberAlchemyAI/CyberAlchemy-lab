"""Owned exact review guards; public API implementation count remains twelve."""
import argparse,base64,copy,importlib.util,json,os,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True);a=parser.parse_args()
    name='_cal_exact_review_checks';spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    B=__import__(name+'.base',fromlist=['*']);F=__import__(name+'.fixtures',fromlist=['*']);B.guard(a.source_sha256)
    examples=[];cases=[]
    class Checks(unittest.TestCase):
        def example(self,**kwargs):return self.enterContext(F.example(a.source_sha256,**kwargs))
        def build(self,builder,review):return builder.build(review,B.P.compact(review))
        def manifest(self,builder,package):return B.P.frame_parse(builder.vault.object_read(package['manifest_binding']))
        def rejected(self,mutate):
            builder,review,_=self.example();changed=copy.deepcopy(review);mutate(changed)
            with self.assertRaises(Exception):self.build(builder,changed)
        def test_00_actual_two_target_package(self):
            builder,review,witness=self.example();package,bindings=self.build(builder,review);manifest=self.manifest(builder,package)
            self.assertEqual(len(manifest['targets']),2);self.assertEqual(package['ordered_core_bindings'],review['stable_core_bindings'])
            self.assertEqual(len(manifest['ordered_required_owner_responses']),2);self.assertEqual(package['human_checkpoint_count'],1)
            self.assertFalse(manifest['current_owner_authority_verified']);self.assertIsNone(manifest['actual_owner_outcome'])
            self.assertEqual(manifest['original_semantic_and_operational_gaps'],review['gaps']);self.assertEqual(manifest['input_posture'],review['posture'])
            self.assertFalse(manifest['preference_current_admission_claimed']);self.assertFalse(manifest['workflow_protocol_is_WorkflowRun_artifact'])
            originals=[]
            for row in manifest['generated_carriers']:
                raw=builder.vault.object_read(row['object_binding']);self.assertEqual(B.sha(raw),row['artifact']['byte_sha256'])
                body=B.P.frame_parse(raw)
                if body['kind']=='decision-bundle':self.assertTrue(all(r['selected_outcome'] is None for r in body['payload']['ordered_decisions']))
                else:self.assertEqual(body['payload']['presentation_state'],'pending');self.assertIsNone(body['payload']['closed_at'])
                originals.append({'artifact':row['artifact'],'original_bytes_base64':base64.b64encode(raw).decode(),'decoded_body':body})
            examples.append({'source_name':'reference-corrected','public_witness':witness,'review_package':package,'materialization_manifest':manifest,'actual_generated_originals':originals,'claim_ceiling':'Historical owned candidate preview; no current host authority after cleanup','authority_effect':'none','actual_owner_outcome':None})
        def test_01_actual_multi_voice_one_checkpoint(self):
            builder,review,_=self.example(multiple_voices=True);package,_=self.build(builder,review);m=self.manifest(builder,package)
            self.assertEqual(len(m['targets']),2);self.assertEqual(len(m['ordered_required_owner_responses']),4)
            self.assertEqual([r['core_index'] for r in m['ordered_required_owner_responses']],[0,0,1,1])
            self.assertEqual([r['voice_index'] for r in m['ordered_required_owner_responses']],[0,1,0,1])
            self.assertTrue(all(r['selected_outcome'] is None and not r['current_owner_authority_verified'] for r in m['ordered_required_owner_responses']))
            self.assertEqual(package['human_checkpoint_count'],1)
        def test_02_unresolved_current_preference_not_aliased(self):
            builder,review,_=self.example(proposed_preference=False)
            with self.assertRaisesRegex(Exception,'preference owner is unresolved'):self.build(builder,review)
        def test_03_changed_core_order_refused(self):self.rejected(lambda v:v['stable_core_bindings'].reverse())
        def test_04_changed_cut_refused(self):self.rejected(lambda v:v['source_cut'].update(commit_sha256='0'*64))
        def test_05_changed_validation_refused(self):self.rejected(lambda v:v['validation_report_binding'].update(sha256='0'*64))
        def test_06_caller_cannot_clear_semantic_gaps(self):self.rejected(lambda v:v.update(gaps=[],posture='ready'))
        def test_07_changed_example_refused(self):self.rejected(lambda v:v['example_bindings'][0].update(sha256='0'*64))
        def test_08_changed_consequences_refused(self):self.rejected(lambda v:v['declared_consequence_bindings'][0].update(sha256='0'*64))
        def test_09_changed_privacy_refused(self):self.rejected(lambda v:v['private_public_review_binding'].update(sha256='0'*64))
        def test_10_wrong_original_message_refused(self):
            builder,review,_=self.example();changed=copy.deepcopy(review);changed['posture']='ready'
            with self.assertRaises(Exception):builder.build(review,B.P.compact(changed))
        def test_11_routing_file_revocation_refused(self):
            builder,review,_=self.example();raw=builder.path.read_bytes();builder.path.write_bytes(raw+b' ')
            try:
                with self.assertRaises(Exception):self.build(builder,review)
            finally:builder.path.write_bytes(raw)
        def test_12_mutated_routing_capture_refused(self):
            builder,review,_=self.example();builder.routing['current_owner_authority_verified']=True
            with self.assertRaises(Exception):self.build(builder,review)
        def test_13_private_notes_refused(self):self.rejected(lambda v:v.update(session_memory={'private_note':'must not persist'}))
        def test_14_profile_body_is_not_recreated(self):
            builder,review,_=self.example();package,_=self.build(builder,review)
            self.assertEqual(package['workflow_decision_profile'],builder.routing['workflow_decision_profile'])
            m=self.manifest(builder,package);self.assertFalse(any(r['artifact']['carrier_ref']=='cal.artifact-type.workflow-decision-profile/v1' for r in m['generated_carriers']))
        def test_15_schema_unknown_property_refused(self):self.rejected(lambda v:v.update(owner_authorized=True))
        def test_16_exact_repeated_preparation_keeps_package(self):
            builder,review,_=self.example();first,_=self.build(builder,review);second,_=self.build(builder,review)
            self.assertEqual(first,second)
        def test_17_actual_raw_source_two_original_targets(self):
            builder,review,_=self.example(source_name='custody-participation');package,_=self.build(builder,review);m=self.manifest(builder,package)
            self.assertEqual(len(m['targets']),2);self.assertEqual(package['base_cut'],builder.view.custody_signed_sources.source_cut)
            for row in m['targets']:
                target=row['target'];raw=builder.vault.material(row['original_content_binding']);self.assertEqual(B.sha(raw),target['artifact']['byte_sha256'])
                self.assertNotEqual(raw,builder.view.handle.common.encoded(B.P.frame_parse(raw)))
        def test_18_independent_nonce_actual_signature(self):
            builder,review,witness=self.example()
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
            proof=witness['signed_nonce_proof'];self.assertEqual(proof['challenge'],witness['nonce_challenge'])
            Ed25519PublicKey.from_public_bytes(base64.b64decode(witness['public_policy']['reader_public_key'])).verify(base64.b64decode(proof['signature']),B.P.compact(proof['challenge']))
            self.assertEqual(witness['actual_preparation_reply']['operation'],'change.prepare');self.assertEqual(witness['actual_preparation_reply']['kind'],'result')
        def test_19_original_API_scope_unchanged(self):
            builder,review,_=self.example();self.assertEqual(len(builder.schemas.operations),34);self.assertEqual(len(B.P.SUPPORTED),12)
    class Result(unittest.TextTestResult):
        def addSuccess(self,t):super().addSuccess(t);cases.append({'test':t.id(),'result':'PASS'})
        def addFailure(self,t,e):
            super().addFailure(t,e);detail=self._exc_info_to_string(e,t);cases.append({'test':t.id(),'result':'FAIL','detail':detail});self.stream.write('\n'+detail);self.stream.flush()
        def addError(self,t,e):
            super().addError(t,e);detail=self._exc_info_to_string(e,t);cases.append({'test':t.id(),'result':'ERROR','detail':detail});self.stream.write('\n'+detail);self.stream.flush()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Checks);count=suite.countTestCases();assert count==20
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite);B.guard(a.source_sha256)
    out=HERE/'receipts';out.mkdir(exist_ok=True,mode=0o700)
    report={'schema_version':'lab-exact-review-kernel-checks/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==count else 'FAIL','tests_run':result.testsRun,'expected_tests':count,'cases':cases,'source_sha256':a.source_sha256,'actual_public_API_operations':12,'original_operations':34,'remaining_public_API_operations':22,'public_review_adapter_implemented':False,'actual_owner_outcome':None,'authority_effect':'none','task_complete':False}
    for filename,v in [('checks.json',report),('examples.json',examples)]:
        fd=os.open(out/filename,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':report['result'],'tests_run':result.testsRun,'expected_tests':count,'actual_public_API_operations':12,'public_review_adapter_implemented':False}),flush=True)
    raise SystemExit(0 if report['result']=='PASS' else 1)
if __name__=='__main__':main()
