import OuterFixture

set_option autoImplicit false

namespace RelationalSuccessor.CandidateIntentRecordShape.Examples
open RelationalSuccessor.CandidateIntentRecordShape

theorem invalid_authority_effect : recordShapeCheck ({ sourceFixture with authority_effect := "grant" }) = false := by decide

theorem invalid_owner_ref : recordShapeCheck ({ sourceFixture with owner_ref := "" }) = false := by decide

theorem invalid_scope_ref : recordShapeCheck ({ sourceFixture with scope_ref := "" }) = false := by decide

theorem invalid_challenge_route : recordShapeCheck ({ sourceFixture with challenge_route := "" }) = false := by decide

theorem invalid_claim_ceiling : recordShapeCheck ({ sourceFixture with claim_ceiling := "" }) = false := by decide

theorem evidence_refs_empty_member : recordShapeCheck ({ sourceFixture with evidence_refs := [""] }) = false := by decide

#print axioms invalid_authority_effect
#print axioms invalid_owner_ref
#print axioms invalid_scope_ref
#print axioms invalid_challenge_route
#print axioms invalid_claim_ceiling
#print axioms evidence_refs_empty_member
end RelationalSuccessor.CandidateIntentRecordShape.Examples
