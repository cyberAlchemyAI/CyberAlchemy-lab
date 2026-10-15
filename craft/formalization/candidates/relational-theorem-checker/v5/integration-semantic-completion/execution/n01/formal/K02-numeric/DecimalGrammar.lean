import DecimalEpochCheck

set_option autoImplicit false
namespace RelationalSuccessor.CandidateDecimal

-- JSON number lexical grammar, stated independently over ASCII characters.
def IsDigit (c : Char) : Prop := c ∈ ['0','1','2','3','4','5','6','7','8','9']
def IsNonzeroDigit (c : Char) : Prop := c ∈ ['1','2','3','4','5','6','7','8','9']
def DigitWord (chars : List Char) : Prop := chars ≠ [] ∧ ∀ c ∈ chars, IsDigit c
def IntegerWord (chars : List Char) : Prop :=
  chars = ['0'] ∨ ∃ first rest, chars = first :: rest ∧ IsNonzeroDigit first ∧ ∀ c ∈ rest, IsDigit c
def FractionWord (chars : List Char) : Prop :=
  chars = [] ∨ ∃ digits, chars = '.' :: digits ∧ DigitWord digits
def ExponentWord (chars : List Char) : Prop :=
  chars = [] ∨ ∃ marker sign digits,
    marker ∈ ['e','E'] ∧ sign ∈ [[],['+'],['-']] ∧ DigitWord digits ∧ chars = marker :: (sign ++ digits)
def NumberGrammar (chars : List Char) : Prop :=
  ∃ sign integer fraction exponent,
    (sign = [] ∨ sign = ['-']) ∧ IntegerWord integer ∧ FractionWord fraction ∧
    ExponentWord exponent ∧ chars = sign ++ integer ++ fraction ++ exponent

theorem digit_char_valid (digit : Nat) (valid : digit < 10) : IsDigit (digitChar digit) := by
  have options : digit = 0 ∨ digit = 1 ∨ digit = 2 ∨ digit = 3 ∨ digit = 4 ∨
      digit = 5 ∨ digit = 6 ∨ digit = 7 ∨ digit = 8 ∨ digit = 9 := by omega
  rcases options with h | h | h | h | h | h | h | h | h | h <;> subst digit <;> simp [IsDigit,digitChar]

theorem digit_char_nonzero (digit : Nat) (positive : 0 < digit) (valid : digit < 10) :
    IsNonzeroDigit (digitChar digit) := by
  have options : digit = 1 ∨ digit = 2 ∨ digit = 3 ∨ digit = 4 ∨ digit = 5 ∨
      digit = 6 ∨ digit = 7 ∨ digit = 8 ∨ digit = 9 := by omega
  rcases options with h | h | h | h | h | h | h | h | h <;> subst digit <;> simp [IsNonzeroDigit,digitChar]

theorem mapped_digits_are_word (digits : List Nat) (valid : DigitValid digits) : DigitWord (digitChars digits) := by
  constructor
  · cases digits with
    | nil => exact False.elim (valid.1 rfl)
    | cons first rest => simp [digitChars]
  · intro c member
    rcases List.mem_map.mp member with ⟨digit,owned,same⟩
    rw [← same]
    exact digit_char_valid digit (valid.2 digit owned)

theorem valid_integer_has_grammar (digits : List Nat) (valid : IntegerValid digits) : IntegerWord (digitChars digits) := by
  cases digits with
  | nil => exact False.elim (valid.1.1 rfl)
  | cons first rest =>
    by_cases zero : first = 0
    · have singleton := valid.2 (by simp [zero])
      exact Or.inl (by rw [singleton]; rfl)
    · apply Or.inr
      refine ⟨digitChar first,digitChars rest,rfl,?_,?_⟩
      · exact digit_char_nonzero first (by omega) (valid.1.2 first (by simp))
      · intro c member
        rcases List.mem_map.mp member with ⟨digit,owned,same⟩
        rw [← same]
        exact digit_char_valid digit (valid.1.2 digit (by simp [owned]))

theorem valid_fraction_has_grammar (parts : Parts) (valid : FractionValid parts.fraction) : FractionWord (fractionWord parts) := by
  cases found : parts.fraction with
  | none => exact Or.inl (by simp [fractionWord,found])
  | some digits =>
    refine Or.inr ⟨digitChars digits,by simp [fractionWord,found],?_⟩
    exact mapped_digits_are_word digits (by simpa [found,FractionValid] using valid)

theorem valid_exponent_has_grammar (parts : Parts) (valid : ExponentValid parts.exponent) : ExponentWord (exponentWord parts) := by
  cases found : parts.exponent with
  | none => exact Or.inl (by simp [exponentWord,found])
  | some exponent =>
    refine Or.inr ⟨(if exponent.upper then 'E' else 'e'),exponentSign exponent.sign,digitChars exponent.digits,?_,?_,?_,?_⟩
    · cases exponent.upper <;> decide
    · cases exponent.sign <;> decide
    · exact mapped_digits_are_word exponent.digits (by simpa [found,ExponentValid] using valid)
    · simp [exponentWord,found]

theorem valid_parts_have_JSON_grammar (parts : Parts) (valid : Valid parts) : NumberGrammar (spellingChars parts) := by
  refine ⟨signPrefix parts,digitChars parts.integer,fractionWord parts,exponentWord parts,?_,
    valid_integer_has_grammar parts.integer valid.integer,
    valid_fraction_has_grammar parts valid.fraction,
    valid_exponent_has_grammar parts valid.exponent,rfl⟩
  cases found : parts.negative <;> simp [signPrefix,found]

theorem successful_witness_has_JSON_number (token : String) (parts : Parts) (epoch : Nat)
    (accepted : decodeWitness (.number token) parts = some epoch) : NumberGrammar token.toList := by
  have meaning := (decode_witness_exact (.number token) parts epoch).mp accepted
  have same : token = spelling parts := by cases meaning.spelling; rfl
  rw [same,spelling,String.toList_ofList]
  exact valid_parts_have_JSON_grammar parts meaning.value.valid


theorem invalid_number_grammar_refuses_every_witness (token : String)
    (invalid : ¬ NumberGrammar token.toList) (parts : Parts) : decodeWitness (.number token) parts = none := by
  cases found : decodeWitness (.number token) parts with
  | none => rfl
  | some epoch => exact False.elim (invalid (successful_witness_has_JSON_number token parts epoch found))

#print axioms digit_char_valid
#print axioms digit_char_nonzero
#print axioms mapped_digits_are_word
#print axioms valid_integer_has_grammar
#print axioms valid_fraction_has_grammar
#print axioms valid_exponent_has_grammar
#print axioms valid_parts_have_JSON_grammar
#print axioms successful_witness_has_JSON_number
#print axioms invalid_number_grammar_refuses_every_witness
end RelationalSuccessor.CandidateDecimal
