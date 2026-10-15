import BodyKindDispatch
import CachedNestedEntry
set_option autoImplicit false
namespace RelationalSuccessor.CandidateBodyDispatch
open CandidateBindingAst (J Decoder)
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits)
open CandidateEvidenceResources (NumericLimits)
open CandidateIntentSourcePipeline (FramedWorld Claim)
open CandidateNestedProvenance (Inputs)
abbrev PayloadArtifact := CandidateFiniteSourceCatalog.Artifact PayloadBody
abbrev PayloadOutput := CandidateNestedProvenance.Output PayloadBody

def ArtifactAlignment (artifact : PayloadArtifact) : Prop :=
  artifact.sourceKind = kindName (bodyKind artifact.body) ∧
    artifact.ref.key.artifact = CandidateTypedBodies.Body.identity artifact.body

instance : DecidablePred ArtifactAlignment := fun artifact => by
  unfold ArtifactAlignment
  infer_instance

def alignedArtifact : Decoder PayloadArtifact :=
  CandidateTypedBodies.constrained (CandidateCatalogSnapshots.artifact bodyDecoder) ArtifactAlignment

def AlignedArtifactMeaning (ast : J) (artifact : PayloadArtifact) : Prop :=
  CandidateCatalogSnapshots.ArtifactMeaning bodyDecoder ast artifact ∧ ArtifactAlignment artifact

theorem aligned_artifact_exact (ast : J) (artifact : PayloadArtifact) :
    alignedArtifact.decode ast = some artifact ↔ AlignedArtifactMeaning ast artifact :=
  alignedArtifact.exact ast artifact

def CatalogAlignment (catalogs : CandidateCatalogSnapshots.Catalogs PayloadBody) : Prop :=
  ∀ artifact ∈ CandidateFiniteSourceCatalog.allArtifacts catalogs.payload, ArtifactAlignment artifact

def alignmentCheck (catalogs : CandidateCatalogSnapshots.Catalogs PayloadBody) : Bool :=
  (CandidateFiniteSourceCatalog.allArtifacts catalogs.payload).all (fun artifact => decide (ArtifactAlignment artifact))

theorem catalog_alignment_check_exact (catalogs : CandidateCatalogSnapshots.Catalogs PayloadBody) :
    alignmentCheck catalogs = true ↔ CatalogAlignment catalogs := by
  simp [alignmentCheck,CatalogAlignment,List.all_eq_true]

inductive TypedRefusal where
  | original (reason : CandidateNestedProvenance.FullRefusal)
  | alignment
  deriving DecidableEq, Repr

def runTypedFull (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) :
    Except TypedRefusal PayloadOutput :=
  match CandidateRetainedCatalogs.runCachedFull bodyDecoder bootstrap limits numbers root ref inputs world claim with
  | .error reason => .error (.original reason)
  | .ok output => if alignmentCheck output.catalogs then .ok output else .error .alignment

def TypedFullMeaning (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim)
    (output : PayloadOutput) : Prop :=
  CandidateNestedProvenance.FullMeaning bodyDecoder bootstrap limits numbers root ref inputs world claim output ∧
    CatalogAlignment output.catalogs

theorem typed_full_exact (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : PayloadOutput) :
    runTypedFull bootstrap limits numbers root ref inputs world claim = .ok output ↔
      TypedFullMeaning bootstrap limits numbers root ref inputs world claim output := by
  constructor
  · intro accepted
    cases found : CandidateRetainedCatalogs.runCachedFull bodyDecoder bootstrap limits numbers root ref inputs world claim with
    | error reason => simp [runTypedFull,found] at accepted
    | ok actual =>
      simp only [runTypedFull,found] at accepted
      split at accepted
      · rename_i aligned
        have same : actual = output := Except.ok.inj accepted
        subst output
        exact ⟨(CandidateRetainedCatalogs.cached_full_exact _ _ _ _ _ _ _ _ _ _).mp found,
          (catalog_alignment_check_exact _).mp aligned⟩
      · contradiction
  · rintro ⟨meaning,aligned⟩
    have found := (CandidateRetainedCatalogs.cached_full_exact _ _ _ _ _ _ _ _ _ _).mpr meaning
    simp [runTypedFull,found,(catalog_alignment_check_exact _).mpr aligned]

theorem successful_full_all_occurrences_aligned (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : PayloadOutput)
    (accepted : runTypedFull bootstrap limits numbers root ref inputs world claim = .ok output)
    (artifact : PayloadArtifact) (member : artifact ∈ CandidateFiniteSourceCatalog.allArtifacts output.catalogs.payload) :
    artifact.sourceKind = kindName (bodyKind artifact.body) ∧
      artifact.ref.key.artifact = CandidateTypedBodies.Body.identity artifact.body :=
  ((typed_full_exact _ _ _ _ _ _ _ _ _).mp accepted).2 artifact member

theorem typed_original_interpretation_with_remaining_policies
    (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : PayloadOutput)
    (policy : CandidateIntentSourceContract.Policies PayloadBody)
    (accepted : runTypedFull bootstrap limits numbers root ref inputs world claim = .ok output)
    (remaining : CandidateOriginalBytePipeline.RemainingPolicies policy output.catalogs.metadata
      output.catalogs.payload world claim output.parent.relation) :
    ∃ sourceAst qualifierAst,
      CandidateIntentSourceContract.SourceInterpretation (CandidateOriginalBytePipeline.bytePolicy policy)
        output.catalogs.metadata output.catalogs.payload world output.parent.relation.resolution.ref
        inputs.parent.relation.source.content sourceAst qualifierAst output.parent.relation.projected
        output.parent.relation.qualifiers claim := by
  have original := (CandidateRetainedCatalogs.cached_full_exact _ _ _ _ _ _ _ _ _ _).mpr
    ((typed_full_exact _ _ _ _ _ _ _ _ _).mp accepted).1
  exact CandidateRetainedCatalogs.cached_original_interpretation_with_remaining_policies
    _ _ _ _ _ _ _ _ _ _ _ original remaining

#print axioms aligned_artifact_exact
#print axioms catalog_alignment_check_exact
#print axioms typed_full_exact
#print axioms successful_full_all_occurrences_aligned
#print axioms typed_original_interpretation_with_remaining_policies
end RelationalSuccessor.CandidateBodyDispatch
