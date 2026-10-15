import ScalarValueDecoder
import DocumentExactness
set_option autoImplicit false
namespace RelationalSuccessor.CandidateScalarConversion
open CandidateJsonBytes (RawValue Bytes ByteDocumentMeaning)
open CandidateJsonParser (parseDocumentBytes)
open CandidateJsonCompleteness (byte_document_parser_exact byte_document_none_iff_no_meaning)

def ScalarByteDocumentMeaning (bytes : Bytes) (value : CandidateJsonSource.Value) : Prop :=
  ∃ raw, ByteDocumentMeaning bytes raw ∧ ValueMeaning raw value

def parseScalarDocumentBytes (bytes : Bytes) : Option CandidateJsonSource.Value :=
  (parseDocumentBytes bytes).bind convertValue

theorem scalar_byte_document_sound (bytes : Bytes) (value : CandidateJsonSource.Value)
    (parsed : parseScalarDocumentBytes bytes = some value) : ScalarByteDocumentMeaning bytes value := by
  unfold parseScalarDocumentBytes at parsed
  cases decoded : parseDocumentBytes bytes with
  | none => simp [decoded] at parsed
  | some raw =>
      simp only [decoded,Option.bind_some] at parsed
      exact ⟨raw,(byte_document_parser_exact bytes raw).mp decoded,convert_value_sound raw value parsed⟩

theorem scalar_byte_document_complete (bytes : Bytes) (value : CandidateJsonSource.Value)
    (meaning : ScalarByteDocumentMeaning bytes value) : parseScalarDocumentBytes bytes = some value := by
  rcases meaning with ⟨raw,grammar,scalar⟩
  simp only [parseScalarDocumentBytes,(byte_document_parser_exact bytes raw).mpr grammar,Option.bind_some]
  exact convert_value_complete raw value scalar

theorem scalar_byte_document_exact (bytes : Bytes) (value : CandidateJsonSource.Value) :
    parseScalarDocumentBytes bytes = some value ↔ ScalarByteDocumentMeaning bytes value :=
  ⟨scalar_byte_document_sound bytes value,scalar_byte_document_complete bytes value⟩

theorem scalar_byte_meaning_unique (bytes : Bytes) (first second : CandidateJsonSource.Value)
    (a : ScalarByteDocumentMeaning bytes first) (b : ScalarByteDocumentMeaning bytes second) : first = second :=
  Option.some.inj ((scalar_byte_document_complete bytes first a).symm.trans (scalar_byte_document_complete bytes second b))

theorem scalar_byte_none_exact (bytes : Bytes) :
    parseScalarDocumentBytes bytes = none ↔ ¬ ∃ value, ScalarByteDocumentMeaning bytes value := by
  constructor
  · intro refused; rintro ⟨value,meaning⟩
    have accepted := scalar_byte_document_complete bytes value meaning
    rw [refused] at accepted; contradiction
  · intro invalid
    cases parsed : parseScalarDocumentBytes bytes with
    | none => rfl
    | some value => exact False.elim (invalid ⟨value,scalar_byte_document_sound bytes value parsed⟩)

inductive ConversionOutcome where
  | invalidSyntax
  | unsupportedScalar (raw : RawValue)
  | converted (value : CandidateJsonSource.Value)
  deriving Repr

def classifyBytes (bytes : Bytes) : ConversionOutcome :=
  match parseDocumentBytes bytes with
  | none => .invalidSyntax
  | some raw => match convertValue raw with
      | none => .unsupportedScalar raw
      | some value => .converted value

theorem invalid_outcome_exact (bytes : Bytes) :
    classifyBytes bytes = .invalidSyntax ↔ ¬ ∃ raw, ByteDocumentMeaning bytes raw := by
  have same : classifyBytes bytes = .invalidSyntax ↔ parseDocumentBytes bytes = none := by
    cases parsed : parseDocumentBytes bytes with
    | none => simp [classifyBytes,parsed]
    | some raw => cases converted : convertValue raw <;> simp [classifyBytes,parsed,converted]
  exact same.trans (byte_document_none_iff_no_meaning bytes)

theorem unsupported_outcome_exact (bytes : Bytes) (raw : RawValue) :
    classifyBytes bytes = .unsupportedScalar raw ↔
      ByteDocumentMeaning bytes raw ∧ ¬ ∃ value, ValueMeaning raw value := by
  constructor
  · intro outcome
    cases parsed : parseDocumentBytes bytes with
    | none => simp [classifyBytes,parsed] at outcome
    | some actual =>
        cases converted : convertValue actual with
        | none =>
            simp only [classifyBytes,parsed,converted,ConversionOutcome.unsupportedScalar.injEq] at outcome
            subst actual
            exact ⟨(byte_document_parser_exact bytes raw).mp parsed,(conversion_none_exact raw).mp converted⟩
        | some value => simp [classifyBytes,parsed,converted] at outcome
  · rintro ⟨grammar,unsupported⟩
    simp only [classifyBytes,(byte_document_parser_exact bytes raw).mpr grammar,
      (conversion_none_exact raw).mpr unsupported]

theorem converted_outcome_exact (bytes : Bytes) (value : CandidateJsonSource.Value) :
    classifyBytes bytes = .converted value ↔ ScalarByteDocumentMeaning bytes value := by
  constructor
  · intro outcome
    cases parsed : parseDocumentBytes bytes with
    | none => simp [classifyBytes,parsed] at outcome
    | some raw =>
        cases converted : convertValue raw with
        | none => simp [classifyBytes,parsed,converted] at outcome
        | some actual =>
            simp only [classifyBytes,parsed,converted,ConversionOutcome.converted.injEq] at outcome
            subst actual
            exact ⟨raw,(byte_document_parser_exact bytes raw).mp parsed,convert_value_sound raw value converted⟩
  · rintro ⟨raw,grammar,meaning⟩
    simp only [classifyBytes,(byte_document_parser_exact bytes raw).mpr grammar,
      convert_value_complete raw value meaning]

theorem unsupported_is_valid_raw_document (bytes : Bytes) (raw : RawValue)
    (outcome : classifyBytes bytes = .unsupportedScalar raw) : ByteDocumentMeaning bytes raw :=
  ((unsupported_outcome_exact bytes raw).mp outcome).1

theorem unsupported_has_no_scalar_document (bytes : Bytes) (raw : RawValue)
    (outcome : classifyBytes bytes = .unsupportedScalar raw) : ¬ ∃ value, ScalarByteDocumentMeaning bytes value := by
  rcases (unsupported_outcome_exact bytes raw).mp outcome with ⟨grammar,unsupported⟩
  rintro ⟨value,actual,actualSyntax,meaning⟩
  have same := CandidateJsonCompleteness.byte_document_meaning_unique bytes actual raw actualSyntax grammar
  subst actual
  exact unsupported ⟨value,meaning⟩

#print axioms scalar_byte_document_sound
#print axioms scalar_byte_document_complete
#print axioms scalar_byte_document_exact
#print axioms scalar_byte_meaning_unique
#print axioms scalar_byte_none_exact
#print axioms invalid_outcome_exact
#print axioms unsupported_outcome_exact
#print axioms converted_outcome_exact
#print axioms unsupported_is_valid_raw_document
#print axioms unsupported_has_no_scalar_document
end RelationalSuccessor.CandidateScalarConversion
