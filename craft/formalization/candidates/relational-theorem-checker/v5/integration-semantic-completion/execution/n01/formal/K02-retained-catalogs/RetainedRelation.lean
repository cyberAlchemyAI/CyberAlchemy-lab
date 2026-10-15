import NestedPipeline
set_option autoImplicit false
namespace RelationalSuccessor.CandidateRetainedCatalogs
open CandidateBindingAst (Decoder)
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits)
open CandidateEvidenceResources (NumericLimits)
open CandidateIntentSourcePipeline (FramedWorld Claim)

structure RelationState (α : Type) (profile : Profile) (limits : Limits) (numbers : NumericLimits)
    (inputs : CandidateCatalogSnapshots.Inputs) where
  batch : CandidateOriginalBytePipeline.Batch profile limits numbers inputs.original
  catalogs : CandidateCatalogSnapshots.Catalogs α
  relation : CandidateIntentSourcePipeline.Output

def RelationMeaning {α : Type} {profile : Profile} {limits : Limits} {numbers : NumericLimits}
    {inputs : CandidateCatalogSnapshots.Inputs} (body : Decoder α) (world : FramedWorld) (claim : Claim)
    (state : RelationState α profile limits numbers inputs) : Prop :=
  CandidateCatalogSnapshots.CapturedMeaning body inputs state.catalogs ∧
    CandidateOriginalBytePipeline.Meaning profile limits numbers inputs.original state.catalogs.metadata
      state.catalogs.payload state.catalogs.owned world claim state.relation

def runRelation {α : Type} [DecidableEq α] (body : Decoder α) (profile : Profile) (limits : Limits) (numbers : NumericLimits)
    (inputs : CandidateCatalogSnapshots.Inputs) (world : FramedWorld) (claim : Claim) :
    Except CandidateCatalogSnapshots.Refusal (RelationState α profile limits numbers inputs) :=
  match CandidateOriginalBytePipeline.checkedBatch profile limits numbers inputs.original with
  | .error reason => .error (.input reason)
  | .ok batch =>
    match CandidateCatalogSnapshots.decodePrepared body batch with
    | none => .error .catalog
    | some catalogs =>
      match CandidateOriginalBytePipeline.runPrepared catalogs.metadata catalogs.payload catalogs.owned world claim batch with
      | none => .error .relation
      | some relation => .ok ⟨batch,catalogs,relation⟩

def eraseRelation {α : Type} {profile : Profile} {limits : Limits} {numbers : NumericLimits}
    {inputs : CandidateCatalogSnapshots.Inputs} :
    Except CandidateCatalogSnapshots.Refusal (RelationState α profile limits numbers inputs) →
      Except CandidateCatalogSnapshots.Refusal CandidateIntentSourcePipeline.Output
  | .error reason => .error reason
  | .ok state => .ok state.relation

theorem relation_erasure_exact {α : Type} [DecidableEq α] (body : Decoder α) (profile : Profile) (limits : Limits) (numbers : NumericLimits)
    (inputs : CandidateCatalogSnapshots.Inputs) (world : FramedWorld) (claim : Claim) :
    eraseRelation (runRelation body profile limits numbers inputs world claim) =
      CandidateCatalogSnapshots.run body profile limits numbers inputs world claim := by
  cases checked : CandidateOriginalBytePipeline.checkedBatch profile limits numbers inputs.original with
  | error reason => simp only [runRelation,CandidateCatalogSnapshots.run,checked,eraseRelation]
  | ok batch =>
    cases decoded : CandidateCatalogSnapshots.decodePrepared body batch with
    | none => simp only [runRelation,CandidateCatalogSnapshots.run,checked,CandidateCatalogSnapshots.runPrepared,decoded,eraseRelation]
    | some catalogs =>
      cases joined : CandidateOriginalBytePipeline.runPrepared catalogs.metadata catalogs.payload catalogs.owned world claim batch <;>
        simp only [runRelation,CandidateCatalogSnapshots.run,checked,CandidateCatalogSnapshots.runPrepared,decoded,joined,eraseRelation]

theorem retained_relation_sound {α : Type} [DecidableEq α] (body : Decoder α) (profile : Profile) (limits : Limits) (numbers : NumericLimits)
    (inputs : CandidateCatalogSnapshots.Inputs) (world : FramedWorld) (claim : Claim)
    (state : RelationState α profile limits numbers inputs)
    (accepted : runRelation body profile limits numbers inputs world claim = .ok state) :
    RelationMeaning body world claim state := by
  cases checked : CandidateOriginalBytePipeline.checkedBatch profile limits numbers inputs.original with
  | error reason => simp only [runRelation,checked] at accepted; contradiction
  | ok batch =>
    cases decoded : CandidateCatalogSnapshots.decodePrepared body batch with
    | none => simp only [runRelation,checked,decoded] at accepted; contradiction
    | some catalogs =>
      cases joined : CandidateOriginalBytePipeline.runPrepared catalogs.metadata catalogs.payload catalogs.owned world claim batch with
      | none => simp only [runRelation,checked,decoded,joined] at accepted; contradiction
      | some relation =>
        simp only [runRelation,checked,decoded,joined,Except.ok.injEq] at accepted
        subst state
        exact ⟨(CandidateCatalogSnapshots.prepared_catalogs_exact _ _ _).mp decoded,
          (CandidateOriginalBytePipeline.prepared_original_meaning _ _ _ _ _ _ _).mp joined⟩

theorem retained_certificates_cover_exact_inputs {α : Type} {profile : Profile} {limits : Limits} {numbers : NumericLimits}
    {inputs : CandidateCatalogSnapshots.Inputs} (state : RelationState α profile limits numbers inputs) :
    state.batch.val.map (fun input => input.val.capture) = inputs.original.captures ∧
      CandidateEvidenceResources.AllPreflightMeaning profile limits.perCaptureBytes numbers inputs.original.captures :=
  ⟨state.batch.property.2,CandidateOriginalBytePipeline.batch_all_preflight _ _ _ _ state.batch⟩

#print axioms relation_erasure_exact
#print axioms retained_relation_sound
#print axioms retained_certificates_cover_exact_inputs
end RelationalSuccessor.CandidateRetainedCatalogs
