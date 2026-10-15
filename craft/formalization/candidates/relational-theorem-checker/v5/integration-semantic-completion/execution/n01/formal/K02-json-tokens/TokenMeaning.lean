import JsonDocumentMeaning
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonTokens
open CandidateJsonBytes CandidateDecimal CandidateNumberParser

-- Independent maximal-run and token meanings precede their executable scanners.
def Stops (predicate : Nat → Prop) (rest : List Nat) : Prop :=
  rest = [] ∨ ∃ first tail, rest = first::tail ∧ ¬ predicate first

def RunMeaning (predicate : Nat → Prop) (input word remaining : List Nat) : Prop :=
  input = word ++ remaining ∧ (∀ code ∈ word, predicate code) ∧ Stops predicate remaining

def WhiteCode (code : Nat) : Prop := code = 32 ∨ code = 9 ∨ code = 10 ∨ code = 13
instance (code : Nat) : Decidable (WhiteCode code) := inferInstanceAs (Decidable (code = 32 ∨ code = 9 ∨ code = 10 ∨ code = 13))

def NumberCode (code : Nat) : Prop := code ∈ [48,49,50,51,52,53,54,55,56,57,43,45,46,69,101]
instance (code : Nat) : Decidable (NumberCode code) := inferInstanceAs (Decidable (code ∈ [48,49,50,51,52,53,54,55,56,57,43,45,46,69,101]))

def ValueBoundaryCode (code : Nat) : Prop := WhiteCode code ∨ code = 44 ∨ code = 93 ∨ code = 125

def FollowsValue (remaining : List Nat) : Prop :=
  remaining = [] ∨ ∃ first tail, remaining = first::tail ∧ ValueBoundaryCode first

def BoundedValuePrefixMeaning (input : List Nat) (value : RawValue) (remaining : List Nat) : Prop :=
  ∃ word, input = word ++ remaining ∧ ValueMeaning word value ∧ FollowsValue remaining

def NumberPrefixMeaning (input : List Nat) (token : String) (remaining : List Nat) : Prop :=
  NumberGrammar token.toList ∧ input = token.toList.map Char.toNat ++ remaining ∧ Stops NumberCode remaining

inductive LiteralMeaning : List Nat → RawValue → Prop
  | null : LiteralMeaning [110,117,108,108] .null
  | false : LiteralMeaning [102,97,108,115,101] (.boolean false)
  | true : LiteralMeaning [116,114,117,101] (.boolean true)

def LiteralPrefixMeaning (input : List Nat) (value : RawValue) (remaining : List Nat) : Prop :=
  ∃ word, input = word ++ remaining ∧ LiteralMeaning word value

theorem whitespace_run_equivalence (input word remaining : List Nat) :
    RunMeaning WhiteCode input word remaining ↔ input = word ++ remaining ∧ WhiteSpace word ∧ Stops WhiteCode remaining := by
  rfl

theorem number_code_roundtrip (code : Nat) (allowed : NumberCode code) : (Char.ofNat code).toNat = code := by
  simp [NumberCode] at allowed
  rcases allowed with h|h|h|h|h|h|h|h|h|h|h|h|h|h|h <;> subst code <;> decide

theorem numeric_word_roundtrip (word : List Nat) (allowed : ∀ code ∈ word, NumberCode code) :
    (word.map Char.ofNat).map Char.toNat = word := by
  induction word with
  | nil => rfl
  | cons first rest ih =>
    have head := number_code_roundtrip first (allowed first (by simp))
    have tail := ih (by intro code owned; exact allowed code (by simp [owned]))
    simp only [List.map_cons,head,tail]

theorem scalar_word_roundtrip (chars : List Char) :
    (chars.map Char.toNat).map Char.ofNat = chars := by
  induction chars with
  | nil => rfl
  | cons first rest ih => simp only [List.map_cons,Char.ofNat_toNat,ih]

theorem digit_number_code (c : Char) (digit : IsDigit c) : NumberCode c.toNat := by
  simp [IsDigit] at digit
  rcases digit with h|h|h|h|h|h|h|h|h|h <;> subst c <;> decide

theorem nonzero_digit_number_code (c : Char) (digit : IsNonzeroDigit c) : NumberCode c.toNat := by
  simp [IsNonzeroDigit] at digit
  rcases digit with h|h|h|h|h|h|h|h|h <;> subst c <;> decide

theorem grammar_number_codes (chars : List Char) (grammar : NumberGrammar chars) :
    ∀ code ∈ chars.map Char.toNat, NumberCode code := by
  rcases grammar with ⟨sign,integer,fraction,exponent,signValid,integerValid,fractionValid,exponentValid,same⟩
  have signCodes : ∀ c ∈ sign, NumberCode c.toNat := by
    rcases signValid with empty | negative <;> subst sign <;> simp [NumberCode]
  have integerCodes : ∀ c ∈ integer, NumberCode c.toNat := by
    rcases integerValid with zero | ⟨first,rest,word,head,tail⟩
    · subst integer; simp [NumberCode]
    · rw [word]; intro c member
      rcases List.mem_cons.mp member with eq | owned
      · subst c; exact nonzero_digit_number_code first head
      · exact digit_number_code c (tail c owned)
  have fractionCodes : ∀ c ∈ fraction, NumberCode c.toNat := by
    rcases fractionValid with empty | ⟨digits,word,digitWord⟩
    · subst fraction; simp
    · rw [word]; intro c member
      rcases List.mem_cons.mp member with eq | owned
      · subst c; decide
      · exact digit_number_code c (digitWord.2 c owned)
  have exponentCodes : ∀ c ∈ exponent, NumberCode c.toNat := by
    rcases exponentValid with empty | ⟨marker,expSign,digits,markerValid,expSignValid,digitWord,word⟩
    · subst exponent; simp
    · have markerCode : NumberCode marker.toNat := by
        simp at markerValid
        rcases markerValid with eq|eq <;> subst marker <;> decide
      have expSignCodes : ∀ c ∈ expSign, NumberCode c.toNat := by
        simp at expSignValid
        rcases expSignValid with eq|eq|eq <;> subst expSign <;> simp [NumberCode]
      rw [word]; intro c member
      rcases List.mem_cons.mp member with eq | owned
      · subst c; exact markerCode
      · rcases List.mem_append.mp owned with owned|owned
        · exact expSignCodes c owned
        · exact digit_number_code c (digitWord.2 c owned)
  intro code owned
  rcases List.mem_map.mp owned with ⟨c,member,encoded⟩
  rw [←encoded]
  rw [same] at member
  simp only [List.mem_append] at member
  rcases member with ((hs|hi)|hf)|he
  · exact signCodes c hs
  · exact integerCodes c hi
  · exact fractionCodes c hf
  · exact exponentCodes c he

theorem grammar_word_nonempty (chars : List Char) (grammar : NumberGrammar chars) : chars ≠ [] := by
  rcases grammar with ⟨sign,integer,fraction,exponent,_,integerValid,_,_,same⟩
  have positive : 0 < integer.length := by
    rcases integerValid with zero | ⟨first,rest,word,_,_⟩ <;> simp [*]
  intro empty
  have lengths := congrArg List.length same
  simp only [empty,List.length_nil,List.length_append] at lengths
  omega

theorem literal_value_meaning (word : List Nat) (value : RawValue) (meaning : LiteralMeaning word value) :
    ValueMeaning word value := by
  cases meaning <;> constructor

theorem value_boundary_stops_number (remaining : List Nat) (boundary : FollowsValue remaining) :
    Stops NumberCode remaining := by
  rcases boundary with empty | ⟨first,tail,same,allowed⟩
  · exact Or.inl empty
  · refine Or.inr ⟨first,tail,same,?_⟩
    rcases allowed with white | comma | closeArray | closeObject
    · rcases white with space|tab|newline|carriage <;> subst first <;> decide
    · subst first; decide
    · subst first; decide
    · subst first; decide

#print axioms whitespace_run_equivalence
#print axioms number_code_roundtrip
#print axioms numeric_word_roundtrip
#print axioms scalar_word_roundtrip
#print axioms digit_number_code
#print axioms nonzero_digit_number_code
#print axioms grammar_number_codes
#print axioms grammar_word_nonempty
#print axioms literal_value_meaning
#print axioms value_boundary_stops_number
end RelationalSuccessor.CandidateJsonTokens
