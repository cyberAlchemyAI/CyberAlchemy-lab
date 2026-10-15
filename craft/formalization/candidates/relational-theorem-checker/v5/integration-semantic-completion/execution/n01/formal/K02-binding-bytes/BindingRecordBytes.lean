import ScalarDocumentComposition
import CaptureCatalog
set_option autoImplicit false
namespace RelationalSuccessor.CandidateBindingBytes
open CandidateJsonBytes (Bytes RawValue ByteDocumentMeaning)
open CandidateScalarConversion (ScalarByteDocumentMeaning parseScalarDocumentBytes)
abbrev J := CandidateJsonSource.Value

def RecordBytesMeaning {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (bytes : Bytes) (record : CandidateBindingRecords.Record α) : Prop :=
  ∃ ast, ScalarByteDocumentMeaning bytes ast ∧ CandidateBindingRecords.RecordMeaning version kind target ast record

def decodeRecordBytes {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (bytes : Bytes) : Option (CandidateBindingRecords.Record α) :=
  (parseScalarDocumentBytes bytes).bind (CandidateBindingRecords.record version kind target).decode

theorem record_bytes_sound {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (bytes : Bytes) (record : CandidateBindingRecords.Record α)
    (parsed : decodeRecordBytes version kind target bytes = some record) :
    RecordBytesMeaning version kind target bytes record := by
  unfold decodeRecordBytes at parsed
  cases decoded : parseScalarDocumentBytes bytes with
  | none => simp [decoded] at parsed
  | some ast =>
      simp only [decoded,Option.bind_some] at parsed
      exact ⟨ast,(CandidateScalarConversion.scalar_byte_document_exact bytes ast).mp decoded,
        (CandidateBindingRecords.record_exact version kind target ast record).mp parsed⟩

theorem record_bytes_complete {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (bytes : Bytes) (record : CandidateBindingRecords.Record α)
    (meaning : RecordBytesMeaning version kind target bytes record) :
    decodeRecordBytes version kind target bytes = some record := by
  rcases meaning with ⟨ast,byteMeaning,recordMeaning⟩
  simp only [decodeRecordBytes,(CandidateScalarConversion.scalar_byte_document_exact bytes ast).mpr byteMeaning,
    Option.bind_some]
  exact (CandidateBindingRecords.record_exact version kind target ast record).mpr recordMeaning

theorem record_bytes_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (bytes : Bytes) (record : CandidateBindingRecords.Record α) :
    decodeRecordBytes version kind target bytes = some record ↔ RecordBytesMeaning version kind target bytes record :=
  ⟨record_bytes_sound version kind target bytes record,record_bytes_complete version kind target bytes record⟩

theorem record_bytes_unique {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (bytes : Bytes) (first second : CandidateBindingRecords.Record α)
    (a : RecordBytesMeaning version kind target bytes first) (b : RecordBytesMeaning version kind target bytes second) : first = second :=
  Option.some.inj ((record_bytes_complete version kind target bytes first a).symm.trans
    (record_bytes_complete version kind target bytes second b))

theorem record_bytes_none_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (bytes : Bytes) : decodeRecordBytes version kind target bytes = none ↔
      ¬ ∃ record, RecordBytesMeaning version kind target bytes record := by
  constructor
  · intro refused; rintro ⟨record,meaning⟩
    have accepted := record_bytes_complete version kind target bytes record meaning
    rw [refused] at accepted; contradiction
  · intro invalid
    cases parsed : decodeRecordBytes version kind target bytes with
    | none => rfl
    | some record => exact False.elim (invalid ⟨record,record_bytes_sound version kind target bytes record parsed⟩)

def decodeResolutionBytes (bytes : Bytes) : Option (CandidateBindingRecords.Record CandidateIntentAddressing.Resolution) :=
  decodeRecordBytes CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution bytes

def decodeRoleBytes (bytes : Bytes) : Option (CandidateBindingRecords.Record CandidateIntentAddressing.Role) :=
  decodeRecordBytes CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role bytes

theorem resolution_bytes_exact (bytes : Bytes) (record : CandidateBindingRecords.Record CandidateIntentAddressing.Resolution) :
    decodeResolutionBytes bytes = some record ↔ RecordBytesMeaning CandidateBindingRecords.resolutionVersion
      CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution bytes record :=
  record_bytes_exact CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution bytes record

theorem role_bytes_exact (bytes : Bytes) (record : CandidateBindingRecords.Record CandidateIntentAddressing.Role) :
    decodeRoleBytes bytes = some record ↔ RecordBytesMeaning CandidateBindingRecords.roleVersion
      CandidateBindingRecords.roleKind CandidateBindingAst.role bytes record :=
  record_bytes_exact CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role bytes record

theorem record_bytes_constants {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (bytes : Bytes) (record : CandidateBindingRecords.Record α)
    (meaning : RecordBytesMeaning version kind target bytes record) : record.schemaVersion = version ∧ record.kind = kind := by
  rcases meaning with ⟨ast,_,recordMeaning⟩
  exact CandidateBindingRecords.accepted_record_constants version kind target ast record
    ((CandidateBindingRecords.record_exact version kind target ast record).mpr recordMeaning)

theorem record_bytes_retains_all_fields {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (bytes : Bytes) (record : CandidateBindingRecords.Record α)
    (meaning : RecordBytesMeaning version kind target bytes record) :
    ∃ ast a b c d e, ScalarByteDocumentMeaning bytes ast ∧
      CandidateJsonSource.ObjectValueMeaning CandidateBindingRecords.recordKeys ast [a,b,c,d,e] ∧
      CandidateBindingRecords.ConstantMeaning version a record.schemaVersion ∧
      CandidateBindingAst.KeyMeaning b record.bindingKey ∧
      CandidateBindingRecords.ConstantMeaning kind c record.kind ∧
      CandidateBindingRecords.BodyMeaning target d record.body ∧
      CandidateBindingAst.ReferenceMeaning e record.ownerReview := by
  rcases meaning with ⟨ast,byteMeaning,recordMeaning⟩
  rcases CandidateBindingRecords.record_field_meanings version kind target ast record recordMeaning
    with ⟨a,b,c,d,e,fields⟩
  exact ⟨ast,a,b,c,d,e,byteMeaning,fields⟩

#print axioms record_bytes_sound
#print axioms record_bytes_complete
#print axioms record_bytes_exact
#print axioms record_bytes_unique
#print axioms record_bytes_none_exact
#print axioms resolution_bytes_exact
#print axioms role_bytes_exact
#print axioms record_bytes_constants
#print axioms record_bytes_retains_all_fields
end RelationalSuccessor.CandidateBindingBytes
