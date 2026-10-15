import SupportingBodyDispatch
import CachedNestedEntry
set_option autoImplicit false
namespace RelationalSuccessor.CandidateSupportingSources
open CandidateBindingAst (J Decoder)
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits)
open CandidateEvidenceResources (NumericLimits)
open CandidateIntentSourcePipeline (FramedWorld Claim)
open CandidateNestedProvenance (Inputs)
abbrev FamilyArtifact := CandidateFiniteSourceCatalog.Artifact FamilyBody
abbrev FamilyOutput := CandidateNestedProvenance.Output FamilyBody

def ArtifactAlignment (artifact : FamilyArtifact) : Prop :=
  artifact.sourceKind = FamilyBody.sourceKind artifact.body ∧
    artifact.ref.key.artifact = FamilyBody.identity artifact.body

instance : DecidablePred ArtifactAlignment := fun artifact => by
  unfold ArtifactAlignment
  infer_instance

def alignedArtifact : Decoder FamilyArtifact :=
  CandidateTypedBodies.constrained (CandidateCatalogSnapshots.artifact familyDecoder) ArtifactAlignment

def AlignedArtifactMeaning (ast : J) (artifact : FamilyArtifact) : Prop :=
  CandidateCatalogSnapshots.ArtifactMeaning familyDecoder ast artifact ∧ ArtifactAlignment artifact

theorem aligned_artifact_exact (ast : J) (artifact : FamilyArtifact) :
    alignedArtifact.decode ast = some artifact ↔ AlignedArtifactMeaning ast artifact :=
  alignedArtifact.exact ast artifact

def CatalogAlignment (catalogs : CandidateCatalogSnapshots.Catalogs FamilyBody) : Prop :=
  ∀ artifact ∈ CandidateFiniteSourceCatalog.allArtifacts catalogs.payload, ArtifactAlignment artifact

def alignmentCheck (catalogs : CandidateCatalogSnapshots.Catalogs FamilyBody) : Bool :=
  (CandidateFiniteSourceCatalog.allArtifacts catalogs.payload).all (fun artifact => decide (ArtifactAlignment artifact))

theorem catalog_alignment_check_exact (catalogs : CandidateCatalogSnapshots.Catalogs FamilyBody) :
    alignmentCheck catalogs = true ↔ CatalogAlignment catalogs := by
  simp [alignmentCheck,CatalogAlignment,List.all_eq_true]

inductive TypedRefusal where
  | original (reason : CandidateNestedProvenance.FullRefusal)
  | alignment
  deriving DecidableEq, Repr

def runSupportingFull (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) :
    Except TypedRefusal FamilyOutput :=
  match CandidateRetainedCatalogs.runCachedFull familyDecoder bootstrap limits numbers root ref inputs world claim with
  | .error reason => .error (.original reason)
  | .ok output => if alignmentCheck output.catalogs then .ok output else .error .alignment

def SupportingFullMeaning (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim)
    (output : FamilyOutput) : Prop :=
  CandidateNestedProvenance.FullMeaning familyDecoder bootstrap limits numbers root ref inputs world claim output ∧
    CatalogAlignment output.catalogs

theorem supporting_full_exact (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : FamilyOutput) :
    runSupportingFull bootstrap limits numbers root ref inputs world claim = .ok output ↔
      SupportingFullMeaning bootstrap limits numbers root ref inputs world claim output := by
  constructor
  · intro accepted
    cases found : CandidateRetainedCatalogs.runCachedFull familyDecoder bootstrap limits numbers root ref inputs world claim with
    | error reason => simp [runSupportingFull,found] at accepted
    | ok actual =>
      simp only [runSupportingFull,found] at accepted
      split at accepted
      · rename_i aligned
        have same : actual = output := Except.ok.inj accepted
        subst output
        exact ⟨(CandidateRetainedCatalogs.cached_full_exact _ _ _ _ _ _ _ _ _ _).mp found,
          (catalog_alignment_check_exact _).mp aligned⟩
      · contradiction
  · rintro ⟨meaning,aligned⟩
    have found := (CandidateRetainedCatalogs.cached_full_exact _ _ _ _ _ _ _ _ _ _).mpr meaning
    simp [runSupportingFull,found,(catalog_alignment_check_exact _).mpr aligned]

theorem successful_full_all_occurrences_aligned (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : FamilyOutput)
    (accepted : runSupportingFull bootstrap limits numbers root ref inputs world claim = .ok output)
    (artifact : FamilyArtifact) (member : artifact ∈ CandidateFiniteSourceCatalog.allArtifacts output.catalogs.payload) :
    artifact.sourceKind = FamilyBody.sourceKind artifact.body ∧
      artifact.ref.key.artifact = FamilyBody.identity artifact.body :=
  ((supporting_full_exact _ _ _ _ _ _ _ _ _).mp accepted).2 artifact member

theorem supporting_original_interpretation_with_remaining_policies
    (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : FamilyOutput)
    (policy : CandidateIntentSourceContract.Policies FamilyBody)
    (accepted : runSupportingFull bootstrap limits numbers root ref inputs world claim = .ok output)
    (remaining : CandidateOriginalBytePipeline.RemainingPolicies policy output.catalogs.metadata
      output.catalogs.payload world claim output.parent.relation) :
    ∃ sourceAst qualifierAst,
      CandidateIntentSourceContract.SourceInterpretation (CandidateOriginalBytePipeline.bytePolicy policy)
        output.catalogs.metadata output.catalogs.payload world output.parent.relation.resolution.ref
        inputs.parent.relation.source.content sourceAst qualifierAst output.parent.relation.projected
        output.parent.relation.qualifiers claim := by
  have original := (CandidateRetainedCatalogs.cached_full_exact _ _ _ _ _ _ _ _ _ _).mpr
    ((supporting_full_exact _ _ _ _ _ _ _ _ _).mp accepted).1
  exact CandidateRetainedCatalogs.cached_original_interpretation_with_remaining_policies
    _ _ _ _ _ _ _ _ _ _ _ original remaining

#print axioms aligned_artifact_exact
#print axioms catalog_alignment_check_exact
#print axioms supporting_full_exact
#print axioms successful_full_all_occurrences_aligned
#print axioms supporting_original_interpretation_with_remaining_policies
end RelationalSuccessor.CandidateSupportingSources
