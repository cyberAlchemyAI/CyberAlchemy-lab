import FramedIntentJoin
import IntentQualifiers

set_option autoImplicit false
namespace RelationalSuccessor.CandidateIntentSourceContract
open RelationalSuccessor
abbrev Metadata := CandidateCapturedMetadata.Context
abbrev Receipt := CandidateCapturedMetadata.Receipt
abbrev Ast := CandidateJsonSource.Value
abbrev RawBody := CandidateIntentRecordShape.RawRecord

-- An open semantic interface, not a request body or executable approval flags.
-- No concrete policy realization or authentic provider is proved here.
structure Policies (α : Type) where
  authenticMetadata : Metadata → Prop
  authenticPayload : CandidateFiniteSourceCatalog.Capture α → Prop
  parses : List UInt8 → Ast → Prop
  schema : Frame → RevisionRef → String → Prop
  typedIdentity : Frame → CandidateCapturedMetadata.IdentityBinding → String → String → Prop
  ownerScope : Frame → CandidateCapturedMetadata.OwnerBinding → CandidateCapturedMetadata.ScopeBinding → Prop
  provenance : Frame → CandidateCapturedMetadata.Artifact RawBody → Prop
  lifecycle : Frame → RevisionRef → String → Prop
  evidence : Frame → RevisionRef → List String → Prop
  challenge : Frame → RevisionRef → String → Prop
  successors : Frame → RevisionRef → List String → Prop
  companions : Frame → RevisionRef → List CandidateIntentRecordShape.RawRelationRef → Prop
  claimCeiling : Frame → RevisionRef → String → Prop
  payloadRoles : Frame → CandidateIntentSource.Payload → Prop
  resolutionToken : Frame → String → RevisionRef → Prop
  addressingRole : Frame → CandidateIntentAddressing.SubjectKind → CandidateIntentAddressing.Role → String → Prop

structure PolicyMeaning {α : Type} (policy : Policies α) (metadata : Metadata)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (frame : Frame)
    (bytes : List UInt8) (ast : Ast) (projected : Projected) : Prop where
  authenticMetadata : policy.authenticMetadata metadata
  authenticPayload : policy.authenticPayload payloads
  byteParsing : policy.parses bytes ast
  schema : policy.schema frame projected.receipt.schema projected.receipt.artifact.body.schema_version
  typedIdentity : policy.typedIdentity frame projected.receipt.identity
    projected.receipt.artifact.body.node_id projected.receipt.artifact.body.kind
  ownerScope : policy.ownerScope frame projected.receipt.owner projected.receipt.scope
  provenance : policy.provenance frame projected.receipt.artifact
  lifecycle : policy.lifecycle frame projected.receipt.artifact.ref projected.receipt.artifact.body.lifecycle_state
  evidence : policy.evidence frame projected.receipt.artifact.ref projected.receipt.artifact.body.evidence_refs
  challenge : policy.challenge frame projected.receipt.artifact.ref projected.receipt.artifact.body.challenge_route
  successors : policy.successors frame projected.receipt.artifact.ref projected.receipt.artifact.body.successor_refs
  companions : policy.companions frame projected.receipt.artifact.ref projected.receipt.artifact.body.relation_refs
  claimCeiling : policy.claimCeiling frame projected.receipt.artifact.ref projected.receipt.artifact.body.claim_ceiling
  payloadRoles : policy.payloadRoles frame projected.payload

-- Full source contract candidate: independent component predicates plus explicit
-- unrealized provider policies. Supplying arbitrary predicates cannot discharge
-- an inherited obligation or establish authenticity in the real application.
structure SourceInterpretation {α : Type} (policy : Policies α) (metadata : Metadata)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (world : FramedWorld)
    (ref : RevisionRef) (bytes : List UInt8) (ast qualifierAst : Ast)
    (projected : Projected) (raw : Qualifiers.Raw) (claim : Claim) : Prop where
  projection : CandidateCapturedMetadata.ProjectionMeaning metadata payloads world.frame ref bytes ast projected
  policies : PolicyMeaning policy metadata payloads world.frame bytes ast projected
  qualifiers : Qualifiers.Meaning qualifierAst raw
  joined : Joined world projected claim
  resolutionTokenNonempty : raw.intent_resolution_ref ≠ ""
  resolutionToken : policy.resolutionToken world.frame raw.intent_resolution_ref claim.resolutionQualifier
  roleTokenNonempty : raw.addressing_role ≠ ""
  roleToken : policy.addressingRole world.frame claim.subject.kind claim.role raw.addressing_role
  exactRoleCode : raw.addressing_role = claim.addressingRole

theorem interpretation_requires_parsing {α : Type} (policy : Policies α) (metadata : Metadata)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (world : FramedWorld)
    (ref : RevisionRef) (bytes : List UInt8) (ast qualifierAst : Ast)
    (projected : Projected) (raw : Qualifiers.Raw) (claim : Claim)
    (meaning : SourceInterpretation policy metadata payloads world ref bytes ast qualifierAst projected raw claim) :
    policy.parses bytes ast := meaning.policies.byteParsing

theorem interpretation_requires_authentic_capture {α : Type} (policy : Policies α) (metadata : Metadata)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (world : FramedWorld)
    (ref : RevisionRef) (bytes : List UInt8) (ast qualifierAst : Ast)
    (projected : Projected) (raw : Qualifiers.Raw) (claim : Claim)
    (meaning : SourceInterpretation policy metadata payloads world ref bytes ast qualifierAst projected raw claim) :
    policy.authenticMetadata metadata ∧ policy.authenticPayload payloads :=
  ⟨meaning.policies.authenticMetadata, meaning.policies.authenticPayload⟩

theorem interpretation_checks_components {α : Type} [DecidableEq α]
    (policy : Policies α) (metadata : Metadata)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (world : FramedWorld)
    (ref : RevisionRef) (bytes : List UInt8) (ast qualifierAst : Ast)
    (projected : Projected) (raw : Qualifiers.Raw) (claim : Claim)
    (meaning : SourceInterpretation policy metadata payloads world ref bytes ast qualifierAst projected raw claim) :
    CandidateCapturedMetadata.decodeResolution metadata payloads world.frame ref bytes ast = some projected ∧
    Qualifiers.decode qualifierAst = some raw ∧ joinCheck world projected claim = true :=
  ⟨(CandidateCapturedMetadata.decode_resolution_exact _ _ _ _ _ _ _).mpr meaning.projection,
    (Qualifiers.decode_exact _ _).mpr meaning.qualifiers,
    (join_check_exact _ _ _).mpr meaning.joined⟩

theorem components_need_remaining_policies {α : Type} [DecidableEq α]
    (policy : Policies α) (metadata : Metadata)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (world : FramedWorld)
    (ref : RevisionRef) (bytes : List UInt8) (ast qualifierAst : Ast)
    (projected : Projected) (raw : Qualifiers.Raw) (claim : Claim)
    (projection : CandidateCapturedMetadata.decodeResolution metadata payloads world.frame ref bytes ast = some projected)
    (qualifiers : Qualifiers.decode qualifierAst = some raw)
    (joined : joinCheck world projected claim = true)
    (policies : PolicyMeaning policy metadata payloads world.frame bytes ast projected)
    (resolutionTokenNonempty : raw.intent_resolution_ref ≠ "")
    (resolutionToken : policy.resolutionToken world.frame raw.intent_resolution_ref claim.resolutionQualifier)
    (roleTokenNonempty : raw.addressing_role ≠ "")
    (roleToken : policy.addressingRole world.frame claim.subject.kind claim.role raw.addressing_role)
    (exactRoleCode : raw.addressing_role = claim.addressingRole) :
    SourceInterpretation policy metadata payloads world ref bytes ast qualifierAst projected raw claim :=
  ⟨(CandidateCapturedMetadata.decode_resolution_exact _ _ _ _ _ _ _).mp projection,
    policies, (Qualifiers.decode_exact _ _).mp qualifiers, (join_check_exact _ _ _).mp joined,
    resolutionTokenNonempty, resolutionToken, roleTokenNonempty, roleToken, exactRoleCode⟩

#print axioms interpretation_requires_parsing
#print axioms interpretation_requires_authentic_capture
#print axioms interpretation_checks_components
#print axioms components_need_remaining_policies
end RelationalSuccessor.CandidateIntentSourceContract
