import RecursiveCompleteness
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonCompleteness
open CandidateJsonBytes CandidateJsonTokens CandidateJsonParser CandidateJsonSoundness

theorem wrapper_budget_sufficient (word remaining : List Nat) :
    2*word.length < RecursionBudget (word++remaining) := by
  simp only [RecursionBudget,List.length_append]; omega

theorem bounded_value_complete (input : List Nat) (value : RawValue) (remaining : List Nat)
    (meaning : BoundedValuePrefixMeaning input value remaining) : parseValue input = some (value,remaining) := by
  rcases meaning with ⟨word,same,grammar,boundary⟩
  rw [same]
  exact grammar_value_complete word value grammar remaining (RecursionBudget (word++remaining))
    (wrapper_budget_sufficient word remaining) boundary

theorem wrapped_value_exact (input : List Nat) (value : RawValue) (remaining : List Nat) :
    parseValue input = some (value,remaining) ↔ BoundedValuePrefixMeaning input value remaining :=
  ⟨wrapped_value_sound input value remaining,bounded_value_complete input value remaining⟩

theorem whitespace_follows_value (space : List Nat) (ws : WhiteSpace space) : FollowsValue space := by
  cases space with
  | nil => exact Or.inl rfl
  | cons first rest => exact Or.inr ⟨first,rest,rfl,Or.inl (ws first (by simp))⟩

theorem document_parser_complete (input : List Nat) (value : RawValue)
    (meaning : DocumentMeaning input value) : parseDocument input = some value := by
  rcases meaning with ⟨left,word,right,wl,head,wr,same⟩
  have leading := scan_white_before_value left word right value wl head
  have parsed := bounded_value_complete (word++right) value right ⟨word,rfl,head,whitespace_follows_value right wr⟩
  have trailing := scan_white_prefix right [] wr (Or.inl rfl)
  simp only [List.append_nil] at trailing
  rw [same]
  unfold parseDocument
  rw [leading,parsed]
  simp only [Option.bind_some]
  rw [trailing]; rfl

theorem document_parser_exact (input : List Nat) (value : RawValue) :
    parseDocument input = some value ↔ DocumentMeaning input value :=
  ⟨document_parser_sound input value,document_parser_complete input value⟩

theorem byte_document_parser_complete (bytes : Bytes) (value : RawValue)
    (meaning : ByteDocumentMeaning bytes value) : parseDocumentBytes bytes = some value := by
  rcases meaning with ⟨input,utf8,grammar⟩
  apply (byte_parser_composition bytes value).mpr
  exact ⟨input,utf8,document_parser_complete input value grammar⟩

theorem byte_document_parser_exact (bytes : Bytes) (value : RawValue) :
    parseDocumentBytes bytes = some value ↔ ByteDocumentMeaning bytes value :=
  ⟨byte_document_parser_sound bytes value,byte_document_parser_complete bytes value⟩

theorem bounded_value_meaning_unique (input : List Nat) (value1 value2 : RawValue) (rest1 rest2 : List Nat)
    (first : BoundedValuePrefixMeaning input value1 rest1) (second : BoundedValuePrefixMeaning input value2 rest2) :
    value1 = value2 ∧ rest1 = rest2 := by
  have same := Option.some.inj ((bounded_value_complete input value1 rest1 first).symm.trans
    (bounded_value_complete input value2 rest2 second))
  exact ⟨congrArg Prod.fst same,congrArg Prod.snd same⟩

theorem document_meaning_unique (input : List Nat) (value1 value2 : RawValue)
    (first : DocumentMeaning input value1) (second : DocumentMeaning input value2) : value1 = value2 :=
  Option.some.inj ((document_parser_complete input value1 first).symm.trans (document_parser_complete input value2 second))

theorem byte_document_meaning_unique (bytes : Bytes) (value1 value2 : RawValue)
    (first : ByteDocumentMeaning bytes value1) (second : ByteDocumentMeaning bytes value2) : value1 = value2 :=
  Option.some.inj ((byte_document_parser_complete bytes value1 first).symm.trans (byte_document_parser_complete bytes value2 second))

theorem document_none_iff_no_meaning (input : List Nat) :
    parseDocument input = none ↔ ¬ ∃ value, DocumentMeaning input value := by
  constructor
  · intro refused
    rintro ⟨value,meaning⟩
    have accepted := document_parser_complete input value meaning
    rw [refused] at accepted; contradiction
  · exact invalid_document_refused input

theorem byte_document_none_iff_no_meaning (bytes : Bytes) :
    parseDocumentBytes bytes = none ↔ ¬ ∃ value, ByteDocumentMeaning bytes value := by
  constructor
  · intro refused
    rintro ⟨value,meaning⟩
    have accepted := byte_document_parser_complete bytes value meaning
    rw [refused] at accepted; contradiction
  · exact invalid_byte_document_refused bytes

#print axioms wrapper_budget_sufficient
#print axioms bounded_value_complete
#print axioms wrapped_value_exact
#print axioms whitespace_follows_value
#print axioms document_parser_complete
#print axioms document_parser_exact
#print axioms byte_document_parser_complete
#print axioms byte_document_parser_exact
#print axioms bounded_value_meaning_unique
#print axioms document_meaning_unique
#print axioms byte_document_meaning_unique
#print axioms document_none_iff_no_meaning
#print axioms byte_document_none_iff_no_meaning
end RelationalSuccessor.CandidateJsonCompleteness
