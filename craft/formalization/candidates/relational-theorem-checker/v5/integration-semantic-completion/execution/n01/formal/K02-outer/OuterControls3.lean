import OuterFixture

set_option autoImplicit false

namespace RelationalSuccessor.CandidateIntentRecordShape.Examples
open RelationalSuccessor.CandidateIntentRecordShape

theorem evidence_refs_duplicates : recordShapeCheck ({ sourceFixture with evidence_refs := ["x", "x"] }) = false := by decide

theorem successor_refs_empty_member : recordShapeCheck ({ sourceFixture with successor_refs := [""] }) = false := by decide

theorem successor_refs_duplicates : recordShapeCheck ({ sourceFixture with successor_refs := ["x", "x"] }) = false := by decide

theorem empty_relation_list : recordShapeCheck ({ sourceFixture with relation_refs := [] }) = false := by decide

theorem invalid_relation_relation_kind_ref : recordShapeCheck ({ sourceFixture with relation_refs := [{ relation_kind_ref := "relation.addresses-intent", direction := "target", counterpart_kind := "challenge-event", counterpart_ref := "challenge-event:example-001" }] }) = false := by decide

theorem invalid_relation_direction : recordShapeCheck ({ sourceFixture with relation_refs := [{ relation_kind_ref := "relation.challenges", direction := "both", counterpart_kind := "challenge-event", counterpart_ref := "challenge-event:example-001" }] }) = false := by decide

#print axioms evidence_refs_duplicates
#print axioms successor_refs_empty_member
#print axioms successor_refs_duplicates
#print axioms empty_relation_list
#print axioms invalid_relation_relation_kind_ref
#print axioms invalid_relation_direction
end RelationalSuccessor.CandidateIntentRecordShape.Examples
