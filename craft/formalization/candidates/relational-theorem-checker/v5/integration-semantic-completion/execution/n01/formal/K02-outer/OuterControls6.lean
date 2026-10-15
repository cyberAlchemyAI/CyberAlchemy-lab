import OuterFixture

set_option autoImplicit false

namespace RelationalSuccessor.CandidateIntentRecordShape.Examples
open RelationalSuccessor.CandidateIntentRecordShape

theorem owner_label_alone_is_shape_valid : recordShapeCheck ({ sourceFixture with owner_ref := "unverified-label" }) = true := by decide

theorem empty_payload_lists_are_shape_valid : recordShapeCheck ({ sourceFixture with payload := { intent_ref := "intent:complete-lab-model", owner_decision_ref := "decision:select-lab-model-work", selected_subject_refs := [], satisfaction_test_refs := [], excluded_subject_refs := [] } }) = true := by decide

theorem selected_excluded_overlap_is_shape_valid : recordShapeCheck ({ sourceFixture with payload := { intent_ref := "intent:complete-lab-model", owner_decision_ref := "decision:select-lab-model-work", selected_subject_refs := ["project:lab-semantic-governance", "goal:complete-integrated-model"], satisfaction_test_refs := ["test:all-definitions-realized", "test:all-relations-closed"], excluded_subject_refs := ["project:lab-semantic-governance"] } }) = true := by decide

theorem unjoined_relation_enums_are_shape_valid : recordShapeCheck ({ sourceFixture with relation_refs := [{ relation_kind_ref := "relation.successor-of", direction := "target", counterpart_kind := "challenge-event", counterpart_ref := "challenge-event:example-001" }] }) = true := by decide

theorem distinct_selected_alias_tokens_are_shape_valid : recordShapeCheck ({ sourceFixture with payload := { sourceFixture.payload with selected_subject_refs := ["project:lab-semantic-governance", "alias:project-subject"] } }) = true := by decide

#print axioms owner_label_alone_is_shape_valid
#print axioms empty_payload_lists_are_shape_valid
#print axioms selected_excluded_overlap_is_shape_valid
#print axioms unjoined_relation_enums_are_shape_valid
#print axioms distinct_selected_alias_tokens_are_shape_valid
end RelationalSuccessor.CandidateIntentRecordShape.Examples
