import JsonDocumentMeaning
import ClosedJsonObject
set_option autoImplicit false
namespace RelationalSuccessor.CandidateScalarConversion
open CandidateJsonBytes

def BmpUnit (unit : Nat) : Prop := unit < 65536 ∧ (unit < 55296 ∨ 57344 ≤ unit)
def HighUnit (unit : Nat) : Prop := 55296 ≤ unit ∧ unit < 56320
def LowUnit (unit : Nat) : Prop := 56320 ≤ unit ∧ unit < 57344
instance (unit : Nat) : Decidable (BmpUnit unit) :=
  inferInstanceAs (Decidable (unit < 65536 ∧ (unit < 55296 ∨ 57344 ≤ unit)))
instance (unit : Nat) : Decidable (HighUnit unit) :=
  inferInstanceAs (Decidable (55296 ≤ unit ∧ unit < 56320))
instance (unit : Nat) : Decidable (LowUnit unit) :=
  inferInstanceAs (Decidable (56320 ≤ unit ∧ unit < 57344))

def pairScalar (high low : Nat) : Nat := 65536 + (high-55296)*1024 + (low-56320)

inductive UnitCharsMeaning : List Nat → List Char → Prop
  | nil : UnitCharsMeaning [] []
  | bmp (char : Char) (units : List Nat) (chars : List Char)
      (bound : char.toNat < 65536) (tail : UnitCharsMeaning units chars) :
      UnitCharsMeaning (char.toNat::units) (char::chars)
  | pair (high low : Nat) (char : Char) (units : List Nat) (chars : List Char)
      (highBound : HighUnit high) (lowBound : LowUnit low)
      (scalar : char.toNat = pairScalar high low) (tail : UnitCharsMeaning units chars) :
      UnitCharsMeaning (high::low::units) (char::chars)

def StringMeaning (units : List Nat) (text : String) : Prop := UnitCharsMeaning units text.toList

theorem char_scalar (char : Char) : Scalar char.toNat := by
  have valid := char.valid
  change char.toNat < 55296 ∨ 57343 < char.toNat ∧ char.toNat < 1114112 at valid
  unfold Scalar; omega

theorem bmp_char_unit (char : Char) (bound : char.toNat < 65536) : BmpUnit char.toNat := by
  have scalar := char_scalar char
  unfold Scalar at scalar
  unfold BmpUnit; omega

theorem bmp_is_scalar (unit : Nat) (bmp : BmpUnit unit) : Scalar unit := by
  unfold BmpUnit at bmp; unfold Scalar; omega

theorem high_not_bmp (unit : Nat) (high : HighUnit unit) : ¬ BmpUnit unit := by
  unfold HighUnit at high; unfold BmpUnit; omega

theorem low_not_bmp (unit : Nat) (low : LowUnit unit) : ¬ BmpUnit unit := by
  unfold LowUnit at low; unfold BmpUnit; omega

theorem pair_scalar_bounds (high low : Nat) (hb : HighUnit high) (lb : LowUnit low) :
    65536 ≤ pairScalar high low ∧ pairScalar high low < 1114112 := by
  unfold HighUnit at hb; unfold LowUnit at lb; unfold pairScalar; omega

theorem pair_is_scalar (high low : Nat) (hb : HighUnit high) (lb : LowUnit low) :
    Scalar (pairScalar high low) := by
  have bounds := pair_scalar_bounds high low hb lb
  unfold Scalar; omega

theorem of_nat_scalar_exact (value : Nat) (scalar : Scalar value) : (Char.ofNat value).toNat = value := by
  have valid : value.isValidChar := by unfold Scalar at scalar; unfold Nat.isValidChar; omega
  simp only [Char.ofNat,dif_pos valid,Char.ofNatAux,Char.toNat]
  rfl

theorem unit_meaning_bounded (units : List Nat) (chars : List Char) (meaning : UnitCharsMeaning units chars) :
    ∀ unit ∈ units, unit < 65536 := by
  induction meaning with
  | nil => intro unit member; simp at member
  | bmp char units chars bound tail ih =>
      intro unit member
      rcases List.mem_cons.mp member with same | inside
      · subst unit; exact bound
      · exact ih unit inside
  | pair high low char units chars hb lb scalar tail ih =>
      intro unit member
      rcases List.mem_cons.mp member with same | inside
      · subst unit; unfold HighUnit at hb; omega
      · rcases List.mem_cons.mp inside with same | inside
        · subst unit; unfold LowUnit at lb; omega
        · exact ih unit inside

theorem unit_meaning_empty (units : List Nat) (meaning : UnitCharsMeaning units []) : units = [] := by
  cases meaning; rfl

#print axioms char_scalar
#print axioms bmp_char_unit
#print axioms bmp_is_scalar
#print axioms high_not_bmp
#print axioms low_not_bmp
#print axioms pair_scalar_bounds
#print axioms pair_is_scalar
#print axioms of_nat_scalar_exact
#print axioms unit_meaning_bounded
#print axioms unit_meaning_empty
end RelationalSuccessor.CandidateScalarConversion
