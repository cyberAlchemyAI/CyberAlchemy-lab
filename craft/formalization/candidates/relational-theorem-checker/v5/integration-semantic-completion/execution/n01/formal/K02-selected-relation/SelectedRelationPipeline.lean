import SelectedRelationBudget
set_option autoImplicit false
namespace RelationalSuccessor.CandidateSelectedRelation
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits)
open CandidateEvidenceResources (NumericLimits)
open CandidateProfileEvidence (EvidenceStage)
open CandidateIntentSourcePipeline (FramedWorld Claim)

structure Output where
  evidence : EvidenceStage
  relation : CandidateIntentSourcePipeline.Output
  deriving DecidableEq, Repr
inductive Refusal where
  | budget
  | profile (outcome : CandidateEvidenceResources.BoundedOutcome)
  | relation (reason : CandidateCatalogSnapshots.Refusal)
  deriving DecidableEq, Repr

def Meaning {α : Type} (body : CandidateBindingAst.Decoder α) (bootstrap : Profile) (limits : Limits)
    (numbers : NumericLimits) (root ref : RevisionRef) (inputs : Inputs)
    (world : FramedWorld) (claim : Claim) (output : Output) : Prop :=
  BudgetMeaning limits inputs ∧
    CandidateEvidenceResources.BoundedPreparedMeaning bootstrap limits numbers world.frame root ref
      inputs.authority inputs.declarations inputs.selections output.evidence ∧
    CandidateCatalogSnapshots.Meaning body output.evidence.profile.profile limits numbers
      inputs.relation world claim output.relation

def run {α : Type} [DecidableEq α] (body : CandidateBindingAst.Decoder α) (bootstrap : Profile) (limits : Limits)
    (numbers : NumericLimits) (root ref : RevisionRef) (inputs : Inputs)
    (world : FramedWorld) (claim : Claim) : Except Refusal Output :=
  if budgetCheck limits inputs then
    match CandidatePreflightReuse.run bootstrap limits numbers world.frame root ref
        inputs.authority inputs.declarations inputs.selections with
    | .data (.prepared evidence) =>
      match CandidateCatalogSnapshots.run body evidence.profile.profile limits numbers inputs.relation world claim with
      | .error reason => .error (.relation reason)
      | .ok relation => .ok ⟨evidence, relation⟩
    | outcome => .error (.profile outcome)
  else .error .budget

theorem run_sound {α : Type} [DecidableEq α] (body : CandidateBindingAst.Decoder α) (bootstrap : Profile) (limits : Limits)
    (numbers : NumericLimits) (root ref : RevisionRef) (inputs : Inputs)
    (world : FramedWorld) (claim : Claim) (output : Output)
    (accepted : run body bootstrap limits numbers root ref inputs world claim = .ok output) :
    Meaning body bootstrap limits numbers root ref inputs world claim output := by
  unfold run at accepted
  split at accepted
  · rename_i budget
    cases checked : CandidatePreflightReuse.run bootstrap limits numbers world.frame root ref
        inputs.authority inputs.declarations inputs.selections with
    | budgetRefused => simp only [checked] at accepted; contradiction
    | sourceRefused index capture reason => simp only [checked] at accepted; contradiction
    | data data =>
      cases data with
      | profileDataRefused => simp only [checked] at accepted; contradiction
      | authorityDataRefused => simp only [checked] at accepted; contradiction
      | evidenceJoinRefused => simp only [checked] at accepted; contradiction
      | prepared evidence =>
        simp only [checked] at accepted
        cases found : CandidateCatalogSnapshots.run body evidence.profile.profile limits numbers inputs.relation world claim with
        | error reason => simp only [found] at accepted; contradiction
        | ok relation =>
          simp only [found, Except.ok.injEq] at accepted
          subst output
          exact ⟨(budget_exact _ _).mp budget,
            (CandidatePreflightReuse.reusable_prepared_exact _ _ _ _ _ _ _ _ _ _).mp checked,
            (CandidateCatalogSnapshots.run_exact _ _ _ _ _ _ _ _).mp found⟩
  · contradiction

theorem run_complete {α : Type} [DecidableEq α] (body : CandidateBindingAst.Decoder α) (bootstrap : Profile) (limits : Limits)
    (numbers : NumericLimits) (root ref : RevisionRef) (inputs : Inputs)
    (world : FramedWorld) (claim : Claim) (output : Output)
    (meaning : Meaning body bootstrap limits numbers root ref inputs world claim output) :
    run body bootstrap limits numbers root ref inputs world claim = .ok output := by
  have budget := (budget_exact _ _).mpr meaning.1
  have profile := (CandidatePreflightReuse.reusable_prepared_exact _ _ _ _ _ _ _ _ _ _).mpr meaning.2.1
  have relation := (CandidateCatalogSnapshots.run_exact _ _ _ _ _ _ _ _).mpr meaning.2.2
  simp only [run, budget, if_true, profile, relation]

theorem run_exact {α : Type} [DecidableEq α] (body : CandidateBindingAst.Decoder α) (bootstrap : Profile) (limits : Limits)
    (numbers : NumericLimits) (root ref : RevisionRef) (inputs : Inputs)
    (world : FramedWorld) (claim : Claim) (output : Output) :
    run body bootstrap limits numbers root ref inputs world claim = .ok output ↔
      Meaning body bootstrap limits numbers root ref inputs world claim output :=
  ⟨run_sound _ _ _ _ _ _ _ _ _ _, run_complete _ _ _ _ _ _ _ _ _ _⟩

theorem selected_profile_and_world_frame_bound {α : Type} [DecidableEq α]
    (body : CandidateBindingAst.Decoder α) (bootstrap : Profile) (limits : Limits)
    (numbers : NumericLimits) (root ref : RevisionRef) (inputs : Inputs)
    (world : FramedWorld) (claim : Claim) (output : Output)
    (accepted : run body bootstrap limits numbers root ref inputs world claim = .ok output) :
    CandidateProfileSelection.SelectedDataMeaning bootstrap limits world.frame inputs.declarations inputs.selections output.evidence.profile ∧
      output.evidence.profile.frame = world.frame ∧
      CandidateCatalogSnapshots.Meaning body output.evidence.profile.profile limits numbers inputs.relation world claim output.relation := by
  have meaning := (run_exact _ _ _ _ _ _ _ _ _ _).mp accepted
  exact ⟨meaning.2.1.2.2.profile, meaning.2.1.2.2.profile.frame, meaning.2.2⟩

theorem all_relation_capture_profiles_bound {α : Type} [DecidableEq α]
    (body : CandidateBindingAst.Decoder α) (bootstrap : Profile) (limits : Limits)
    (numbers : NumericLimits) (root ref : RevisionRef) (inputs : Inputs)
    (world : FramedWorld) (claim : Claim) (output : Output)
    (accepted : run body bootstrap limits numbers root ref inputs world claim = .ok output) :
    ∀ capture ∈ inputs.relation.original.captures,
      capture.digestProfile = output.evidence.profile.profile.ref := by
  have meaning := (run_exact _ _ _ _ _ _ _ _ _ _).mp accepted
  rcases meaning.2.2 with ⟨catalogs, _, relation⟩
  intro capture member
  have preflight := relation.2.1 capture member
  exact preflight.2.1.1.1.symm

theorem actual_root_boundary_still_required {α : Type} [DecidableEq α]
    (body : CandidateBindingAst.Decoder α) (bootstrap : Profile) (limits : Limits)
    (numbers : NumericLimits) (root ref : RevisionRef) (inputs : Inputs)
    (world : FramedWorld) (claim : Claim) (output : Output) (policy : CandidateProfileEvidence.RootPolicy)
    (accepted : run body bootstrap limits numbers root ref inputs world claim = .ok output)
    (authentic : policy.authoritativeSnapshot root world.frame inputs.authority) :
    CandidateProfileSelection.OwnedSelectionMeaning
      (CandidateProfileEvidence.interpretedRequirements policy bootstrap limits root ref inputs.authority output.evidence.authority)
      bootstrap limits world.frame inputs.declarations inputs.selections output.evidence.profile := by
  have meaning := (run_exact _ _ _ _ _ _ _ _ _ _).mp accepted
  exact CandidateProfileEvidence.prepared_evidence_and_authentic_boundary_construct_ownership
    policy bootstrap limits world.frame root ref inputs.authority inputs.declarations inputs.selections output.evidence
    meaning.2.1.2.2 authentic

#print axioms run_sound
#print axioms run_complete
#print axioms run_exact
#print axioms selected_profile_and_world_frame_bound
#print axioms all_relation_capture_profiles_bound
#print axioms actual_root_boundary_still_required
end RelationalSuccessor.CandidateSelectedRelation
