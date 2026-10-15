import CombinedBudget
set_option autoImplicit false
namespace RelationalSuccessor.CandidateEvidenceResources
open CandidateBindingCapture (Envelope EnvelopeMeaning)
open CandidateDigest (Profile VerifiedDigestMeaning Outcome)
open CandidateScalarConversion (ScalarByteDocumentMeaning parseScalarDocumentBytes)

inductive PreflightOutcome where
  | invalidEnvelope
  | digestRefused (reason : Outcome)
  | scalarRefused
  | numericRefused (token : String)
  | ready
  deriving DecidableEq, Repr
def PreflightMeaning (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope) : Prop :=
  EnvelopeMeaning capture ∧ VerifiedDigestMeaning profile capture.digestProfile capture.content capture.digest budget ∧
    ∃ ast,ScalarByteDocumentMeaning capture.content ast ∧ NumericTreeMeaning numbers ast
def classifyPreflight (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope) : PreflightOutcome :=
  if CandidateBindingCapture.envelopeCheck capture then
    let digest:=CandidateDigest.classifyDigest profile capture.digestProfile capture.content capture.digest budget
    if digest=.verified then
      match parseScalarDocumentBytes capture.content with
      | none=>.scalarRefused
      | some ast=>match firstUnsupported numbers (numberTokens ast) with
        | none=>.ready
        | some token=>.numericRefused token
    else .digestRefused digest
  else .invalidEnvelope

theorem preflight_ready_exact (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope) :
    classifyPreflight profile budget numbers capture=.ready ↔ PreflightMeaning profile budget numbers capture := by
  constructor
  · intro ready
    unfold classifyPreflight at ready
    dsimp only at ready
    split at ready
    · rename_i envelope
      split at ready
      · rename_i digest
        cases parsed : parseScalarDocumentBytes capture.content with
        | none=>simp only [parsed] at ready;contradiction
        | some ast=>
          simp only [parsed] at ready
          cases checked : firstUnsupported numbers (numberTokens ast) with
          | some token=>simp only [checked] at ready;contradiction
          | none=>exact ⟨(CandidateBindingCapture.envelope_check_exact capture).mp envelope,
              (CandidateDigest.classified_verified_exact profile capture.digestProfile capture.content capture.digest budget).mp digest,
              ast,(CandidateScalarConversion.scalar_byte_document_exact capture.content ast).mp parsed,
              (numeric_tree_none_exact numbers ast).mp checked⟩
      · contradiction
    · contradiction
  · rintro ⟨envelope,digest,ast,parsed,bounds⟩
    simp only [classifyPreflight,(CandidateBindingCapture.envelope_check_exact capture).mpr envelope,
      (CandidateDigest.classified_verified_exact profile capture.digestProfile capture.content capture.digest budget).mpr digest,if_true,
      (CandidateScalarConversion.scalar_byte_document_exact capture.content ast).mpr parsed,
      (numeric_tree_none_exact numbers ast).mpr bounds]

theorem preflight_invalid_envelope_exact (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope) :
    classifyPreflight profile budget numbers capture=.invalidEnvelope ↔ ¬EnvelopeMeaning capture := by
  rw [←CandidateBindingCapture.envelope_check_exact capture]
  cases envelope : CandidateBindingCapture.envelopeCheck capture with
  | false=>simp [classifyPreflight,envelope]
  | true=>
    unfold classifyPreflight
    simp only [envelope,if_true]
    split <;> simp_all
    cases parsed : parseScalarDocumentBytes capture.content with
    | none=>simp
    | some ast=>cases checked : firstUnsupported numbers (numberTokens ast) <;> simp [checked]

theorem preflight_digest_verified_never_refused (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope) :
    classifyPreflight profile budget numbers capture≠.digestRefused .verified := by
  intro refused
  unfold classifyPreflight at refused
  dsimp only at refused
  split at refused
  · split at refused
    · cases parsed : parseScalarDocumentBytes capture.content with
      | none=>simp_all
      | some ast=>cases checked : firstUnsupported numbers (numberTokens ast) <;> simp_all
    · rename_i absent
      exact absent (PreflightOutcome.digestRefused.inj refused)
  · contradiction

theorem preflight_numeric_refusal_actual_cause (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope) (token : String)
    (refused : classifyPreflight profile budget numbers capture=.numericRefused token) :
    ∃ ast,ScalarByteDocumentMeaning capture.content ast ∧ NumberOccurs token ast ∧ ¬TokenWorkMeaning numbers token := by
  unfold classifyPreflight at refused
  dsimp only at refused
  split at refused
  · split at refused
    · cases parsed : parseScalarDocumentBytes capture.content with
      | none=>simp only [parsed] at refused;contradiction
      | some ast=>
        simp only [parsed] at refused
        cases checked : firstUnsupported numbers (numberTokens ast) with
        | none=>simp only [checked] at refused;contradiction
        | some actual=>
          simp only [checked,PreflightOutcome.numericRefused.injEq] at refused
          subst actual
          have cause:=numeric_tree_refusal_has_actual_occurrence numbers ast token checked
          exact ⟨ast,(CandidateScalarConversion.scalar_byte_document_exact capture.content ast).mp parsed,cause⟩
    · contradiction
  · contradiction

def firstSourceRefusal (profile : Profile) (budget : Nat) (numbers : NumericLimits) : List Envelope → Option (Nat × Envelope × PreflightOutcome)
  | []=>none
  | capture::rest=>
    let outcome:=classifyPreflight profile budget numbers capture
    if outcome=.ready then (firstSourceRefusal profile budget numbers rest).map fun row=>(row.1+1,row.2)
    else some (0,capture,outcome)
def AllPreflightMeaning (profile : Profile) (budget : Nat) (numbers : NumericLimits) (inputs : List Envelope) : Prop :=
  ∀ input∈inputs,PreflightMeaning profile budget numbers input
theorem all_preflight_exact (profile : Profile) (budget : Nat) (numbers : NumericLimits) (inputs : List Envelope) :
    firstSourceRefusal profile budget numbers inputs=none ↔ AllPreflightMeaning profile budget numbers inputs := by
  induction inputs with
  | nil=>simp [firstSourceRefusal,AllPreflightMeaning]
  | cons capture rest ih=>
    simp only [firstSourceRefusal,AllPreflightMeaning,List.mem_cons,forall_eq_or_imp]
    split
    · rename_i ready
      rw [Option.map_eq_none_iff,ih]
      simp only [AllPreflightMeaning]
      exact (and_iff_right ((preflight_ready_exact profile budget numbers capture).mp ready)).symm
    · rename_i absent
      have noMeaning : ¬PreflightMeaning profile budget numbers capture := fun h=>absent ((preflight_ready_exact profile budget numbers capture).mpr h)
      simp [noMeaning]

theorem first_source_refusal_retains_capture (profile : Profile) (budget : Nat) (numbers : NumericLimits)
    (inputs : List Envelope) (index : Nat) (capture : Envelope) (reason : PreflightOutcome)
    (found : firstSourceRefusal profile budget numbers inputs=some (index,capture,reason)) :
    capture∈inputs ∧ classifyPreflight profile budget numbers capture=reason ∧ reason≠.ready := by
  induction inputs generalizing index with
  | nil=>simp [firstSourceRefusal] at found
  | cons first rest ih=>
    unfold firstSourceRefusal at found
    dsimp only at found
    split at found
    · cases tail : firstSourceRefusal profile budget numbers rest with
      | none=>simp only [tail,Option.map_none] at found;contradiction
      | some row=>
        rcases row with ⟨position,actual,actualReason⟩
        simp only [tail,Option.map_some,Option.some.injEq,Prod.mk.injEq] at found
        rcases found with ⟨_,eqCapture,eqReason⟩
        subst actual;subst actualReason
        have retained:=ih position tail
        exact ⟨by simp [retained.1],retained.2⟩
    · rename_i absent
      simp only [Option.some.injEq,Prod.mk.injEq] at found
      rcases found with ⟨_,eqCapture,eqReason⟩
      subst first
      exact ⟨by simp,eqReason,by intro ready;exact absent (eqReason.trans ready)⟩

-- The reported ordinal is zero based and every earlier capture passed.
theorem first_source_refusal_exact_position (profile : Profile) (budget : Nat) (numbers : NumericLimits)
    (inputs : List Envelope) (index : Nat) (capture : Envelope) (reason : PreflightOutcome)
    (found : firstSourceRefusal profile budget numbers inputs=some (index,capture,reason)) :
    ∃ before after,inputs=before++capture::after ∧ before.length=index ∧
      AllPreflightMeaning profile budget numbers before ∧ classifyPreflight profile budget numbers capture=reason ∧ reason≠.ready := by
  induction inputs generalizing index with
  | nil=>simp [firstSourceRefusal] at found
  | cons first rest ih=>
    unfold firstSourceRefusal at found
    dsimp only at found
    split at found
    · rename_i ready
      cases tail : firstSourceRefusal profile budget numbers rest with
      | none=>simp only [tail,Option.map_none] at found;contradiction
      | some row=>
        rcases row with ⟨position,actual,actualReason⟩
        simp only [tail,Option.map_some,Option.some.injEq,Prod.mk.injEq] at found
        rcases found with ⟨eqIndex,eqCapture,eqReason⟩
        subst actual;subst actualReason
        rcases ih position tail with ⟨before,after,inputsEq,length,passed,cause,notReady⟩
        refine ⟨first::before,after,by simp only [inputsEq,List.cons_append],?_,?_,cause,notReady⟩
        · simp only [List.length_cons];omega
        · intro input member
          rcases List.mem_cons.mp member with same | earlier
          · subst input;exact (preflight_ready_exact profile budget numbers first).mp ready
          · exact passed input earlier
    · rename_i absent
      simp only [Option.some.injEq,Prod.mk.injEq] at found
      rcases found with ⟨eqIndex,eqCapture,eqReason⟩
      subst first
      exact ⟨[],rest,rfl,eqIndex,by simp [AllPreflightMeaning],eqReason,by intro ready;exact absent (eqReason.trans ready)⟩

def DigestReasonMeaning (profile : Profile) (capture : Envelope) (budget : Nat) : Outcome → Prop
  | .unsupportedProfile=>¬CandidateDigest.ProfileMeaning profile capture.digestProfile
  | .outsideAlgorithmDomain=>CandidateDigest.ProfileMeaning profile capture.digestProfile ∧ ¬capture.content.length<2^61
  | .byteBudgetExceeded=>CandidateDigest.ProfileMeaning profile capture.digestProfile ∧ capture.content.length<2^61 ∧ ¬capture.content.length≤budget
  | .malformedDigest=>CandidateDigest.ProfileMeaning profile capture.digestProfile ∧ capture.content.length<2^61 ∧ capture.content.length≤budget ∧ ¬CandidateDigest.HexMeaning capture.digest
  | .digestMismatch=>CandidateDigest.ProfileMeaning profile capture.digestProfile ∧ capture.content.length<2^61 ∧ capture.content.length≤budget ∧ CandidateDigest.HexMeaning capture.digest ∧ ¬CandidateDigest.DigestMeaning capture.content capture.digest
  | .verified=>VerifiedDigestMeaning profile capture.digestProfile capture.content capture.digest budget

theorem digest_reason_exact (profile : Profile) (capture : Envelope) (budget : Nat) (reason : Outcome) :
    CandidateDigest.classifyDigest profile capture.digestProfile capture.content capture.digest budget=reason ↔ DigestReasonMeaning profile capture budget reason := by
  cases reason with
  | unsupportedProfile=>exact CandidateDigest.profile_refusal_exact profile capture.digestProfile capture.content capture.digest budget
  | outsideAlgorithmDomain=>exact CandidateDigest.domain_refusal_exact profile capture.digestProfile capture.content capture.digest budget
  | byteBudgetExceeded=>exact CandidateDigest.budget_refusal_exact profile capture.digestProfile capture.content capture.digest budget
  | malformedDigest=>exact CandidateDigest.malformed_refusal_exact profile capture.digestProfile capture.content capture.digest budget
  | digestMismatch=>exact CandidateDigest.mismatch_refusal_exact profile capture.digestProfile capture.content capture.digest budget
  | verified=>exact CandidateDigest.classified_verified_exact profile capture.digestProfile capture.content capture.digest budget

theorem preflight_digest_refusal_exact (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope) (reason : Outcome) :
    classifyPreflight profile budget numbers capture=.digestRefused reason ↔
      EnvelopeMeaning capture ∧ reason≠.verified ∧ DigestReasonMeaning profile capture budget reason := by
  rw [←CandidateBindingCapture.envelope_check_exact capture,←digest_reason_exact profile capture budget reason]
  cases envelope : CandidateBindingCapture.envelopeCheck capture with
  | false=>simp [classifyPreflight,envelope]
  | true=>
    by_cases verified : CandidateDigest.classifyDigest profile capture.digestProfile capture.content capture.digest budget=.verified
    · cases parsed : parseScalarDocumentBytes capture.content with
      | none=>simp [classifyPreflight,envelope,verified,parsed,eq_comm]
      | some ast=>cases checked : firstUnsupported numbers (numberTokens ast) <;> simp [classifyPreflight,envelope,verified,parsed,checked,eq_comm]
    · simp only [classifyPreflight,envelope,if_true,if_neg verified,PreflightOutcome.digestRefused.injEq,true_and]
      constructor
      · intro same;exact ⟨fun ready=>verified (same.trans ready),same⟩
      · intro cause;exact cause.2

theorem preflight_scalar_refusal_exact (profile : Profile) (budget : Nat) (numbers : NumericLimits) (capture : Envelope) :
    classifyPreflight profile budget numbers capture=.scalarRefused ↔
      EnvelopeMeaning capture ∧ VerifiedDigestMeaning profile capture.digestProfile capture.content capture.digest budget ∧
        ¬∃ast,ScalarByteDocumentMeaning capture.content ast := by
  rw [←CandidateBindingCapture.envelope_check_exact capture,
    ←CandidateDigest.classified_verified_exact profile capture.digestProfile capture.content capture.digest budget,
    ←CandidateScalarConversion.scalar_byte_none_exact capture.content]
  cases envelope : CandidateBindingCapture.envelopeCheck capture with
  | false=>simp [classifyPreflight,envelope]
  | true=>
    by_cases verified : CandidateDigest.classifyDigest profile capture.digestProfile capture.content capture.digest budget=.verified
    · cases parsed : parseScalarDocumentBytes capture.content with
      | none=>simp [classifyPreflight,envelope,verified,parsed]
      | some ast=>cases checked : firstUnsupported numbers (numberTokens ast) <;> simp [classifyPreflight,envelope,verified,parsed,checked]
    · simp [classifyPreflight,envelope,verified]
#print axioms preflight_ready_exact
#print axioms preflight_invalid_envelope_exact
#print axioms preflight_digest_verified_never_refused
#print axioms preflight_numeric_refusal_actual_cause
#print axioms all_preflight_exact
#print axioms first_source_refusal_retains_capture
#print axioms first_source_refusal_exact_position
#print axioms digest_reason_exact
#print axioms preflight_digest_refusal_exact
#print axioms preflight_scalar_refusal_exact
end RelationalSuccessor.CandidateEvidenceResources
