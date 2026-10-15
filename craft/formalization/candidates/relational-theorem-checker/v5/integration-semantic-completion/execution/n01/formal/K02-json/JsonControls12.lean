import JsonFixture

set_option autoImplicit false

namespace RelationalSuccessor.CandidateJsonSource.Examples
open RelationalSuccessor.CandidateJsonSource
open RelationalSuccessor.CandidateIntentRecordShape

def ast_satisfaction_test_refs_invalid_tail : Value := Value.object [("authority_effect", Value.string "none"), ("challenge_route", Value.string "route:artifact-type-challenge"), ("claim_ceiling", Value.string "Realistic Intent Resolution example for candidate review only."), ("evidence_refs", Value.array [Value.string "evidence:intent-resolution-example"]), ("kind", Value.string "intent-resolution"), ("lifecycle_state", Value.string "candidate"), ("name", Value.string "Example Intent Resolution"), ("node_id", Value.string "intent-resolution:example-001"), ("owner_ref", Value.string "role:artifact-type-owner"), ("payload", Value.object [("excluded_subject_refs", Value.array [Value.string "runtime:unapproved-cutover"]), ("intent_ref", Value.string "intent:complete-lab-model"), ("owner_decision_ref", Value.string "decision:select-lab-model-work"), ("satisfaction_test_refs", Value.array [Value.string "test:all-definitions-realized", Value.string "test:all-relations-closed", Value.null]), ("selected_subject_refs", Value.array [Value.string "project:lab-semantic-governance", Value.string "goal:complete-integrated-model"])]), ("relation_refs", Value.array [Value.object [("counterpart_kind", Value.string "challenge-event"), ("counterpart_ref", Value.string "challenge-event:example-001"), ("direction", Value.string "target"), ("relation_kind_ref", Value.string "relation.challenges")]]), ("schema_version", Value.string "cyberalchemy-lab-intent-resolution/v1"), ("scope_ref", Value.string "scope:lab-integrated-model"), ("successor_refs", Value.array [])]
theorem satisfaction_test_refs_invalid_tail : decodeRecord ast_satisfaction_test_refs_invalid_tail = none := by decide

def ast_excluded_subject_refs_invalid_head : Value := Value.object [("authority_effect", Value.string "none"), ("challenge_route", Value.string "route:artifact-type-challenge"), ("claim_ceiling", Value.string "Realistic Intent Resolution example for candidate review only."), ("evidence_refs", Value.array [Value.string "evidence:intent-resolution-example"]), ("kind", Value.string "intent-resolution"), ("lifecycle_state", Value.string "candidate"), ("name", Value.string "Example Intent Resolution"), ("node_id", Value.string "intent-resolution:example-001"), ("owner_ref", Value.string "role:artifact-type-owner"), ("payload", Value.object [("excluded_subject_refs", Value.array [Value.null, Value.string "runtime:unapproved-cutover"]), ("intent_ref", Value.string "intent:complete-lab-model"), ("owner_decision_ref", Value.string "decision:select-lab-model-work"), ("satisfaction_test_refs", Value.array [Value.string "test:all-definitions-realized", Value.string "test:all-relations-closed"]), ("selected_subject_refs", Value.array [Value.string "project:lab-semantic-governance", Value.string "goal:complete-integrated-model"])]), ("relation_refs", Value.array [Value.object [("counterpart_kind", Value.string "challenge-event"), ("counterpart_ref", Value.string "challenge-event:example-001"), ("direction", Value.string "target"), ("relation_kind_ref", Value.string "relation.challenges")]]), ("schema_version", Value.string "cyberalchemy-lab-intent-resolution/v1"), ("scope_ref", Value.string "scope:lab-integrated-model"), ("successor_refs", Value.array [])]
theorem excluded_subject_refs_invalid_head : decodeRecord ast_excluded_subject_refs_invalid_head = none := by decide

def ast_excluded_subject_refs_invalid_tail : Value := Value.object [("authority_effect", Value.string "none"), ("challenge_route", Value.string "route:artifact-type-challenge"), ("claim_ceiling", Value.string "Realistic Intent Resolution example for candidate review only."), ("evidence_refs", Value.array [Value.string "evidence:intent-resolution-example"]), ("kind", Value.string "intent-resolution"), ("lifecycle_state", Value.string "candidate"), ("name", Value.string "Example Intent Resolution"), ("node_id", Value.string "intent-resolution:example-001"), ("owner_ref", Value.string "role:artifact-type-owner"), ("payload", Value.object [("excluded_subject_refs", Value.array [Value.string "runtime:unapproved-cutover", Value.null]), ("intent_ref", Value.string "intent:complete-lab-model"), ("owner_decision_ref", Value.string "decision:select-lab-model-work"), ("satisfaction_test_refs", Value.array [Value.string "test:all-definitions-realized", Value.string "test:all-relations-closed"]), ("selected_subject_refs", Value.array [Value.string "project:lab-semantic-governance", Value.string "goal:complete-integrated-model"])]), ("relation_refs", Value.array [Value.object [("counterpart_kind", Value.string "challenge-event"), ("counterpart_ref", Value.string "challenge-event:example-001"), ("direction", Value.string "target"), ("relation_kind_ref", Value.string "relation.challenges")]]), ("schema_version", Value.string "cyberalchemy-lab-intent-resolution/v1"), ("scope_ref", Value.string "scope:lab-integrated-model"), ("successor_refs", Value.array [])]
theorem excluded_subject_refs_invalid_tail : decodeRecord ast_excluded_subject_refs_invalid_tail = none := by decide

def ast_wrong_top_null : Value := Value.null
theorem wrong_top_null : decodeRecord ast_wrong_top_null = none := by decide

def ast_wrong_top_boolean : Value := Value.boolean true
theorem wrong_top_boolean : decodeRecord ast_wrong_top_boolean = none := by decide

def ast_wrong_top_number : Value := Value.number "0"
theorem wrong_top_number : decodeRecord ast_wrong_top_number = none := by decide

#print axioms satisfaction_test_refs_invalid_tail
#print axioms excluded_subject_refs_invalid_head
#print axioms excluded_subject_refs_invalid_tail
#print axioms wrong_top_null
#print axioms wrong_top_boolean
#print axioms wrong_top_number
end RelationalSuccessor.CandidateJsonSource.Examples
