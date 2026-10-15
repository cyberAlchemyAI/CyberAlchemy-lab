import ResourceDiagnostics
set_option autoImplicit false
namespace RelationalSuccessor.CandidatePreflightReuse
open CandidateBindingCapture (Envelope EnvelopeMeaning)
open CandidateDigest (Profile VerifiedDigestMeaning)
open CandidateEvidenceResources (NumericLimits PreflightOutcome NumericTreeMeaning)
open CandidateScalarConversion (ScalarByteDocumentMeaning parseScalarDocumentBytes)
abbrev J := CandidateJsonSource.Value

structure Input where
  capture : Envelope
  ast : J

def InputMeaning (profile : Profile) (budget : Nat) (numbers : NumericLimits) (input : Input) : Prop :=
  EnvelopeMeaning input.capture ∧
    VerifiedDigestMeaning profile input.capture.digestProfile input.capture.content input.capture.digest budget ∧
    ScalarByteDocumentMeaning input.capture.content input.ast ∧ NumericTreeMeaning numbers input.ast
abbrev CertifiedInput (profile : Profile) (budget : Nat) (numbers : NumericLimits) :=
  {input : Input // InputMeaning profile budget numbers input}

def certify (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope) : Except PreflightOutcome Input :=
  if CandidateBindingCapture.envelopeCheck capture then
    if CandidateDigest.classifyDigest profile capture.digestProfile capture.content capture.digest budget=.verified then
      match parseScalarDocumentBytes capture.content with
      | none=>.error .scalarRefused
      | some ast=>match CandidateEvidenceResources.firstUnsupported numbers (CandidateEvidenceResources.numberTokens ast) with
        | some token=>.error (.numericRefused token)
        | none=>.ok ⟨capture,ast⟩
    else .error (.digestRefused (CandidateDigest.classifyDigest profile capture.digestProfile capture.content capture.digest budget))
  else .error .invalidEnvelope

def forget : Except PreflightOutcome Input → PreflightOutcome
  | .ok _=>.ready
  | .error reason=>reason

theorem certified_diagnostic_equivalence (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope) :
    forget (certify profile budget numbers capture)=CandidateEvidenceResources.classifyPreflight profile budget numbers capture := by
  unfold certify CandidateEvidenceResources.classifyPreflight
  by_cases envelope : CandidateBindingCapture.envelopeCheck capture=true
  · simp only [envelope,if_true]
    by_cases digest : CandidateDigest.classifyDigest profile capture.digestProfile capture.content capture.digest budget=.verified
    · simp only [digest,if_true]
      cases parsed : parseScalarDocumentBytes capture.content with
      | none=>simp only [forget]
      | some ast=>
        cases checked : CandidateEvidenceResources.firstUnsupported numbers (CandidateEvidenceResources.numberTokens ast) <;> simp only [checked,forget]
    · simp only [if_neg digest,forget]
  · simp only [if_neg envelope,forget]

theorem certified_retains_original_capture (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope)
    (input : Input) (found : certify profile budget numbers capture=.ok input) : input.capture=capture := by
  unfold certify at found
  split at found
  · split at found
    · cases parsed : parseScalarDocumentBytes capture.content with
      | none=>simp only [parsed] at found;contradiction
      | some ast=>
        simp only [parsed] at found
        cases checked : CandidateEvidenceResources.firstUnsupported numbers (CandidateEvidenceResources.numberTokens ast) with
        | some token=>simp only [checked] at found;contradiction
        | none=>simp only [checked,Except.ok.injEq] at found;subst input;rfl
    · contradiction
  · contradiction

theorem certified_is_ready (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope)
    (input : Input) (found : certify profile budget numbers capture=.ok input) :
    CandidateEvidenceResources.PreflightMeaning profile budget numbers capture := by
  apply (CandidateEvidenceResources.preflight_ready_exact profile budget numbers capture).mp
  rw [←certified_diagnostic_equivalence,found]
  rfl

theorem certified_input_sound (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope)
    (input : Input) (found : certify profile budget numbers capture=.ok input) : InputMeaning profile budget numbers input := by
  unfold certify at found
  split at found
  · rename_i envelope
    split at found
    · rename_i digest
      cases parsed : parseScalarDocumentBytes capture.content with
      | none=>simp only [parsed] at found;contradiction
      | some ast=>
        simp only [parsed] at found
        cases checked : CandidateEvidenceResources.firstUnsupported numbers (CandidateEvidenceResources.numberTokens ast) with
        | some token=>simp only [checked] at found;contradiction
        | none=>
          simp only [checked,Except.ok.injEq] at found
          subst input
          exact ⟨(CandidateBindingCapture.envelope_check_exact capture).mp envelope,
            (CandidateDigest.classified_verified_exact profile capture.digestProfile capture.content capture.digest budget).mp digest,
            (CandidateScalarConversion.scalar_byte_document_exact capture.content ast).mp parsed,
            (CandidateEvidenceResources.numeric_tree_none_exact numbers ast).mp checked⟩
    · contradiction
  · contradiction

theorem certified_ast_unique {profile : Profile} {budget : Nat} {numbers : NumericLimits}
    (a b : CertifiedInput profile budget numbers) (same : a.val.capture=b.val.capture) : a.val.ast=b.val.ast := by
  have parsed : ScalarByteDocumentMeaning a.val.capture.content b.val.ast := by rw [same];exact b.property.2.2.1
  exact CandidateScalarConversion.scalar_byte_meaning_unique a.val.capture.content a.val.ast b.val.ast a.property.2.2.1 parsed

def checked (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope) :
    Except PreflightOutcome (CertifiedInput profile budget numbers) :=
  match found : certify profile budget numbers capture with
  | .error reason=>.error reason
  | .ok input=>.ok ⟨input,certified_input_sound profile budget numbers capture input found⟩
def forgetChecked {profile : Profile} {budget : Nat} {numbers : NumericLimits} :
    Except PreflightOutcome (CertifiedInput profile budget numbers) → PreflightOutcome
  | .ok _=>.ready
  | .error reason=>reason

theorem checked_diagnostic_equivalence (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope) :
    forgetChecked (checked profile budget numbers capture)=CandidateEvidenceResources.classifyPreflight profile budget numbers capture := by
  rw [←certified_diagnostic_equivalence]
  unfold checked
  split <;> rename_i _ found <;> simp only [forgetChecked] <;> rw [found] <;> rfl

theorem checked_retains_capture (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope)
    (input : CertifiedInput profile budget numbers) (found : checked profile budget numbers capture=.ok input) : input.val.capture=capture := by
  unfold checked at found
  split at found
  · contradiction
  · rename_i actual raw
    have same:=Except.ok.inj found
    rw [←same]
    exact certified_retains_original_capture profile budget numbers capture actual raw
#print axioms certified_diagnostic_equivalence
#print axioms certified_retains_original_capture
#print axioms certified_is_ready
#print axioms certified_input_sound
#print axioms certified_ast_unique
#print axioms checked_diagnostic_equivalence
#print axioms checked_retains_capture
end RelationalSuccessor.CandidatePreflightReuse
