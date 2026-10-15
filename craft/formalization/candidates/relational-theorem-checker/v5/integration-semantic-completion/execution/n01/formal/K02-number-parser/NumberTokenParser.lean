import NumberDigitScan
set_option autoImplicit false
namespace RelationalSuccessor.CandidateNumberParser
open RelationalSuccessor.CandidateDecimal

def parseSign : List Char → Bool × List Char
  | [] => (false,[])
  | c :: rest => if c = '-' then (true,rest) else (false,c :: rest)

def parseFraction : List Char → Option (List Nat) × List Char
  | [] => (none,[])
  | c :: rest => if c = '.' then
      let scanned := scanDigits rest; (some scanned.1,scanned.2)
    else (none,c :: rest)

def parseExpSign : List Char → ExpSign × List Char
  | [] => (.unsigned,[])
  | c :: rest => if c = '+' then (.plus,rest) else if c = '-' then (.minus,rest) else (.unsigned,c :: rest)

def parseExponent : List Char → Option Exponent
  | [] => none
  | marker :: rest => if marker = 'e' ∨ marker = 'E' then
      let signed := parseExpSign rest
      let scanned := scanDigits signed.2
      some ⟨decide (marker = 'E'),signed.1,scanned.1⟩
    else none

def candidate (chars : List Char) : Parts :=
  let signed := parseSign chars
  let integer := scanDigits signed.2
  let fraction := parseFraction integer.2
  ⟨signed.1,integer.1,fraction.1,parseExponent fraction.2⟩

-- Neither a partial scan nor the candidate constructor can alone qualify a
-- token. Validation and complete retained-character reconstruction are mandatory.
def parseChars (chars : List Char) : Option Parts :=
  let parts := candidate chars
  if validCheck parts && decide (spellingChars parts = chars) then some parts else none

def Representation (chars : List Char) (parts : Parts) : Prop := Valid parts ∧ spellingChars parts = chars

theorem sign_inverse (parts : Parts) (valid : Valid parts) :
    parseSign (spellingChars parts) = (parts.negative,digitChars parts.integer ++ fractionWord parts ++ exponentWord parts) := by
  cases negative : parts.negative with
  | true => simp [spellingChars,signPrefix,negative,parseSign]
  | false =>
    cases integer : parts.integer with
    | nil => exact False.elim (valid.integer.1.1 integer)
    | cons first rest =>
      have headValid : first < 10 := valid.integer.1.2 first (by simp [integer])
      simp [spellingChars,signPrefix,negative,integer,digitChars,parseSign,encoded_digit_not_minus first headValid]

theorem fraction_inverse (parts : Parts) (valid : Valid parts) :
    parseFraction (fractionWord parts ++ exponentWord parts) = (parts.fraction,exponentWord parts) := by
  cases fraction : parts.fraction with
  | none =>
    cases exponent : parts.exponent with
    | none => simp [fractionWord,exponentWord,fraction,exponent,parseFraction]
    | some e => cases upper : e.upper <;> simp [fractionWord,exponentWord,fraction,exponent,parseFraction,upper]
  | some digits =>
    have allDigits : ∀ d ∈ digits, d < 10 := (by simpa [FractionValid,fraction] using valid.fraction : DigitValid digits).2
    simp [fractionWord,fraction,parseFraction,scan_encoded_digits digits allDigits (exponentWord parts) (exponent_suffix_stops parts)]

theorem exponent_sign_inverse (sign : ExpSign) (digits : List Nat) (valid : DigitValid digits) :
    parseExpSign (exponentSign sign ++ digitChars digits) = (sign,digitChars digits) := by
  cases sign with
  | plus => simp [exponentSign,parseExpSign]
  | minus => simp [exponentSign,parseExpSign]
  | unsigned =>
    cases digits with
    | nil => exact False.elim (valid.1 rfl)
    | cons first rest =>
      have signs := encoded_digit_not_exponent_sign first (valid.2 first (by simp))
      simp [exponentSign,digitChars,parseExpSign,signs.1,signs.2]

theorem exponent_inverse (parts : Parts) (valid : Valid parts) : parseExponent (exponentWord parts) = parts.exponent := by
  cases exponent : parts.exponent with
  | none => simp [exponentWord,exponent,parseExponent]
  | some e =>
    have digits : DigitValid e.digits := by simpa [exponent,ExponentValid] using valid.exponent
    have signed := exponent_sign_inverse e.sign e.digits digits
    have scanned := scan_encoded_digits e.digits digits.2 [] (Or.inl rfl)
    simp only [List.append_nil] at scanned
    cases e.upper <;> simp [exponentWord,exponent,parseExponent,signed,scanned]

theorem candidate_spelling_inverse (parts : Parts) (valid : Valid parts) : candidate (spellingChars parts) = parts := by
  have signed := sign_inverse parts valid
  have integer := scan_encoded_digits parts.integer valid.integer.1.2
    (fractionWord parts ++ exponentWord parts) (fraction_exponent_suffix_stops parts)
  have fraction := fraction_inverse parts valid
  have exponent := exponent_inverse parts valid
  simp only [candidate,signed,List.append_assoc,integer,fraction,exponent] <;> rfl

theorem parse_chars_sound (chars : List Char) (parts : Parts) (accepted : parseChars chars = some parts) : Representation chars parts := by
  change (if validCheck (candidate chars) && decide (spellingChars (candidate chars) = chars) then some (candidate chars) else none) = some parts at accepted
  split at accepted
  · rename_i checked
    cases accepted
    have conditions : validCheck (candidate chars) = true ∧ decide (spellingChars (candidate chars) = chars) = true := by
      simpa only [Bool.and_eq_true] using checked
    exact ⟨(valid_check_exact _).mp conditions.1,of_decide_eq_true conditions.2⟩
  · cases accepted

theorem parse_chars_complete (chars : List Char) (parts : Parts) (meaning : Representation chars parts) : parseChars chars = some parts := by
  rw [← meaning.2]
  simp [parseChars,candidate_spelling_inverse parts meaning.1,(valid_check_exact parts).mpr meaning.1]

theorem parse_chars_exact (chars : List Char) (parts : Parts) : parseChars chars = some parts ↔ Representation chars parts :=
  ⟨parse_chars_sound chars parts,parse_chars_complete chars parts⟩

theorem token_representation_unique (chars : List Char) (a b : Parts)
    (ha : Representation chars a) (hb : Representation chars b) : a = b :=
  Option.some.inj ((parse_chars_complete chars a ha).symm.trans (parse_chars_complete chars b hb))

def parseToken (token : String) : Option Parts := parseChars token.toList

theorem parse_token_exact (token : String) (parts : Parts) :
    parseToken token = some parts ↔ Representation token.toList parts := parse_chars_exact token.toList parts

#print axioms sign_inverse
#print axioms fraction_inverse
#print axioms exponent_sign_inverse
#print axioms exponent_inverse
#print axioms candidate_spelling_inverse
#print axioms parse_chars_sound
#print axioms parse_chars_complete
#print axioms parse_chars_exact
#print axioms token_representation_unique
#print axioms parse_token_exact
end RelationalSuccessor.CandidateNumberParser
