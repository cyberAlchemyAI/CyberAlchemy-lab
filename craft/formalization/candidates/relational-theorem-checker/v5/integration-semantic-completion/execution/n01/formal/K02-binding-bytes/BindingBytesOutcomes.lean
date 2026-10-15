import BindingRecordBytes
set_option autoImplicit false
namespace RelationalSuccessor.CandidateBindingBytes
open CandidateJsonBytes (Bytes RawValue ByteDocumentMeaning)
open CandidateScalarConversion (ScalarByteDocumentMeaning)

inductive RecordOutcome (α : Type) where
  | invalidSyntax
  | unsupportedScalar (raw : RawValue)
  | invalidRecord (ast : J)
  | decoded (record : CandidateBindingRecords.Record α)
  deriving Repr

def classifyRecordBytes {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (bytes : Bytes) : RecordOutcome α :=
  match CandidateScalarConversion.classifyBytes bytes with
  | .invalidSyntax => .invalidSyntax
  | .unsupportedScalar raw => .unsupportedScalar raw
  | .converted ast => match (CandidateBindingRecords.record version kind target).decode ast with
      | none => .invalidRecord ast
      | some record => .decoded record

theorem record_ast_none_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (ast : J) : (CandidateBindingRecords.record version kind target).decode ast = none ↔
      ¬ ∃ record, CandidateBindingRecords.RecordMeaning version kind target ast record := by
  constructor
  · intro refused; rintro ⟨record,meaning⟩
    have accepted := (CandidateBindingRecords.record_exact version kind target ast record).mpr meaning
    rw [refused] at accepted; contradiction
  · intro invalid
    cases parsed : (CandidateBindingRecords.record version kind target).decode ast with
    | none => rfl
    | some record => exact False.elim (invalid ⟨record,(CandidateBindingRecords.record_exact version kind target ast record).mp parsed⟩)

theorem invalid_syntax_outcome_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (bytes : Bytes) : classifyRecordBytes version kind target bytes = .invalidSyntax ↔
      ¬ ∃ raw, ByteDocumentMeaning bytes raw := by
  have same : classifyRecordBytes version kind target bytes = .invalidSyntax ↔
      CandidateScalarConversion.classifyBytes bytes = .invalidSyntax := by
    cases parsed : CandidateScalarConversion.classifyBytes bytes with
    | invalidSyntax => simp [classifyRecordBytes,parsed]
    | unsupportedScalar raw => simp [classifyRecordBytes,parsed]
    | converted ast => cases decoded : (CandidateBindingRecords.record version kind target).decode ast <;>
        simp [classifyRecordBytes,parsed,decoded]
  exact same.trans (CandidateScalarConversion.invalid_outcome_exact bytes)

theorem unsupported_scalar_outcome_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (bytes : Bytes) (raw : RawValue) : classifyRecordBytes version kind target bytes = .unsupportedScalar raw ↔
      ByteDocumentMeaning bytes raw ∧ ¬ ∃ value, CandidateScalarConversion.ValueMeaning raw value := by
  have same : classifyRecordBytes version kind target bytes = .unsupportedScalar raw ↔
      CandidateScalarConversion.classifyBytes bytes = .unsupportedScalar raw := by
    cases parsed : CandidateScalarConversion.classifyBytes bytes with
    | invalidSyntax => simp [classifyRecordBytes,parsed]
    | unsupportedScalar actual => simp [classifyRecordBytes,parsed]
    | converted ast => cases decoded : (CandidateBindingRecords.record version kind target).decode ast <;>
        simp [classifyRecordBytes,parsed,decoded]
  exact same.trans (CandidateScalarConversion.unsupported_outcome_exact bytes raw)

theorem invalid_record_outcome_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (bytes : Bytes) (ast : J) : classifyRecordBytes version kind target bytes = .invalidRecord ast ↔
      ScalarByteDocumentMeaning bytes ast ∧ ¬ ∃ record, CandidateBindingRecords.RecordMeaning version kind target ast record := by
  constructor
  · intro outcome
    cases parsed : CandidateScalarConversion.classifyBytes bytes with
    | invalidSyntax => simp [classifyRecordBytes,parsed] at outcome
    | unsupportedScalar raw => simp [classifyRecordBytes,parsed] at outcome
    | converted actual =>
        cases decoded : (CandidateBindingRecords.record version kind target).decode actual with
        | none =>
            simp only [classifyRecordBytes,parsed,decoded,RecordOutcome.invalidRecord.injEq] at outcome
            subst actual
            exact ⟨(CandidateScalarConversion.converted_outcome_exact bytes ast).mp parsed,
              (record_ast_none_exact version kind target ast).mp decoded⟩
        | some record => simp [classifyRecordBytes,parsed,decoded] at outcome
  · rintro ⟨byteMeaning,noRecord⟩
    simp only [classifyRecordBytes,(CandidateScalarConversion.converted_outcome_exact bytes ast).mpr byteMeaning,
      (record_ast_none_exact version kind target ast).mpr noRecord]

theorem decoded_record_outcome_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (bytes : Bytes) (record : CandidateBindingRecords.Record α) :
    classifyRecordBytes version kind target bytes = .decoded record ↔ RecordBytesMeaning version kind target bytes record := by
  constructor
  · intro outcome
    cases parsed : CandidateScalarConversion.classifyBytes bytes with
    | invalidSyntax => simp [classifyRecordBytes,parsed] at outcome
    | unsupportedScalar raw => simp [classifyRecordBytes,parsed] at outcome
    | converted ast =>
        cases decoded : (CandidateBindingRecords.record version kind target).decode ast with
        | none => simp [classifyRecordBytes,parsed,decoded] at outcome
        | some actual =>
            simp only [classifyRecordBytes,parsed,decoded,RecordOutcome.decoded.injEq] at outcome
            subst actual
            exact ⟨ast,(CandidateScalarConversion.converted_outcome_exact bytes ast).mp parsed,
              (CandidateBindingRecords.record_exact version kind target ast record).mp decoded⟩
  · rintro ⟨ast,byteMeaning,recordMeaning⟩
    simp only [classifyRecordBytes,(CandidateScalarConversion.converted_outcome_exact bytes ast).mpr byteMeaning,
      (CandidateBindingRecords.record_exact version kind target ast record).mpr recordMeaning]

theorem decoded_outcome_matches_entrypoint {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (bytes : Bytes) (record : CandidateBindingRecords.Record α) :
    classifyRecordBytes version kind target bytes = .decoded record ↔ decodeRecordBytes version kind target bytes = some record :=
  (decoded_record_outcome_exact version kind target bytes record).trans (record_bytes_exact version kind target bytes record).symm

#print axioms record_ast_none_exact
#print axioms invalid_syntax_outcome_exact
#print axioms unsupported_scalar_outcome_exact
#print axioms invalid_record_outcome_exact
#print axioms decoded_record_outcome_exact
#print axioms decoded_outcome_matches_entrypoint
end RelationalSuccessor.CandidateBindingBytes
