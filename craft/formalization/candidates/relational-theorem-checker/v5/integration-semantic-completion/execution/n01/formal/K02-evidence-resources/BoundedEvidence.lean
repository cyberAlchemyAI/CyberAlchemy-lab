import ResourcePreflight
set_option autoImplicit false
namespace RelationalSuccessor.CandidateEvidenceResources
open CandidateBindingCapture (Envelope)
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits)
open CandidateProfileEvidence (EvidenceStage PreparedEvidenceMeaning AuthorityDataMeaning EvidenceRowsMeaning)

inductive DataOutcome where
  | profileDataRefused
  | authorityDataRefused
  | evidenceJoinRefused
  | prepared (stage : EvidenceStage)
  deriving DecidableEq, Repr

def classifyData (bootstrap : Profile) (limits : Limits) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (declarations selections : List Envelope) : DataOutcome :=
  match CandidateProfileSelection.prepareSelectedProfile bootstrap limits frame declarations selections with
  | none=>.profileDataRefused
  | some profile=>match CandidateProfileEvidence.prepareAuthority bootstrap limits.perCaptureBytes frame root ref capture with
    | none=>.authorityDataRefused
    | some authority=>if CandidateProfileEvidence.evidenceRowsCheck frame profile authority then .prepared ⟨profile,authority⟩ else .evidenceJoinRefused

def DataOutcomeMeaning (bootstrap : Profile) (limits : Limits) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (declarations selections : List Envelope) : DataOutcome → Prop
  | .profileDataRefused=>¬∃profile,CandidateProfileSelection.SelectedDataMeaning bootstrap limits frame declarations selections profile
  | .authorityDataRefused=>(∃profile,CandidateProfileSelection.SelectedDataMeaning bootstrap limits frame declarations selections profile) ∧
      ¬∃authority,AuthorityDataMeaning bootstrap limits.perCaptureBytes frame root ref capture authority
  | .evidenceJoinRefused=>∃profile authority,
      CandidateProfileSelection.SelectedDataMeaning bootstrap limits frame declarations selections profile ∧
      AuthorityDataMeaning bootstrap limits.perCaptureBytes frame root ref capture authority ∧ ¬EvidenceRowsMeaning frame profile authority
  | .prepared stage=>PreparedEvidenceMeaning bootstrap limits frame root ref capture declarations selections stage

theorem authority_none_exact (bootstrap : Profile) (budget : Nat) (frame : Frame) (root ref : RevisionRef) (capture : Envelope) :
    CandidateProfileEvidence.prepareAuthority bootstrap budget frame root ref capture=none ↔
      ¬∃authority,AuthorityDataMeaning bootstrap budget frame root ref capture authority := by
  constructor
  · intro absent;rintro ⟨authority,meaning⟩
    have found:=(CandidateProfileEvidence.authority_preparation_exact bootstrap budget frame root ref capture authority).mpr meaning
    rw [absent] at found;contradiction
  · intro absent
    cases found : CandidateProfileEvidence.prepareAuthority bootstrap budget frame root ref capture with
    | none=>rfl
    | some authority=>exact False.elim (absent ⟨authority,(CandidateProfileEvidence.authority_preparation_exact bootstrap budget frame root ref capture authority).mp found⟩)

theorem data_prepared_exact (bootstrap : Profile) (limits : Limits) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (declarations selections : List Envelope) (stage : EvidenceStage) :
    classifyData bootstrap limits frame root ref capture declarations selections=.prepared stage ↔
      PreparedEvidenceMeaning bootstrap limits frame root ref capture declarations selections stage := by
  constructor
  · intro accepted
    unfold classifyData at accepted
    cases p : CandidateProfileSelection.prepareSelectedProfile bootstrap limits frame declarations selections with
    | none=>simp only [p] at accepted;contradiction
    | some profile=>
      cases a : CandidateProfileEvidence.prepareAuthority bootstrap limits.perCaptureBytes frame root ref capture with
      | none=>simp only [p,a] at accepted;contradiction
      | some authority=>
        simp only [p,a] at accepted
        split at accepted
        · rename_i guard
          cases accepted
          exact ⟨(CandidateProfileSelection.selected_preparation_exact bootstrap limits frame declarations selections profile).mp p,
            (CandidateProfileEvidence.authority_preparation_exact bootstrap limits.perCaptureBytes frame root ref capture authority).mp a,
            (CandidateProfileEvidence.evidence_rows_exact frame profile authority).mp guard⟩
        · contradiction
  · intro meaning
    have p:=(CandidateProfileSelection.selected_preparation_exact bootstrap limits frame declarations selections stage.profile).mpr meaning.profile
    have a:=(CandidateProfileEvidence.authority_preparation_exact bootstrap limits.perCaptureBytes frame root ref capture stage.authority).mpr meaning.authority
    have rows:=(CandidateProfileEvidence.evidence_rows_exact frame stage.profile stage.authority).mpr meaning.rows
    cases stage
    simp only [classifyData,p,a,rows,if_true]

theorem data_outcome_has_independent_cause (bootstrap : Profile) (limits : Limits) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (declarations selections : List Envelope) :
    DataOutcomeMeaning bootstrap limits frame root ref capture declarations selections
      (classifyData bootstrap limits frame root ref capture declarations selections) := by
  cases p : CandidateProfileSelection.prepareSelectedProfile bootstrap limits frame declarations selections with
  | none=>
    simp only [classifyData,p,DataOutcomeMeaning]
    exact (CandidateProfileSelection.selected_preparation_none_exact bootstrap limits frame declarations selections).mp p
  | some profile=>
    have pm:=(CandidateProfileSelection.selected_preparation_exact bootstrap limits frame declarations selections profile).mp p
    cases a : CandidateProfileEvidence.prepareAuthority bootstrap limits.perCaptureBytes frame root ref capture with
    | none=>
      simp only [classifyData,p,a,DataOutcomeMeaning]
      exact ⟨⟨profile,pm⟩,(authority_none_exact bootstrap limits.perCaptureBytes frame root ref capture).mp a⟩
    | some authority=>
      have am:=(CandidateProfileEvidence.authority_preparation_exact bootstrap limits.perCaptureBytes frame root ref capture authority).mp a
      simp only [classifyData,p,a]
      split
      · rename_i rows
        exact ⟨pm,am,(CandidateProfileEvidence.evidence_rows_exact frame profile authority).mp rows⟩
      · rename_i absent
        exact ⟨profile,authority,pm,am,fun rows=>absent ((CandidateProfileEvidence.evidence_rows_exact frame profile authority).mpr rows)⟩

inductive BoundedOutcome where
  | budgetRefused
  | sourceRefused (index : Nat) (capture : Envelope) (reason : PreflightOutcome)
  | data (outcome : DataOutcome)
  deriving DecidableEq, Repr

def BoundedPreparedMeaning (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (declarations selections : List Envelope) (stage : EvidenceStage) : Prop :=
  CombinedBudgetMeaning limits capture declarations selections ∧
    AllPreflightMeaning bootstrap limits.perCaptureBytes numbers (allInputs capture declarations selections) ∧
    PreparedEvidenceMeaning bootstrap limits frame root ref capture declarations selections stage

def classifyBoundedEvidence (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (declarations selections : List Envelope) : BoundedOutcome :=
  if combinedBudgetCheck limits capture declarations selections then
    match firstSourceRefusal bootstrap limits.perCaptureBytes numbers (allInputs capture declarations selections) with
    | some (index,input,reason)=>.sourceRefused index input reason
    | none=>.data (classifyData bootstrap limits frame root ref capture declarations selections)
  else .budgetRefused

theorem bounded_prepared_exact (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (declarations selections : List Envelope) (stage : EvidenceStage) :
    classifyBoundedEvidence bootstrap limits numbers frame root ref capture declarations selections=.data (.prepared stage) ↔
      BoundedPreparedMeaning bootstrap limits numbers frame root ref capture declarations selections stage := by
  constructor
  · intro accepted
    unfold classifyBoundedEvidence at accepted
    split at accepted
    · rename_i budget
      cases preflight : firstSourceRefusal bootstrap limits.perCaptureBytes numbers (allInputs capture declarations selections) with
      | some refused=>simp only [preflight] at accepted;contradiction
      | none=>
        simp only [preflight,BoundedOutcome.data.injEq] at accepted
        exact ⟨(combined_budget_exact limits capture declarations selections).mp budget,
          (all_preflight_exact bootstrap limits.perCaptureBytes numbers (allInputs capture declarations selections)).mp preflight,
          (data_prepared_exact bootstrap limits frame root ref capture declarations selections stage).mp accepted⟩
    · contradiction
  · rintro ⟨budget,preflight,prepared⟩
    simp only [classifyBoundedEvidence,(combined_budget_exact limits capture declarations selections).mpr budget,if_true,
      (all_preflight_exact bootstrap limits.perCaptureBytes numbers (allInputs capture declarations selections)).mpr preflight,
      (data_prepared_exact bootstrap limits frame root ref capture declarations selections stage).mpr prepared]

theorem bounded_budget_refusal_exact (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (declarations selections : List Envelope) :
    classifyBoundedEvidence bootstrap limits numbers frame root ref capture declarations selections=.budgetRefused ↔
      ¬CombinedBudgetMeaning limits capture declarations selections := by
  rw [←combined_budget_exact limits capture declarations selections]
  cases budget : combinedBudgetCheck limits capture declarations selections with
  | false=>simp [classifyBoundedEvidence,budget]
  | true=>
    cases preflight : firstSourceRefusal bootstrap limits.perCaptureBytes numbers (allInputs capture declarations selections) with
    | none=>simp [classifyBoundedEvidence,budget,preflight]
    | some row=>rcases row with ⟨index,input,reason⟩;simp [classifyBoundedEvidence,budget,preflight]

theorem bounded_success_retains_original_inputs (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (declarations selections : List Envelope) (stage : EvidenceStage)
    (meaning : BoundedPreparedMeaning bootstrap limits numbers frame root ref capture declarations selections stage) :
    stage.profile.declarations.map CandidateBindingCapture.Prepared.envelope=declarations ∧
      stage.profile.selections.map CandidateBindingCapture.Prepared.envelope=selections ∧ stage.authority.envelope=capture :=
  CandidateProfileEvidence.prepared_evidence_retains_inputs bootstrap limits frame root ref capture declarations selections stage meaning.2.2

theorem bounded_success_still_requires_authentic_boundary (policy : CandidateProfileEvidence.RootPolicy) (bootstrap : Profile)
    (limits : Limits) (numbers : NumericLimits) (frame : Frame) (root ref : RevisionRef) (capture : Envelope)
    (declarations selections : List Envelope) (stage : EvidenceStage)
    (meaning : BoundedPreparedMeaning bootstrap limits numbers frame root ref capture declarations selections stage)
    (authentic : policy.authoritativeSnapshot root frame capture) :
    CandidateProfileSelection.OwnedSelectionMeaning
      (CandidateProfileEvidence.interpretedRequirements policy bootstrap limits root ref capture stage.authority)
      bootstrap limits frame declarations selections stage.profile :=
  CandidateProfileEvidence.prepared_evidence_and_authentic_boundary_construct_ownership policy bootstrap limits frame root ref capture
    declarations selections stage meaning.2.2 authentic

theorem data_outcome_meaning_exact (bootstrap : Profile) (limits : Limits) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (declarations selections : List Envelope) (outcome : DataOutcome) :
    classifyData bootstrap limits frame root ref capture declarations selections=outcome ↔
      DataOutcomeMeaning bootstrap limits frame root ref capture declarations selections outcome := by
  constructor
  · intro classified;subst outcome
    exact data_outcome_has_independent_cause bootstrap limits frame root ref capture declarations selections
  · intro meaning
    cases outcome with
    | profileDataRefused=>
      have absent:=(CandidateProfileSelection.selected_preparation_none_exact bootstrap limits frame declarations selections).mpr meaning
      simp only [classifyData,absent]
    | authorityDataRefused=>
      rcases meaning with ⟨⟨profile,pm⟩,noAuthority⟩
      have p:=(CandidateProfileSelection.selected_preparation_exact bootstrap limits frame declarations selections profile).mpr pm
      have a:=(authority_none_exact bootstrap limits.perCaptureBytes frame root ref capture).mpr noAuthority
      simp only [classifyData,p,a]
    | evidenceJoinRefused=>
      rcases meaning with ⟨profile,authority,pm,am,noRows⟩
      have p:=(CandidateProfileSelection.selected_preparation_exact bootstrap limits frame declarations selections profile).mpr pm
      have a:=(CandidateProfileEvidence.authority_preparation_exact bootstrap limits.perCaptureBytes frame root ref capture authority).mpr am
      have rows : CandidateProfileEvidence.evidenceRowsCheck frame profile authority≠true := fun good=>noRows ((CandidateProfileEvidence.evidence_rows_exact frame profile authority).mp good)
      simp only [classifyData,p,a,if_neg rows]
    | prepared stage=>exact (data_prepared_exact bootstrap limits frame root ref capture declarations selections stage).mpr meaning

def BoundedOutcomeMeaning (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (declarations selections : List Envelope) : BoundedOutcome → Prop
  | .budgetRefused=>¬CombinedBudgetMeaning limits capture declarations selections
  | .sourceRefused index input reason=>CombinedBudgetMeaning limits capture declarations selections ∧
      ∃ before after,allInputs capture declarations selections=before++input::after ∧ before.length=index ∧
        AllPreflightMeaning bootstrap limits.perCaptureBytes numbers before ∧
        classifyPreflight bootstrap limits.perCaptureBytes numbers input=reason ∧ reason≠.ready
  | .data outcome=>CombinedBudgetMeaning limits capture declarations selections ∧
      AllPreflightMeaning bootstrap limits.perCaptureBytes numbers (allInputs capture declarations selections) ∧
      DataOutcomeMeaning bootstrap limits frame root ref capture declarations selections outcome

theorem bounded_outcome_has_independent_cause (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (declarations selections : List Envelope) :
    BoundedOutcomeMeaning bootstrap limits numbers frame root ref capture declarations selections
      (classifyBoundedEvidence bootstrap limits numbers frame root ref capture declarations selections) := by
  unfold classifyBoundedEvidence
  split
  · rename_i budget
    have bm:=(combined_budget_exact limits capture declarations selections).mp budget
    cases checked : firstSourceRefusal bootstrap limits.perCaptureBytes numbers (allInputs capture declarations selections) with
    | none=>
      simp only [BoundedOutcomeMeaning]
      exact ⟨bm,(all_preflight_exact bootstrap limits.perCaptureBytes numbers (allInputs capture declarations selections)).mp checked,
        data_outcome_has_independent_cause bootstrap limits frame root ref capture declarations selections⟩
    | some row=>
      rcases row with ⟨index,input,reason⟩
      exact ⟨bm,first_source_refusal_exact_position bootstrap limits.perCaptureBytes numbers (allInputs capture declarations selections) index input reason checked⟩
  · rename_i absent
    exact fun bm=>absent ((combined_budget_exact limits capture declarations selections).mpr bm)
#print axioms authority_none_exact
#print axioms data_prepared_exact
#print axioms data_outcome_has_independent_cause
#print axioms bounded_prepared_exact
#print axioms bounded_budget_refusal_exact
#print axioms bounded_success_retains_original_inputs
#print axioms bounded_success_still_requires_authentic_boundary
#print axioms data_outcome_meaning_exact
#print axioms bounded_outcome_has_independent_cause
end RelationalSuccessor.CandidateEvidenceResources
