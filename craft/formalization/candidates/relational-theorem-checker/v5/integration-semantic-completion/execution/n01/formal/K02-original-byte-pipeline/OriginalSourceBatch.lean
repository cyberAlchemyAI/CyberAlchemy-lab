import ReusableEntry
import IntentSourcePipeline
set_option autoImplicit false
namespace RelationalSuccessor.CandidateOriginalBytePipeline
open CandidateBindingCapture (Envelope)
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits)
open CandidateEvidenceResources (NumericLimits AllPreflightMeaning)
open CandidatePreflightReuse (CertifiedInput)

structure Inputs where
  source : Envelope
  qualifiers : Envelope
  catalogs : List Envelope
  deriving DecidableEq, Repr
def Inputs.captures (inputs : Inputs) : List Envelope :=
  inputs.source :: inputs.qualifiers :: inputs.catalogs
def BudgetMeaning (limits : Limits) (inputs : Inputs) : Prop :=
  CandidateEvidenceResources.CombinedBudgetMeaning limits inputs.source
    (inputs.qualifiers :: inputs.catalogs) []
def budgetCheck (limits : Limits) (inputs : Inputs) : Bool :=
  CandidateEvidenceResources.combinedBudgetCheck limits inputs.source
    (inputs.qualifiers :: inputs.catalogs) []
inductive Refusal where
  | budget
  | source (failure : CandidatePreflightReuse.Failure)
  | relation
  deriving DecidableEq, Repr

def prepare (profile : Profile) (limits : Limits) (numbers : NumericLimits) (inputs : Inputs) :
    Except Refusal (List (CertifiedInput profile limits.perCaptureBytes numbers)) :=
  if budgetCheck limits inputs then
    match CandidatePreflightReuse.collect profile limits.perCaptureBytes numbers inputs.captures with
    | .error failure => .error (.source failure)
    | .ok captures => .ok captures
  else .error .budget

def BatchMeaning (profile : Profile) (limits : Limits) (numbers : NumericLimits) (inputs : Inputs)
    (captures : List (CertifiedInput profile limits.perCaptureBytes numbers)) : Prop :=
  BudgetMeaning limits inputs ∧ captures.map (fun capture => capture.val.capture) = inputs.captures
abbrev Batch (profile : Profile) (limits : Limits) (numbers : NumericLimits) (inputs : Inputs) :=
  {captures : List (CertifiedInput profile limits.perCaptureBytes numbers) //
    BatchMeaning profile limits numbers inputs captures}

theorem prepare_sound (profile : Profile) (limits : Limits) (numbers : NumericLimits) (inputs : Inputs)
    (captures : List (CertifiedInput profile limits.perCaptureBytes numbers))
    (accepted : prepare profile limits numbers inputs = .ok captures) :
    BatchMeaning profile limits numbers inputs captures := by
  unfold prepare at accepted
  split at accepted
  · rename_i budget
    cases collected : CandidatePreflightReuse.collect profile limits.perCaptureBytes numbers inputs.captures with
    | error reason => simp only [collected] at accepted; contradiction
    | ok actual =>
      simp only [collected, Except.ok.injEq] at accepted
      subst captures
      exact ⟨(CandidateEvidenceResources.combined_budget_exact _ _ _ _).mp budget,
        CandidatePreflightReuse.collected_original_inputs _ _ _ _ _ collected⟩
  · contradiction

theorem prepare_budget_refusal_exact (profile : Profile) (limits : Limits) (numbers : NumericLimits) (inputs : Inputs) :
    prepare profile limits numbers inputs = .error .budget ↔ ¬ BudgetMeaning limits inputs := by
  unfold prepare
  by_cases budget : budgetCheck limits inputs = true
  · have valid := (CandidateEvidenceResources.combined_budget_exact _ _ _ _).mp budget
    simp only [budget, if_true]
    cases CandidatePreflightReuse.collect profile limits.perCaptureBytes numbers inputs.captures <;>
      simp [BudgetMeaning, valid]
  · have invalid : ¬ BudgetMeaning limits inputs := by
      intro valid
      exact budget ((CandidateEvidenceResources.combined_budget_exact _ _ _ _).mpr valid)
    simp only [if_neg budget, true_iff]
    exact invalid

theorem batch_all_preflight (profile : Profile) (limits : Limits) (numbers : NumericLimits) (inputs : Inputs)
    (batch : Batch profile limits numbers inputs) :
    AllPreflightMeaning profile limits.perCaptureBytes numbers inputs.captures := by
  intro capture member
  rw [←batch.property.2] at member
  rcases List.mem_map.mp member with ⟨input, _, same⟩
  subst capture
  exact ⟨input.property.1, input.property.2.1, input.val.ast,
    input.property.2.2.1, input.property.2.2.2⟩

theorem prepare_exists_exact (profile : Profile) (limits : Limits) (numbers : NumericLimits) (inputs : Inputs) :
    (∃ captures, prepare profile limits numbers inputs = .ok captures) ↔
      BudgetMeaning limits inputs ∧ AllPreflightMeaning profile limits.perCaptureBytes numbers inputs.captures := by
  constructor
  · rintro ⟨captures, accepted⟩
    have meaning := prepare_sound _ _ _ _ _ accepted
    exact ⟨meaning.1, batch_all_preflight _ _ _ _ ⟨captures, meaning⟩⟩
  · rintro ⟨budget, all⟩
    have ready := (CandidateEvidenceResources.all_preflight_exact _ _ _ _).mpr all
    have equal := CandidatePreflightReuse.collected_refusal_equal_legacy profile limits.perCaptureBytes numbers inputs.captures
    cases collected : CandidatePreflightReuse.collect profile limits.perCaptureBytes numbers inputs.captures with
    | error reason => rw [collected, ready] at equal; contradiction
    | ok captures =>
      refine ⟨captures, ?_⟩
      have checked : budgetCheck limits inputs = true :=
        (CandidateEvidenceResources.combined_budget_exact _ _ _ _).mpr budget
      simp only [prepare, checked, if_true, collected]

def checkedBatch (profile : Profile) (limits : Limits) (numbers : NumericLimits) (inputs : Inputs) :
    Except Refusal (Batch profile limits numbers inputs) :=
  match accepted : prepare profile limits numbers inputs with
  | .error reason => .error reason
  | .ok captures => .ok ⟨captures, prepare_sound _ _ _ _ _ accepted⟩
def eraseBatch {profile : Profile} {limits : Limits} {numbers : NumericLimits} {inputs : Inputs} :
    Except Refusal (Batch profile limits numbers inputs) →
      Except Refusal (List (CertifiedInput profile limits.perCaptureBytes numbers))
  | .error reason => .error reason
  | .ok batch => .ok batch.val

theorem checked_batch_exact (profile : Profile) (limits : Limits) (numbers : NumericLimits) (inputs : Inputs) :
    eraseBatch (checkedBatch profile limits numbers inputs) = prepare profile limits numbers inputs := by
  unfold checkedBatch
  split <;> rename_i _ accepted <;> simp only [eraseBatch] <;> rw [accepted] <;> rfl

theorem batch_catalog_coverage (profile : Profile) (limits : Limits) (numbers : NumericLimits) (inputs : Inputs)
    (batch : Batch profile limits numbers inputs) :
    (batch.val.drop 2).map (fun capture => capture.val.capture) = inputs.catalogs := by
  rw [List.map_drop, batch.property.2]
  rfl

#print axioms prepare_sound
#print axioms prepare_budget_refusal_exact
#print axioms batch_all_preflight
#print axioms prepare_exists_exact
#print axioms checked_batch_exact
#print axioms batch_catalog_coverage
end RelationalSuccessor.CandidateOriginalBytePipeline
