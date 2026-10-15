import NestedManifest
set_option autoImplicit false
namespace RelationalSuccessor.CandidateNestedProvenance
open CandidateBindingAst (Decoder)
open CandidateBindingCapture (Envelope)
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits)
open CandidateEvidenceResources (NumericLimits)
open CandidateIntentSourcePipeline (FramedWorld Claim)
open CandidateScalarConversion (parseScalarDocumentBytes ScalarByteDocumentMeaning)

def decodeRawCatalogs {α : Type} (body : Decoder α) (inputs : CandidateCatalogSnapshots.Inputs) :
    Option (CandidateCatalogSnapshots.Catalogs α) :=
  match parseScalarDocumentBytes inputs.metadata.content, parseScalarDocumentBytes inputs.payload.content,
        parseScalarDocumentBytes inputs.owned.content with
  | some m, some p, some o => CandidateCatalogSnapshots.decodeCatalogs body m p o
  | _, _, _ => none

theorem raw_catalogs_exact {α : Type} (body : Decoder α) (inputs : CandidateCatalogSnapshots.Inputs)
    (catalogs : CandidateCatalogSnapshots.Catalogs α) :
    decodeRawCatalogs body inputs = some catalogs ↔ CandidateCatalogSnapshots.CapturedMeaning body inputs catalogs := by
  constructor
  · intro accepted
    cases m : parseScalarDocumentBytes inputs.metadata.content with
    | none => simp only [decodeRawCatalogs,m] at accepted; contradiction
    | some ma =>
      cases p : parseScalarDocumentBytes inputs.payload.content with
      | none => simp only [decodeRawCatalogs,m,p] at accepted; contradiction
      | some pa =>
        cases o : parseScalarDocumentBytes inputs.owned.content with
        | none => simp only [decodeRawCatalogs,m,p,o] at accepted; contradiction
        | some oa =>
          simp only [decodeRawCatalogs,m,p,o] at accepted
          exact ⟨ma,pa,oa,(CandidateScalarConversion.scalar_byte_document_exact _ _).mp m,
            (CandidateScalarConversion.scalar_byte_document_exact _ _).mp p,
            (CandidateScalarConversion.scalar_byte_document_exact _ _).mp o,
            (CandidateCatalogSnapshots.decode_catalogs_exact _ _ _ _ _).mp accepted⟩
  · rintro ⟨m,p,o,pm,pp,po,decoded⟩
    simp only [decodeRawCatalogs,(CandidateScalarConversion.scalar_byte_document_exact _ _).mpr pm,
      (CandidateScalarConversion.scalar_byte_document_exact _ _).mpr pp,
      (CandidateScalarConversion.scalar_byte_document_exact _ _).mpr po]
    exact (CandidateCatalogSnapshots.decode_catalogs_exact _ _ _ _ _).mpr decoded

structure Inputs where
  parent : CandidateSelectedRelation.Inputs
  nested : List Envelope
  deriving DecidableEq, Repr
def Inputs.captures (inputs : Inputs) : List Envelope := inputs.parent.captures ++ inputs.nested
structure Output (α : Type) where
  parent : CandidateSelectedRelation.Output
  catalogs : CandidateCatalogSnapshots.Catalogs α
  deriving DecidableEq, Repr
inductive FullRefusal where
  | budget
  | parent (reason : CandidateSelectedRelation.Refusal)
  | catalog
  | nested (reason : Refusal)
  deriving DecidableEq, Repr

def FullMeaning {α : Type} (body : Decoder α) (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : Output α) : Prop :=
  NestedBudgetMeaning limits inputs.captures ∧
    CandidateSelectedRelation.Meaning body bootstrap limits numbers root ref inputs.parent world claim output.parent ∧
    CandidateCatalogSnapshots.CapturedMeaning body inputs.parent.relation output.catalogs ∧
    NestedMeaning body output.parent.evidence.profile.profile limits numbers world.frame (required output.catalogs) inputs.nested

def runFull {α : Type} [DecidableEq α] (body : Decoder α) (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) : Except FullRefusal (Output α) :=
  if nestedBudgetCheck limits inputs.captures then
    match CandidateSelectedRelation.run body bootstrap limits numbers root ref inputs.parent world claim with
    | .error reason => .error (.parent reason)
    | .ok parent =>
      match decodeRawCatalogs body inputs.parent.relation with
      | none => .error .catalog
      | some catalogs =>
        match runNested body parent.evidence.profile.profile limits numbers world.frame (required catalogs) inputs.nested with
        | .error reason => .error (.nested reason)
        | .ok _ => .ok ⟨parent,catalogs⟩
  else .error .budget

theorem full_run_sound {α : Type} [DecidableEq α] (body : Decoder α) (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : Output α)
    (accepted : runFull body bootstrap limits numbers root ref inputs world claim = .ok output) :
    FullMeaning body bootstrap limits numbers root ref inputs world claim output := by
  unfold runFull at accepted
  split at accepted
  · rename_i budget
    cases parentFound : CandidateSelectedRelation.run body bootstrap limits numbers root ref inputs.parent world claim with
    | error reason => simp only [parentFound] at accepted; contradiction
    | ok parent =>
      simp only [parentFound] at accepted
      cases catalogFound : decodeRawCatalogs body inputs.parent.relation with
      | none => simp only [catalogFound] at accepted; contradiction
      | some catalogs =>
        simp only [catalogFound] at accepted
        cases nestedFound : runNested body parent.evidence.profile.profile limits numbers world.frame (required catalogs) inputs.nested with
        | error reason => simp only [nestedFound] at accepted; contradiction
        | ok marker =>
          cases marker
          simp only [nestedFound,Except.ok.injEq] at accepted
          subst output
          exact ⟨(nested_budget_exact _ _).mp budget,
            (CandidateSelectedRelation.run_exact _ _ _ _ _ _ _ _ _ _).mp parentFound,
            (raw_catalogs_exact _ _ _).mp catalogFound,
            (nested_run_exact _ _ _ _ _ _ _).mp nestedFound⟩
  · contradiction

theorem full_run_complete {α : Type} [DecidableEq α] (body : Decoder α) (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : Output α)
    (meaning : FullMeaning body bootstrap limits numbers root ref inputs world claim output) :
    runFull body bootstrap limits numbers root ref inputs world claim = .ok output := by
  have budget := (nested_budget_exact _ _).mpr meaning.1
  have parentFound := (CandidateSelectedRelation.run_exact _ _ _ _ _ _ _ _ _ _).mpr meaning.2.1
  have catalogFound := (raw_catalogs_exact _ _ _).mpr meaning.2.2.1
  have nestedFound := (nested_run_exact _ _ _ _ _ _ _).mpr meaning.2.2.2
  cases output
  simp only [runFull,budget,if_true,parentFound,catalogFound,nestedFound]

theorem full_run_exact {α : Type} [DecidableEq α] (body : Decoder α) (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : Output α) :
    runFull body bootstrap limits numbers root ref inputs world claim = .ok output ↔
      FullMeaning body bootstrap limits numbers root ref inputs world claim output :=
  ⟨full_run_sound _ _ _ _ _ _ _ _ _ _,full_run_complete _ _ _ _ _ _ _ _ _ _⟩

theorem successful_full_manifest_exact {α : Type} [DecidableEq α] (body : Decoder α) (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : Output α)
    (accepted : runFull body bootstrap limits numbers root ref inputs world claim = .ok output) :
    inputs.nested = (required output.catalogs).map (envelope output.parent.evidence.profile.profile) ∧
      ∀ item ∈ required output.catalogs,
        ItemMeaning body output.parent.evidence.profile.profile limits.perCaptureBytes numbers world.frame item
          (envelope output.parent.evidence.profile.profile item) := by
  have meaning := (full_run_exact _ _ _ _ _ _ _ _ _ _).mp accepted
  exact ⟨pairs_exact_manifest _ _ _ _ _ _ _ meaning.2.2.2.2,pairs_all_expected _ _ _ _ _ _ _ meaning.2.2.2.2⟩

theorem successful_original_context_preserved {α : Type} [DecidableEq α] (body : Decoder α) (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : Output α)
    (accepted : runFull body bootstrap limits numbers root ref inputs world claim = .ok output) :
    CandidateOriginalBytePipeline.Meaning output.parent.evidence.profile.profile limits numbers inputs.parent.relation.original
      output.catalogs.metadata output.catalogs.payload output.catalogs.owned world claim output.parent.relation := by
  have meaning := (full_run_exact _ _ _ _ _ _ _ _ _ _).mp accepted
  rcases meaning.2.1.2.2 with ⟨catalogs,captured,original⟩
  have old := (raw_catalogs_exact _ _ _).mpr captured
  have new := (raw_catalogs_exact _ _ _).mpr meaning.2.2.1
  have same : catalogs = output.catalogs := Option.some.inj (old.symm.trans new)
  rw [same] at original
  exact original

theorem successful_full_original_interpretation_with_remaining_policies {α : Type} [DecidableEq α]
    (body : Decoder α) (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : Output α)
    (policy : CandidateIntentSourceContract.Policies α)
    (accepted : runFull body bootstrap limits numbers root ref inputs world claim = .ok output)
    (remaining : CandidateOriginalBytePipeline.RemainingPolicies policy output.catalogs.metadata output.catalogs.payload world claim output.parent.relation) :
    ∃ sourceAst qualifierAst,
      CandidateIntentSourceContract.SourceInterpretation (CandidateOriginalBytePipeline.bytePolicy policy)
        output.catalogs.metadata output.catalogs.payload world output.parent.relation.resolution.ref
        inputs.parent.relation.source.content sourceAst qualifierAst output.parent.relation.projected
        output.parent.relation.qualifiers claim := by
  exact CandidateOriginalBytePipeline.original_meaning_with_remaining_policies _ _ _ _ _ _ _ _ _ _ _
    (successful_original_context_preserved _ _ _ _ _ _ _ _ _ _ accepted) remaining

#print axioms raw_catalogs_exact
#print axioms full_run_sound
#print axioms full_run_complete
#print axioms full_run_exact
#print axioms successful_full_manifest_exact
#print axioms successful_original_context_preserved
#print axioms successful_full_original_interpretation_with_remaining_policies
end RelationalSuccessor.CandidateNestedProvenance
