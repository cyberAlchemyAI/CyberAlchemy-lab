import BindingRecordBytes
set_option autoImplicit false
namespace RelationalSuccessor.CandidateBindingBytes
open CandidateScalarConversion (ScalarByteDocumentMeaning parseScalarDocumentBytes)
open CandidateBindingCapture (Envelope EnvelopeMeaning Prepared PreparedMeaning)

def PreparedBytesMeaning {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (prepared : Prepared α) : Prop :=
  ∃ ast, ScalarByteDocumentMeaning capture.content ast ∧ PreparedMeaning version kind target frame capture ast prepared

def prepareBytes {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) : Option (Prepared α) :=
  (parseScalarDocumentBytes capture.content).bind (CandidateBindingCapture.prepare version kind target frame capture)

theorem prepare_bytes_sound {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (prepared : Prepared α)
    (parsed : prepareBytes version kind target frame capture = some prepared) :
    PreparedBytesMeaning version kind target frame capture prepared := by
  unfold prepareBytes at parsed
  cases decoded : parseScalarDocumentBytes capture.content with
  | none => simp [decoded] at parsed
  | some ast =>
      simp only [decoded,Option.bind_some] at parsed
      exact ⟨ast,(CandidateScalarConversion.scalar_byte_document_exact capture.content ast).mp decoded,
        (CandidateBindingCapture.prepare_exact version kind target frame capture ast prepared).mp parsed⟩

theorem prepare_bytes_complete {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (prepared : Prepared α)
    (meaning : PreparedBytesMeaning version kind target frame capture prepared) :
    prepareBytes version kind target frame capture = some prepared := by
  rcases meaning with ⟨ast,byteMeaning,data⟩
  simp only [prepareBytes,(CandidateScalarConversion.scalar_byte_document_exact capture.content ast).mpr byteMeaning,
    Option.bind_some]
  exact (CandidateBindingCapture.prepare_exact version kind target frame capture ast prepared).mpr data

theorem prepare_bytes_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (prepared : Prepared α) :
    prepareBytes version kind target frame capture = some prepared ↔ PreparedBytesMeaning version kind target frame capture prepared :=
  ⟨prepare_bytes_sound version kind target frame capture prepared,prepare_bytes_complete version kind target frame capture prepared⟩

theorem prepare_bytes_none_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) : prepareBytes version kind target frame capture = none ↔
      ¬ ∃ prepared, PreparedBytesMeaning version kind target frame capture prepared := by
  constructor
  · intro refused; rintro ⟨prepared,meaning⟩
    have accepted := prepare_bytes_complete version kind target frame capture prepared meaning
    rw [refused] at accepted; contradiction
  · intro invalid
    cases parsed : prepareBytes version kind target frame capture with
    | none => rfl
    | some prepared => exact False.elim (invalid ⟨prepared,prepare_bytes_sound version kind target frame capture prepared parsed⟩)

theorem prepared_bytes_unique {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (first second : Prepared α)
    (a : PreparedBytesMeaning version kind target frame capture first)
    (b : PreparedBytesMeaning version kind target frame capture second) : first = second :=
  Option.some.inj ((prepare_bytes_complete version kind target frame capture first a).symm.trans
    (prepare_bytes_complete version kind target frame capture second b))

theorem prepared_bytes_record_meaning {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (prepared : Prepared α)
    (meaning : PreparedBytesMeaning version kind target frame capture prepared) :
    RecordBytesMeaning version kind target capture.content prepared.record := by
  rcases meaning with ⟨ast,byteMeaning,data⟩
  exact ⟨ast,byteMeaning,data.decoded⟩

theorem prepared_bytes_entry_fields {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (prepared : Prepared α)
    (meaning : PreparedBytesMeaning version kind target frame capture prepared) :
    prepared.entry.ref.key = prepared.record.bindingKey ∧ prepared.entry.ref.digest = capture.digest ∧
    prepared.entry.sourceKind = kind ∧ prepared.entry.body = prepared.record.body ∧
    prepared.entry.content = capture.content ∧ prepared.entry.ownerReview = prepared.record.ownerReview ∧
    prepared.entry.body.frame = frame := by
  rcases meaning with ⟨ast,_,data⟩
  exact CandidateBindingCapture.prepared_entry_field_bridge version kind target frame capture ast prepared
    ((CandidateBindingCapture.prepare_exact version kind target frame capture ast prepared).mpr data)

theorem prepared_bytes_retains_capture {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (prepared : Prepared α)
    (meaning : PreparedBytesMeaning version kind target frame capture prepared) :
    prepared.envelope = capture ∧ prepared.envelope.byteLength = prepared.entry.content.length := by
  rcases meaning with ⟨ast,_,data⟩
  refine ⟨data.capture,?_⟩
  simp only [CandidateBindingCapture.Prepared.entry,data.capture]
  exact data.envelope.length

theorem bad_envelope_prevents_byte_preparation {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (bad : ¬ EnvelopeMeaning capture) :
    prepareBytes version kind target frame capture = none := by
  apply (prepare_bytes_none_exact version kind target frame capture).mpr
  rintro ⟨prepared,ast,_,data⟩
  exact bad data.envelope

def prepareResolutionBytes (frame : Frame) (capture : Envelope) : Option (Prepared CandidateIntentAddressing.Resolution) :=
  prepareBytes CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution frame capture

def prepareRoleBytes (frame : Frame) (capture : Envelope) : Option (Prepared CandidateIntentAddressing.Role) :=
  prepareBytes CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role frame capture

theorem prepare_resolution_bytes_exact (frame : Frame) (capture : Envelope) (prepared : Prepared CandidateIntentAddressing.Resolution) :
    prepareResolutionBytes frame capture = some prepared ↔ PreparedBytesMeaning CandidateBindingRecords.resolutionVersion
      CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution frame capture prepared :=
  prepare_bytes_exact CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution frame capture prepared

theorem prepare_role_bytes_exact (frame : Frame) (capture : Envelope) (prepared : Prepared CandidateIntentAddressing.Role) :
    prepareRoleBytes frame capture = some prepared ↔ PreparedBytesMeaning CandidateBindingRecords.roleVersion
      CandidateBindingRecords.roleKind CandidateBindingAst.role frame capture prepared :=
  prepare_bytes_exact CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role frame capture prepared

-- Only the parse relation is supplied by this adapter. Every other policy stays
-- exactly the caller's separate requirement; no default evidence is constructed.
def withParsedPolicy {α : Type} (policies : CandidateBindingCapture.Policies α) : CandidateBindingCapture.Policies α :=
  { policies with parses := ScalarByteDocumentMeaning }

theorem parsed_policy_exact {α : Type} (policies : CandidateBindingCapture.Policies α)
    (bytes : CandidateJsonBytes.Bytes) (ast : J) :
    (withParsedPolicy policies).parses bytes ast ↔ ScalarByteDocumentMeaning bytes ast := Iff.rfl

theorem remaining_capture_policies_unchanged {α : Type} (policies : CandidateBindingCapture.Policies α) :
    (withParsedPolicy policies).digest = policies.digest ∧
    (withParsedPolicy policies).ownedDigestProfile = policies.ownedDigestProfile ∧
    (withParsedPolicy policies).schema = policies.schema ∧
    (withParsedPolicy policies).reviewed = policies.reviewed := ⟨rfl,rfl,rfl,rfl⟩

theorem parsed_capture_construction {α : Type} (policies : CandidateBindingCapture.Policies α)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope)
    (ast : J) (prepared : Prepared α) (data : PreparedMeaning version kind target frame capture ast prepared)
    (parsed : ScalarByteDocumentMeaning capture.content ast)
    (digest : policies.digest capture.digestProfile capture.content capture.digest)
    (owned : policies.ownedDigestProfile frame capture.digestProfile)
    (schema : policies.schema frame version kind ast)
    (reviewed : policies.reviewed frame prepared.entry) :
    CandidateBindingCapture.CaptureMeaning (withParsedPolicy policies) version kind target frame capture ast prepared :=
  ⟨data,parsed,digest,owned,schema,reviewed⟩

theorem parsed_capture_implies_byte_preparation {α : Type} (policies : CandidateBindingCapture.Policies α)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) (capture : Envelope)
    (ast : J) (prepared : Prepared α)
    (meaning : CandidateBindingCapture.CaptureMeaning (withParsedPolicy policies) version kind target frame capture ast prepared) :
    prepareBytes version kind target frame capture = some prepared :=
  prepare_bytes_complete version kind target frame capture prepared ⟨ast,meaning.bytesParse,meaning.preparedData⟩

theorem prepared_bytes_components {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (prepared : Prepared α) :
    PreparedBytesMeaning version kind target frame capture prepared ↔
      EnvelopeMeaning capture ∧ RecordBytesMeaning version kind target capture.content prepared.record ∧
      prepared.record.body.frame = frame ∧ prepared.envelope = capture := by
  constructor
  · rintro ⟨ast,byteMeaning,data⟩
    exact ⟨data.envelope,⟨ast,byteMeaning,data.decoded⟩,data.frame,data.capture⟩
  · rintro ⟨envelope,⟨ast,byteMeaning,recordMeaning⟩,sameFrame,sameCapture⟩
    exact ⟨ast,byteMeaning,⟨envelope,recordMeaning,sameFrame,sameCapture⟩⟩

#print axioms prepare_bytes_sound
#print axioms prepare_bytes_complete
#print axioms prepare_bytes_exact
#print axioms prepare_bytes_none_exact
#print axioms prepared_bytes_unique
#print axioms prepared_bytes_record_meaning
#print axioms prepared_bytes_entry_fields
#print axioms prepared_bytes_retains_capture
#print axioms bad_envelope_prevents_byte_preparation
#print axioms prepare_resolution_bytes_exact
#print axioms prepare_role_bytes_exact
#print axioms parsed_policy_exact
#print axioms remaining_capture_policies_unchanged
#print axioms parsed_capture_construction
#print axioms parsed_capture_implies_byte_preparation
#print axioms prepared_bytes_components
end RelationalSuccessor.CandidateBindingBytes
