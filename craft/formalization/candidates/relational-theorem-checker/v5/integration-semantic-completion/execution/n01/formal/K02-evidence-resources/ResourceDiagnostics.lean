import BoundedEvidence
set_option autoImplicit false
namespace RelationalSuccessor.CandidateEvidenceResources
open CandidateBindingCapture (Envelope)
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits)

-- Local candidate diagnostics. These are not frozen public API contracts.
structure Diagnostic where
  code : String
  explanation : String
  sourceIndex : Option Nat
  numericToken : Option String
  deriving DecidableEq, Repr

def preflightCode : PreflightOutcome → String
  | .invalidEnvelope=>"source.invalid-envelope"
  | .scalarRefused=>"source.unsupported-scalar-document"
  | .numericRefused _=>"resource.numeric-work-unsupported"
  | .ready=>"source.ready"
  | .digestRefused reason=>match reason with
    | .unsupportedProfile=>"digest.unsupported-profile"
    | .outsideAlgorithmDomain=>"digest.outside-algorithm-domain"
    | .byteBudgetExceeded=>"digest.byte-budget-exceeded"
    | .malformedDigest=>"digest.malformed"
    | .digestMismatch=>"digest.mismatch"
    | .verified=>"internal.unreachable-verified-refusal"

def diagnose : BoundedOutcome → Diagnostic
  | .budgetRefused=>⟨"resource.combined-budget-exceeded","The original authority, declaration and selection bytes or capture count exceed the configured combined limits.",none,none⟩
  | .sourceRefused index _ reason=>⟨preflightCode reason,"This original capture failed preflight. The zero-based source index counts authority first, then declarations, then selections.",some index,match reason with | .numericRefused token=>some token | _=>none⟩
  | .data outcome=>match outcome with
    | .profileDataRefused=>⟨"data.profile-preparation-refused","No prepared profile data satisfies the pinned source, catalog and selection meanings. This cause does not identify a field path.",none,none⟩
    | .authorityDataRefused=>⟨"data.authority-preparation-refused","Profile data exists but no authority data satisfies the exact reference, frame, root, bootstrap, shape and coherence constraints. This is not an authenticity verdict.",none,none⟩
    | .evidenceJoinRefused=>⟨"data.evidence-join-refused","Prepared profile and authority data exist but their exact source-evidence joins fail. This cause does not assign blame or identify one missing field.",none,none⟩
    | .prepared _=>⟨"data.prepared","Bounded captured evidence data is prepared. Authentic snapshot, Schema/review and downstream proof requirements remain separate.",none,none⟩

theorem diagnostic_source_position_has_checked_prefix (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (frame : Frame) (root ref : RevisionRef) (capture : Envelope) (declarations selections : List Envelope)
    (index : Nat) (input : Envelope) (reason : PreflightOutcome)
    (found : classifyBoundedEvidence bootstrap limits numbers frame root ref capture declarations selections=.sourceRefused index input reason) :
    (diagnose (.sourceRefused index input reason)).sourceIndex=some index ∧
      ∃ before after,allInputs capture declarations selections=before++input::after ∧ before.length=index ∧
        AllPreflightMeaning bootstrap limits.perCaptureBytes numbers before ∧
        classifyPreflight bootstrap limits.perCaptureBytes numbers input=reason ∧ reason≠.ready := by
  have cause:=bounded_outcome_has_independent_cause bootstrap limits numbers frame root ref capture declarations selections
  rw [found] at cause
  exact ⟨rfl,cause.2⟩

theorem diagnostic_numeric_token_has_original_occurrence (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (frame : Frame) (root ref : RevisionRef) (capture : Envelope) (declarations selections : List Envelope)
    (index : Nat) (input : Envelope) (token : String)
    (found : classifyBoundedEvidence bootstrap limits numbers frame root ref capture declarations selections=.sourceRefused index input (.numericRefused token)) :
    (diagnose (.sourceRefused index input (.numericRefused token))).numericToken=some token ∧
      ∃ ast,CandidateScalarConversion.ScalarByteDocumentMeaning input.content ast ∧ NumberOccurs token ast ∧ ¬TokenWorkMeaning numbers token := by
  have cause:=bounded_outcome_has_independent_cause bootstrap limits numbers frame root ref capture declarations selections
  rw [found] at cause
  rcases cause.2 with ⟨before,after,_,_,_,actual,_⟩
  exact ⟨rfl,preflight_numeric_refusal_actual_cause bootstrap limits.perCaptureBytes numbers input token actual⟩

theorem diagnostic_data_only_after_complete_preflight (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits)
    (frame : Frame) (root ref : RevisionRef) (capture : Envelope) (declarations selections : List Envelope) (outcome : DataOutcome)
    (found : classifyBoundedEvidence bootstrap limits numbers frame root ref capture declarations selections=.data outcome) :
    CombinedBudgetMeaning limits capture declarations selections ∧
      AllPreflightMeaning bootstrap limits.perCaptureBytes numbers (allInputs capture declarations selections) ∧
      DataOutcomeMeaning bootstrap limits frame root ref capture declarations selections outcome := by
  have cause:=bounded_outcome_has_independent_cause bootstrap limits numbers frame root ref capture declarations selections
  rw [found] at cause
  exact cause
#print axioms diagnostic_source_position_has_checked_prefix
#print axioms diagnostic_numeric_token_has_original_occurrence
#print axioms diagnostic_data_only_after_complete_preflight
end RelationalSuccessor.CandidateEvidenceResources
