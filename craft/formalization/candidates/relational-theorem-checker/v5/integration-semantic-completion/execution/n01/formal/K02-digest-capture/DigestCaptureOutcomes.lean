import DigestCapturePolicies
set_option autoImplicit false
namespace RelationalSuccessor.CandidateDigestCapture
open CandidateBindingCapture (Envelope EnvelopeMeaning Prepared)
open CandidateDigest (Profile Outcome classifyDigest VerifiedDigestMeaning)

inductive CaptureOutcome (α : Type) where
  | invalidEnvelope
  | digestRefused (reason : Outcome)
  | byteStage (reason : CandidateBindingBytes.CaptureOutcome α)
  deriving Repr

def classifyCheckedCapture {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope) : CaptureOutcome α :=
  if CandidateBindingCapture.envelopeCheck capture then
    let result := classifyDigest profile capture.digestProfile capture.content capture.digest budget
    if result=.verified then .byteStage (CandidateBindingBytes.classifyCaptureBytes version kind target frame capture)
    else .digestRefused result
  else .invalidEnvelope

theorem checked_invalid_envelope_exact {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope) :
    classifyCheckedCapture profile budget version kind target frame capture=.invalidEnvelope ↔ ¬EnvelopeMeaning capture := by
  rw [←CandidateBindingCapture.envelope_check_exact capture]
  cases good : CandidateBindingCapture.envelopeCheck capture <;>
    cases result : classifyDigest profile capture.digestProfile capture.content capture.digest budget <;>
    simp [classifyCheckedCapture,good,result]

theorem checked_digest_refusal_exact {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope) (reason : Outcome) :
    classifyCheckedCapture profile budget version kind target frame capture=.digestRefused reason ↔
      EnvelopeMeaning capture ∧ classifyDigest profile capture.digestProfile capture.content capture.digest budget=reason ∧ reason≠.verified := by
  rw [←CandidateBindingCapture.envelope_check_exact capture]
  cases good : CandidateBindingCapture.envelopeCheck capture <;> cases reason <;>
    cases result : classifyDigest profile capture.digestProfile capture.content capture.digest budget <;>
    simp [classifyCheckedCapture,good,result]

theorem checked_byte_stage_exact {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope)
    (reason : CandidateBindingBytes.CaptureOutcome α) :
    classifyCheckedCapture profile budget version kind target frame capture=.byteStage reason ↔
      EnvelopeMeaning capture ∧ VerifiedDigestMeaning profile capture.digestProfile capture.content capture.digest budget ∧
        CandidateBindingBytes.classifyCaptureBytes version kind target frame capture=reason := by
  rw [←CandidateBindingCapture.envelope_check_exact capture,←CandidateDigest.classified_verified_exact profile capture.digestProfile capture.content capture.digest budget]
  cases good : CandidateBindingCapture.envelopeCheck capture <;>
    cases result : classifyDigest profile capture.digestProfile capture.content capture.digest budget <;>
    simp [classifyCheckedCapture,good,result]

theorem checked_prepared_outcome_exact {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope) (prepared : Prepared α) :
    classifyCheckedCapture profile budget version kind target frame capture=.byteStage (.prepared prepared) ↔
      DigestPreparedMeaning profile budget version kind target frame capture prepared := by
  rw [checked_byte_stage_exact,CandidateBindingBytes.prepared_outcome_exact]
  constructor
  · rintro ⟨_,digest,bytes⟩;exact ⟨bytes,digest⟩
  · rintro ⟨⟨ast,parsed,data⟩,digest⟩;exact ⟨data.envelope,digest,ast,parsed,data⟩

theorem checked_outcome_entrypoint_agree {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope) (prepared : Prepared α) :
    classifyCheckedCapture profile budget version kind target frame capture=.byteStage (.prepared prepared) ↔
      prepareDigestBytes profile budget version kind target frame capture=some prepared :=
  (checked_prepared_outcome_exact profile budget version kind target frame capture prepared).trans
    (digest_capture_exact profile budget version kind target frame capture prepared).symm

theorem digest_verified_never_reported_as_refusal {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope) :
    classifyCheckedCapture profile budget version kind target frame capture≠.digestRefused .verified := by
  intro outcome
  exact ((checked_digest_refusal_exact profile budget version kind target frame capture .verified).mp outcome).2.2 rfl

theorem byte_invalid_envelope_unreachable {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope) :
    classifyCheckedCapture profile budget version kind target frame capture≠.byteStage .invalidEnvelope := by
  intro outcome
  have parts := (checked_byte_stage_exact profile budget version kind target frame capture .invalidEnvelope).mp outcome
  exact ((CandidateBindingBytes.invalid_envelope_outcome_exact version kind target frame capture).mp parts.2.2) parts.1

theorem checked_stale_frame_exact {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope)
    (record : CandidateBindingRecords.Record α) :
    classifyCheckedCapture profile budget version kind target frame capture=.byteStage (.staleFrame record) ↔
      EnvelopeMeaning capture ∧ VerifiedDigestMeaning profile capture.digestProfile capture.content capture.digest budget ∧
        CandidateBindingBytes.RecordBytesMeaning version kind target capture.content record ∧ record.body.frame≠frame := by
  rw [checked_byte_stage_exact,CandidateBindingBytes.stale_frame_outcome_exact]
  constructor
  · rintro ⟨envelope,digest,_,record,stale⟩;exact ⟨envelope,digest,record,stale⟩
  · rintro ⟨envelope,digest,record,stale⟩;exact ⟨envelope,digest,envelope,record,stale⟩

theorem checked_syntax_exact {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope)  :
    classifyCheckedCapture profile budget version kind target frame capture=.byteStage (.recordRefused .invalidSyntax) ↔
      EnvelopeMeaning capture ∧ VerifiedDigestMeaning profile capture.digestProfile capture.content capture.digest budget ∧
        (¬∃raw,CandidateJsonBytes.ByteDocumentMeaning capture.content raw) := by
  rw [checked_byte_stage_exact,CandidateBindingBytes.capture_invalid_syntax_meaning_exact]
  constructor
  · rintro ⟨envelope,digest,_,rest⟩;exact ⟨envelope,digest,rest⟩
  · rintro ⟨envelope,digest,rest⟩;exact ⟨envelope,digest,envelope,rest⟩

theorem checked_scalar_exact {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope) (raw : CandidateJsonBytes.RawValue) :
    classifyCheckedCapture profile budget version kind target frame capture=.byteStage (.recordRefused (.unsupportedScalar raw)) ↔
      EnvelopeMeaning capture ∧ VerifiedDigestMeaning profile capture.digestProfile capture.content capture.digest budget ∧
        (CandidateJsonBytes.ByteDocumentMeaning capture.content raw ∧ ¬∃value,CandidateScalarConversion.ValueMeaning raw value) := by
  rw [checked_byte_stage_exact,CandidateBindingBytes.capture_unsupported_scalar_meaning_exact]
  constructor
  · rintro ⟨envelope,digest,_,rest⟩;exact ⟨envelope,digest,rest⟩
  · rintro ⟨envelope,digest,rest⟩;exact ⟨envelope,digest,envelope,rest⟩

theorem checked_record_exact {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope) (ast : CandidateBindingCapture.J) :
    classifyCheckedCapture profile budget version kind target frame capture=.byteStage (.recordRefused (.invalidRecord ast)) ↔
      EnvelopeMeaning capture ∧ VerifiedDigestMeaning profile capture.digestProfile capture.content capture.digest budget ∧
        (CandidateScalarConversion.ScalarByteDocumentMeaning capture.content ast ∧ ¬∃record,CandidateBindingRecords.RecordMeaning version kind target ast record) := by
  rw [checked_byte_stage_exact,CandidateBindingBytes.capture_invalid_record_meaning_exact]
  constructor
  · rintro ⟨envelope,digest,_,rest⟩;exact ⟨envelope,digest,rest⟩
  · rintro ⟨envelope,digest,rest⟩;exact ⟨envelope,digest,envelope,rest⟩

theorem checked_profile_refusal_exact {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope) :
    classifyCheckedCapture profile budget version kind target frame capture=.digestRefused .unsupportedProfile ↔
      EnvelopeMeaning capture ∧ (¬CandidateDigest.ProfileMeaning profile capture.digestProfile) := by
  rw [checked_digest_refusal_exact,CandidateDigest.profile_refusal_exact]
  simp

theorem checked_domain_refusal_exact {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope) :
    classifyCheckedCapture profile budget version kind target frame capture=.digestRefused .outsideAlgorithmDomain ↔
      EnvelopeMeaning capture ∧ (CandidateDigest.ProfileMeaning profile capture.digestProfile ∧ ¬capture.content.length<2^61) := by
  rw [checked_digest_refusal_exact,CandidateDigest.domain_refusal_exact]
  simp

theorem checked_budget_refusal_exact {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope) :
    classifyCheckedCapture profile budget version kind target frame capture=.digestRefused .byteBudgetExceeded ↔
      EnvelopeMeaning capture ∧ (CandidateDigest.ProfileMeaning profile capture.digestProfile ∧ capture.content.length<2^61 ∧ ¬capture.content.length≤budget) := by
  rw [checked_digest_refusal_exact,CandidateDigest.budget_refusal_exact]
  simp

theorem checked_format_refusal_exact {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope) :
    classifyCheckedCapture profile budget version kind target frame capture=.digestRefused .malformedDigest ↔
      EnvelopeMeaning capture ∧ (CandidateDigest.ProfileMeaning profile capture.digestProfile ∧ capture.content.length<2^61 ∧ capture.content.length≤budget ∧ ¬CandidateDigest.HexMeaning capture.digest) := by
  rw [checked_digest_refusal_exact,CandidateDigest.malformed_refusal_exact]
  simp

theorem checked_mismatch_refusal_exact {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope) :
    classifyCheckedCapture profile budget version kind target frame capture=.digestRefused .digestMismatch ↔
      EnvelopeMeaning capture ∧ (CandidateDigest.ProfileMeaning profile capture.digestProfile ∧ capture.content.length<2^61 ∧ capture.content.length≤budget ∧ CandidateDigest.HexMeaning capture.digest ∧ ¬CandidateDigest.DigestMeaning capture.content capture.digest) := by
  rw [checked_digest_refusal_exact,CandidateDigest.mismatch_refusal_exact]
  simp
#print axioms checked_invalid_envelope_exact
#print axioms checked_digest_refusal_exact
#print axioms checked_byte_stage_exact
#print axioms checked_prepared_outcome_exact
#print axioms checked_outcome_entrypoint_agree
#print axioms digest_verified_never_reported_as_refusal
#print axioms byte_invalid_envelope_unreachable
#print axioms checked_stale_frame_exact
#print axioms checked_syntax_exact
#print axioms checked_scalar_exact
#print axioms checked_record_exact
#print axioms checked_profile_refusal_exact
#print axioms checked_domain_refusal_exact
#print axioms checked_budget_refusal_exact
#print axioms checked_format_refusal_exact
#print axioms checked_mismatch_refusal_exact
end RelationalSuccessor.CandidateDigestCapture
