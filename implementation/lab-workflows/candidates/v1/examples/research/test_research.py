"""Closed mechanism tests use labeled process fixtures; retained episode uses real replay."""
import copy,json,shutil,subprocess,tempfile,unittest
from unittest.mock import patch
from dataclasses import replace
from run_episode import *
from build_inputs import prepare

INPUTS=EXAMPLE/'packages/0007'


class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='lab-W04-test-only-');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.pin=byte_sha((INPUTS/'selection.json').read_bytes());self.selection,self.records,self.procedure=resolve(INPUTS,self.pin)
        self.f=fixture(self.selection,self.records);self.addCleanup(self.f.session.close)
        self.input=encoded({'selection_sha256':self.pin,'procedure_sha256':self.selection['procedure']['sha256']})
        self.f.request['input_sha256']=byte_sha(self.input);self.child_roots=[]

    def fake_process(self,args,**kwargs):
        # Shape/transition fixture only; no replay or performance evidence claim.
        self.child_roots.append(Path(args[-1]))
        value={'authority_effect':'none','approach':args[-3],'archive_sha256':args[-2],
            'projection_sha256':'1'*64,'head':read(ARCHIVE)['project_pins']['expected_head'],
            'actual_owner_outcome':None,'cache_enabled':False,'owned_store_removed_on_return':True}
        return subprocess.CompletedProcess(args,0,encoded(value),b'')

    def workflow(self):return ResearchWorkflow(INPUTS,self.pin,self.root/'workflow')
    def executed(self):
        w=self.workflow();w.design()
        with patch('research.subprocess.run',self.fake_process):self.assertEqual(w.execute(self.f.authority,self.f.raw(),self.input)['posture'],'completed')
        return w

    def variant(self,mutate):
        p=self.root/'inputs';shutil.copytree(INPUTS,p);s=read(p/'selection.json');mutate(p,s)
        raw=encoded(s);(p/'selection.json').write_bytes(raw);return p,byte_sha(raw)

    def trials(self,ratios=(0.5,0.5,0.5)):
        return [{'sample':i+1,'order':order,'observations':{'direct':{'posture':'completed','seconds':10.,'projection_sha256':'a'*64,'head':'b'*64},
            'facade':{'posture':'completed','seconds':10.*ratios[i],'projection_sha256':'a'*64,'head':'b'*64}}} for i,order in enumerate(self.procedure['order'])]

    def test_exact_scoped_inputs(self):
        self.assertEqual(len(self.records),13);self.assertIsNone(self.selection['actual_owner_outcome'])
    def test_independent_selection_pin(self):
        with self.assertRaisesRegex(BoundaryFault,'selection pin'):resolve(INPUTS,'0'*64)
    def test_input_bytes_drift(self):
        p,pin=self.variant(lambda p,s:(p/'hypothesis.json').write_bytes(b'{}'))
        with self.assertRaisesRegex(BoundaryFault,'input bytes'):resolve(p,pin)
    def test_body_version_drift(self):
        def mutate(p,s):
            row=next(r for r in s['records'] if r['kind']=='method');row['version_ref']=row['identity_ref']+'@wrong'
        p,pin=self.variant(mutate)
        with self.assertRaisesRegex(BoundaryFault,'body version'):resolve(p,pin)
    def test_no_fabricated_owner_outcome(self):
        p,pin=self.variant(lambda p,s:s.update(actual_owner_outcome='admit'))
        with self.assertRaisesRegex(BoundaryFault,'owner outcome'):resolve(p,pin)
    def test_procedure_original_bytes(self):
        p,pin=self.variant(lambda p,s:(p/'procedure.json').write_bytes(b'{}'))
        with self.assertRaisesRegex(BoundaryFault,'method bytes'):resolve(p,pin)
    def test_procedure_is_closed(self):
        def mutate(p,s):
            value=read(p/'procedure.json');value['caller_confirmation']='PASS';raw=encoded(value);(p/'procedure.json').write_bytes(raw);s['procedure']['sha256']=byte_sha(raw)
        p,pin=self.variant(mutate)
        with self.assertRaisesRegex(BoundaryFault,'closed research procedure'):resolve(p,pin)
    def test_falsifier_required_before_run(self):
        def mutate(p,s):
            value=read(p/'hypothesis.json');value['payload']['falsification_conditions']=[];raw=encoded(value);(p/'hypothesis.json').write_bytes(raw)
            next(r for r in s['records'] if r['kind']=='hypothesis')['sha256']=byte_sha(raw)
        p,pin=self.variant(mutate)
        with self.assertRaisesRegex(BoundaryFault,'invalid hypothesis'):resolve(p,pin)
    def test_product_capability_context_exact(self):
        def mutate(p,s):
            value=read(p/'experiment-design.json');value['product_evaluation_context']['product_capability_refs']=['capability:wrong'];raw=encoded(value);(p/'experiment-design.json').write_bytes(raw)
            next(r for r in s['records'] if r['kind']=='experiment-design')['sha256']=byte_sha(raw)
        p,pin=self.variant(mutate)
        with self.assertRaisesRegex(BoundaryFault,'Product evaluation'):resolve(p,pin)
    def test_execution_requires_design(self):
        w=self.workflow()
        with self.assertRaisesRegex(BoundaryFault,'design required'):w.execute(self.f.authority,self.f.raw(),self.input)
        self.assertFalse(w.journal.exists())
    def test_current_authority_before_effect(self):
        w=self.workflow();w.design();self.f.status['revoked_refs']=[self.f.ref('delegation')]
        with self.assertRaisesRegex(BoundaryFault,'authority denied'):w.execute(self.f.authority,self.f.raw(),self.input)
        self.assertFalse(w.journal.exists())
    def test_profile_output_kinds_checked_before_execution(self):
        w=self.workflow();w.design();self.f.by_kind['agent-profile']['payload']['allowed_output_kinds']=['agent-action'];self.f.reselect('agent-profile')
        with self.assertRaisesRegex(BoundaryFault,'Profile denies planned'):w.execute(self.f.authority,self.f.raw(),self.input)
        self.assertFalse(w.journal.exists())
    def test_revocation_before_candidate_materialization(self):
        w=self.executed();w.assess();self.f.status['revoked_refs']=[self.f.ref('delegation')]
        with self.assertRaisesRegex(BoundaryFault,'authority denied'):w.materialize()
        self.assertFalse((w.output/'review-effects.json').exists())
    def test_tool_input_closed(self):
        w=self.workflow();w.design();raw=encoded({**parse(self.input),'path':'authority'});self.f.request['input_sha256']=byte_sha(raw)
        with self.assertRaisesRegex(BoundaryFault,'closed selected research input'):w.execute(self.f.authority,self.f.raw(),raw)
    def test_tool_contract_exact(self):
        w=self.workflow();w.design();self.f.by_kind['tool']['payload']['evidence_route_ref']='protocol:unselected';self.f.reselect('tool')
        with self.assertRaisesRegex(BoundaryFault,'Tool contract'):w.execute(self.f.authority,self.f.raw(),self.input)
    def test_revocation_between_replays_indeterminate(self):
        w=self.workflow();w.design()
        def revoke(args,**kwargs):
            result=self.fake_process(args,**kwargs);self.f.status['revoked_refs']=[self.f.ref('delegation')];return result
        with patch('research.subprocess.run',revoke):result=w.execute(self.f.authority,self.f.raw(),self.input)
        self.assertEqual(result['posture'],'indeterminate');self.assertFalse(result['retry_allowed'])
        self.assertEqual(len(self.child_roots),1)
    def test_pending_no_automatic_redispatch(self):
        w=self.workflow();w.design()
        with patch('research.subprocess.run',self.fake_process):result=w.execute(self.f.authority,self.f.raw(),self.input,interrupt_after_observations=True)
        self.assertEqual(result['posture'],'indeterminate')
        with self.assertRaisesRegex(BoundaryFault,'design required'):w.execute(self.f.authority,self.f.raw(),self.input)
    def test_original_child_output_contract(self):
        w=self.workflow();w.design()
        def wrong(args,**kwargs):
            child=self.fake_process(args,**kwargs);value=parse(child.stdout);value['actual_owner_outcome']='admit';return subprocess.CompletedProcess(args,0,encoded(value),b'')
        with patch('research.subprocess.run',wrong):result=w.execute(self.f.authority,self.f.raw(),self.input)
        self.assertEqual(result['posture'],'indeterminate');self.assertFalse(result['retry_allowed'])
    def test_child_roots_removed_after_success(self):
        self.executed();self.assertEqual(len(self.child_roots),6);self.assertTrue(all(not p.exists() for p in self.child_roots))
    def test_timeout_rows_and_roots_preserved(self):
        w=self.workflow();w.design();roots=[]
        def timeout(args,**kwargs):roots.append(Path(args[-1]));raise subprocess.TimeoutExpired(args,45,output=b'partial-fixture',stderr=b'timeout-fixture')
        with patch('research.subprocess.run',timeout):self.assertEqual(w.execute(self.f.authority,self.f.raw(),self.input)['posture'],'completed')
        self.assertTrue(all(not p.exists() for p in roots));result=w.assess();self.assertEqual(result['disposition'],'inconclusive');self.assertEqual(result['labels'],['timeout']*3)
        self.assertTrue((w.output/'sample-1-direct.stdout').exists())
    def test_negative_process_rows_retained(self):
        w=self.workflow();w.design()
        def rejected(args,**kwargs):return subprocess.CompletedProcess(args,1,b'',b'negative-fixture')
        with patch('research.subprocess.run',rejected):w.execute(self.f.authority,self.f.raw(),self.input)
        self.assertEqual(w.assess()['labels'],['rejected']*3);self.assertEqual((w.output/'sample-1-direct.stderr').read_bytes(),b'negative-fixture')
    def test_method_change_after_run_denied(self):
        p=self.root/'mutable-inputs';shutil.copytree(INPUTS,p);w=ResearchWorkflow(p,self.pin,self.root/'workflow');w.design()
        with patch('research.subprocess.run',self.fake_process):w.execute(self.f.authority,self.f.raw(),self.input)
        (p/'procedure.json').write_bytes(b'{}')
        with self.assertRaisesRegex(BoundaryFault,'method bytes'):w.assess()
    def test_completion_is_not_confirmation(self):
        w=self.executed();self.assertIsNone(w.assessment);self.assertEqual(w.state,'executed');self.assertIsNone(w.events[-1]['detail']['hypothesis_support'])
    def test_assessment_needs_observations(self):
        with self.assertRaisesRegex(BoundaryFault,'observations required'):self.workflow().assess()
    def test_expired_session_cannot_assess(self):
        w=self.executed();self.f.session.close()
        with self.assertRaisesRegex(BoundaryFault,'authority denied'):w.assess()
        self.assertFalse((w.output/'assessment.json').exists())
    def test_missing_sample_is_inconclusive_input_error(self):
        with self.assertRaisesRegex(BoundaryFault,'missing declared'):evaluate(self.trials()[:-1],self.procedure)
    def test_positive_negative_and_inconclusive_finite(self):
        self.assertEqual(evaluate(self.trials((.5,.6,.7)),self.procedure)['disposition'],'positive')
        self.assertEqual(evaluate(self.trials((1.,1.1,1.2)),self.procedure)['disposition'],'negative')
        self.assertEqual(evaluate(self.trials((.5,1.1,.7)),self.procedure)['disposition'],'inconclusive')
    def test_mismatched_projection_contradicts(self):
        rows=self.trials();rows[0]['observations']['facade']['projection_sha256']='c'*64
        self.assertEqual(evaluate(rows,self.procedure)['support_state'],'contradicted')
    def test_invalid_timing_denied(self):
        rows=self.trials();rows[0]['observations']['direct']['seconds']=float('nan')
        with self.assertRaisesRegex(BoundaryFault,'invalid observed timing'):evaluate(rows,self.procedure)
    def test_residue_entropy_has_declared_register(self):
        self.assertEqual(entropy(['parity']*3),0);self.assertAlmostEqual(entropy(['parity','timeout']),math.log(2))
        with self.assertRaisesRegex(BoundaryFault,'undeclared residue'):entropy(['clock-speed'])
    def test_negative_evidence_not_suppressed(self):
        w=self.executed();value=read(w.output/'observed.json');value['trials']=[];(w.output/'observed.json').write_bytes(encoded(value))
        with self.assertRaisesRegex(BoundaryFault,'observed bytes changed'):w.assess()
    def test_original_process_evidence_not_replaced(self):
        w=self.executed();(w.output/'sample-1-direct.stdout').write_bytes(b'forged-pass')
        with self.assertRaisesRegex(BoundaryFault,'process evidence changed'):w.assess()
    def test_review_requires_assessment(self):
        with self.assertRaisesRegex(BoundaryFault,'assessment required'):self.executed().materialize()
    def test_fabricated_assessment_after_evaluation(self):
        w=self.executed();w.assess();w.assessment['support_state']='fabricated'
        with self.assertRaisesRegex(BoundaryFault,'assessment altered'):w.materialize()
    def test_unknown_global_endpoint_denied(self):
        with self.assertRaisesRegex(BoundaryFault,'endpoint unresolved'):typed('bad','relation.evaluates','absent',self.selection['capability_ref'],self.records,{})
    def test_invented_product_pair_denied(self):
        with self.assertRaisesRegex(BoundaryFault,'pair undeclared'):typed('bad','relation.tests-hypothesis',self.selection['design_ref'],self.selection['product_ref'],self.records,{'test_role':'x'})
    def test_closed_qualifier_axes(self):
        with self.assertRaisesRegex(BoundaryFault,'qualifier domain'):typed('bad','relation.evaluates',self.selection['design_ref'],self.selection['capability_ref'],self.records,{'evaluation_role':'x','evaluation_purpose':'y','invented':'z'})
    def test_all_review_records_are_exact_candidate(self):
        w=self.executed();w.assess();result=w.materialize()
        self.assertEqual(len(result['candidates']),11);self.assertEqual(len(result['relations']),22)
        members=result['review']['selected_candidate_members'];self.assertEqual(len(members),33);self.assertEqual(len({r['version_ref'] for r in members}),33)
        self.assertIsNone(result['review']['actual_owner_outcome']);self.assertEqual(result['review']['canonical_effects_applied'],0)
        self.assertIn('evaluated-candidate.1',next(r['version_ref'] for r in members if r['kind']=='work'))
        self.assertEqual(result['candidates']['measurement-result']['observable_kind'],'shannon-entropy')
        self.assertEqual(result['candidates']['generated-output']['payload']['generator_ref'],ref(result['candidates']['implementation']))
    def test_protocol_axes_keep_work_satisfaction_separate(self):
        w=self.executed();w.assess();result=w.materialize()
        actors=[{'version_ref':r.version_ref,'sha256':r.expected_sha256} for r in self.f.records.values()]
        protocol=protocol_run(w,result,actors)
        self.assertEqual(protocol['state'],'evaluated');self.assertIsNone(protocol['outcome_assessment'])
        self.assertIsNone(protocol['status_axes']['outcome_satisfaction']);self.assertEqual(protocol['status_axes']['admission'],'candidate-unadmitted')
        self.assertEqual(len(protocol['actor']['role_assignment_refs']),1)
    def test_product_experiment_needs_no_inquiry_link(self):
        p=self.root/'product-only-inputs';pin=prepare(p,inquiry_link=False);s,r,_=resolve(p,pin);f=fixture(s,r);self.addCleanup(f.session.close)
        original=encoded({'selection_sha256':pin,'procedure_sha256':s['procedure']['sha256']});f.request['input_sha256']=byte_sha(original)
        w=ResearchWorkflow(p,pin,self.root/'workflow');w.design()
        with patch('research.subprocess.run',self.fake_process):w.execute(f.authority,f.raw(),original)
        w.assess();result=w.materialize();self.assertEqual(result['candidates']['experiment-run']['research_refs'],[])
        self.assertFalse(any(r['payload']['relation_kind_ref']=='relation.engages-inquiry' and r['payload']['source']['kind']=='experiment-run' for r in result['relations']))
        self.assertTrue(any(r['payload']['relation_kind_ref']=='relation.evaluates' and r['payload']['source']['kind']=='experiment-run' for r in result['relations']))
    def test_private_session_memory_erased_and_excluded(self):
        self.f.session.note('W04-PRIVATE-NOTE');w=self.executed();w.assess();w.materialize()
        self.assertTrue(all(b'W04-PRIVATE-NOTE' not in p.read_bytes() for p in w.output.glob('*') if p.is_file()))
        self.f.session.close();self.assertEqual(self.f.session._memory,[])


if __name__=='__main__':unittest.main()
