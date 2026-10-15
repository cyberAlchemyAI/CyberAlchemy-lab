import RecordingBindings
import IntentAddressingWitnesses
import ScopedImpactWitnesses

set_option autoImplicit false

namespace RelationalSuccessor.CandidateRecording.BindingExamples
open RelationalSuccessor
open Bindings

namespace IntentCases
open CandidateIntentAddressing.Witnesses

def proposal : Envelope CandidateIntentAddressing.Claim :=
  ⟨ref "issued-relation-record", claim .project, []⟩
def issued : IssuedRevision :=
  ⟨proposal.ref, "relation.addresses-intent", proposal.body.selection.frame,
    proposal.body.selection.ref, proposal.content⟩
def before : State CandidateIntentAddressing.Claim (List Nat) := ⟨[11, 12], []⟩
def recorded : State CandidateIntentAddressing.Claim (List Nat) := ⟨[11, 12], [proposal]⟩

theorem qualified_issued_intent_appends :
    (Intent.record (world .project) [issued] before proposal).outcome = .appended := by decide

theorem qualified_intent_retry_retains :
    (Intent.record (world .project) [issued] recorded proposal).outcome = .retained ∧
    (Intent.record (world .project) [issued] recorded proposal).state.records = [proposal] := by decide

theorem wrong_kind_issuance_refuses :
    (Intent.record (world .project) [{ issued with kind := "relation.affects" }] before proposal).outcome = .unqualified := by decide

theorem primary_witness_is_not_issued_relation_identity :
    (Intent.record (world .project) [issued] before
      { proposal with ref := proposal.body.selection.ref }).outcome = .unqualified := by decide

theorem wrong_issued_bytes_refuses :
    (Intent.record (world .project) [{ issued with content := [1] }] before proposal).outcome = .unqualified := by decide

theorem valid_issuance_does_not_qualify_wrong_role :
    (Intent.record (world .project) [issued] before
      { proposal with body := { proposal.body with addressingRole := "all-powerful" } }).outcome = .unqualified := by decide

theorem recorded_intent_does_not_replace_missing_witness :
    (Intent.record { world .project with selections := [] } [issued] recorded proposal).outcome = .unqualified ∧
    (Intent.record { world .project with selections := [] } [issued] recorded proposal).state.records = [proposal] := by decide
end IntentCases

namespace ImpactCases
open CandidateScopedImpact.Witnesses

def proposal : Envelope CandidateScopedImpact.Claim :=
  ⟨ref "issued-impact-relation", claim .incident .work, []⟩
def issued : IssuedRevision :=
  ⟨proposal.ref, "relation.affects", proposal.body.observation.frame,
    proposal.body.observation.ref, proposal.content⟩
def before : State CandidateScopedImpact.Claim (List Nat) := ⟨[11, 12], []⟩
def recorded : State CandidateScopedImpact.Claim (List Nat) := ⟨[11, 12], [proposal]⟩

theorem qualified_issued_impact_appends :
    (Impact.record (world .incident .work) [issued] before proposal).outcome = .appended := by decide

theorem prediction_not_qualified_by_issuance :
    (Impact.record (world .incident .work) [issued] before
      { proposal with body := { proposal.body with observation :=
        { proposal.body.observation with posture := .predicted } } }).outcome = .unqualified := by decide

theorem recorded_impact_does_not_replace_provenance :
    (Impact.record { world .incident .work with provenanceRoots := [] } [issued] recorded proposal).outcome = .unqualified ∧
    (Impact.record { world .incident .work with provenanceRoots := [] } [issued] recorded proposal).state.records = [proposal] := by decide
end ImpactCases

#print axioms IntentCases.qualified_issued_intent_appends
#print axioms IntentCases.qualified_intent_retry_retains
#print axioms IntentCases.wrong_kind_issuance_refuses
#print axioms IntentCases.primary_witness_is_not_issued_relation_identity
#print axioms IntentCases.wrong_issued_bytes_refuses
#print axioms IntentCases.valid_issuance_does_not_qualify_wrong_role
#print axioms IntentCases.recorded_intent_does_not_replace_missing_witness
#print axioms ImpactCases.qualified_issued_impact_appends
#print axioms ImpactCases.prediction_not_qualified_by_issuance
#print axioms ImpactCases.recorded_impact_does_not_replace_provenance
end RelationalSuccessor.CandidateRecording.BindingExamples
