import ReuseCollection
set_option autoImplicit false
namespace RelationalSuccessor.CandidatePreflightReuse
open CandidateBindingCapture (Envelope)
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits)
open CandidateEvidenceResources (NumericLimits BoundedOutcome)

def run (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame) (root ref : RevisionRef)
    (authority : Envelope) (declarations selections : List Envelope) : BoundedOutcome :=
  if CandidateEvidenceResources.combinedBudgetCheck limits authority declarations selections then
    match collect bootstrap limits.perCaptureBytes numbers (CandidateEvidenceResources.allInputs authority declarations selections) with
    | .error (index,input,reason)=>.sourceRefused index input reason
    | .ok []=>.data .authorityDataRefused
    | .ok (input::rest)=>.data (classifyData bootstrap limits numbers frame root ref input
        (rest.take declarations.length) (rest.drop declarations.length))
  else .budgetRefused

theorem reusable_entry_equal_guarded (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame) (root ref : RevisionRef)
    (authority : Envelope) (declarations selections : List Envelope) :
    run bootstrap limits numbers frame root ref authority declarations selections=
      CandidateEvidenceResources.classifyBoundedEvidence bootstrap limits numbers frame root ref authority declarations selections := by
  cases budget : CandidateEvidenceResources.combinedBudgetCheck limits authority declarations selections with
  | false=>simp [run,CandidateEvidenceResources.classifyBoundedEvidence,budget]
  | true=>
    have refusal:=collected_refusal_equal_legacy bootstrap limits.perCaptureBytes numbers (CandidateEvidenceResources.allInputs authority declarations selections)
    cases collected : collect bootstrap limits.perCaptureBytes numbers (CandidateEvidenceResources.allInputs authority declarations selections) with
    | error tuple=>
      rcases tuple with ⟨index,input,reason⟩
      rw [collected] at refusal
      simp only [failed] at refusal
      simp only [run,CandidateEvidenceResources.classifyBoundedEvidence,budget,if_true,collected,←refusal]
    | ok inputs=>
      rw [collected] at refusal
      simp only [failed] at refusal
      have retained:=collected_original_inputs bootstrap limits.perCaptureBytes numbers (CandidateEvidenceResources.allInputs authority declarations selections) inputs collected
      cases inputs with
      | nil=>simp [CandidateEvidenceResources.allInputs] at retained
      | cons input rest=>
        simp only [List.map_cons,CandidateEvidenceResources.allInputs,List.cons.injEq] at retained
        rcases retained with ⟨sameAuthority,sameRest⟩
        have sameDeclarations : (rest.take declarations.length).map (fun input=>input.val.capture)=declarations := by
          rw [List.map_take,sameRest,List.take_append_length]
        have sameSelections : (rest.drop declarations.length).map (fun input=>input.val.capture)=selections := by
          rw [List.map_drop,sameRest,List.drop_append_length]
        simp only [run,CandidateEvidenceResources.classifyBoundedEvidence,budget,if_true,collected,←refusal,
          reused_data_equal_legacy,sameAuthority,sameDeclarations,sameSelections]

theorem reusable_prepared_exact (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame) (root ref : RevisionRef)
    (authority : Envelope) (declarations selections : List Envelope) (stage : CandidateProfileEvidence.EvidenceStage) :
    run bootstrap limits numbers frame root ref authority declarations selections=.data (.prepared stage) ↔
      CandidateEvidenceResources.BoundedPreparedMeaning bootstrap limits numbers frame root ref authority declarations selections stage := by
  rw [reusable_entry_equal_guarded]
  exact CandidateEvidenceResources.bounded_prepared_exact bootstrap limits numbers frame root ref authority declarations selections stage

theorem reusable_diagnostics_preserved (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame) (root ref : RevisionRef)
    (authority : Envelope) (declarations selections : List Envelope) :
    CandidateEvidenceResources.diagnose (run bootstrap limits numbers frame root ref authority declarations selections)=
      CandidateEvidenceResources.diagnose (CandidateEvidenceResources.classifyBoundedEvidence bootstrap limits numbers frame root ref authority declarations selections) := by
  rw [reusable_entry_equal_guarded]
#print axioms reusable_entry_equal_guarded
#print axioms reusable_prepared_exact
#print axioms reusable_diagnostics_preserved
end RelationalSuccessor.CandidatePreflightReuse
