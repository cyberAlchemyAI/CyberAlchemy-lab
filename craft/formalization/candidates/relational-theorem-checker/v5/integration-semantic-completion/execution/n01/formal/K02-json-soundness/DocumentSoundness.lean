import RecursiveSoundness
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonSoundness
open CandidateJsonBytes CandidateJsonTokens CandidateJsonParser

theorem wrapped_value_sound (input : List Nat) (value : RawValue) (remaining : List Nat)
    (decoded : parseValue input = some (value,remaining)) : BoundedValuePrefixMeaning input value remaining :=
  recursive_value_sound (RecursionBudget input) input value remaining decoded

theorem document_parser_sound (input : List Nat) (value : RawValue)
    (decoded : parseDocument input = some value) : DocumentMeaning input value := by
  unfold parseDocument at decoded
  rcases Option.bind_eq_some_iff.mp decoded with ⟨parsed,valueParsed,whole⟩
  split at whole
  · rename_i empty
    have val := Option.some.inj whole
    rcases wrapped_value_sound (scanWhitespace input).2 parsed.1 parsed.2 valueParsed with ⟨word,valueEq,head,_⟩
    let left := (scanWhitespace input).1
    let right := (scanWhitespace parsed.2).1
    have wl : WhiteSpace left := (whitespace_reconstruction input).2
    have wr : WhiteSpace right := (whitespace_reconstruction parsed.2).2
    have leftEq : input = left ++ (scanWhitespace input).2 := (whitespace_reconstruction input).1
    have rightEq : parsed.2 = right := by
      simpa only [empty,List.append_nil] using (whitespace_reconstruction parsed.2).1
    refine ⟨left,word,right,wl,?_,wr,?_⟩
    · simpa only [val] using head
    · rw [leftEq,valueEq,rightEq]
      simp only [List.append_assoc]
  · contradiction

theorem byte_document_parser_sound (bytes : Bytes) (value : RawValue)
    (decoded : parseDocumentBytes bytes = some value) : ByteDocumentMeaning bytes value := by
  rcases (byte_parser_composition bytes value).mp decoded with ⟨input,utf8,parsed⟩
  exact ⟨input,utf8,document_parser_sound input value parsed⟩

theorem invalid_document_refused (input : List Nat) (invalid : ¬ ∃ value, DocumentMeaning input value) :
    parseDocument input = none := by
  cases decoded : parseDocument input with
  | none => rfl
  | some value => exact False.elim (invalid ⟨value,document_parser_sound input value decoded⟩)

theorem invalid_byte_document_refused (bytes : Bytes) (invalid : ¬ ∃ value, ByteDocumentMeaning bytes value) :
    parseDocumentBytes bytes = none := by
  cases decoded : parseDocumentBytes bytes with
  | none => rfl
  | some value => exact False.elim (invalid ⟨value,byte_document_parser_sound bytes value decoded⟩)

theorem value_word_nonempty (word : List Nat) (value : RawValue) (meaning : ValueMeaning word value) : word ≠ [] := by
  cases meaning with
  | null => simp
  | false => simp
  | true => simp
  | number token grammar =>
    have nonempty := grammar_word_nonempty token.toList grammar
    cases chars : token.toList with
    | nil => exact False.elim (nonempty chars)
    | cons first rest => simp
  | string text units meaning => rcases meaning with ⟨content,same,_⟩; simp [same]
  | emptyArray space ws => simp
  | array left text right values wl items wr => simp
  | emptyObject space ws => simp
  | object left text right entries wl members wr => simp

theorem recursive_value_progress (fuel : Nat) (input : List Nat) (value : RawValue) (remaining : List Nat)
    (decoded : parseValueFuel fuel input = some (value,remaining)) : remaining.length < input.length := by
  rcases recursive_value_sound fuel input value remaining decoded with ⟨word,same,meaning,_⟩
  have nonempty := value_word_nonempty word value meaning
  have positive : 0 < word.length := by cases word <;> simp_all
  rw [same]
  simp only [List.length_append]; omega

theorem post_comma_array_nonempty (fuel : Nat) (input : List Nat) (values : List RawValue) (remaining : List Nat)
    (decoded : parseArrayFuel fuel input false = some (values,remaining)) : values ≠ [] :=
  (recursive_array_sound fuel input values remaining false decoded).2 rfl

theorem post_comma_object_nonempty (fuel : Nat) (input : List Nat) (entries : List (List Nat × RawValue)) (remaining : List Nat)
    (decoded : parseObjectFuel fuel input false = some (entries,remaining)) : entries ≠ [] :=
  (recursive_object_sound fuel input entries remaining false decoded).2 rfl

#print axioms wrapped_value_sound
#print axioms document_parser_sound
#print axioms byte_document_parser_sound
#print axioms invalid_document_refused
#print axioms invalid_byte_document_refused
#print axioms value_word_nonempty
#print axioms recursive_value_progress
#print axioms post_comma_array_nonempty
#print axioms post_comma_object_nonempty
end RelationalSuccessor.CandidateJsonSoundness
