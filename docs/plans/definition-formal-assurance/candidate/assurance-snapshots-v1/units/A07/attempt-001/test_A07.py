"""Source-backed pilot types, interpretation alternatives and exact frame controls."""
import copy
import json
import sys
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[3]
UNIT=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/units/A07';sys.path[:0]=[str(UNIT),str(HERE)]
import pilot_spec as p
import examples as x
sys.path.insert(0,str(UNIT.parent/'A04'))
import correspondence as cc


class RecordMeaningControls(unittest.TestCase):
    def fault(self,code,fn):
        with self.assertRaises(p.SemanticFault) as caught:fn()
        self.assertEqual(code,caught.exception.code)
    def test_complete_ungranted_claim_remains_representable(self):
        state=x.right(x.base_state('complete'),grant=False);out=p.inspect_state(state);self.assertEqual(['claim:local-use'],out['explicit_claims']);self.assertEqual(['claim:local-use'],out['unbacked_claims']);self.assertEqual([],out['qualified_right_grants']);self.assertEqual([],out['usable_right_claims'])
    def test_grant_is_independent_of_assertion_presence(self):
        state=x.right(x.base_state('complete'),claim=False);out=p.inspect_state(state);self.assertEqual(['grant:local-use'],out['qualified_right_grants']);self.assertEqual([],out['authority_right_claims']);self.assertEqual([],out['claims'] if 'claims' in out else out['explicit_claims']);self.assertFalse(out['semantic_ready'])
    def test_obligation_is_a_position_without_permission(self):
        state=x.responsibility(x.base_state('complete'));out=p.inspect_state(state);self.assertEqual(['duty:route-review'],out['assigned_responsibilities']);self.assertEqual(['claim:duty'],out['responsibility_claims']);self.assertEqual([],out['qualified_right_grants']);self.assertEqual([],out['usable_right_claims']);self.assertEqual('not-assessed',out['responsibility_fulfillment']);self.assertEqual('responsibility',out['authority_positions'][0]['kind'])
    def test_duty_can_exist_without_any_claim(self):
        out=p.inspect_state(x.responsibility(x.base_state('complete'),claim=False));self.assertEqual(['duty:route-review'],out['assigned_responsibilities']);self.assertEqual([],out['responsibility_claims']);self.assertEqual([],out['qualified_right_grants'])
    def test_right_and_duty_can_coexist_without_merging_tags(self):
        state=x.responsibility(x.right(x.base_state('complete')));out=p.inspect_state(state);self.assertEqual({'right','responsibility'},{row['kind'] for row in out['authority_positions']});self.assertEqual(1,len(out['qualified_right_grants']));self.assertEqual(1,len(out['assigned_responsibilities']))
    def test_known_empty_unknown_deferred_are_distinct(self):
        outputs=[p.inspect_state(x.base_state(mode)) for mode in ['empty','unknown','deferred']];self.assertEqual(['known:empty','unknown:unavailable','deferred:unavailable'],[row['provenance_state'] for row in outputs]);self.assertTrue(all(not row['traceable_for_selected_scope'] for row in outputs))
    def test_unknown_cannot_be_encoded_as_empty_list(self):
        state=x.base_state();state['provenance']['steps']=[];self.fault('unknown-provenance-is-not-empty-trail',lambda:p.inspect_state(state))
    def test_empty_sequence_is_valid_but_local_use_profile_requires_trace(self):
        state=x.right(x.base_state('empty'));self.assertEqual(['claim:local-use'],p.inspect_state(state,'none')['usable_right_claims']);out=p.inspect_state(state,'admission-use-requires-trace');self.assertEqual([],out['usable_right_claims']);self.assertEqual(['grant:local-use'],out['qualified_right_grants'])
    def test_unknown_origin_does_not_remove_independent_grant(self):
        state=x.right(x.base_state());out=p.inspect_state(state,'admission-use-requires-trace');self.assertEqual(['grant:local-use'],out['qualified_right_grants']);self.assertEqual(['claim:local-use'],out['authority_right_claims']);self.assertEqual([],out['usable_right_claims'])
    def test_trace_record_never_grants_rights(self):
        for mode in ['complete','incomplete','source-local']:
            out=p.inspect_state(x.base_state(mode),'admission-use-requires-trace');self.assertTrue(out['traceable_for_selected_scope']);self.assertEqual([],out['qualified_right_grants'])
    def test_incomplete_trace_requires_explicit_gap_residue_and_owner_route(self):
        state=x.base_state('incomplete');state['provenance']['steps'][1].pop('owner_route');self.fault('malformed-provenance-step',lambda:p.inspect_state(state))
        state=x.base_state('incomplete');state['provenance']['steps'][1]['residue_ref']='';self.fault('explicit-nonempty-identifier-required',lambda:p.inspect_state(state))
    def test_source_local_scope_is_retained_not_promoted(self):
        state=x.right(x.base_state('source-local'));self.assertEqual(['claim:local-use'],p.inspect_state(state,'admission-use-requires-trace')['usable_right_claims']);state['provenance']['scope_ref']='scope:other-source';state['posture']['provenance']['scope_ref']='scope:other-source';out=p.inspect_state(state,'admission-use-requires-trace');self.assertFalse(out['traceable_for_selected_scope']);self.assertEqual([],out['usable_right_claims']);self.assertEqual(['grant:local-use'],out['qualified_right_grants'])
    def test_scope_surface_object_principal_operation_and_effect_do_not_transfer(self):
        for key in p.QUERY_FIELDS:
            state=x.right(x.base_state('complete'));state['claims'][0][key]='other:'+key;state['grants'][0][key]='other:'+key;out=p.inspect_state(state);self.assertEqual([],out['qualified_right_grants']);self.assertEqual(['claim:local-use'],out['unbacked_claims'])
    def test_shared_principal_does_not_merge_owner_boundaries(self):
        state=x.right(x.base_state('complete'));state['role_bindings'].append({'binding_id':'binding:context-owner','principal':state['context']['principal'],'owner_role':'role:context-owner'});state['grants'][0]['role_binding_ref']='binding:context-owner';out=p.inspect_state(state);self.assertEqual([],out['qualified_right_grants'])
    def test_excluded_effect_overrides_allowed_effect(self):
        state=x.right(x.base_state('complete'));state['boundaries'][0]['excluded_effects']=[state['context']['effect']];self.assertEqual([],p.inspect_state(state)['qualified_right_grants'])
    def test_field_presence_does_not_establish_owner_role_or_boundary(self):
        for key in ['boundary_ref','role_binding_ref']:
            state=x.right(x.base_state('complete'));state['grants'][0][key]='missing:binding';self.assertEqual([],p.inspect_state(state)['qualified_right_grants'])
    def test_missing_claim_fields_are_candidate_assertion_information(self):
        state=x.right(x.base_state('complete'));state['claims'][0]['scope']=None;out=p.inspect_state(state);self.assertEqual([],out['explicit_claims']);self.assertEqual(['claim:local-use'],out['unbacked_claims']);self.assertEqual(['grant:local-use'],out['qualified_right_grants'])
    def test_duty_role_binding_cannot_supply_itself(self):
        state=x.responsibility(x.base_state('complete'));state['responsibilities'][0]['role_binding_ref']='missing:binding';out=p.inspect_state(state);self.assertEqual([],out['assigned_responsibilities']);self.assertEqual(['claim:duty'],out['unbacked_claims'])
    def test_closed_state_shape_and_duplicate_assignment_identity(self):
        state=x.right(x.base_state('complete'));state['grants'].append(copy.deepcopy(state['grants'][0]));self.fault('duplicate-record-identity',lambda:p.inspect_state(state))
        state=x.base_state();state['permission']=True;self.fault('malformed-state',lambda:p.inspect_state(state))
    def test_all_information_states_are_explicit_and_bool_is_not_value(self):
        state=x.base_state();state['posture']['evidence']=x.info('high',state='source-local',scope='scope:source');self.assertTrue(p.validate_state(state));state['posture']['evidence']=x.info('0',state='unknown');self.fault('unknown-or-deferred-is-not-known-value',lambda:p.inspect_state(state))
        state=x.base_state();state['posture']['evidence']=x.info(True);self.fault('explicit-nonempty-identifier-required',lambda:p.inspect_state(state))
    def test_malformed_enum_containers_nonfinite_and_unicode_have_no_raw_escape(self):
        for value in [[],{},True,None]:
            state=x.base_state();state['posture']['status']['state']=value;self.fault('unsupported-information-state',lambda:p.inspect_state(state))
            state=x.base_state();state['provenance']['knowledge']=value;self.fault('unsupported-provenance-knowledge',lambda:p.inspect_state(state))
        for value in [float('nan'),'\ud800']:
            state=x.base_state();state['revision']=value
            with self.assertRaises(p.c.InputError):p.inspect_state(state)


class MoveControls(unittest.TestCase):
    def setUp(self):
        self.before=x.right(x.base_state());self.after=copy.deepcopy(self.before);self.after['revision']='state:after';x.set_provenance(self.after,'complete')
    def fault(self,code,move):
        with self.assertRaises(p.SemanticFault) as caught:p.check_move(move,self.before,self.after)
        self.assertEqual(code,caught.exception.code)
    def test_provenance_only_move_bound_to_actual_snapshots_and_grants(self):
        out=p.check_move(x.move(self.before,self.after),self.before,self.after);self.assertEqual(['provenance'],out['changed_axes']);self.assertEqual(0,out['grant_changes']);self.assertFalse(out['semantic_ready'])
    def test_subject_context_and_snapshot_digest_mismatch_rejected(self):
        for key,value,code in [('subject_id','artifact:other','move-subject-mismatch'),('context',{},'move-query-context-mismatch')]:
            move=x.move(self.before,self.after);move[key]=value;self.fault(code,move)
        move=x.move(self.before,self.after);move['after_ref']['sha256']='0'*64;self.fault('move-record-binding-mismatch',move)
    def test_reusing_detached_axis_vectors_cannot_hide_changed_records(self):
        move=x.move(self.before,self.after);self.after['claims'][0]['basis']='decision:other';self.fault('move-record-binding-mismatch',move)
        move=x.move(self.before,self.after);self.fault('silent-frame-change-or-unperformed-intention',move)
    def test_silent_status_change_rejected_explicit_byte_bound_coupling_passes(self):
        self.after['posture']['status']=x.info('reviewed');move=x.move(self.before,self.after);self.fault('silent-frame-change-or-unperformed-intention',move)
        move=x.move(self.before,self.after,recorded=['status']);self.assertEqual(['status'],p.check_move(move,self.before,self.after)['recorded_axes']);move['recorded_changes'][0]['after_sha256']='0'*64;self.fault('recorded-axis-binding-mismatch',move)
    def test_unrecorded_grant_change_rejected_even_when_axis_intention_is_explicit(self):
        self.after['grants'][0]['basis']='decision:new-act';move=x.move(self.before,self.after,intended=['provenance','grants']);move['grant_changes']=[];self.fault('unrecorded-assignment-change',move)
        move=x.move(self.before,self.after,intended=['provenance','grants']);self.assertEqual(1,p.check_move(move,self.before,self.after)['grant_changes'])
    def test_grant_addition_removal_and_revision_have_exact_delta_records(self):
        for grants in [[],self.after['grants']+[dict(self.after['grants'][0],grant_id='grant:second')],[dict(self.after['grants'][0],basis='decision:revised')]]:
            self.after['grants']=copy.deepcopy(grants);move=x.move(self.before,self.after,intended=['provenance','grants']);out=p.check_move(move,self.before,self.after);self.assertGreater(out['grant_changes'],0);move['grant_changes'][0]['after_sha256']='0'*64;self.fault('assignment-change-record-mismatch',move)
    def test_unchanged_assignment_cannot_be_declared_as_changed(self):
        move=x.move(self.before,self.after);move['grant_changes']=[{'grant_id':self.before['grants'][0]['grant_id'],'before_sha256':p.ir.digest(self.before['grants'][0]),'after_sha256':p.ir.digest(self.before['grants'][0]),'basis_ref':'decision:fake-change'}];self.fault('assignment-change-record-mismatch',move)
    def test_unrecorded_duty_assignment_rejected_without_creating_permission(self):
        x.responsibility(self.after,claim=False);move=x.move(self.before,self.after,intended=['provenance','responsibilities']);move['responsibility_changes']=[];self.fault('unrecorded-assignment-change',move)
        move=x.move(self.before,self.after,intended=['provenance','responsibilities']);self.assertEqual(1,p.check_move(move,self.before,self.after)['responsibility_changes']);self.assertEqual(1,len(p.inspect_state(self.after)['qualified_right_grants']))
    def test_boundary_or_role_changes_cannot_be_authorized_by_move_metadata(self):
        self.after['boundaries'][0]['allowed_effects'].append('effect:publish');move=x.move(self.before,self.after,intended=['provenance','boundaries']);self.fault('authority-boundary-or-principal-binding-change-outside-pilot',move)
    def test_unperformed_intent_and_unchanged_recorded_axis_rejected(self):
        move=x.move(self.before,self.after,intended=['status']);self.fault('silent-frame-change-or-unperformed-intention',move)
        move=x.move(self.before,self.after,recorded=['status']);self.fault('recorded-axis-not-changed-or-duplicated',move)
    def test_move_has_no_authority_effect_even_when_grant_delta_is_recorded(self):
        self.after['grants']=[];move=x.move(self.before,self.after,intended=['provenance','grants']);out=p.check_move(move,self.before,self.after);self.assertEqual('none',out['authority_effect']);self.assertEqual([],p.inspect_state(self.after)['qualified_right_grants'])


class SourceAndWorkedControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=json.loads((UNIT.parent.parent/'pilot-v2/interpretation.json').read_text());cls.snapshot=json.loads((UNIT.parent.parent/'current-snapshot.json').read_text())
    def test_seven_exact_current_sources_and_predecessor_preserved(self):
        out=p.bind_sources(self.spec);self.assertEqual(7,out['sources']);self.assertEqual(201,out['source_capture_files']);ref=self.spec['predecessor_ref'];self.assertEqual(ref['sha256'],p.r.digest((ROOT/ref['path']).read_bytes()))
    def test_source_omission_or_digest_substitution_rejected(self):
        for change,code in [(lambda spec:spec['sources'].pop(),'pilot-source-denominator-mismatch'),(lambda spec:spec['sources'][0].update(sha256='0'*64),'pilot-source-substitution')]:
            spec=copy.deepcopy(self.spec);change(spec)
            with self.assertRaises(p.SemanticFault) as caught:p.bind_sources(spec)
            self.assertEqual(code,caught.exception.code)
    def test_all_source_rules_bind_exact_current_spans(self):
        documents={row['definition_id']:json.loads((ROOT/row['path']).read_text()) for row in self.spec['sources']}
        for rule in self.spec['source_rules']:
            texts=dict(cc.string_leaves(documents[rule['source']['definition_id']]))
            for span in rule['source_spans']:
                self.assertEqual(span['excerpt'],texts[span['selector']][span['start_character']:span['end_character']]);self.assertEqual(span['excerpt_sha256'],p.r.digest(span['excerpt'].encode()))
    def test_166_source_units_accounted_without_whole_definition_fidelity(self):
        count=0
        for entry in self.spec['source_packets']:
            packet=json.loads((ROOT/entry['packet_ref']['path']).read_text());required=[row['finding_id'] for row in packet['source_precedence']['conflicts']];out=cc.check(packet,self.snapshot,required_conflicts=required);self.assertEqual('correspondence-pending',out['status']);self.assertTrue(out['character_accounting_complete']);self.assertFalse(out['semantic_ready']);count+=out['source_units'];self.assertEqual('pending',packet['interpretation']['source_fidelity'])
        self.assertEqual(166,count);self.assertFalse(self.spec['semantic_ready'])
    def test_responsibility_and_empty_provenance_choices_remain_owner_pending(self):
        findings={row['finding_id']:row for row in self.spec['interpretation_alternatives']};self.assertEqual('owner-review-pending',findings['FID-RESP-001']['disposition']);self.assertEqual('owner-review-pending',findings['FID-PROV-EMPTY-001']['disposition']);self.assertEqual('none',self.spec['selected_coupling']['global_implication']);self.assertEqual('unresolved',self.spec['dependencies']['semantic_closure'])
    def test_retained_example_records_and_moves_replay_exactly(self):
        ref=self.spec['worked_examples_ref'];self.assertEqual(ref['sha256'],p.r.digest((ROOT/ref['path']).read_bytes()));worked=json.loads((ROOT/ref['path']).read_text());self.assertEqual(11,len(worked['states']));self.assertEqual(1,len(worked['moves']))
        for row in worked['states']:self.assertTrue(p.r.same_json(row['actual'],p.inspect_state(row['state'],'admission-use-requires-trace')))
        for row in worked['moves']:self.assertTrue(p.r.same_json(row['actual'],p.check_move(row['move'],row['before'],row['after'])))


if __name__=='__main__':unittest.main()
