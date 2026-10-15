import IntentSourcePipeline
import OwnedQualifierFixture
import OwnedQualifierBranches

set_option autoImplicit false
namespace RelationalSuccessor.CandidateIntentSourcePipeline.Fixture
open RelationalSuccessor
open RelationalSuccessor.CandidateIntentSourcePipeline
abbrev metadata := CandidateCapturedMetadata.Examples.context
abbrev payloads := CandidateCapturedMetadata.Examples.payloads
abbrev bytes := CandidateCapturedMetadata.Examples.originalBytes
abbrev sourceAst := CandidateCapturedMetadata.Examples.ast
abbrev bindings := CandidateOwnedIntentQualifiers.Fixture.context
abbrev world := CandidateOwnedIntentQualifiers.Fixture.Eworld
abbrev claim := CandidateOwnedIntentQualifiers.Fixture.Eclaim
abbrev projected := CandidateOwnedIntentQualifiers.Fixture.Eprojected
abbrev raw := CandidateOwnedIntentQualifiers.Fixture.raw

def qualifierAst : Ast := CandidateIntentSourceContract.Qualifiers.encode raw
def output : Output := ⟨projected.resolution, projected, raw⟩

theorem original_pipeline_meaning : Meaning metadata payloads bindings world bytes sourceAst qualifierAst claim output := by
  have joined := (CandidateOwnedIntentQualifiers.check_exact _ _ _ _ _).mp
    CandidateOwnedIntentQualifiers.Fixture.original_qualifiers_accept
  refine ⟨(CandidateIntentSourceContract.Qualifiers.decode_exact _ _).mp
    (CandidateIntentSourceContract.Qualifiers.encoding_exact raw), joined.resolution, ?_, joined⟩
  exact (CandidateCapturedMetadata.decode_resolution_exact _ _ _ _ _ _ _).mp
    CandidateCapturedMetadata.Examples.complete_structural_projection

theorem original_pipeline_accepts : run metadata payloads bindings world bytes sourceAst qualifierAst claim = some output :=
  (run_exact _ _ _ _ _ _ _ _ _).mpr original_pipeline_meaning

theorem source_and_claim_resolution_agree : output.resolution = claim.resolution ∧ output.resolution = output.projected.resolution :=
  output_resolution_exact _ _ _ _ _ _ _ _ _ original_pipeline_accepts

theorem malformed_qualifier_pipeline_refuses : run metadata payloads bindings world bytes sourceAst (.null) claim = none := by
  apply malformed_qualifier_refuses
  rfl

def missingResolution : Bindings :=
  { bindings with resolutions := { bindings.resolutions with records := [], roots := [] } }
theorem no_owned_resolution_cannot_start_pipeline :
    run metadata payloads missingResolution world bytes sourceAst qualifierAst claim = none := by
  cases accepted : run metadata payloads missingResolution world bytes sourceAst qualifierAst claim with
  | none => rfl
  | some out =>
    have meaning := (run_exact _ _ _ _ _ _ _ _ _).mp accepted
    rcases meaning.resolution.binding with ⟨entry, member, _, _⟩
    simp [missingResolution] at member

-- Composition controls share the real byte fixture and synthetic captured
-- bindings/Worlds. They do not authenticate the six assigned subject kinds.
theorem branch_pipeline_meaning (kind : CandidateIntentAddressing.SubjectKind)
    (checked : CandidateOwnedIntentQualifiers.check
      (CandidateOwnedIntentQualifiers.Branches.branchContext kind)
      (CandidateOwnedIntentQualifiers.Branches.branchWorld kind) projected raw
      (CandidateOwnedIntentQualifiers.Branches.branchClaim kind) = true) :
    Meaning metadata payloads (CandidateOwnedIntentQualifiers.Branches.branchContext kind)
      (CandidateOwnedIntentQualifiers.Branches.branchWorld kind) bytes sourceAst qualifierAst
      (CandidateOwnedIntentQualifiers.Branches.branchClaim kind) output := by
  have joined := (CandidateOwnedIntentQualifiers.check_exact _ _ _ _ _).mp checked
  refine ⟨(CandidateIntentSourceContract.Qualifiers.decode_exact _ _).mp
    (CandidateIntentSourceContract.Qualifiers.encoding_exact raw), joined.resolution, ?_, joined⟩
  exact (CandidateCapturedMetadata.decode_resolution_exact _ _ _ _ _ _ _).mp
    CandidateCapturedMetadata.Examples.complete_structural_projection

#print axioms original_pipeline_meaning
#print axioms original_pipeline_accepts
#print axioms source_and_claim_resolution_agree
#print axioms malformed_qualifier_pipeline_refuses
#print axioms no_owned_resolution_cannot_start_pipeline
#print axioms branch_pipeline_meaning
end RelationalSuccessor.CandidateIntentSourcePipeline.Fixture
