import IntentRecordShape

set_option autoImplicit false

namespace RelationalSuccessor.CandidateIntentRecordShape.Examples
open RelationalSuccessor.CandidateIntentRecordShape

def sourceFixture : RawRecord where
  schema_version := "cyberalchemy-lab-intent-resolution/v1"
  node_id := "intent-resolution:example-001"
  kind := "intent-resolution"
  name := "Example Intent Resolution"
  lifecycle_state := "candidate"
  authority_effect := "none"
  owner_ref := "role:artifact-type-owner"
  scope_ref := "scope:lab-integrated-model"
  evidence_refs := ["evidence:intent-resolution-example"]
  challenge_route := "route:artifact-type-challenge"
  successor_refs := []
  relation_refs := [{ relation_kind_ref := "relation.challenges", direction := "target", counterpart_kind := "challenge-event", counterpart_ref := "challenge-event:example-001" }]
  payload := { intent_ref := "intent:complete-lab-model", owner_decision_ref := "decision:select-lab-model-work", selected_subject_refs := ["project:lab-semantic-governance", "goal:complete-integrated-model"], satisfaction_test_refs := ["test:all-definitions-realized", "test:all-relations-closed"], excluded_subject_refs := ["runtime:unapproved-cutover"] }
  claim_ceiling := "Realistic Intent Resolution example for candidate review only."

end RelationalSuccessor.CandidateIntentRecordShape.Examples
