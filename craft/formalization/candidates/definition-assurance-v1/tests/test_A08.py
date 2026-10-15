"""Record denotation controls and actual bounded-search failure behavior."""
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE))
loader=importlib.util.spec_from_file_location('governance_pilot_v2',HERE/'pilot-v2.py');v=importlib.util.module_from_spec(loader);loader.loader.exec_module(v)


class RecordTests(unittest.TestCase):
    def control(self):return v.Control(v.f.load_limits())
    def value(self,path='complete',grant=False,duty=False,claim='none',index=0):return v.record_values(v.make_state(index,path,grant,duty,claim),self.control())
    def test_lineage_never_creates_assignment(self):
        for path in ['complete','incomplete','source-local']:
            row=self.value(path);self.assertTrue(row['Traceable']);self.assertFalse(row['Position']);self.assertFalse(row['BackedRight'])
    def test_assertion_never_supplies_missing_grant(self):
        row=self.value(claim='right');self.assertFalse(row['Right']);self.assertFalse(row['Position']);self.assertEqual(['claim:right:0'],row['unbacked_claims'])
    def test_unclaimed_grant_is_a_position(self):
        row=self.value(grant=True);self.assertTrue(row['Right']);self.assertEqual(['grant:0'],row['unclaimed_right_grants']);self.assertFalse(row['BackedRight'])
    def test_duty_is_position_without_right(self):
        row=self.value(duty=True,claim='responsibility');self.assertTrue(row['Duty']);self.assertTrue(row['Position']);self.assertFalse(row['Right']);self.assertFalse(row['BackedRight'])
    def test_permit_and_duty_coexist_with_distinct_assignment_ids(self):
        row=self.value(grant=True,duty=True,claim='both');self.assertEqual(['grant:0'],row['right_grants']);self.assertEqual(['duty:0'],row['assigned_duties']);self.assertTrue(row['BackedRight'])
    def test_missing_origin_does_not_revoke_grant(self):
        for mode in ['unknown','deferred','empty']:
            row=self.value(mode,True,False,'right');self.assertFalse(row['Traceable']);self.assertTrue(row['Right']);self.assertTrue(row['BackedRight'])
    def test_incomplete_assertion_does_not_complete_itself(self):
        row=self.value(grant=True,claim='incomplete-right');self.assertTrue(row['Right']);self.assertFalse(row['BackedRight']);self.assertEqual(['claim:right:0'],row['incomplete_claims'])
    def test_trace_and_authority_predicates_are_independent_of_A07_evaluators(self):
        with patch.object(v.p,'inspect_state',side_effect=AssertionError('must not call')):
            self.assertTrue(self.value(grant=True,claim='right')['BackedRight'])
    def test_scope_principal_and_assignment_kind_do_not_transfer(self):
        for key in ['scope','principal','object','operation','effect']:
            state=v.make_state(0,'complete',True,False,'right');state['grants'][0][key]='other:'+key
            self.assertFalse(v.record_values(state,self.control())['Right'])
        state=v.make_state(0,'complete',False,True,'right');state['claims'][0]['assignment_ref']='duty:0';self.assertFalse(v.record_values(state,self.control())['BackedRight'])
    def test_boundary_exclusion_and_wrong_role_take_effect(self):
        state=v.make_state(0,'complete',True,False,'right');state['boundaries'][0]['excluded_effects']=[state['context']['effect']];self.assertFalse(v.record_values(state,self.control())['Right'])
        state=v.make_state(0,'complete',False,True,'none');state['role_bindings'][0]['owner_role']='role:other';self.assertFalse(v.record_values(state,self.control())['Duty'])
    def test_local_trace_scope_is_not_promoted(self):
        state=v.make_state(0,'source-local',True,False,'right');state['provenance']['scope_ref']='scope:other';state['posture']['provenance']['scope_ref']='scope:other';row=v.record_values(state,self.control());self.assertFalse(row['Traceable']);self.assertTrue(row['Right'])
    def test_closed_typing_rejects_unknown_as_empty(self):
        state=v.make_state(0,'unknown',False,False,'none');state['provenance']['steps']=[]
        with self.assertRaises(v.p.SemanticFault):v.record_values(state,self.control())


class MoveTests(unittest.TestCase):
    def check(self,world):return v.transition_holds(world['transition'],world['records'],v.Control(v.f.load_limits()))
    def test_provenance_only_and_recorded_status_valid(self):self.assertTrue(self.check(v.point(0)));self.assertTrue(self.check(v.point(2)))
    def test_silent_status_invalid(self):self.assertFalse(self.check(v.point(1)))
    def test_transition_does_not_use_A07_move_checker(self):
        with patch.object(v.p,'check_move',side_effect=AssertionError('must not call')):self.assertTrue(self.check(v.point(0)))
    def test_unrelated_subject_is_not_same_context(self):
        world=v.point(0);world['transition']['move']['subject_id']=v.SUBJECTS[1];self.assertFalse(self.check(world))
    def test_full_snapshot_hash_and_revision_required(self):
        for key in ['before_ref','after_ref']:
            world=v.point(0);world['transition']['move'][key]['sha256']='0'*64;self.assertFalse(self.check(world))
        world=v.point(0);world['transition']['move']['before_ref']['revision']='other';self.assertFalse(self.check(world))
    def test_transition_after_must_be_actual_carrier_record(self):
        world=v.point(0);world['records'][0]['posture']['evidence']=v.info('different');self.assertFalse(self.check(world))
    def test_grant_add_requires_exact_delta_and_basis(self):
        world=v.point(0);after=world['transition']['after'];after['grants']=v.make_state(0,'complete',True,False,'none')['grants'];world['records'][0]=copy.deepcopy(after);move=world['transition']['move'];move['after_ref']['sha256']=v.ir.digest(after);move['intended_axes'].append('grants')
        self.assertFalse(self.check(world));move['grant_changes']=[{'grant_id':'grant:0','before_sha256':None,'after_sha256':v.ir.digest(after['grants'][0]),'basis_ref':'decision:explicit-grant'}];self.assertTrue(self.check(world))
        move['grant_changes'][0]['before_sha256']='0'*64;self.assertFalse(self.check(world))
    def test_unrecorded_duty_assignment_is_invalid(self):
        world=v.point(0);after=world['transition']['after'];after['responsibilities']=v.make_state(0,'complete',False,True,'none')['responsibilities'];world['records'][0]=copy.deepcopy(after);move=world['transition']['move'];move['after_ref']['sha256']=v.ir.digest(after);move['intended_axes'].append('responsibilities');self.assertFalse(self.check(world))
        move['responsibility_changes']=[{'assignment_id':'duty:0','before_sha256':None,'after_sha256':v.ir.digest(after['responsibilities'][0]),'basis_ref':'decision:explicit-duty'}];self.assertTrue(self.check(world))


class SearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.prepared=v.prepare()
    def run_search(self,**kwargs):
        # Reuse the verified inputs in algorithm controls, retaining actual end-read checks.
        with patch.object(v,'prepare',return_value=self.prepared):return v.search(**kwargs)
    def test_actual_pipeline_finds_every_required_existential(self):
        out=v.search();self.assertEqual('witnesses-found',out['status']);self.assertEqual(11,len(out['query_results']));self.assertTrue(all(row['strength']=='model-witness' for row in out['query_results']));self.assertEqual(79,out['counts']['visited']);self.assertFalse(out['exhaustion_complete']);self.assertFalse(out['semantic_ready']);self.assertIsNone(out['unbounded_conclusion']);self.assertEqual(11,len(out['pending_gates']))
    def test_saved_witnesses_recheck_predicates_and_theory(self):
        out=self.run_search()
        for row in out['query_results']:
            witness=row['witness'];actual=v.assess(witness['model'],self.prepared,v.Control(v.f.load_limits()));self.assertTrue(actual['theory']);self.assertTrue(actual['queries'][row['obligation_id']]);self.assertEqual(witness['projection_model'],actual['projection_model']);self.assertEqual(witness['model_sha256'],v.ir.digest(witness['model']))
    def test_generator_uses_all_factored_coordinates_not_examples(self):
        self.assertEqual(8640,__import__('math').prod(v.RADICES));seen=set()
        for rank in range(90):seen.add(v.ir.digest(v.point(rank)))
        self.assertEqual(90,len(seen));self.assertNotEqual(v.point(0),v.point(8639))
    def test_exact_small_range_exhaustion_only(self):
        out=self.run_search(mode='exhaustive',stop=3);self.assertEqual('bounded-checked',out['status']);self.assertTrue(out['exhaustion_complete']);self.assertEqual(3,out['counts']['visited']);self.assertEqual(2,out['counts']['theory_models']);self.assertEqual(0,out['counts']['joint_models']);self.assertTrue(all(row['status']=='bounded-no-joint-population-model' for row in out['query_results'] if row['obligation_id']!='query:consistency'));self.assertIsNone(out['unbounded_conclusion'])
    def test_contradictory_constraints_do_not_prove_queries_vacuously(self):
        out=self.run_search(constraints=['no-position','some-position'],mode='exhaustive',stop=90);self.assertTrue(out['exhaustion_complete']);self.assertEqual(0,out['counts']['theory_models']);self.assertTrue(all(row['status']=='bounded-no-theory-model' and row['witness'] is None for row in out['query_results']))
    def test_empty_required_population_is_distinct_from_inconsistent_theory(self):
        out=self.run_search(constraints=['no-right'],mode='exhaustive',stop=90);self.assertGreater(out['counts']['theory_models'],0);self.assertEqual(0,out['counts']['joint_models']);self.assertTrue(all(row['witness'] is None for row in out['query_results'] if row['obligation_id']!='query:consistency'))
    def test_collapsing_constraint_removes_left_difference_without_addition_to_T(self):
        before=copy.deepcopy(self.prepared['theory']);out=self.run_search(constraints=['trace-implies-position'],mode='exhaustive',stop=240);self.assertGreater(out['counts']['joint_models'],0);row=next(row for row in out['query_results'] if row['obligation_id']=='relation:TRACE-Position:left-difference');self.assertEqual('bounded-no-witness',row['status']);self.assertEqual(before,self.prepared['theory'])
    def test_configuration_limit_has_no_absence_conclusion(self):
        out=self.run_search(mode='exhaustive',budgets={'max_interpretations':1});self.assertEqual('resource-limit',out['status']);self.assertFalse(out['exhaustion_complete']);self.assertEqual(1,out['counts']['visited']);self.assertTrue(all(row['strength']=='none' for row in out['query_results'] if row['witness'] is None));self.assertEqual('verified-at-final-read',out['source_runtime_currentness'])
    def test_step_limit_has_no_absence_conclusion(self):
        out=self.run_search(budgets={'max_evaluation_steps':1});self.assertEqual('resource-limit',out['status']);self.assertEqual(1,out['counts']['evaluation_steps']);self.assertTrue(all(row['witness'] is None for row in out['query_results']))
    def test_output_limit_retains_all_required_identities_and_removes_witnesses(self):
        out=self.run_search(budgets={'max_output_bytes':8192});self.assertEqual('resource-limit',out['status']);self.assertLessEqual(len(v.ir.canonical(out)),8192);self.assertEqual(11,len(out['query_results']));self.assertTrue(all(row['witness'] is None and row['strength']=='none' for row in out['query_results']));self.assertEqual(11,len(out['pending_gate_ids']))
    def test_domain_budget_cannot_silently_restrict_required_carrier(self):
        out=self.run_search(budgets={'max_domain_cardinality':1});self.assertEqual('malformed',out['status']);self.assertEqual(0,out['counts']['visited'])
    def test_real_cancellation_before_and_during_search(self):
        out=self.run_search(cancelled=lambda:True);self.assertEqual('cancelled',out['status']);self.assertEqual(0,out['counts']['visited']);self.assertEqual('unresolved-no-evidence-emitted',out['required_denominator_status'])
        calls=[0]
        def cancel():calls[0]+=1;return calls[0]>120
        out=self.run_search(cancelled=cancel,mode='exhaustive');self.assertEqual('cancelled',out['status']);self.assertGreater(out['counts']['visited'],0);self.assertEqual(11,len(out['query_results']));self.assertFalse(out['exhaustion_complete']);self.assertEqual('verified-at-final-read',out['source_runtime_currentness'])
    def test_real_deadline_is_not_a_canned_result(self):
        out=self.run_search(budgets={'timeout_seconds':0.000000001});self.assertEqual('timeout',out['status']);self.assertFalse(out['exhaustion_complete']);self.assertEqual(0,out['counts']['visited'])
    def test_input_changed_at_final_read_invalidates_all_found_witnesses(self):
        prepared=copy.deepcopy(self.prepared);key=next(iter(prepared['captured']));prepared['captured'][key]+=b'\n'
        with patch.object(v,'prepare',return_value=prepared):out=v.search(stop=3,mode='exhaustive')
        self.assertEqual('unresolved-input-or-binding',out['status']);self.assertFalse(out['exhaustion_complete']);self.assertTrue(all(row['witness'] is None for row in out['query_results']))
    def test_runtime_change_during_cancellation_invalidates_partial_results(self):
        with patch.object(v,'prepare',return_value=self.prepared),patch.object(v,'verify_bindings',side_effect=v.PilotFault('runtime-or-checker-changed-during-search')):
            calls=[0]
            def cancel():calls[0]+=1;return calls[0]>120
            out=v.search(cancelled=cancel)
        self.assertEqual('unresolved-input-or-binding',out['status']);self.assertTrue(all(row['witness'] is None for row in out['query_results']))
    def test_malformed_and_unsupported_requests_never_escape_or_emit_truth(self):
        for kwargs in [{'constraints':[[]]},{'constraints':[True]},{'constraints':['invented']},{'constraints':['no-right','no-right']},{'mode':[]},{'start':True},{'start':float('nan')},{'stop':8641},{'constraints':['\ud800']},{'budgets':{'timeout_seconds':31}}]:
            out=v.search(**kwargs);self.assertIn(out['status'],{'malformed','unsupported'});self.assertFalse(out['exhaustion_complete']);self.assertEqual(0,out['counts']['visited']);self.assertTrue(all(row['witness'] is None for row in out['query_results']));json.dumps(out,allow_nan=False).encode('utf-8')
    def test_nominal_mapping_substitution_rejected_even_with_valid_json(self):
        bundle={key:copy.deepcopy(self.prepared[key]) for key in ['config','subject','inputs','theory','required']};bundle['config']['symbol_mapping']['Right']=bundle['config']['symbol_mapping']['Duty']
        with self.assertRaises(v.PilotFault):v.typed_projection(v.ir.canonical(bundle).decode())
    def test_forged_required_set_omission_rejected(self):
        original=v.read_ref
        def read(ref,captured):
            value=original(ref,captured)
            if ref['path'].endswith('projection-required-set.json'):value['logical_manifest']['obligations'].pop()
            return value
        with patch.object(v,'read_ref',side_effect=read):out=v.search()
        self.assertEqual('unresolved-input-or-binding',out['status']);self.assertEqual('required-set-omitted-substituted-weakened-or-stale',out['diagnostics'][0]['code']);self.assertEqual(0,out['counts']['visited'])
    def test_rehashed_theory_cannot_turn_counterexample_into_axiom(self):
        original=v.read_ref;modified=copy.deepcopy(self.prepared['theory']);modified['statements'].append(v.o.p.quant('forall','Record',v.o.p.pred('Position')))
        def read(ref,captured):
            value=original(ref,captured)
            if ref['path'].endswith('projection-theory.json'):return modified
            if ref['path'].endswith('projection-required-set.json'):
                unit=v.UNIT
                return v.o.generate(modified,json.loads((unit/'projection-relations.json').read_text()),json.loads((unit/'projection-populations.json').read_text()),json.loads((unit/'projection-endpoints.json').read_text()),v.ROOT)
            return value
        with patch.object(v,'read_ref',side_effect=read):out=v.search()
        self.assertEqual('unsupported',out['status']);self.assertEqual('unsupported-record-projection-theory',out['diagnostics'][0]['code']);self.assertEqual(0,out['counts']['visited'])
    def test_timeout_inside_evaluation_preserves_required_denominator(self):
        real=v.record_values
        def expire(state,control):
            result=real(state,control);control.deadline=v.monotonic()-1;control.poll();return result
        with patch.object(v,'prepare',return_value=self.prepared),patch.object(v,'record_values',side_effect=expire):out=v.search()
        self.assertEqual('timeout',out['status']);self.assertEqual(11,len(out['query_results']));self.assertFalse(out['exhaustion_complete']);self.assertTrue(all(row['witness'] is None for row in out['query_results']))
    def test_faulty_record_and_projection_carrier_have_no_truth(self):
        world=v.point(78);world['records'][0]['authority_effect']='grant'
        with self.assertRaises(v.p.SemanticFault):v.assess(world,self.prepared,v.Control(v.f.load_limits()))
        world=v.point(78);world['records'].append(copy.deepcopy(world['records'][0]))
        with self.assertRaises(v.PilotFault):v.assess(world,self.prepared,v.Control(v.f.load_limits()))
    def test_projection_IR_missing_input_is_not_semantic_closure(self):
        bundle={key:copy.deepcopy(self.prepared[key]) for key in ['config','subject','inputs','theory','required']};bundle['inputs'].pop()
        with self.assertRaises((v.PilotFault,v.ir.IRFault)):v.typed_projection(v.ir.canonical(bundle).decode())


if __name__=='__main__':unittest.main()
