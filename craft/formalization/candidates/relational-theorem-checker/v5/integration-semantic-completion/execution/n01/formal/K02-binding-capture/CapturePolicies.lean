import CaptureEnvelope
set_option autoImplicit false
namespace RelationalSuccessor.CandidateBindingCapture
open RelationalSuccessor

-- Open provider requirements. No implementation, default predicates, authentication
-- boolean, signature verification or digest algorithm realization is supplied.
structure Policies (α : Type) where
  parses : List UInt8 → J → Prop
  digest : RevisionRef → List UInt8 → String → Prop
  ownedDigestProfile : Frame → RevisionRef → Prop
  schema : Frame → String → String → J → Prop
  reviewed : Frame → CandidateOwnedBindings.Entry α → Prop

structure CaptureMeaning {α : Type} (policies : Policies α) (version kind : String)
    (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope)
    (ast : J) (prepared : Prepared α) : Prop where
  preparedData : PreparedMeaning version kind target frame capture ast prepared
  bytesParse : policies.parses capture.content ast
  digest : policies.digest capture.digestProfile capture.content capture.digest
  ownedProfile : policies.ownedDigestProfile frame capture.digestProfile
  schema : policies.schema frame version kind ast
  reviewed : policies.reviewed frame prepared.entry

-- These are conditional construction/refinement results. They cannot realize the
-- provider predicates or certify the application's real source policy.
theorem capture_construction_exact {α : Type} (policies : Policies α) (version kind : String)
    (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope)
    (ast : J) (prepared : Prepared α) :
    CaptureMeaning policies version kind target frame capture ast prepared ↔
      prepare version kind target frame capture ast = some prepared ∧
      policies.parses capture.content ast ∧
      policies.digest capture.digestProfile capture.content capture.digest ∧
      policies.ownedDigestProfile frame capture.digestProfile ∧
      policies.schema frame version kind ast ∧ policies.reviewed frame prepared.entry := by
  constructor
  · intro meaning
    exact ⟨(prepare_exact version kind target frame capture ast prepared).mpr meaning.preparedData,
      meaning.bytesParse,meaning.digest,meaning.ownedProfile,meaning.schema,meaning.reviewed⟩
  · rintro ⟨h,p,d,o,s,r⟩
    exact ⟨(prepare_exact version kind target frame capture ast prepared).mp h,p,d,o,s,r⟩

theorem captured_entry_evidence_bridge {α : Type} (policies : Policies α) (version kind : String)
    (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope)
    (ast : J) (prepared : Prepared α)
    (meaning : CaptureMeaning policies version kind target frame capture ast prepared) :
    EntryProjectionMeaning prepared prepared.entry ∧
      policies.parses prepared.entry.content ast ∧
      policies.digest prepared.envelope.digestProfile prepared.entry.content prepared.entry.ref.digest ∧
      policies.ownedDigestProfile frame prepared.envelope.digestProfile ∧
      policies.schema frame prepared.record.schemaVersion prepared.entry.sourceKind ast ∧
      policies.reviewed prepared.entry.body.frame prepared.entry := by
  have constants := CandidateBindingRecords.accepted_record_constants version kind target ast prepared.record
    ((CandidateBindingRecords.record_exact version kind target ast prepared.record).mpr meaning.preparedData.decoded)
  refine ⟨(entry_projection_exact prepared prepared.entry).mp rfl,?_,?_,?_,?_,?_⟩
  · simpa only [Prepared.entry,meaning.preparedData.capture] using meaning.bytesParse
  · simpa only [Prepared.entry,meaning.preparedData.capture] using meaning.digest
  · simpa only [meaning.preparedData.capture] using meaning.ownedProfile
  · simpa only [Prepared.entry,constants.1,constants.2] using meaning.schema
  · simpa only [Prepared.entry,meaning.preparedData.frame] using meaning.reviewed

theorem absent_review_prevents_capture {α : Type} (policies : Policies α) (version kind : String)
    (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope)
    (ast : J) (prepared : Prepared α) (absent : ¬ policies.reviewed frame prepared.entry) :
    ¬ CaptureMeaning policies version kind target frame capture ast prepared := by
  intro meaning; exact absent meaning.reviewed

theorem unparsed_bytes_prevent_capture {α : Type} (policies : Policies α) (version kind : String)
    (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope)
    (ast : J) (prepared : Prepared α) (unparsed : ¬ policies.parses capture.content ast) :
    ¬ CaptureMeaning policies version kind target frame capture ast prepared := by
  intro meaning; exact unparsed meaning.bytesParse

#print axioms capture_construction_exact
#print axioms captured_entry_evidence_bridge
#print axioms absent_review_prevents_capture
#print axioms unparsed_bytes_prevent_capture
end RelationalSuccessor.CandidateBindingCapture
