-- Captured source signature only; raw semantic decoding remains pending.
import ScopedImpactWitnesses
set_option autoImplicit false
namespace RelationalSuccessor.CandidateScopedImpact.SourceSignature
-- Source SHA256: 279f185d1d70e04737747a26c3605c95a570d1cbda77049aa2c8c3a23b0c8850
def capturedPairs : List (SourceKind × TargetKind) := [(.failureOccurrence, .agentCapability), (.failureOccurrence, .agentSession), (.failureOccurrence, .artifactType), (.failureOccurrence, .generatedOutput), (.failureOccurrence, .implementation), (.failureOccurrence, .ontology), (.failureOccurrence, .personReference), (.failureOccurrence, .product), (.failureOccurrence, .productCapability), (.failureOccurrence, .project), (.failureOccurrence, .work), (.incident, .agentCapability), (.incident, .agentSession), (.incident, .artifactType), (.incident, .generatedOutput), (.incident, .implementation), (.incident, .ontology), (.incident, .personReference), (.incident, .product), (.incident, .productCapability), (.incident, .project), (.incident, .work)]

theorem captured_pairs_exact : capturedPairs = allowedSources.flatMap
    (fun s => allowedTargets.map (fun t => (s, t))) := rfl

theorem captured_pair_constraints (s : SourceKind) (t : TargetKind) :
    (s, t) ∈ capturedPairs → s ∈ allowedSources ∧ t ∈ allowedTargets := by
  cases s <;> cases t <;> decide

theorem every_captured_branch_has_valid_model (s : SourceKind) (t : TargetKind)
    (captured : (s, t) ∈ capturedPairs) :
    Affects (Witnesses.world s t) (Witnesses.claim s t) :=
  Witnesses.legitimate_impact s t (captured_pair_constraints s t captured).1
    (captured_pair_constraints s t captured).2

#print axioms captured_pairs_exact
#print axioms captured_pair_constraints
#print axioms every_captured_branch_has_valid_model
end RelationalSuccessor.CandidateScopedImpact.SourceSignature
