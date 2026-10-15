import RetainedSelected
set_option autoImplicit false
namespace RelationalSuccessor.CandidateRetainedCatalogs
open CandidateBindingAst (Decoder)
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits)
open CandidateEvidenceResources (NumericLimits)
open CandidateIntentSourcePipeline (FramedWorld Claim)
open CandidateNestedProvenance (Inputs FullRefusal Output)

def runCachedFull {α : Type} [DecidableEq α] (body : Decoder α) (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) : Except FullRefusal (Output α) :=
  if CandidateNestedProvenance.nestedBudgetCheck limits inputs.captures then
    match runSelected body bootstrap limits numbers root ref inputs.parent world claim with
    | .error reason => .error (.parent reason)
    | .ok state =>
      match CandidateNestedProvenance.runNested body state.evidence.profile.profile limits numbers world.frame
          (CandidateNestedProvenance.required state.state.catalogs) inputs.nested with
      | .error reason => .error (.nested reason)
      | .ok _ => .ok state.fullPublic
  else .error .budget

theorem cached_full_equal_original {α : Type} [DecidableEq α] (body : Decoder α) (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) :
    runCachedFull body bootstrap limits numbers root ref inputs world claim =
      CandidateNestedProvenance.runFull body bootstrap limits numbers root ref inputs world claim := by
  unfold runCachedFull CandidateNestedProvenance.runFull
  by_cases budget : CandidateNestedProvenance.nestedBudgetCheck limits inputs.captures = true
  · simp only [budget,if_true]
    have erasure := selected_erasure_exact body bootstrap limits numbers root ref inputs.parent world claim
    cases found : runSelected body bootstrap limits numbers root ref inputs.parent world claim with
    | error reason =>
      rw [found] at erasure
      simp only [eraseSelected] at erasure
      simp only [←erasure]
    | ok state =>
      rw [found] at erasure
      simp only [eraseSelected] at erasure
      have captured := retained_selected_catalogs_sound _ _ _ _ _ _ _ _ _ _ found
      have decoded := (CandidateNestedProvenance.raw_catalogs_exact _ _ _).mpr captured
      simp only [←erasure,decoded,SelectedState.public,SelectedState.fullPublic]
      rfl
  · simp only [if_neg budget]

theorem cached_full_exact {α : Type} [DecidableEq α] (body : Decoder α) (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : Output α) :
    runCachedFull body bootstrap limits numbers root ref inputs world claim = .ok output ↔
      CandidateNestedProvenance.FullMeaning body bootstrap limits numbers root ref inputs world claim output := by
  rw [cached_full_equal_original]
  exact CandidateNestedProvenance.full_run_exact _ _ _ _ _ _ _ _ _ _

theorem cached_original_interpretation_with_remaining_policies {α : Type} [DecidableEq α]
    (body : Decoder α) (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : Output α)
    (policy : CandidateIntentSourceContract.Policies α)
    (accepted : runCachedFull body bootstrap limits numbers root ref inputs world claim = .ok output)
    (remaining : CandidateOriginalBytePipeline.RemainingPolicies policy output.catalogs.metadata output.catalogs.payload world claim output.parent.relation) :
    ∃ sourceAst qualifierAst,
      CandidateIntentSourceContract.SourceInterpretation (CandidateOriginalBytePipeline.bytePolicy policy)
        output.catalogs.metadata output.catalogs.payload world output.parent.relation.resolution.ref
        inputs.parent.relation.source.content sourceAst qualifierAst output.parent.relation.projected
        output.parent.relation.qualifiers claim := by
  have original : CandidateNestedProvenance.runFull body bootstrap limits numbers root ref inputs world claim = .ok output := by
    rw [←cached_full_equal_original]; exact accepted
  exact CandidateNestedProvenance.successful_full_original_interpretation_with_remaining_policies
    _ _ _ _ _ _ _ _ _ _ _ original remaining

#print axioms cached_full_equal_original
#print axioms cached_full_exact
#print axioms cached_original_interpretation_with_remaining_policies
end RelationalSuccessor.CandidateRetainedCatalogs
