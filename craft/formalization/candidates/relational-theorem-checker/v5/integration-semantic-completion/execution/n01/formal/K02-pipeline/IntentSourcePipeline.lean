import OwnedIntentQualifierCheck

set_option autoImplicit false
namespace RelationalSuccessor.CandidateIntentSourcePipeline
open RelationalSuccessor
abbrev Metadata := CandidateCapturedMetadata.Context
abbrev Bindings := CandidateOwnedIntentQualifiers.Context
abbrev FramedWorld := CandidateIntentSourceContract.FramedWorld
abbrev Claim := CandidateIntentAddressing.Claim
abbrev Resolution := CandidateIntentAddressing.Resolution
abbrev Projected := CandidateCapturedMetadata.Projected
abbrev Raw := CandidateIntentSourceContract.Qualifiers.Raw
abbrev Ast := CandidateJsonSource.Value

structure Output where
  resolution : Resolution
  projected : Projected
  qualifiers : Raw
  deriving DecidableEq, Repr

-- Independent composition of component meanings. This does not call run and
-- does not establish the unrealized authentication/parser/policy obligations.
structure Meaning {α : Type} (metadata : Metadata) (payloads : CandidateFiniteSourceCatalog.Capture α)
    (bindings : Bindings) (world : FramedWorld) (bytes : List UInt8) (sourceAst qualifierAst : Ast)
    (claim : Claim) (output : Output) : Prop where
  qualifiers : CandidateIntentSourceContract.Qualifiers.Meaning qualifierAst output.qualifiers
  resolution : CandidateOwnedBindings.Resolved bindings.resolutions CandidateOwnedIntentQualifiers.resolutionKind
    CandidateOwnedIntentQualifiers.resolutionKey world.frame output.qualifiers.intent_resolution_ref output.resolution
  source : CandidateCapturedMetadata.ProjectionMeaning metadata payloads world.frame
    output.resolution.ref bytes sourceAst output.projected
  joined : CandidateOwnedIntentQualifiers.Meaning bindings world output.projected output.qualifiers claim

-- The source reference is derived from the owned qualifier result, not a second
-- free caller parameter. None is unqualified in this captured fragment, not a
-- public factual-false result or the final unknown/unsupported classifier.
def run {α : Type} [DecidableEq α] (metadata : Metadata) (payloads : CandidateFiniteSourceCatalog.Capture α)
    (bindings : Bindings) (world : FramedWorld) (bytes : List UInt8) (sourceAst qualifierAst : Ast)
    (claim : Claim) : Option Output :=
  match CandidateIntentSourceContract.Qualifiers.decode qualifierAst with
  | none => none
  | some raw =>
    match CandidateOwnedBindings.resolve bindings.resolutions CandidateOwnedIntentQualifiers.resolutionKind
        CandidateOwnedIntentQualifiers.resolutionKey world.frame raw.intent_resolution_ref with
    | none => none
    | some resolution =>
      match CandidateCapturedMetadata.decodeResolution metadata payloads world.frame resolution.ref bytes sourceAst with
      | none => none
      | some projected =>
        if CandidateOwnedIntentQualifiers.check bindings world projected raw claim then
          some ⟨resolution, projected, raw⟩
        else none

theorem run_exact {α : Type} [DecidableEq α] (metadata : Metadata)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (bindings : Bindings) (world : FramedWorld)
    (bytes : List UInt8) (sourceAst qualifierAst : Ast) (claim : Claim) (output : Output) :
    run metadata payloads bindings world bytes sourceAst qualifierAst claim = some output ↔
      Meaning metadata payloads bindings world bytes sourceAst qualifierAst claim output := by
  constructor
  · intro accepted
    cases parsed : CandidateIntentSourceContract.Qualifiers.decode qualifierAst with
    | none => simp [run, parsed] at accepted
    | some raw =>
      cases resolved : CandidateOwnedBindings.resolve bindings.resolutions CandidateOwnedIntentQualifiers.resolutionKind
          CandidateOwnedIntentQualifiers.resolutionKey world.frame raw.intent_resolution_ref with
      | none => simp [run, parsed, resolved] at accepted
      | some resolution =>
        cases source : CandidateCapturedMetadata.decodeResolution metadata payloads world.frame resolution.ref bytes sourceAst with
        | none => simp [run, parsed, resolved, source] at accepted
        | some projected =>
          simp only [run, parsed, resolved, source] at accepted
          split at accepted
          · rename_i checked
            have same : (⟨resolution, projected, raw⟩ : Output) = output := Option.some.inj accepted
            cases same
            exact ⟨(CandidateIntentSourceContract.Qualifiers.decode_exact _ _).mp parsed,
              (CandidateOwnedBindings.resolve_exact _ _ _ _ _ _).mp resolved,
              (CandidateCapturedMetadata.decode_resolution_exact _ _ _ _ _ _ _).mp source,
              (CandidateOwnedIntentQualifiers.check_exact _ _ _ _ _).mp checked⟩
          · cases accepted
  · intro meaning
    have parsed := (CandidateIntentSourceContract.Qualifiers.decode_exact _ _).mpr meaning.qualifiers
    have resolved := (CandidateOwnedBindings.resolve_exact _ _ _ _ _ _).mpr meaning.resolution
    have source := (CandidateCapturedMetadata.decode_resolution_exact _ _ _ _ _ _ _).mpr meaning.source
    have checked := (CandidateOwnedIntentQualifiers.check_exact _ _ _ _ _).mpr meaning.joined
    simp only [run, parsed, resolved, source, if_pos checked]

theorem output_resolution_exact {α : Type} [DecidableEq α] (metadata : Metadata)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (bindings : Bindings) (world : FramedWorld)
    (bytes : List UInt8) (sourceAst qualifierAst : Ast) (claim : Claim) (output : Output)
    (accepted : run metadata payloads bindings world bytes sourceAst qualifierAst claim = some output) :
    output.resolution = claim.resolution ∧ output.resolution = output.projected.resolution := by
  have meaning := (run_exact _ _ _ _ _ _ _ _ _).mp accepted
  have sourceResolution := (CandidateOwnedBindings.resolve_exact _ _ _ _ _ _).mpr meaning.resolution
  have claimResolution := (CandidateOwnedBindings.resolve_exact _ _ _ _ _ _).mpr meaning.joined.resolution
  have same : output.resolution = claim.resolution := Option.some.inj (sourceResolution.symm.trans claimResolution)
  exact ⟨same, same.trans meaning.joined.joined.projection⟩

theorem output_reference_and_frame_exact {α : Type} [DecidableEq α] (metadata : Metadata)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (bindings : Bindings) (world : FramedWorld)
    (bytes : List UInt8) (sourceAst qualifierAst : Ast) (claim : Claim) (output : Output)
    (accepted : run metadata payloads bindings world bytes sourceAst qualifierAst claim = some output) :
    output.projected.receipt.artifact.ref = output.resolution.ref ∧
      output.projected.receipt.frame = world.frame ∧ claim.selection.frame = world.frame := by
  have meaning := (run_exact _ _ _ _ _ _ _ _ _).mp accepted
  exact ⟨meaning.source.1.metadata.source,
    meaning.source.1.metadata.receiptMeaning.frame.trans meaning.source.1.metadata.frame,
    meaning.joined.joined.fullFrame⟩

theorem malformed_qualifier_refuses {α : Type} [DecidableEq α] (metadata : Metadata)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (bindings : Bindings) (world : FramedWorld)
    (bytes : List UInt8) (sourceAst qualifierAst : Ast) (claim : Claim)
    (malformed : CandidateIntentSourceContract.Qualifiers.decode qualifierAst = none) :
    run metadata payloads bindings world bytes sourceAst qualifierAst claim = none := by
  simp [run, malformed]

theorem no_meaning_refuses {α : Type} [DecidableEq α] (metadata : Metadata)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (bindings : Bindings) (world : FramedWorld)
    (bytes : List UInt8) (sourceAst qualifierAst : Ast) (claim : Claim)
    (invalid : ∀ output, ¬ Meaning metadata payloads bindings world bytes sourceAst qualifierAst claim output) :
    run metadata payloads bindings world bytes sourceAst qualifierAst claim = none := by
  cases accepted : run metadata payloads bindings world bytes sourceAst qualifierAst claim with
  | none => rfl
  | some output => exact False.elim (invalid output ((run_exact _ _ _ _ _ _ _ _ _).mp accepted))

#print axioms run_exact
#print axioms output_resolution_exact
#print axioms output_reference_and_frame_exact
#print axioms malformed_qualifier_refuses
#print axioms no_meaning_refuses
end RelationalSuccessor.CandidateIntentSourcePipeline
