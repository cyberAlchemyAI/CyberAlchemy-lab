import EvidenceReuse
set_option autoImplicit false
namespace RelationalSuccessor.CandidatePreflightReuse
open CandidateBindingCapture (Envelope)
open CandidateDigest (Profile)
open CandidateEvidenceResources (NumericLimits PreflightOutcome)
abbrev Failure := Nat × Envelope × PreflightOutcome

theorem certify_error_never_ready (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope)
    (reason : PreflightOutcome) (found : certify profile budget numbers capture=.error reason) : reason≠.ready := by
  unfold certify at found
  split at found
  · split at found
    · cases parsed : CandidateScalarConversion.parseScalarDocumentBytes capture.content with
      | none=>simp only [parsed,Except.error.injEq] at found;subst reason;intro same;cases same
      | some ast=>
        simp only [parsed] at found
        cases tokens : CandidateEvidenceResources.firstUnsupported numbers (CandidateEvidenceResources.numberTokens ast) with
        | none=>simp only [tokens] at found;contradiction
        | some token=>simp only [tokens,Except.error.injEq] at found;subst reason;intro same;cases same
    · have same:=Except.error.inj found;subst reason;intro same;cases same
  · have same:=Except.error.inj found;subst reason;intro same;cases same

theorem checked_error_never_ready (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope)
    (reason : PreflightOutcome) (found : checked profile budget numbers capture=.error reason) : reason≠.ready := by
  unfold checked at found
  split at found
  · rename_i actual raw
    have same:=Except.error.inj found
    subst reason
    exact certify_error_never_ready profile budget numbers capture actual raw
  · contradiction

def collect (profile : Profile) (budget : Nat) (numbers : NumericLimits) :
    List Envelope → Except Failure (List (CertifiedInput profile budget numbers))
  | []=>.ok []
  | capture::captures=>match checked profile budget numbers capture with
    | .error reason=>.error (0,capture,reason)
    | .ok input=>match collect profile budget numbers captures with
      | .error (index,failed,reason)=>.error (index+1,failed,reason)
      | .ok rest=>.ok (input::rest)
def failed {profile : Profile} {budget : Nat} {numbers : NumericLimits} :
    Except Failure (List (CertifiedInput profile budget numbers)) → Option Failure
  | .error reason=>some reason
  | .ok _=>none

theorem collected_refusal_equal_legacy (profile : Profile) (budget : Nat) (numbers : NumericLimits) (captures : List Envelope) :
    failed (collect profile budget numbers captures)=CandidateEvidenceResources.firstSourceRefusal profile budget numbers captures := by
  induction captures with
  | nil=>rfl
  | cons capture captures ih=>
    have outcome:=checked_diagnostic_equivalence profile budget numbers capture
    cases head : checked profile budget numbers capture with
    | error reason=>
      rw [head] at outcome
      simp only [forgetChecked] at outcome
      have notReady:=checked_error_never_ready profile budget numbers capture reason head
      simp only [collect,head,failed,CandidateEvidenceResources.firstSourceRefusal,←outcome,if_neg notReady]
    | ok input=>
      rw [head] at outcome
      simp only [forgetChecked] at outcome
      cases tail : collect profile budget numbers captures with
      | error tuple=>
        rcases tuple with ⟨index,failedInput,reason⟩
        rw [tail] at ih
        simp only [failed] at ih
        simp only [collect,head,tail,failed,CandidateEvidenceResources.firstSourceRefusal,←outcome,if_true,←ih,Option.map_some]
      | ok rest=>
        rw [tail] at ih
        simp only [failed] at ih
        simp only [collect,head,tail,failed,CandidateEvidenceResources.firstSourceRefusal,←outcome,if_true,←ih,Option.map_none]

theorem collected_original_inputs (profile : Profile) (budget : Nat) (numbers : NumericLimits) (captures : List Envelope)
    (inputs : List (CertifiedInput profile budget numbers)) (found : collect profile budget numbers captures=.ok inputs) :
    inputs.map (fun input=>input.val.capture)=captures := by
  induction captures generalizing inputs with
  | nil=>simp only [collect,Except.ok.injEq] at found;subst inputs;rfl
  | cons capture captures ih=>
    cases head : checked profile budget numbers capture with
    | error reason=>simp only [collect,head] at found;contradiction
    | ok input=>
      cases tail : collect profile budget numbers captures with
      | error tuple=>rcases tuple with ⟨index,failedInput,reason⟩;simp only [collect,head,tail] at found;contradiction
      | ok rest=>
        simp only [collect,head,tail,Except.ok.injEq] at found
        subst inputs
        simp only [List.map_cons,checked_retains_capture profile budget numbers capture input head,ih rest tail]
#print axioms certify_error_never_ready
#print axioms checked_error_never_ready
#print axioms collected_refusal_equal_legacy
#print axioms collected_original_inputs
end RelationalSuccessor.CandidatePreflightReuse
