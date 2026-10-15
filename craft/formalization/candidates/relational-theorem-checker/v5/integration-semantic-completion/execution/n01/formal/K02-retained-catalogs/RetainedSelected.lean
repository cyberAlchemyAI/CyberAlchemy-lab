import RetainedRelation
set_option autoImplicit false
namespace RelationalSuccessor.CandidateRetainedCatalogs
open CandidateBindingAst (Decoder)
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits)
open CandidateEvidenceResources (NumericLimits)
open CandidateIntentSourcePipeline (FramedWorld Claim)

structure SelectedState (α : Type) (limits : Limits) (numbers : NumericLimits) (inputs : CandidateSelectedRelation.Inputs) where
  evidence : CandidateProfileEvidence.EvidenceStage
  state : RelationState α evidence.profile.profile limits numbers inputs.relation

def SelectedState.public {α : Type} {limits : Limits} {numbers : NumericLimits} {inputs : CandidateSelectedRelation.Inputs}
    (state : SelectedState α limits numbers inputs) : CandidateSelectedRelation.Output :=
  ⟨state.evidence,state.state.relation⟩
def SelectedState.fullPublic {α : Type} {limits : Limits} {numbers : NumericLimits} {inputs : CandidateSelectedRelation.Inputs}
    (state : SelectedState α limits numbers inputs) : CandidateNestedProvenance.Output α :=
  ⟨state.public,state.state.catalogs⟩
def runSelected {α : Type} [DecidableEq α] (body : Decoder α) (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : CandidateSelectedRelation.Inputs) (world : FramedWorld) (claim : Claim) :
    Except CandidateSelectedRelation.Refusal (SelectedState α limits numbers inputs) :=
  if CandidateSelectedRelation.budgetCheck limits inputs then
    match CandidatePreflightReuse.run bootstrap limits numbers world.frame root ref inputs.authority inputs.declarations inputs.selections with
    | .data (.prepared evidence) =>
      match runRelation body evidence.profile.profile limits numbers inputs.relation world claim with
      | .error reason => .error (.relation reason)
      | .ok state => .ok ⟨evidence,state⟩
    | reason => .error (.profile reason)
  else .error .budget

def eraseSelected {α : Type} {limits : Limits} {numbers : NumericLimits} {inputs : CandidateSelectedRelation.Inputs} :
    Except CandidateSelectedRelation.Refusal (SelectedState α limits numbers inputs) →
      Except CandidateSelectedRelation.Refusal CandidateSelectedRelation.Output
  | .error reason => .error reason
  | .ok state => .ok state.public

theorem selected_erasure_exact {α : Type} [DecidableEq α] (body : Decoder α) (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : CandidateSelectedRelation.Inputs) (world : FramedWorld) (claim : Claim) :
    eraseSelected (runSelected body bootstrap limits numbers root ref inputs world claim) =
      CandidateSelectedRelation.run body bootstrap limits numbers root ref inputs world claim := by
  unfold runSelected CandidateSelectedRelation.run
  by_cases budget : CandidateSelectedRelation.budgetCheck limits inputs = true
  · simp only [budget,if_true]
    cases profileFound : CandidatePreflightReuse.run bootstrap limits numbers world.frame root ref inputs.authority inputs.declarations inputs.selections with
    | budgetRefused => rfl
    | sourceRefused index capture reason => rfl
    | data data =>
      cases data with
      | profileDataRefused => rfl
      | authorityDataRefused => rfl
      | evidenceJoinRefused => rfl
      | prepared evidence =>
        have erasure := relation_erasure_exact body evidence.profile.profile limits numbers inputs.relation world claim
        cases relationFound : runRelation body evidence.profile.profile limits numbers inputs.relation world claim with
        | error reason =>
          rw [relationFound] at erasure
          simp only [eraseRelation] at erasure
          simp only [relationFound,eraseSelected,←erasure]
        | ok state =>
          rw [relationFound] at erasure
          simp only [eraseRelation] at erasure
          simp only [relationFound,eraseSelected,SelectedState.public,←erasure]
  · simp only [if_neg budget,eraseSelected]

theorem retained_selected_catalogs_sound {α : Type} [DecidableEq α] (body : Decoder α) (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : CandidateSelectedRelation.Inputs) (world : FramedWorld) (claim : Claim)
    (state : SelectedState α limits numbers inputs)
    (accepted : runSelected body bootstrap limits numbers root ref inputs world claim = .ok state) :
    CandidateCatalogSnapshots.CapturedMeaning body inputs.relation state.state.catalogs := by
  unfold runSelected at accepted
  split at accepted
  · cases profileFound : CandidatePreflightReuse.run bootstrap limits numbers world.frame root ref inputs.authority inputs.declarations inputs.selections with
    | budgetRefused => simp only [profileFound] at accepted; contradiction
    | sourceRefused index capture reason => simp only [profileFound] at accepted; contradiction
    | data data =>
      cases data with
      | profileDataRefused => simp only [profileFound] at accepted; contradiction
      | authorityDataRefused => simp only [profileFound] at accepted; contradiction
      | evidenceJoinRefused => simp only [profileFound] at accepted; contradiction
      | prepared evidence =>
        simp only [profileFound] at accepted
        cases relationFound : runRelation body evidence.profile.profile limits numbers inputs.relation world claim with
        | error reason => simp only [relationFound] at accepted; contradiction
        | ok relation =>
          simp only [relationFound,Except.ok.injEq] at accepted
          subst state
          exact (retained_relation_sound _ _ _ _ _ _ _ _ relationFound).1
  · contradiction

theorem retained_selected_original_meaning {α : Type} [DecidableEq α] (body : Decoder α) (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (root ref : RevisionRef) (inputs : CandidateSelectedRelation.Inputs) (world : FramedWorld) (claim : Claim)
    (state : SelectedState α limits numbers inputs)
    (accepted : runSelected body bootstrap limits numbers root ref inputs world claim = .ok state) :
    CandidateSelectedRelation.Meaning body bootstrap limits numbers root ref inputs world claim state.public ∧
      CandidateCatalogSnapshots.CapturedMeaning body inputs.relation state.state.catalogs := by
  have erasure := selected_erasure_exact body bootstrap limits numbers root ref inputs world claim
  rw [accepted] at erasure
  simp only [eraseSelected] at erasure
  exact ⟨(CandidateSelectedRelation.run_exact _ _ _ _ _ _ _ _ _ _).mp erasure.symm,
    retained_selected_catalogs_sound _ _ _ _ _ _ _ _ _ _ accepted⟩

#print axioms selected_erasure_exact
#print axioms retained_selected_catalogs_sound
#print axioms retained_selected_original_meaning
end RelationalSuccessor.CandidateRetainedCatalogs
