import OuterFixture

set_option autoImplicit false

namespace RelationalSuccessor.CandidateIntentRecordShape.Examples
open RelationalSuccessor.CandidateIntentRecordShape

theorem satisfaction_test_refs_empty_member : recordShapeCheck ({ sourceFixture with payload := { sourceFixture.payload with satisfaction_test_refs := [""] } }) = false := by decide

theorem satisfaction_test_refs_duplicates : recordShapeCheck ({ sourceFixture with payload := { sourceFixture.payload with satisfaction_test_refs := ["x", "x"] } }) = false := by decide

theorem excluded_subject_refs_empty_member : recordShapeCheck ({ sourceFixture with payload := { sourceFixture.payload with excluded_subject_refs := [""] } }) = false := by decide

theorem excluded_subject_refs_duplicates : recordShapeCheck ({ sourceFixture with payload := { sourceFixture.payload with excluded_subject_refs := ["x", "x"] } }) = false := by decide

theorem empty_evidence_is_shape_valid : recordShapeCheck ({ sourceFixture with evidence_refs := [] }) = true := by decide

theorem retired_is_shape_valid : recordShapeCheck ({ sourceFixture with lifecycle_state := "retired" }) = true := by decide

#print axioms satisfaction_test_refs_empty_member
#print axioms satisfaction_test_refs_duplicates
#print axioms excluded_subject_refs_empty_member
#print axioms excluded_subject_refs_duplicates
#print axioms empty_evidence_is_shape_valid
#print axioms retired_is_shape_valid
end RelationalSuccessor.CandidateIntentRecordShape.Examples
