import NumericTree
set_option autoImplicit false
namespace RelationalSuccessor.CandidateEvidenceResources
open CandidateBindingCapture (Envelope)
open CandidateDigestCapture (Limits originalByteCount)

def allInputs (authority : Envelope) (declarations selections : List Envelope) : List Envelope := authority::(declarations++selections)
def CombinedBudgetMeaning (limits : Limits) (authority : Envelope) (declarations selections : List Envelope) : Prop :=
  (allInputs authority declarations selections).length≤limits.maxCaptures ∧
    originalByteCount (allInputs authority declarations selections)≤limits.totalBytes ∧
    ∀ input∈allInputs authority declarations selections,input.content.length≤limits.perCaptureBytes
def combinedBudgetCheck (limits : Limits) (authority : Envelope) (declarations selections : List Envelope) : Bool :=
  decide ((allInputs authority declarations selections).length≤limits.maxCaptures) &&
    decide (originalByteCount (allInputs authority declarations selections)≤limits.totalBytes) &&
    (allInputs authority declarations selections).all fun input=>decide (input.content.length≤limits.perCaptureBytes)
theorem combined_budget_exact (limits : Limits) (authority : Envelope) (declarations selections : List Envelope) :
    combinedBudgetCheck limits authority declarations selections=true ↔ CombinedBudgetMeaning limits authority declarations selections := by
  simp only [combinedBudgetCheck,CombinedBudgetMeaning,Bool.and_eq_true,decide_eq_true_eq,List.all_eq_true]
  simp only [and_assoc]

theorem authority_counts_toward_budget (limits : Limits) (authority : Envelope) (declarations selections : List Envelope)
    (meaning : CombinedBudgetMeaning limits authority declarations selections) :
    declarations.length+selections.length+1≤limits.maxCaptures ∧ authority.content.length≤limits.perCaptureBytes := by
  have count:=meaning.1
  simp only [allInputs,List.length_cons,List.length_append] at count
  exact ⟨count,meaning.2.2 authority (by simp [allInputs])⟩
theorem authority_bytes_are_charged (limits : Limits) (authority : Envelope) (declarations selections : List Envelope)
    (meaning : CombinedBudgetMeaning limits authority declarations selections) :
    authority.content.length+originalByteCount (declarations++selections)≤limits.totalBytes := by
  have bytes:=meaning.2.1
  simpa only [allInputs,originalByteCount,List.map_cons,List.sum_cons] using bytes
theorem dishonest_declared_count_does_not_reduce_budget (limits : Limits) (authority : Envelope) (declarations selections : List Envelope) (claimed : Nat) :
    CombinedBudgetMeaning limits {authority with byteLength:=claimed} declarations selections ↔
      CombinedBudgetMeaning limits authority declarations selections := by
  simp [CombinedBudgetMeaning,allInputs,originalByteCount]
#print axioms combined_budget_exact
#print axioms authority_counts_toward_budget
#print axioms authority_bytes_are_charged
#print axioms dishonest_declared_count_does_not_reduce_budget
end RelationalSuccessor.CandidateEvidenceResources
