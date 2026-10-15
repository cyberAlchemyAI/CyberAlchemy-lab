import NumberTokenParser
set_option autoImplicit false
namespace RelationalSuccessor.CandidateNumberParser
open RelationalSuccessor.CandidateDecimal

theorem char_digit_representation (c : Char) (valid : IsDigit c) : ∃ digit, digit < 10 ∧ digitChar digit = c := by
  simp [IsDigit] at valid
  rcases valid with h | h | h | h | h | h | h | h | h | h
  · subst c; exact ⟨0,by decide,rfl⟩
  · subst c; exact ⟨1,by decide,rfl⟩
  · subst c; exact ⟨2,by decide,rfl⟩
  · subst c; exact ⟨3,by decide,rfl⟩
  · subst c; exact ⟨4,by decide,rfl⟩
  · subst c; exact ⟨5,by decide,rfl⟩
  · subst c; exact ⟨6,by decide,rfl⟩
  · subst c; exact ⟨7,by decide,rfl⟩
  · subst c; exact ⟨8,by decide,rfl⟩
  · subst c; exact ⟨9,by decide,rfl⟩

theorem nonzero_char_representation (c : Char) (valid : IsNonzeroDigit c) :
    ∃ digit, 0 < digit ∧ digit < 10 ∧ digitChar digit = c := by
  simp [IsNonzeroDigit] at valid
  rcases valid with h | h | h | h | h | h | h | h | h
  · subst c; exact ⟨1,by decide,by decide,rfl⟩
  · subst c; exact ⟨2,by decide,by decide,rfl⟩
  · subst c; exact ⟨3,by decide,by decide,rfl⟩
  · subst c; exact ⟨4,by decide,by decide,rfl⟩
  · subst c; exact ⟨5,by decide,by decide,rfl⟩
  · subst c; exact ⟨6,by decide,by decide,rfl⟩
  · subst c; exact ⟨7,by decide,by decide,rfl⟩
  · subst c; exact ⟨8,by decide,by decide,rfl⟩
  · subst c; exact ⟨9,by decide,by decide,rfl⟩

theorem digits_represent_chars (chars : List Char) (valid : ∀ c ∈ chars, IsDigit c) :
    ∃ digits, (∀ d ∈ digits, d < 10) ∧ digitChars digits = chars := by
  induction chars with
  | nil => exact ⟨[],by simp,rfl⟩
  | cons first rest ih =>
    rcases char_digit_representation first (valid first (by simp)) with ⟨digit,bound,same⟩
    rcases ih (by intro c owned; exact valid c (by simp [owned])) with ⟨digits,bounds,encoded⟩
    refine ⟨digit :: digits,?_,?_⟩
    · intro d owned
      rcases List.mem_cons.mp owned with head | tail
      · subst d; exact bound
      · exact bounds d tail
    · simp only [digitChars,List.map_cons]
      change digitChar digit :: digitChars digits = first :: rest
      rw [same,encoded]

theorem digit_word_representation (chars : List Char) (valid : DigitWord chars) :
    ∃ digits, DigitValid digits ∧ digitChars digits = chars := by
  rcases digits_represent_chars chars valid.2 with ⟨digits,bounds,same⟩
  refine ⟨digits,⟨?_,bounds⟩,same⟩
  intro empty
  rw [empty] at same
  exact valid.1 same.symm

theorem integer_word_representation (chars : List Char) (valid : IntegerWord chars) :
    ∃ digits, IntegerValid digits ∧ digitChars digits = chars := by
  rcases valid with zero | ⟨first,rest,same,nonzero,tail⟩
  · exact ⟨[0],by decide,by rw [zero]; rfl⟩
  · rcases nonzero_char_representation first nonzero with ⟨digit,positive,bound,head⟩
    rcases digits_represent_chars rest tail with ⟨digits,bounds,encoded⟩
    refine ⟨digit :: digits,⟨⟨by simp,?_⟩,?_⟩,?_⟩
    · intro d owned
      rcases List.mem_cons.mp owned with h | h
      · subst d; exact bound
      · exact bounds d h
    · intro startsZero
      have isZero : digit = 0 := Option.some.inj startsZero
      omega
    · simp only [digitChars,List.map_cons]
      change digitChar digit :: digitChars digits = chars
      rw [head,encoded,same]

def fractionLetters : Option (List Nat) → List Char
  | none => []
  | some digits => '.' :: digitChars digits

def exponentLetters : Option Exponent → List Char
  | none => []
  | some exponent => (if exponent.upper then 'E' else 'e') :: (exponentSign exponent.sign ++ digitChars exponent.digits)

theorem fraction_word_representation (chars : List Char) (valid : FractionWord chars) :
    ∃ fraction, FractionValid fraction ∧ fractionLetters fraction = chars := by
  rcases valid with empty | ⟨word,same,digits⟩
  · exact ⟨none,True.intro,by rw [empty]; rfl⟩
  · rcases digit_word_representation word digits with ⟨values,valid,encoded⟩
    exact ⟨some values,valid,by simp [fractionLetters,encoded,same]⟩

theorem exponent_word_representation (chars : List Char) (valid : ExponentWord chars) :
    ∃ exponent, ExponentValid exponent ∧ exponentLetters exponent = chars := by
  rcases valid with empty | ⟨marker,sign,word,markerValid,signValid,digits,same⟩
  · exact ⟨none,True.intro,by rw [empty]; rfl⟩
  · rcases digit_word_representation word digits with ⟨values,valid,encoded⟩
    simp at markerValid signValid
    rcases markerValid with low | high
    · subst marker
      rcases signValid with unsigned | plus | minus
      · subst sign
        refine ⟨some ⟨false,.unsigned,values⟩,valid,?_⟩
        simpa [exponentLetters,exponentSign,encoded] using same.symm
      · subst sign
        refine ⟨some ⟨false,.plus,values⟩,valid,?_⟩
        simpa [exponentLetters,exponentSign,encoded] using same.symm
      · subst sign
        refine ⟨some ⟨false,.minus,values⟩,valid,?_⟩
        simpa [exponentLetters,exponentSign,encoded] using same.symm
    · subst marker
      rcases signValid with unsigned | plus | minus
      · subst sign
        refine ⟨some ⟨true,.unsigned,values⟩,valid,?_⟩
        simpa [exponentLetters,exponentSign,encoded] using same.symm
      · subst sign
        refine ⟨some ⟨true,.plus,values⟩,valid,?_⟩
        simpa [exponentLetters,exponentSign,encoded] using same.symm
      · subst sign
        refine ⟨some ⟨true,.minus,values⟩,valid,?_⟩
        simpa [exponentLetters,exponentSign,encoded] using same.symm

theorem grammar_has_representation (chars : List Char) (grammar : NumberGrammar chars) : ∃ parts, Representation chars parts := by
  rcases grammar with ⟨sign,integer,fraction,exponent,signValid,integerValid,fractionValid,exponentValid,whole⟩
  rcases integer_word_representation integer integerValid with ⟨digits,iv,ie⟩
  rcases fraction_word_representation fraction fractionValid with ⟨frac,fv,fe⟩
  rcases exponent_word_representation exponent exponentValid with ⟨exp,ev,ee⟩
  rcases signValid with positive | negative
  · subst sign
    refine ⟨⟨false,digits,frac,exp⟩,⟨⟨iv,fv,ev⟩,?_⟩⟩
    change [] ++ digitChars digits ++ fractionLetters frac ++ exponentLetters exp = chars
    rw [ie,fe,ee]; exact whole.symm
  · subst sign
    refine ⟨⟨true,digits,frac,exp⟩,⟨⟨iv,fv,ev⟩,?_⟩⟩
    change ['-'] ++ digitChars digits ++ fractionLetters frac ++ exponentLetters exp = chars
    rw [ie,fe,ee]; exact whole.symm

theorem parser_covers_exact_JSON_grammar (chars : List Char) : (∃ parts, parseChars chars = some parts) ↔ NumberGrammar chars := by
  constructor
  · rintro ⟨parts,accepted⟩
    have meaning := parse_chars_sound chars parts accepted
    rw [← meaning.2]
    exact valid_parts_have_JSON_grammar parts meaning.1
  · intro grammar
    rcases grammar_has_representation chars grammar with ⟨parts,meaning⟩
    exact ⟨parts,parse_chars_complete chars parts meaning⟩

#print axioms char_digit_representation
#print axioms nonzero_char_representation
#print axioms digits_represent_chars
#print axioms digit_word_representation
#print axioms integer_word_representation
#print axioms fraction_word_representation
#print axioms exponent_word_representation
#print axioms grammar_has_representation
#print axioms parser_covers_exact_JSON_grammar
end RelationalSuccessor.CandidateNumberParser
