"""Candidate preparation guards; no live effects or fabricated owner response."""
import datetime
import unittest
from jsonschema.exceptions import ValidationError
from packet import *


class PreparationGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt=prerequisite();cls.original=original(binding(HERE/'packages/0001/preparation.json'))
    def setUp(self):self.value=copy.deepcopy(self.original)
    def check(self):return validate(self.value)
    def reject(self):
        with self.assertRaises((ValueError,ValidationError)):self.check()
    def select(self,kind):return next(m for m in self.value['members'] if m['member_class']==kind)
    def test_complete_independent_members(self):self.assertEqual(self.check()['members'],27)
    def test_ten_models_and_28_transitions(self):
        self.assertEqual(sum(len(m['selected_record']['transitions']) for m in self.value['members'] if m['member_class']=='workflow-transition-protocol'),28)
        self.assertEqual(self.check()['workflow_models'],10)
    def test_original_carrier_bytes_retained(self):
        for r in self.value['selected_carrier_postimages']:self.assertEqual(bound(r['source_binding']),bound(r['postimage_binding']))
        self.assertEqual(self.check()['carrier_postimages'],13)
    def test_all_named_execution_gaps_retained(self):self.assertEqual(self.value['model_execution_gaps_retained'],56);self.check()
    def test_six_case_qualified_collisions_retained(self):self.assertEqual(self.check()['collision_dispositions'],6)
    def test_Lesson_expired_at_actual_observed_time(self):
        m=self.select('scoped-Lesson-evidence');obs=original(m['scope']['expiry_observation_binding'])
        self.assertLess(datetime.datetime.fromisoformat(m['selected_record']['payload']['expires_at']),datetime.datetime.fromisoformat(obs['observed_at']))
        self.assertFalse(m['scope']['current_application_permission']);self.check()
    def test_machine_Agent_memory_sources_are_explicit(self):
        s=self.select('implementation-action-boundary')['scope'];self.assertTrue(s['machine_Agent_ephemeral'])
        self.assertEqual(s['short_memory_owner'],'Session');self.assertEqual(s['durable_memory_sources'],['Project State','Context View','Ontology View']);self.check()
    def test_actual_owner_response_refused(self):self.value['actual_owner_outcome']='admitted';self.reject()
    def test_actual_principal_inferred_from_fixture_refused(self):self.value['actual_answering_principal_ref']='principal:w02-isolated-fixture';self.reject()
    def test_claimed_current_owner_authority_refused(self):self.select('implementation-carrier')['current_owner_authority_verified']=True;self.reject()
    def test_member_admission_refused(self):self.select('implementation-carrier')['admission_posture']='admitted-current';self.reject()
    def test_member_outcome_refused(self):self.select('workflow-transition-protocol')['selected_outcome']='admitted';self.reject()
    def test_missing_member_refused(self):self.value['members'].pop();self.reject()
    def test_collapsed_member_identity_refused(self):self.value['members'][0]['member_ref']=self.value['members'][1]['member_ref'];self.reject()
    def test_widened_requested_effect_refused(self):self.select('implementation-action-boundary')['requested_effect']='Authorize every future action';self.reject()
    def test_omitted_exclusion_refused(self):self.select('scoped-Lesson-evidence')['exclusions'].remove('automatic Lesson promotion');self.reject()
    def test_omitted_invalidation_refused(self):self.select('implementation-carrier')['invalidation'].remove('target bytes changed');self.reject()
    def test_final_package_completeness_inferred_refused(self):self.value['complete_final_package']=True;self.reject()
    def test_local_action_permission_refused(self):self.select('implementation-action-boundary')['scope']['action_permission_included']=True;self.reject()
    def test_long_term_Agent_memory_refused(self):self.select('implementation-action-boundary')['scope']['short_memory_owner']='Agent';self.reject()
    def test_fixture_owner_as_final_owner_refused(self):self.select('implementation-carrier')['scope']['fixture_owner_is_final_owner']=True;self.reject()
    def test_carrier_operational_use_refused(self):self.select('implementation-carrier')['scope']['operational_use_authorized']=True;self.reject()
    def test_current_expired_Lesson_use_refused(self):self.select('scoped-Lesson-evidence')['scope']['current_application_permission']=True;self.reject()
    def test_automatic_Lesson_promotion_refused(self):self.value['lessons_promoted']=1;self.reject()
    def test_Lesson_expiry_rewrite_refused(self):self.select('scoped-Lesson-evidence')['scope']['expires_at']='2099-01-01T00:00:00+00:00';self.reject()
    def test_model_execution_inferred_refused(self):self.select('workflow-transition-protocol')['scope']['all_transitions_operationally_complete']=True;self.reject()
    def test_model_per_run_bindings_omitted_refused(self):self.select('workflow-transition-protocol')['scope']['per_run_bindings_required']=False;self.reject()
    def test_changed_model_postimage_refused(self):self.select('workflow-transition-protocol')['selected_record']['initial_state']='completed';self.reject()
    def test_wrong_source_selector_refused(self):self.select('workflow-transition-protocol')['scope']['source_selection']['json_pointer']='/workflows/999';self.reject()
    def test_execution_gap_omission_refused(self):self.value['model_coverage'][0]['remaining_per_run_obligations'].pop();self.reject()
    def test_execution_gap_replacement_refused(self):self.value['model_coverage'][0]['remaining_per_run_obligations'][0]['gap_id']='invented';self.reject()
    def test_changed_target_binding_refused(self):self.select('implementation-carrier')['targets'][0]['sha256']='0'*64;self.reject()
    def test_path_escape_refused(self):self.select('implementation-carrier')['targets'][0]['path']='../outside.json';self.reject()
    def test_source_context_pin_change_refused(self):self.value['source_context_binding']['sha256']='0'*64;self.reject()
    def test_upstream_proof_change_refused(self):self.value['upstream_workflow_proof_binding']['sha256']='0'*64;self.reject()
    def test_collision_omission_refused(self):self.value['candidate_collision_dispositions'].pop();self.reject()
    def test_collision_merge_refused(self):self.value['candidate_collision_dispositions'][0]['global_merge_allowed']=True;self.reject()
    def test_same_digest_for_distinct_postimages_refused(self):
        c=self.value['candidate_collision_dispositions'][0];c['witnesses'][0]['binding']=copy.deepcopy(c['witnesses'][1]['binding']);self.reject()
    def test_canonical_effect_inferred_refused(self):self.value['canonical_effects_applied']=1;self.reject()
    def test_service_activation_inferred_refused(self):self.value['runtime_activation']=True;self.reject()
    def test_human_pilot_inferred_refused(self):self.value['human_pilot']=True;self.reject()
    def test_unknown_packet_field_refused(self):self.value['blanket_approval']=True;self.reject()


if __name__=='__main__':unittest.main()
