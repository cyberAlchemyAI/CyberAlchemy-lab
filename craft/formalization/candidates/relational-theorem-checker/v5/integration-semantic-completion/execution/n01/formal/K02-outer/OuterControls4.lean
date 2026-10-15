import OuterFixture

set_option autoImplicit false

namespace RelationalSuccessor.CandidateIntentRecordShape.Examples
open RelationalSuccessor.CandidateIntentRecordShape

theorem invalid_relation_counterpart_kind : recordShapeCheck ({ sourceFixture with relation_refs := [{ relation_kind_ref := "relation.challenges", direction := "target", counterpart_kind := "project", counterpart_ref := "challenge-event:example-001" }] }) = false := by decide

theorem invalid_relation_counterpart_ref : recordShapeCheck ({ sourceFixture with relation_refs := [{ relation_kind_ref := "relation.challenges", direction := "target", counterpart_kind := "challenge-event", counterpart_ref := "" }] }) = false := by decide

theorem empty_payload_intent_ref : recordShapeCheck ({ sourceFixture with payload := { sourceFixture.payload with intent_ref := "" } }) = false := by decide

theorem empty_payload_owner_decision_ref : recordShapeCheck ({ sourceFixture with payload := { sourceFixture.payload with owner_decision_ref := "" } }) = false := by decide

theorem selected_subject_refs_empty_member : recordShapeCheck ({ sourceFixture with payload := { sourceFixture.payload with selected_subject_refs := [""] } }) = false := by decide

theorem selected_subject_refs_duplicates : recordShapeCheck ({ sourceFixture with payload := { sourceFixture.payload with selected_subject_refs := ["x", "x"] } }) = false := by decide

#print axioms invalid_relation_counterpart_kind
#print axioms invalid_relation_counterpart_ref
#print axioms empty_payload_intent_ref
#print axioms empty_payload_owner_decision_ref
#print axioms selected_subject_refs_empty_member
#print axioms selected_subject_refs_duplicates
end RelationalSuccessor.CandidateIntentRecordShape.Examples
