"""Independent semantics, malformed evidence and exact finite coverage controls."""
import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[5];UNIT=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/units/A09';sys.path.insert(0,str(UNIT));import replay as a


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prepared=a.prepare();cls.native=json.loads((a.BASE/'units/A08/positive-search.json').read_bytes());cls.first=a.audit(stop=3,prepared=cls.prepared);cls.second=a.audit(start=3,stop=6,prepared=cls.prepared)
    def control(self):return a.Control(a.f.load_limits())
    def fault(self,code,fn):
        with self.assertRaises(a.ReplayFault) as caught:fn()
        self.assertEqual(code,caught.exception.code)
    def test_live_exact_selection_regenerates_eleven_queries(self):
        self.assertEqual(11,len(self.prepared['Q']));self.assertEqual(11,len(self.prepared['required']['administrative_and_semantic_gates']));self.assertEqual(7,len(self.prepared['spec']['sources']));a.verify_bindings(self.prepared)
    def test_independent_constructor_boundary_coordinates(self):
        for rank in [0,1,2,78,119,120,239,240,1439,1440,4321,8639]:self.assertEqual(a.w.world(rank),a.provider.point(rank))
        self.assertEqual((0,0,0,0,0,0,0,0),a.w.coordinates(0));self.assertEqual((5,5,1,1,1,1,4,2),a.w.coordinates(8639))
    def test_reference_predicates_do_not_call_A07_or_A08_evaluators(self):
        with patch.object(a.types,'inspect_state',side_effect=AssertionError()),patch.object(a.provider,'record_values',side_effect=AssertionError()):
            row=a.record(a.w.state(0,'complete',False,True,'responsibility'),self.control());self.assertTrue(row['Duty']);self.assertFalse(row['Right']);self.assertTrue(row['Position'])
    def test_reference_frame_does_not_call_A07_or_A08_move_checkers(self):
        with patch.object(a.types,'check_move',side_effect=AssertionError()),patch.object(a.provider,'transition_holds',side_effect=AssertionError()):
            world=a.w.world(0);self.assertTrue(a.frame(world['transition'],world['records'],self.control()))
    def test_reference_static_truth_does_not_call_C02_evaluator(self):
        with patch.object(a.provider.s.Evaluator,'holds',side_effect=AssertionError()):
            actual=a.assess(a.w.world(78),self.prepared,self.control());self.assertTrue(actual['theory']);self.assertTrue(actual['populations']);self.assertTrue(all(actual['queries'].values()))
    def test_ungranted_claim_and_unclaimed_grant(self):
        row=a.record(a.w.state(0,'complete',False,False,'right'),self.control());self.assertEqual(['claim:right:0'],row['unbacked_claims']);self.assertFalse(row['Right'])
        row=a.record(a.w.state(0,'unknown',True,False,'none'),self.control());self.assertTrue(row['Right']);self.assertFalse(row['Traceable']);self.assertEqual(['grant:0'],row['unclaimed_right_grants'])
    def test_incomplete_assertion_does_not_grant_support(self):
        row=a.record(a.w.state(0,'complete',True,False,'incomplete-right'),self.control());self.assertTrue(row['Right']);self.assertFalse(row['BackedRight']);self.assertEqual(['claim:right:0'],row['incomplete_claims'])
    def test_right_and_duty_overlap_preserves_tags(self):
        row=a.record(a.w.state(0,'complete',True,True,'both'),self.control());self.assertTrue(row['Right']);self.assertTrue(row['Duty']);self.assertEqual(['grant:0'],row['right_grants']);self.assertEqual(['duty:0'],row['assigned_duties'])
    def test_source_local_scope_is_preserved(self):
        state=a.w.state(0,'source-local',True,False,'right');state['provenance']['scope_ref']='scope:elsewhere';state['posture']['provenance']['scope_ref']='scope:elsewhere';row=a.record(state,self.control());self.assertFalse(row['Traceable']);self.assertTrue(row['Right'])
    def test_lineage_information_states_and_gaps(self):
        for mode,truth in [('unknown',False),('deferred',False),('empty',False),('complete',True),('incomplete',True),('source-local',True)]:self.assertEqual(truth,a.record(a.w.state(0,mode,False,False,'none'),self.control())['Traceable'])
        state=a.w.state(0,'incomplete',False,False,'none');state['provenance']['steps'][1].pop('owner_route')
        with self.assertRaises(a.types.SemanticFault):a.record(state,self.control())
    def test_exclusion_wrong_role_scope_and_assignment_kind(self):
        state=a.w.state(0,'complete',True,True,'both');state['boundaries'][0]['excluded_effects']=[state['context']['effect']];row=a.record(state,self.control());self.assertFalse(row['Right']);self.assertTrue(row['Duty'])
        state=a.w.state(0,'complete',True,False,'right');state['claims'][0]['assignment_ref']='duty:0';self.assertFalse(a.record(state,self.control())['BackedRight'])
    def test_silent_status_unrelated_subject_and_hash_mismatch_fail_frame(self):
        for rank,truth in [(0,True),(1,False),(2,True)]:
            world=a.w.world(rank);self.assertEqual(truth,a.frame(world['transition'],world['records'],self.control()))
        world=a.w.world(0);world['transition']['move']['subject_id']=a.w.SUBJECTS[1];self.assertFalse(a.frame(world['transition'],world['records'],self.control()))
        world=a.w.world(0);world['transition']['move']['after_ref']['sha256']='0'*64;self.assertFalse(a.frame(world['transition'],world['records'],self.control()))
    def test_assignment_delta_complete_denominator_and_basis(self):
        world=a.w.world(0);after=world['transition']['after'];after['grants']=a.w.state(0,'complete',True,False,'none')['grants'];world['records'][0]=copy.deepcopy(after);m=world['transition']['move'];m['after_ref']['sha256']=a.ir.digest(after);m['intended_axes'].append('grants');self.assertFalse(a.frame(world['transition'],world['records'],self.control()))
        m['grant_changes']=[{'grant_id':'grant:0','before_sha256':None,'after_sha256':a.ir.digest(after['grants'][0]),'basis_ref':'decision:explicit'}];self.assertTrue(a.frame(world['transition'],world['records'],self.control()))
        m['grant_changes'][0]['basis_ref']=''
        with self.assertRaises(a.types.SemanticFault):a.frame(world['transition'],world['records'],self.control())
    def test_malformed_move_id_not_accepted_as_record_truth(self):
        world=a.w.world(0);world['transition']['move']['move_id']=None
        with self.assertRaises(a.types.SemanticFault):a.frame(world['transition'],world['records'],self.control())
    def test_native_positive_witnesses_all_independently_replay(self):
        checked=a.verify_native(self.native,{},self.prepared);self.assertEqual(11,len(checked['queries']));self.assertTrue(all(row['status']=='independently-checked-record-model-witness' for row in checked['queries']));self.assertFalse(checked['semantic_ready'])
    def test_substituted_model_rank_is_rejected(self):
        value=copy.deepcopy(self.native);value['query_results'][0]['witness']['rank']=79;self.fault('native-witness-rank-or-byte-substitution',lambda:a.verify_native(value,{},self.prepared))
    def test_rehashed_projection_model_cannot_change_truth(self):
        value=copy.deepcopy(self.native);wit=value['query_results'][0]['witness'];key=self.prepared['mapping']['Right'];wit['projection_model']['predicates'][key]=[];wit['projection_model_sha256']=a.ir.digest(wit['projection_model']);self.fault('native-projection-model-substitution',lambda:a.verify_native(value,{},self.prepared))
    def test_witness_cannot_satisfy_a_different_query(self):
        value=copy.deepcopy(self.native);cons=next(row for row in value['query_results'] if row['obligation_id']=='query:consistency');value['query_results'][0]['witness']=copy.deepcopy(cons['witness']);self.fault('native-witness-fails-independent-query',lambda:a.verify_native(value,{},self.prepared))
    def test_native_omitted_query_and_forged_strength_fail(self):
        value=copy.deepcopy(self.native);value['query_results'].pop();self.fault('native-required-denominator-substitution',lambda:a.verify_native(value,{},self.prepared))
        value=copy.deepcopy(self.native);value['query_results'][0]['strength']='kernel-proof';self.fault('native-witness-strength-substitution',lambda:a.verify_native(value,{},self.prepared))
    def test_native_input_request_and_runtime_epoch_not_substitutable(self):
        value=copy.deepcopy(self.native);value['input_bindings']['implementation_sha256']='0'*64;self.fault('native-input-binding-substitution',lambda:a.verify_native(value,{},self.prepared))
        self.fault('native-input-binding-substitution',lambda:a.verify_native(self.native,{'constraints':['no-position']},self.prepared))
    def test_small_range_independently_checks_bad_frames(self):
        self.assertTrue(self.first['exhaustion_complete']);self.assertEqual(3,self.first['counts']['visited']);self.assertEqual(2,self.first['counts']['theory_models']);self.assertEqual(0,self.first['counts']['joint_models'])
    def test_injected_wrong_predicate_and_wrong_enumerator_fail(self):
        original=a.provider.record_values
        def wrong(state,control):row=original(state,control);row['Right']=not row['Right'];return row
        with patch.object(a.provider,'record_values',side_effect=wrong):out=a.audit(stop=3,prepared=self.prepared)
        self.assertEqual('verification-failed',out['status']);self.assertEqual('record-or-logical-denotation-disagreement',out['diagnostics'][0]['code']);self.assertFalse(out['exhaustion_complete'])
        with patch.object(a.provider,'point',return_value=a.w.world(1)):out=a.audit(stop=3,prepared=self.prepared)
        self.assertEqual('configuration-enumeration-disagreement',out['diagnostics'][0]['code'])
    def test_configuration_step_and_tiny_deadline_limits_never_prove_absence(self):
        for budgets,status in [({'max_interpretations':1},'resource-limit'),({'max_evaluation_steps':1},'resource-limit'),({'timeout_seconds':0.000000001},'timeout')]:
            out=a.audit(stop=3,prepared=self.prepared,budgets=budgets);self.assertEqual(status,out['status']);self.assertFalse(out['exhaustion_complete'])
    def test_real_cancellation_before_and_during_audit(self):
        out=a.audit(stop=3,prepared=self.prepared,cancelled=lambda:True);self.assertEqual('cancelled',out['status']);self.assertEqual(0,out['counts']['visited'])
        calls=[0]
        def cancel():calls[0]+=1;return calls[0]>150
        out=a.audit(stop=6,prepared=self.prepared,cancelled=cancel);self.assertEqual('cancelled',out['status']);self.assertFalse(out['exhaustion_complete']);self.assertEqual(11,len(out['query_counts']))
    def test_real_timeout_with_required_queries_already_selected(self):
        real=a.record
        def expire(state,control):row=real(state,control);control.deadline=a.monotonic()-1;control.poll();return row
        with patch.object(a,'record',side_effect=expire):out=a.audit(stop=3,prepared=self.prepared)
        self.assertEqual('timeout',out['status']);self.assertEqual(11,len(out['query_counts']));self.assertFalse(out['exhaustion_complete'])
    def test_final_binding_change_clears_query_counts(self):
        with patch.object(a,'verify_bindings',side_effect=a.ReplayFault('input-changed-during-replay')):out=a.audit(stop=3,prepared=self.prepared)
        self.assertEqual('unresolved-input-or-binding',out['status']);self.assertFalse(out['exhaustion_complete']);self.assertTrue(all(row['true_models'] is None for row in out['query_counts'].values()))
    def test_malformed_nonfinite_unicode_and_unknown_requests_do_not_escape(self):
        for kwargs in [{'constraints':[{}]},{'constraints':['unknown']},{'constraints':['no-right','no-right']},{'start':True},{'stop':float('nan')},{'start':'\ud800'},{'budgets':{'max_evaluation_steps':100001}}]:
            out=a.audit(prepared=self.prepared,**kwargs);self.assertIn(out['status'],['unsupported','verification-failed']);self.assertFalse(out['exhaustion_complete']);json.dumps(out,allow_nan=False).encode('utf-8')
    def test_missing_whole_translation_and_dependency_closure_are_explicit(self):
        original=a.load_ref
        for field,code in [('require_whole_translation','missing-whole-definition-translation'),('require_semantic_closure','missing-semantic-dependency-closure')]:
            def changed(ref,captured,parse=True,field=field):
                value=original(ref,captured,parse)
                if ref==a.SELECTED:value[field]=True
                return value
            with patch.object(a,'load_ref',side_effect=changed):self.fault(code,lambda:a.prepare())
    def test_missing_projection_input_is_not_silently_skipped(self):
        original=a.load_ref
        def changed(ref,captured,parse=True):
            value=original(ref,captured,parse)
            if parse and ref['path'].endswith('/A08/projection.json'):value['input_ir_refs'].pop()
            return value
        with patch.object(a,'load_ref',side_effect=changed):self.fault('missing-selected-projection-input',lambda:a.prepare())
    def test_stale_live_source_in_isolated_copy_is_rejected(self):
        spec=self.prepared['spec'];snapshot=json.loads((a.ROOT/spec['snapshot_ref']['path']).read_bytes())
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for row in snapshot['captured_files']+[spec['snapshot_ref']]:
                target=root/row['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a.ROOT/row['path'],target)
            a.types.bind_sources(spec,root);path=root/spec['sources'][0]['path'];path.write_bytes(path.read_bytes()+b'\n')
            with self.assertRaises(a.r.CaptureFault):a.types.bind_sources(spec,root)
    def test_unsupported_profile_and_stale_selected_bytes_fail_before_truth(self):
        self.fault('stale-selected-input',lambda:a.prepare({**a.SELECTED,'sha256':'0'*64}))
        original=a.load_ref
        def changed(ref,captured,parse=True):
            value=original(ref,captured,parse)
            if ref==a.SELECTED:value['selected_scope']='scope:unsupported'
            return value
        with patch.object(a,'load_ref',side_effect=changed):self.fault('unsupported-record-verification-profile',lambda:a.prepare())
    def test_output_limit_is_bounded_and_preserves_selected_query_ids(self):
        out=a.audit(stop=3,prepared=self.prepared,budgets={'max_output_bytes':2048});self.assertLessEqual(len(a.ir.canonical(out)),2048);self.assertEqual('resource-limit',out['status']);self.assertFalse(out['exhaustion_complete']);self.assertEqual(11,len(out['query_counts']))
    def test_gap_free_merge_preserves_exact_scope(self):
        merged=a.merge([self.second,self.first],stop=6,prepared=self.prepared);self.assertTrue(merged['exhaustion_complete']);self.assertEqual(6,merged['counts']['visited']);self.assertIsNone(merged['unbounded_conclusion'])
    def test_merge_rejects_gap_overlap_missing_tail_and_incomplete(self):
        self.fault('range-gap-overlap-or-outside-scope',lambda:a.merge([self.first,self.first],stop=6,prepared=self.prepared));self.fault('range-cover-incomplete',lambda:a.merge([self.first],stop=6,prepared=self.prepared));self.fault('range-gap-overlap-or-outside-scope',lambda:a.merge([self.second],stop=6,prepared=self.prepared))
        row=copy.deepcopy(self.second);row['exhaustion_complete']=False;self.fault('incomplete-or-invalid-range-evidence',lambda:a.merge([self.first,row],stop=6,prepared=self.prepared))
    def test_merge_rejects_different_runtime_policy_and_query_denominator(self):
        row=copy.deepcopy(self.second);row['input_epoch']['runtime_sha256']='0'*64;self.fault('mixed-range-input-epochs',lambda:a.merge([self.first,row],stop=6,prepared=self.prepared))
        row=copy.deepcopy(self.second);row['query_counts'].pop(next(iter(row['query_counts'])));self.fault('range-query-denominator-substitution',lambda:a.merge([self.first,row],stop=6,prepared=self.prepared))
    def test_merge_rejects_invalid_counts_and_rank_witness(self):
        row=copy.deepcopy(self.second);row['counts']['visited']=0;self.fault('range-count-substitution',lambda:a.merge([self.first,row],stop=6,prepared=self.prepared))
        row=copy.deepcopy(self.second);row['query_counts']['query:consistency']['first_rank']=0;self.fault('range-first-witness-substitution',lambda:a.merge([self.first,row],stop=6,prepared=self.prepared))


if __name__=='__main__':unittest.main()
