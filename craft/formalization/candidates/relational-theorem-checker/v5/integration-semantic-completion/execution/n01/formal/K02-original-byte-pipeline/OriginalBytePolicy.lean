import OriginalBytePipeline
import SourcePolicyContract
set_option autoImplicit false
namespace RelationalSuccessor.CandidateOriginalBytePipeline
open CandidateIntentSourcePipeline (Metadata Bindings FramedWorld Claim Output)
open CandidateIntentSourceContract (Policies SourceInterpretation PolicyMeaning)

def bytePolicy {α : Type} (policy : Policies α) : Policies α :=
  {policy with parses := CandidateScalarConversion.ScalarByteDocumentMeaning}

-- Restoring parses restores the EXACT original 19-field policy record.
theorem byte_policy_preserves_other_slots {α : Type} (policy : Policies α) :
    {bytePolicy policy with parses := policy.parses} = policy := rfl

structure RemainingPolicies {α : Type} (policy : Policies α) (metadata : Metadata)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (world : FramedWorld)
    (claim : Claim) (output : Output) : Prop where
  authenticWorld : policy.authenticWorld world
  selection : policy.selection world claim
  projectionWorld : policy.projectionWorld world output.projected
  authenticMetadata : policy.authenticMetadata metadata
  authenticPayload : policy.authenticPayload payloads
  schema : policy.schema world.frame output.projected.receipt.schema output.projected.receipt.artifact.body.schema_version
  typedIdentity : policy.typedIdentity world.frame output.projected.receipt.identity
    output.projected.receipt.artifact.body.node_id output.projected.receipt.artifact.body.kind
  ownerScope : policy.ownerScope world.frame output.projected.receipt.owner output.projected.receipt.scope
  provenance : policy.provenance world.frame output.projected.receipt.artifact
  lifecycle : policy.lifecycle world.frame output.projected.receipt.artifact.ref output.projected.receipt.artifact.body.lifecycle_state
  evidence : policy.evidence world.frame output.projected.receipt.artifact.ref output.projected.receipt.artifact.body.evidence_refs
  challenge : policy.challenge world.frame output.projected.receipt.artifact.ref output.projected.receipt.artifact.body.challenge_route
  successors : policy.successors world.frame output.projected.receipt.artifact.ref output.projected.receipt.artifact.body.successor_refs
  companions : policy.companions world.frame output.projected.receipt.artifact.ref output.projected.receipt.artifact.body.relation_refs
  claimCeiling : policy.claimCeiling world.frame output.projected.receipt.artifact.ref output.projected.receipt.artifact.body.claim_ceiling
  payloadRoles : policy.payloadRoles world.frame output.projected.payload
  resolutionToken : policy.resolutionToken world.frame output.qualifiers.intent_resolution_ref claim.resolutionQualifier
  addressingRole : policy.addressingRole world.frame claim.subject.kind claim.role output.qualifiers.addressing_role

theorem original_meaning_with_remaining_policies {α : Type} [DecidableEq α]
    (profile : CandidateDigest.Profile) (limits : CandidateDigestCapture.Limits)
    (numbers : CandidateEvidenceResources.NumericLimits) (inputs : Inputs)
    (metadata : Metadata) (payloads : CandidateFiniteSourceCatalog.Capture α)
    (bindings : Bindings) (world : FramedWorld) (claim : Claim) (output : Output)
    (policy : Policies α)
    (meaning : Meaning profile limits numbers inputs metadata payloads bindings world claim output)
    (remaining : RemainingPolicies policy metadata payloads world claim output) :
    ∃ sourceAst qualifierAst,
      SourceInterpretation (bytePolicy policy) metadata payloads world output.resolution.ref
        inputs.source.content sourceAst qualifierAst output.projected output.qualifiers claim := by
  rcases meaning.2.2 with ⟨sourceAst, qualifierAst, parsed, _, pipeline, _⟩
  have checked := (CandidateOwnedIntentQualifiers.check_exact _ _ _ _ _).mpr pipeline.joined
  have nonempty := CandidateOwnedIntentQualifiers.successful_tokens_nonempty _ _ _ _ _ checked
  have role := CandidateOwnedIntentQualifiers.successful_role_and_selection_exact _ _ _ _ _ checked
  refine ⟨sourceAst, qualifierAst, remaining.authenticWorld, remaining.selection,
    remaining.projectionWorld, pipeline.source, ?_, pipeline.qualifiers, pipeline.joined.joined,
    nonempty.1, remaining.resolutionToken, nonempty.2, remaining.addressingRole, role.2.2.2⟩
  exact ⟨remaining.authenticMetadata, remaining.authenticPayload, parsed, remaining.schema,
    remaining.typedIdentity, remaining.ownerScope, remaining.provenance, remaining.lifecycle,
    remaining.evidence, remaining.challenge, remaining.successors, remaining.companions,
    remaining.claimCeiling, remaining.payloadRoles⟩

theorem byte_policy_cannot_supply_authentic_metadata {α : Type} (policy : Policies α)
    (metadata : Metadata) (payloads : CandidateFiniteSourceCatalog.Capture α)
    (world : FramedWorld) (ref : RevisionRef) (bytes : List UInt8)
    (ast qualifierAst : CandidateJsonSource.Value) (projected : CandidateCapturedMetadata.Projected)
    (raw : CandidateIntentSourceContract.Qualifiers.Raw) (claim : Claim)
    (absent : ¬ policy.authenticMetadata metadata) :
    ¬ SourceInterpretation (bytePolicy policy) metadata payloads world ref bytes ast qualifierAst projected raw claim := by
  intro interpreted
  exact absent interpreted.policies.authenticMetadata

#print axioms byte_policy_preserves_other_slots
#print axioms original_meaning_with_remaining_policies
#print axioms byte_policy_cannot_supply_authentic_metadata
end RelationalSuccessor.CandidateOriginalBytePipeline
