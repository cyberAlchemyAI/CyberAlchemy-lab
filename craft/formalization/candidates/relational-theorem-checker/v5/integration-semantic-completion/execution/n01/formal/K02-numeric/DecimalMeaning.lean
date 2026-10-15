import ClosedJsonObject

set_option autoImplicit false
namespace RelationalSuccessor.CandidateDecimal
abbrev Ast := RelationalSuccessor.CandidateJsonSource.Value

inductive ExpSign where
  | unsigned | plus | minus
  deriving DecidableEq, Repr
structure Exponent where
  upper : Bool
  sign : ExpSign
  digits : List Nat
  deriving DecidableEq, Repr
structure Parts where
  negative : Bool
  integer : List Nat
  fraction : Option (List Nat)
  exponent : Option Exponent
  deriving DecidableEq, Repr

def digitChar : Nat → Char
  | 0 => '0' | 1 => '1' | 2 => '2' | 3 => '3' | 4 => '4'
  | 5 => '5' | 6 => '6' | 7 => '7' | 8 => '8' | 9 => '9'
  | _ => '?'
def digitChars (digits : List Nat) : List Char := digits.map digitChar

def DigitValid (digits : List Nat) : Prop := digits ≠ [] ∧ ∀ d ∈ digits, d < 10
instance (digits : List Nat) : Decidable (DigitValid digits) := inferInstanceAs (Decidable (digits ≠ [] ∧ ∀ d ∈ digits, d < 10))
def IntegerValid (digits : List Nat) : Prop :=
  DigitValid digits ∧ (digits.head? = some 0 → digits = [0])
instance (digits : List Nat) : Decidable (IntegerValid digits) := inferInstanceAs (Decidable (DigitValid digits ∧ (digits.head? = some 0 → digits = [0])))
def FractionValid : Option (List Nat) → Prop
  | none => True
  | some digits => DigitValid digits
instance (fraction : Option (List Nat)) : Decidable (FractionValid fraction) := by
  cases fraction <;> unfold FractionValid <;> infer_instance

def ExponentValid : Option Exponent → Prop
  | none => True
  | some exponent => DigitValid exponent.digits
instance (exponent : Option Exponent) : Decidable (ExponentValid exponent) := by
  cases exponent <;> unfold ExponentValid <;> infer_instance

structure Valid (parts : Parts) : Prop where
  integer : IntegerValid parts.integer
  fraction : FractionValid parts.fraction
  exponent : ExponentValid parts.exponent

def validCheck (parts : Parts) : Bool :=
  decide (IntegerValid parts.integer) && decide (FractionValid parts.fraction) && decide (ExponentValid parts.exponent)

theorem valid_check_exact (parts : Parts) : validCheck parts = true ↔ Valid parts := by
  simp only [validCheck,Bool.and_eq_true,decide_eq_true_eq]
  constructor
  · rintro ⟨⟨i,f⟩,e⟩; exact ⟨i,f,e⟩
  · intro h; exact ⟨⟨h.integer,h.fraction⟩,h.exponent⟩

def digitsValue (digits : List Nat) : Nat := digits.foldl (fun value digit => value * 10 + digit) 0

def fractionDigits (parts : Parts) : List Nat := parts.fraction.getD []
def fractionLength (parts : Parts) : Nat := (fractionDigits parts).length

def mantissa (parts : Parts) : Nat :=
  digitsValue parts.integer * 10 ^ fractionLength parts + digitsValue (fractionDigits parts)

def positiveExponent (parts : Parts) : Nat :=
  match parts.exponent with
  | none => 0
  | some exponent => if exponent.sign = .minus then 0 else digitsValue exponent.digits

def negativeExponent (parts : Parts) : Nat :=
  match parts.exponent with
  | none => 0
  | some exponent => if exponent.sign = .minus then digitsValue exponent.digits else 0

def numerator (parts : Parts) : Nat := mantissa parts * 10 ^ positiveExponent parts
def denominator (parts : Parts) : Nat := 10 ^ (fractionLength parts + negativeExponent parts)

def NonnegativeSign (parts : Parts) : Prop := parts.negative = false ∨ numerator parts = 0
instance (parts : Parts) : Decidable (NonnegativeSign parts) := inferInstanceAs (Decidable (parts.negative = false ∨ numerator parts = 0))

-- Independent exact rational-value assertion. In particular, it does not call
-- division, remainder or an executable success check.
structure EpochMeaning (parts : Parts) (epoch : Nat) : Prop where
  valid : Valid parts
  sign : NonnegativeSign parts
  value : numerator parts = epoch * denominator parts

theorem denominator_positive (parts : Parts) : 0 < denominator parts := Nat.pow_pos (by decide : 0 < 10)


theorem numerator_zero_iff (parts : Parts) : numerator parts = 0 ↔ mantissa parts = 0 := by
  simp [numerator,Nat.mul_eq_zero]

theorem epoch_value_unique (parts : Parts) (a b : Nat) (ha : EpochMeaning parts a) (hb : EpochMeaning parts b) : a = b :=
  Nat.mul_right_cancel (denominator_positive parts) (ha.value.symm.trans hb.value)

def signPrefix (parts : Parts) : List Char := if parts.negative then ['-'] else []
def fractionWord (parts : Parts) : List Char :=
  match parts.fraction with
  | none => []
  | some digits => '.' :: digitChars digits

def exponentSign : ExpSign → List Char
  | .unsigned => [] | .plus => ['+'] | .minus => ['-']
def exponentWord (parts : Parts) : List Char :=
  match parts.exponent with
  | none => []
  | some exponent => (if exponent.upper then 'E' else 'e') :: (exponentSign exponent.sign ++ digitChars exponent.digits)

def spellingChars (parts : Parts) : List Char :=
  signPrefix parts ++ digitChars parts.integer ++ fractionWord parts ++ exponentWord parts
def spelling (parts : Parts) : String := String.ofList (spellingChars parts)

#print axioms valid_check_exact
#print axioms denominator_positive
#print axioms numerator_zero_iff
#print axioms epoch_value_unique
end RelationalSuccessor.CandidateDecimal
