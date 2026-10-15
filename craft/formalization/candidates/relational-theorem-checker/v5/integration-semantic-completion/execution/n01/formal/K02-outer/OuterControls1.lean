import OuterFixture

set_option autoImplicit false

namespace RelationalSuccessor.CandidateIntentRecordShape.Examples
open RelationalSuccessor.CandidateIntentRecordShape

theorem original_source_shape : recordShapeCheck (sourceFixture) = true := by decide

theorem invalid_schema_version : recordShapeCheck ({ sourceFixture with schema_version := "wrong-schema" }) = false := by decide

theorem invalid_node_id : recordShapeCheck ({ sourceFixture with node_id := "" }) = false := by decide

theorem invalid_kind : recordShapeCheck ({ sourceFixture with kind := "decision" }) = false := by decide

theorem invalid_name : recordShapeCheck ({ sourceFixture with name := "" }) = false := by decide

theorem invalid_lifecycle_state : recordShapeCheck ({ sourceFixture with lifecycle_state := "unknown" }) = false := by decide

#print axioms original_source_shape
#print axioms invalid_schema_version
#print axioms invalid_node_id
#print axioms invalid_kind
#print axioms invalid_name
#print axioms invalid_lifecycle_state
end RelationalSuccessor.CandidateIntentRecordShape.Examples
