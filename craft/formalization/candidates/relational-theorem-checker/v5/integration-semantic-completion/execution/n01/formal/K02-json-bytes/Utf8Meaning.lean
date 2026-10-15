set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonBytes

abbrev Bytes := List UInt8

def TailByte (byte : UInt8) : Prop := 128 ≤ byte.toNat ∧ byte.toNat ≤ 191
def TwoFirst (byte : UInt8) : Prop := 194 ≤ byte.toNat ∧ byte.toNat ≤ 223
def ThreeFirst (a b : UInt8) : Prop := 224 ≤ a.toNat ∧ a.toNat ≤ 239 ∧
  (a.toNat = 224 → 160 ≤ b.toNat) ∧ (a.toNat = 237 → b.toNat ≤ 159)
def FourFirst (a b : UInt8) : Prop := 240 ≤ a.toNat ∧ a.toNat ≤ 244 ∧
  (a.toNat = 240 → 144 ≤ b.toNat) ∧ (a.toNat = 244 → b.toNat ≤ 143)

instance (a : UInt8) : Decidable (TailByte a) := by unfold TailByte; infer_instance
instance (a : UInt8) : Decidable (TwoFirst a) := by unfold TwoFirst; infer_instance
instance (a b : UInt8) : Decidable (ThreeFirst a b) := by unfold ThreeFirst; infer_instance
instance (a b : UInt8) : Decidable (FourFirst a b) := by unfold FourFirst; infer_instance

def value2 (a b : UInt8) : Nat := (a.toNat - 192)*64 + (b.toNat - 128)
def value3 (a b c : UInt8) : Nat := (a.toNat - 224)*4096 + (b.toNat - 128)*64 + (c.toNat - 128)
def value4 (a b c d : UInt8) : Nat := (a.toNat - 240)*262144 + (b.toNat - 128)*4096 + (c.toNat - 128)*64 + (d.toNat - 128)

-- Independent shortest-form UTF-8 syntax and numeric scalar denotation.
inductive WordMeaning : Bytes → Nat → Prop
  | one (a : UInt8) (ascii : a.toNat < 128) : WordMeaning [a] a.toNat
  | two (a b : UInt8) (first : TwoFirst a) (tail : TailByte b) : WordMeaning [a,b] (value2 a b)
  | three (a b c : UInt8) (first : ThreeFirst a b) (tailB : TailByte b) (tailC : TailByte c) : WordMeaning [a,b,c] (value3 a b c)
  | four (a b c d : UInt8) (first : FourFirst a b) (tailB : TailByte b) (tailC : TailByte c) (tailD : TailByte d) : WordMeaning [a,b,c,d] (value4 a b c d)

def Scalar (value : Nat) : Prop := value < 1114112 ∧ (value < 55296 ∨ 57344 ≤ value)

instance (value : Nat) : Decidable (Scalar value) := by unfold Scalar; infer_instance

theorem word_nonempty (bytes : Bytes) (value : Nat) (meaning : WordMeaning bytes value) : bytes ≠ [] := by
  cases meaning <;> simp

theorem word_length_bounds (bytes : Bytes) (value : Nat) (meaning : WordMeaning bytes value) :
    1 ≤ bytes.length ∧ bytes.length ≤ 4 := by
  cases meaning <;> simp

theorem word_denotes_scalar (bytes : Bytes) (value : Nat) (meaning : WordMeaning bytes value) : Scalar value := by
  cases meaning with
  | one a ascii => unfold Scalar; omega
  | two a b first tail => unfold Scalar value2 TwoFirst TailByte at *; omega
  | three a b c first tb tc =>
    unfold Scalar value3 ThreeFirst TailByte at *
    by_cases before : a.toNat < 237
    · omega
    · by_cases after : 237 < a.toNat
      · omega
      · omega
  | four a b c d first tb tc td => unfold Scalar value4 FourFirst TailByte at *; omega

inductive StreamMeaning : Bytes → List Nat → Prop
  | nil : StreamMeaning [] []
  | cons (word rest : Bytes) (value : Nat) (values : List Nat)
      (head : WordMeaning word value) (tail : StreamMeaning rest values) :
      StreamMeaning (word ++ rest) (value::values)

theorem stream_scalar_values (bytes : Bytes) (values : List Nat) (meaning : StreamMeaning bytes values) :
    ∀ value ∈ values, Scalar value := by
  induction meaning with
  | nil => intro value member; simp at member
  | cons word rest value values head tail ih =>
    intro v member; simp only [List.mem_cons] at member
    rcases member with same | rest
    · subst v; exact word_denotes_scalar word value head
    · exact ih v rest

#print axioms word_nonempty
#print axioms word_length_bounds
#print axioms word_denotes_scalar
#print axioms stream_scalar_values
end RelationalSuccessor.CandidateJsonBytes
