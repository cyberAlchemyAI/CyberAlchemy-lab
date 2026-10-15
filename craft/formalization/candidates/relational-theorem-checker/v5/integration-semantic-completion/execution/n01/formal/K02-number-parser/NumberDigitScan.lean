import DecimalGrammar
set_option autoImplicit false
namespace RelationalSuccessor.CandidateNumberParser
open RelationalSuccessor.CandidateDecimal

def decodeDigit : Char → Option Nat
  | '0' => some 0 | '1' => some 1 | '2' => some 2 | '3' => some 3 | '4' => some 4
  | '5' => some 5 | '6' => some 6 | '7' => some 7 | '8' => some 8 | '9' => some 9
  | _ => none

theorem decode_encoded_digit (digit : Nat) (valid : digit < 10) : decodeDigit (digitChar digit) = some digit := by
  have options : digit = 0 ∨ digit = 1 ∨ digit = 2 ∨ digit = 3 ∨ digit = 4 ∨
      digit = 5 ∨ digit = 6 ∨ digit = 7 ∨ digit = 8 ∨ digit = 9 := by omega
  rcases options with h | h | h | h | h | h | h | h | h | h <;> subst digit <;> rfl

theorem encoded_digit_not_minus (digit : Nat) (valid : digit < 10) : digitChar digit ≠ '-' := by
  intro same
  have exact := decode_encoded_digit digit valid
  rw [same] at exact
  cases exact

theorem encoded_digit_not_exponent_sign (digit : Nat) (valid : digit < 10) :
    digitChar digit ≠ '+' ∧ digitChar digit ≠ '-' := by
  constructor
  · intro same
    have exact := decode_encoded_digit digit valid
    rw [same] at exact
    cases exact
  · exact encoded_digit_not_minus digit valid

def scanDigits : List Char → List Nat × List Char
  | [] => ([],[])
  | c :: rest =>
    match decodeDigit c with
    | none => ([],c :: rest)
    | some digit => let found := scanDigits rest; (digit :: found.1,found.2)

def Stop (chars : List Char) : Prop :=
  chars = [] ∨ ∃ c rest, chars = c :: rest ∧ decodeDigit c = none

theorem scan_stopped (chars : List Char) (stop : Stop chars) : scanDigits chars = ([],chars) := by
  rcases stop with empty | ⟨c,rest,same,notDigit⟩
  · subst chars; rfl
  · rw [same]; simp [scanDigits,notDigit]

theorem scan_encoded_digits (digits : List Nat) (valid : ∀ d ∈ digits, d < 10)
    (rest : List Char) (stop : Stop rest) : scanDigits (digitChars digits ++ rest) = (digits,rest) := by
  induction digits with
  | nil => simpa [digitChars] using scan_stopped rest stop
  | cons first remaining ih =>
    have head := decode_encoded_digit first (valid first (by simp))
    have tail := ih (by intro d owned; exact valid d (by simp [owned]))
    change scanDigits (remaining.map digitChar ++ rest) = (remaining,rest) at tail
    simp [digitChars,scanDigits,head,tail]

theorem exponent_suffix_stops (parts : Parts) : Stop (exponentWord parts) := by
  cases found : parts.exponent with
  | none => exact Or.inl (by simp [exponentWord,found])
  | some exponent =>
    refine Or.inr ⟨(if exponent.upper then 'E' else 'e'),exponentSign exponent.sign ++ digitChars exponent.digits,
      by simp [exponentWord,found],?_⟩
    cases exponent.upper <;> rfl

theorem fraction_exponent_suffix_stops (parts : Parts) : Stop (fractionWord parts ++ exponentWord parts) := by
  cases found : parts.fraction with
  | none => simpa [fractionWord,found] using exponent_suffix_stops parts
  | some digits =>
    exact Or.inr ⟨'.',digitChars digits ++ exponentWord parts,by simp [fractionWord,found],rfl⟩

#print axioms decode_encoded_digit
#print axioms encoded_digit_not_minus
#print axioms encoded_digit_not_exponent_sign
#print axioms scan_stopped
#print axioms scan_encoded_digits
#print axioms exponent_suffix_stops
#print axioms fraction_exponent_suffix_stops
end RelationalSuccessor.CandidateNumberParser
