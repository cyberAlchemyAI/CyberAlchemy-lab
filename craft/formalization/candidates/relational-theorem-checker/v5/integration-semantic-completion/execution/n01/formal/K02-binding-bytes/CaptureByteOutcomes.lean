import CaptureBytes
import BindingBytesOutcomes
set_option autoImplicit false
namespace RelationalSuccessor.CandidateBindingBytes
open CandidateBindingCapture (Envelope EnvelopeMeaning Prepared)

def RecordRefusal {α : Type} : RecordOutcome α → Prop
  | .invalidSyntax => True
  | .unsupportedScalar _ => True
  | .invalidRecord _ => True
  | .decoded _ => False

inductive CaptureOutcome (α : Type) where
  | invalidEnvelope
  | recordRefused (reason : RecordOutcome α)
  | staleFrame (record : CandidateBindingRecords.Record α)
  | prepared (output : Prepared α)
  deriving Repr

def classifyCaptureBytes {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) : CaptureOutcome α :=
  if CandidateBindingCapture.envelopeCheck capture then
    match classifyRecordBytes version kind target capture.content with
    | .invalidSyntax => .recordRefused .invalidSyntax
    | .unsupportedScalar raw => .recordRefused (.unsupportedScalar raw)
    | .invalidRecord ast => .recordRefused (.invalidRecord ast)
    | .decoded record => if record.body.frame = frame then .prepared ⟨record,capture⟩ else .staleFrame record
  else .invalidEnvelope

theorem invalid_envelope_outcome_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) :
    classifyCaptureBytes version kind target frame capture = .invalidEnvelope ↔ ¬ EnvelopeMeaning capture := by
  rw [← CandidateBindingCapture.envelope_check_exact capture]
  cases good : CandidateBindingCapture.envelopeCheck capture with
  | false => simp [classifyCaptureBytes,good]
  | true =>
      cases decoded : classifyRecordBytes version kind target capture.content with
      | invalidSyntax => simp [classifyCaptureBytes,good,decoded]
      | unsupportedScalar raw => simp [classifyCaptureBytes,good,decoded]
      | invalidRecord ast => simp [classifyCaptureBytes,good,decoded]
      | decoded record => by_cases same : record.body.frame = frame <;> simp [classifyCaptureBytes,good,decoded,same]

theorem record_refusal_outcome_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (reason : RecordOutcome α) :
    classifyCaptureBytes version kind target frame capture = .recordRefused reason ↔
      EnvelopeMeaning capture ∧ classifyRecordBytes version kind target capture.content = reason ∧ RecordRefusal reason := by
  rw [← CandidateBindingCapture.envelope_check_exact capture]
  cases good : CandidateBindingCapture.envelopeCheck capture with
  | false => simp [classifyCaptureBytes,good]
  | true =>
      cases decoded : classifyRecordBytes version kind target capture.content with
      | invalidSyntax => cases reason <;> simp [classifyCaptureBytes,good,decoded,RecordRefusal]
      | unsupportedScalar raw => cases reason <;> simp [classifyCaptureBytes,good,decoded,RecordRefusal]
      | invalidRecord ast => cases reason <;> simp [classifyCaptureBytes,good,decoded,RecordRefusal]
      | decoded record => cases reason <;> by_cases same : record.body.frame = frame <;>
          simp [classifyCaptureBytes,good,decoded,same,RecordRefusal]

theorem decoded_never_reported_as_refusal {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (record : CandidateBindingRecords.Record α) :
    classifyCaptureBytes version kind target frame capture ≠ .recordRefused (.decoded record) := by
  intro outcome
  have invalid := ((record_refusal_outcome_exact version kind target frame capture (.decoded record)).mp outcome).2.2
  exact invalid

theorem stale_frame_outcome_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (record : CandidateBindingRecords.Record α) :
    classifyCaptureBytes version kind target frame capture = .staleFrame record ↔
      EnvelopeMeaning capture ∧ RecordBytesMeaning version kind target capture.content record ∧ record.body.frame ≠ frame := by
  rw [← CandidateBindingCapture.envelope_check_exact capture,← decoded_record_outcome_exact version kind target capture.content record]
  cases good : CandidateBindingCapture.envelopeCheck capture with
  | false => simp [classifyCaptureBytes,good]
  | true =>
      cases decoded : classifyRecordBytes version kind target capture.content with
      | invalidSyntax => simp [classifyCaptureBytes,good,decoded]
      | unsupportedScalar raw => simp [classifyCaptureBytes,good,decoded]
      | invalidRecord ast => simp [classifyCaptureBytes,good,decoded]
      | decoded actual =>
          by_cases same : actual.body.frame = frame
          · simp [classifyCaptureBytes,good,decoded,same]
            intro equal; cases equal; exact same
          · simp [classifyCaptureBytes,good,decoded,same]
            intro equal; cases equal; exact same

theorem prepared_outcome_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (prepared : Prepared α) :
    classifyCaptureBytes version kind target frame capture = .prepared prepared ↔
      PreparedBytesMeaning version kind target frame capture prepared := by
  constructor
  · intro outcome
    unfold classifyCaptureBytes at outcome
    split at outcome
    · rename_i good
      cases decoded : classifyRecordBytes version kind target capture.content with
      | invalidSyntax => simp [decoded] at outcome
      | unsupportedScalar raw => simp [decoded] at outcome
      | invalidRecord ast => simp [decoded] at outcome
      | decoded record =>
          simp only [decoded] at outcome
          split at outcome
          · rename_i sameFrame
            simp only [CaptureOutcome.prepared.injEq] at outcome
            subst prepared
            apply (prepared_bytes_components version kind target frame capture ⟨record,capture⟩).mpr
            exact ⟨(CandidateBindingCapture.envelope_check_exact capture).mp good,
              (decoded_record_outcome_exact version kind target capture.content record).mp decoded,sameFrame,rfl⟩
          · simp at outcome
    · simp at outcome
  · intro meaning
    rcases (prepared_bytes_components version kind target frame capture prepared).mp meaning with ⟨good,recordMeaning,sameFrame,sameCapture⟩
    have decoded := (decoded_record_outcome_exact version kind target capture.content prepared.record).mpr recordMeaning
    have same : Prepared.mk prepared.record capture = prepared := by
      cases prepared with
      | mk record envelope => simp only at sameCapture; cases sameCapture; rfl
    simp only [classifyCaptureBytes,(CandidateBindingCapture.envelope_check_exact capture).mpr good,
      if_true,decoded,if_pos sameFrame,same]

theorem prepared_outcome_matches_entrypoint {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (prepared : Prepared α) :
    classifyCaptureBytes version kind target frame capture = .prepared prepared ↔
      prepareBytes version kind target frame capture = some prepared :=
  (prepared_outcome_exact version kind target frame capture prepared).trans (prepare_bytes_exact version kind target frame capture prepared).symm

theorem capture_invalid_syntax_meaning_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) :
    classifyCaptureBytes version kind target frame capture = .recordRefused .invalidSyntax ↔
      EnvelopeMeaning capture ∧ ¬ ∃ raw, CandidateJsonBytes.ByteDocumentMeaning capture.content raw := by
  rw [record_refusal_outcome_exact,invalid_syntax_outcome_exact]
  simp only [RecordRefusal,and_true]

theorem capture_unsupported_scalar_meaning_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (raw : CandidateJsonBytes.RawValue) :
    classifyCaptureBytes version kind target frame capture = .recordRefused (.unsupportedScalar raw) ↔
      EnvelopeMeaning capture ∧ CandidateJsonBytes.ByteDocumentMeaning capture.content raw ∧
        ¬ ∃ value, CandidateScalarConversion.ValueMeaning raw value := by
  rw [record_refusal_outcome_exact,unsupported_scalar_outcome_exact]
  simp only [RecordRefusal,and_true]

theorem capture_invalid_record_meaning_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (ast : J) :
    classifyCaptureBytes version kind target frame capture = .recordRefused (.invalidRecord ast) ↔
      EnvelopeMeaning capture ∧ CandidateScalarConversion.ScalarByteDocumentMeaning capture.content ast ∧
        ¬ ∃ record, CandidateBindingRecords.RecordMeaning version kind target ast record := by
  rw [record_refusal_outcome_exact,invalid_record_outcome_exact]
  simp only [RecordRefusal,and_true]

#print axioms invalid_envelope_outcome_exact
#print axioms record_refusal_outcome_exact
#print axioms decoded_never_reported_as_refusal
#print axioms stale_frame_outcome_exact
#print axioms prepared_outcome_exact
#print axioms prepared_outcome_matches_entrypoint
#print axioms capture_invalid_syntax_meaning_exact
#print axioms capture_unsupported_scalar_meaning_exact
#print axioms capture_invalid_record_meaning_exact
end RelationalSuccessor.CandidateBindingBytes
