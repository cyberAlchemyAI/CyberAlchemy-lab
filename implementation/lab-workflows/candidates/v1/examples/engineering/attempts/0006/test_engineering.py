import copy,json,subprocess,sys,tempfile,unittest
from dataclasses import replace
from run_episode import *

INPUTS=EXAMPLE/'packages/0004'
INPUT_SHA='1dedb3b7ab4b0257857eae09dcdb221cef490b5410d7c5bc87010019f29618a4'


class EngineeringTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='lab-W03-owned-');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.manifest,self.records=resolve_inputs(INPUTS,INPUT_SHA)
        self.module=load_registered(INPUTS/'registered_evaluator.py',self.manifest['output_source_sha256'])
        self.f=fixture_for(self.module);self.addCleanup(self.f.session.close)
        self.input=encoded({'original_sha256':self.manifest['original_source_sha256'],
            'output_sha256':self.manifest['output_source_sha256'],'correction_id':'host-interface-registry/v1'})
        self.f.request['input_sha256']=byte_sha(self.input)

    def tool(self):return SourceCorrection(self.root/'tool',self.manifest['original_source_sha256'],self.manifest['output_source_sha256'])
    def workflow(self):return EngineeringWorkflow(INPUTS,INPUT_SHA,self.root/'workflow')
    def evidence(self):
        return run_behavior(INPUTS/'registered_evaluator.py',self.manifest['output_source_sha256'],self.root/'evidence',default_regression={'result':'NOT-RUN','tests':0})
    def altered_inputs(self,mutate):
        import shutil
        destination=self.root/'inputs';shutil.copytree(INPUTS,destination)
        manifest=read(destination/'input-manifest.json');mutate(destination,manifest)
        raw=encoded(manifest);(destination/'input-manifest.json').write_bytes(raw)
        return destination,byte_sha(raw)

    def test_exact_input_selection(self):
        self.assertEqual(len(self.records),6);self.assertIsNone(self.manifest['actual_owner_outcome'])
    def test_independent_manifest_pin(self):
        with self.assertRaisesRegex(BoundaryFault,'selection pin'):resolve_inputs(INPUTS,'0'*64)
    def test_selected_input_bytes_drift(self):
        def mutate(p,m):(p/'intent.json').write_bytes(b'{}')
        p,pin=self.altered_inputs(mutate)
        with self.assertRaisesRegex(BoundaryFault,'original bytes'):resolve_inputs(p,pin)
    def test_body_revision_mismatch(self):
        def mutate(p,m):m['records'][0]['version_ref']=m['records'][0]['identity_ref']+'@wrong'
        p,pin=self.altered_inputs(mutate)
        with self.assertRaisesRegex(BoundaryFault,'selected version'):resolve_inputs(p,pin)
    def test_fabricated_owner_outcome(self):
        p,pin=self.altered_inputs(lambda p,m:m.update(actual_owner_outcome='admit'))
        with self.assertRaisesRegex(BoundaryFault,'owner outcome'):resolve_inputs(p,pin)
    def test_design_path_escape(self):
        p,pin=self.altered_inputs(lambda p,m:m['plan'].update(path='../plan.json'))
        with self.assertRaisesRegex(BoundaryFault,'outside selected scope'):resolve_inputs(p,pin)
    def test_design_correction_mismatch(self):
        def mutate(p,m):
            value=read(p/'design.json');value['expected_output_sha256']='0'*64
            raw=encoded(value);(p/'design.json').write_bytes(raw);m['design']['sha256']=byte_sha(raw)
        p,pin=self.altered_inputs(mutate)
        with self.assertRaisesRegex(BoundaryFault,'exact correction'):resolve_inputs(p,pin)
    def test_preexecution_satisfaction_rejected(self):
        def mutate(p,m):
            value=read(p/'intent.json');value['satisfaction_refs']=['protocol:fake-pass']
            raw=encoded(value);(p/'intent.json').write_bytes(raw);m['records'][1]['sha256']=byte_sha(raw)
        p,pin=self.altered_inputs(mutate)
        with self.assertRaisesRegex(BoundaryFault,'cannot claim satisfaction'):resolve_inputs(p,pin)
    def test_execution_requires_design(self):
        w=self.workflow()
        with self.assertRaisesRegex(BoundaryFault,'design required'):w.execute(self.f.authority,self.f.raw(),self.input)
        self.assertFalse((w.output_root/'tool').exists())
    def test_assessment_requires_output(self):
        with self.assertRaisesRegex(BoundaryFault,'implementation completion'):self.workflow().assess({},self.root)
    def test_review_requires_assessment(self):
        with self.assertRaisesRegex(BoundaryFault,'assessment missing'):self.workflow().materialize()
    def test_real_exact_correction_and_retry(self):
        t=self.tool();first=t.invoke(self.f.authority,self.f.raw(),self.input)
        self.assertEqual(first['posture'],'completed');self.assertEqual(t.output.read_bytes(),(INPUTS/'registered_evaluator.py').read_bytes())
        self.assertEqual(first,t.invoke(self.f.authority,self.f.raw(),self.input))
    def test_revoked_dispatch_has_no_effect(self):
        t=self.tool();self.f.status['revoked_refs']=[self.f.ref('delegation')]
        with self.assertRaisesRegex(BoundaryFault,'authority denied'):t.invoke(self.f.authority,self.f.raw(),self.input)
        self.assertFalse(t.output.exists());self.assertFalse(t.journal.exists())
    def test_retry_rechecks_current_authority(self):
        t=self.tool();t.invoke(self.f.authority,self.f.raw(),self.input);original=t.output.read_bytes()
        self.f.status['revoked_refs']=[self.f.ref('delegation')]
        with self.assertRaisesRegex(BoundaryFault,'current source correction authority'):t.invoke(self.f.authority,self.f.raw(),self.input)
        self.assertEqual(original,t.output.read_bytes())
    def test_closed_input_no_arbitrary_path(self):
        t=self.tool();raw=encoded({**parse(self.input),'output_path':'authority/overwrite'})
        self.f.request['input_sha256']=byte_sha(raw)
        with self.assertRaisesRegex(BoundaryFault,'closed correction input'):t.invoke(self.f.authority,self.f.raw(),raw)
        self.assertFalse(t.output.exists())
    def test_exact_input_binding(self):
        t=self.tool();self.f.request['input_sha256']='0'*64
        with self.assertRaisesRegex(BoundaryFault,'input binding changed'):t.invoke(self.f.authority,self.f.raw(),self.input)
    def test_output_budget_before_effect(self):
        t=self.tool();self.f.grant=replace(self.f.grant,max_output_bytes=1)
        with self.assertRaisesRegex(BoundaryFault,'output budget'):t.invoke(self.f.authority,self.f.raw(),self.input)
        self.assertFalse(t.output.exists())
    def test_selected_tool_contract(self):
        t=self.tool();self.f.by_kind['tool']['payload']['output_contract_ref']='protocol:other';self.f.reselect('tool')
        with self.assertRaisesRegex(BoundaryFault,'Tool contract differs'):t.invoke(self.f.authority,self.f.raw(),self.input)
    def test_pending_effect_never_redispatched(self):
        t=self.tool();result=t.invoke(self.f.authority,self.f.raw(),self.input,interrupt_after_write=True)
        self.assertEqual(result['posture'],'indeterminate');raw=t.output.read_bytes()
        self.assertEqual(t.invoke(self.f.authority,self.f.raw(),self.input)['posture'],'indeterminate');self.assertEqual(raw,t.output.read_bytes())
    def test_journal_loss_never_resets_effect(self):
        t=self.tool();t.invoke(self.f.authority,self.f.raw(),self.input);t.journal.unlink()
        with self.assertRaisesRegex(BoundaryFault,'journal missing'):t.invoke(self.f.authority,self.f.raw(),self.input)
    def test_completed_output_drift(self):
        t=self.tool();t.invoke(self.f.authority,self.f.raw(),self.input);t.output.write_bytes(b'changed')
        with self.assertRaisesRegex(BoundaryFault,'output drift'):t.invoke(self.f.authority,self.f.raw(),self.input)
    def test_missing_evidence_cannot_satisfy(self):
        checks=self.evidence();checks.pop('source-bytes-exact')
        with self.assertRaisesRegex(BoundaryFault,'incomplete satisfaction'):assess(checks,self.manifest['output_source_sha256'],(INPUTS/'registered_evaluator.py').read_bytes(),evidence_root=self.root/'evidence')
    def test_failed_regression_preserved_as_unsupported(self):
        checks=self.evidence();result=assess(checks,self.manifest['output_source_sha256'],(INPUTS/'registered_evaluator.py').read_bytes(),evidence_root=self.root/'evidence')
        self.assertEqual(result['disposition'],'unsupported');self.assertIsNone(result['actual_owner_outcome'])
    def test_fake_pass_label_rejected(self):
        checks=self.evidence();checks['default-regression-complete']['result']='PASS'
        with self.assertRaisesRegex(BoundaryFault,'evidence differs'):assess(checks,self.manifest['output_source_sha256'],(INPUTS/'registered_evaluator.py').read_bytes(),evidence_root=self.root/'evidence')
    def test_fake_pass_rebound_evidence_rejected(self):
        checks=self.evidence();path=self.root/'evidence/default-regression-complete.json';value=read(path);value['result']='PASS';raw=encoded(value);path.write_bytes(raw)
        checks['default-regression-complete'].update(result='PASS',evidence_sha256=byte_sha(raw))
        with self.assertRaisesRegex(BoundaryFault,'fabricated default regression'):assess(checks,self.manifest['output_source_sha256'],(INPUTS/'registered_evaluator.py').read_bytes(),evidence_root=self.root/'evidence')
    def test_evidence_bytes_drift(self):
        checks=self.evidence();(self.root/'evidence/source-bytes-exact.json').write_bytes(b'{}')
        with self.assertRaisesRegex(BoundaryFault,'original bytes changed'):assess(checks,self.manifest['output_source_sha256'],(INPUTS/'registered_evaluator.py').read_bytes(),evidence_root=self.root/'evidence')
    def test_wrong_output_revision_rejected(self):
        with self.assertRaisesRegex(BoundaryFault,'output revision'):assess(self.evidence(),self.manifest['output_source_sha256'],b'changed',evidence_root=self.root/'evidence')
    def test_unknown_relation_endpoint(self):
        with self.assertRaisesRegex(BoundaryFault,'revision unresolved'):typed_relation('bad','relation.successor-of','absent',self.manifest['work_ref'],self.records,{'succession_effect':'x'})
    def test_undeclared_relation_kind(self):
        ref=self.manifest['work_ref']
        with self.assertRaisesRegex(BoundaryFault,'ordered pair undeclared'):typed_relation('bad','relation.invented',ref,ref,self.records,{})
    def test_closed_relation_qualifiers(self):
        ref=self.manifest['work_ref']
        with self.assertRaisesRegex(BoundaryFault,'qualifier axes'):typed_relation('bad','relation.successor-of',ref,ref,self.records,{'succession_effect':'x','invented':'y'})
    def test_full_unsupported_episode_stays_unadmitted(self):
        result=execute_episode(INPUTS,INPUT_SHA,self.root/'episode',{'result':'NOT-RUN','tests':0})
        self.assertEqual(len(result['candidates']),6);self.assertEqual(len(result['relations']),6)
        self.assertFalse(result['review']['promotion_eligible']);self.assertEqual(result['review']['canonical_effects_applied'],0)
        self.assertIsNone(result['review']['actual_owner_outcome']);self.assertFalse(result['review']['work_effect']['applied'])
        self.assertEqual([e['to'] for e in result['events']],['designed','implemented','assessed'])
        self.assertEqual(len({r['version_ref'] for r in result['review']['member_records']}),12)
        protocol=read(self.root/'episode/workflow-run.json');self.assertEqual(protocol['status_axes']['outcome_satisfaction'],'unsupported')
        self.assertEqual(len(protocol['actor']['role_assignment_refs']),1)
    def test_private_session_memory_not_persisted(self):
        self.f.session.note('W03-PRIVATE-NOTE')
        t=self.tool();t.invoke(self.f.authority,self.f.raw(),self.input)
        self.assertNotIn(b'W03-PRIVATE-NOTE',t.journal.read_bytes());self.f.session.close()
        self.assertEqual(self.f.session._memory,[])
    def test_cold_process_exact_successor(self):
        code='''from pathlib import Path
from behavior import *
m=load_registered(Path(sys.argv[1]),sys.argv[2]);f=fixture_for(m)
try:
 assert f.authority.check(f.raw())['posture']=='permitted'
 f.status['revoked_refs']=[f.ref('delegation')]
 assert f.authority.check(f.raw())['posture']=='denied'
finally:f.session.close()
'''
        result=subprocess.run([sys.executable,'-c',code,str(INPUTS/'registered_evaluator.py'),self.manifest['output_source_sha256']],cwd=EXAMPLE,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)


if __name__=='__main__':unittest.main()
