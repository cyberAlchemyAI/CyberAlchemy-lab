import CapturedCatalogPipeline
import ReusableEntry
import AuthorityOwnership
set_option autoImplicit false
namespace RelationalSuccessor.CandidateSelectedRelation
open CandidateBindingCapture (Envelope)
open CandidateDigestCapture (Limits)

structure Inputs where
  authority : Envelope
  declarations : List Envelope
  selections : List Envelope
  relation : CandidateCatalogSnapshots.Inputs
  deriving DecidableEq, Repr
def Inputs.captures (inputs : Inputs) : List Envelope :=
  inputs.authority :: (inputs.declarations ++ inputs.selections ++ inputs.relation.original.captures)
def BudgetMeaning (limits : Limits) (inputs : Inputs) : Prop :=
  CandidateEvidenceResources.CombinedBudgetMeaning limits inputs.authority
    (inputs.declarations ++ inputs.selections) inputs.relation.original.captures
def budgetCheck (limits : Limits) (inputs : Inputs) : Bool :=
  CandidateEvidenceResources.combinedBudgetCheck limits inputs.authority
    (inputs.declarations ++ inputs.selections) inputs.relation.original.captures
theorem budget_exact (limits : Limits) (inputs : Inputs) :
    budgetCheck limits inputs = true ↔ BudgetMeaning limits inputs :=
  CandidateEvidenceResources.combined_budget_exact _ _ _ _

theorem complete_capture_charge (limits : Limits) (inputs : Inputs) (meaning : BudgetMeaning limits inputs) :
    inputs.declarations.length + inputs.selections.length + 6 ≤ limits.maxCaptures ∧
    CandidateDigestCapture.originalByteCount inputs.captures ≤ limits.totalBytes ∧
    ∀ capture ∈ inputs.captures, capture.content.length ≤ limits.perCaptureBytes := by
  have count := meaning.1
  simp only [CandidateEvidenceResources.allInputs, List.length_cons, List.length_append,
    CandidateCatalogSnapshots.Inputs.original, CandidateOriginalBytePipeline.Inputs.captures,
    List.length_nil] at count
  exact ⟨count, meaning.2.1, meaning.2.2⟩

theorem full_budget_implies_profile_budget (limits : Limits) (inputs : Inputs)
    (meaning : BudgetMeaning limits inputs) :
    CandidateEvidenceResources.CombinedBudgetMeaning limits inputs.authority inputs.declarations inputs.selections := by
  rcases meaning with ⟨count, bytes, each⟩
  simp only [CandidateEvidenceResources.allInputs, List.length_cons, List.length_append] at count
  have subsetCount : (CandidateEvidenceResources.allInputs inputs.authority inputs.declarations inputs.selections).length ≤ limits.maxCaptures := by
    simp only [CandidateEvidenceResources.allInputs, List.length_cons, List.length_append]
    omega
  have subsetBytes : CandidateDigestCapture.originalByteCount
      (CandidateEvidenceResources.allInputs inputs.authority inputs.declarations inputs.selections) ≤ limits.totalBytes := by
    simp only [CandidateEvidenceResources.allInputs, CandidateDigestCapture.originalByteCount,
      List.map_cons, List.sum_cons, List.map_append, List.sum_append] at bytes ⊢
    omega
  refine ⟨subsetCount, subsetBytes, ?_⟩
  intro capture member
  apply each capture
  simp only [CandidateEvidenceResources.allInputs, List.mem_cons, List.mem_append] at member ⊢
  rcases member with head | rest
  · exact Or.inl head
  · exact Or.inr (Or.inl rest)

theorem full_budget_implies_relation_budget (limits : Limits) (inputs : Inputs)
    (meaning : BudgetMeaning limits inputs) : CandidateOriginalBytePipeline.BudgetMeaning limits inputs.relation.original := by
  rcases meaning with ⟨count, bytes, each⟩
  have rawShape : inputs.relation.original.captures =
      CandidateEvidenceResources.allInputs inputs.relation.original.source
        (inputs.relation.original.qualifiers :: inputs.relation.original.catalogs) [] := rfl
  refine ⟨?_, ?_, ?_⟩
  · simp only [CandidateEvidenceResources.allInputs, List.length_cons, List.length_append] at count
    rw [←rawShape]
    omega
  · simp only [CandidateEvidenceResources.allInputs, CandidateDigestCapture.originalByteCount,
      List.map_cons, List.sum_cons, List.map_append, List.sum_append] at bytes
    rw [←rawShape]
    unfold CandidateDigestCapture.originalByteCount
    omega
  · intro capture member
    apply each capture
    rw [←rawShape] at member
    simp only [CandidateEvidenceResources.allInputs, List.mem_cons, List.mem_append]
    exact Or.inr (Or.inr member)

#print axioms budget_exact
#print axioms complete_capture_charge
#print axioms full_budget_implies_profile_budget
#print axioms full_budget_implies_relation_budget
end RelationalSuccessor.CandidateSelectedRelation
