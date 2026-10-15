import JsonDocumentMeaning
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonStrings
open CandidateJsonBytes

def decodeHex (code : Nat) : Option Nat :=
  if 48 ≤ code ∧ code ≤ 57 then some (code-48)
  else if 97 ≤ code ∧ code ≤ 102 then some (10+code-97)
  else if 65 ≤ code ∧ code ≤ 70 then some (10+code-65)
  else none

theorem decode_hex_sound (code value : Nat) (decoded : decodeHex code = some value) :
    HexMeaning code value := by
  unfold decodeHex at decoded
  split at decoded
  · have same := Option.some.inj decoded
    have bound : code-48 < 10 := by omega
    have meaning := HexMeaning.digit (code-48) bound
    have encoded : 48+(code-48) = code := by omega
    rw [encoded] at meaning
    simpa only [same] using meaning
  · split at decoded
    · have same := Option.some.inj decoded
      have bound : code-97 < 6 := by omega
      have meaning := HexMeaning.lower (code-97) bound
      have encoded : 97+(code-97) = code := by omega
      have valueEq : 10+(code-97) = value := by omega
      simpa only [encoded,valueEq] using meaning
    · split at decoded
      · have same := Option.some.inj decoded
        have bound : code-65 < 6 := by omega
        have meaning := HexMeaning.upper (code-65) bound
        have encoded : 65+(code-65) = code := by omega
        have valueEq : 10+(code-65) = value := by omega
        simpa only [encoded,valueEq] using meaning
      · contradiction

theorem decode_hex_complete (code value : Nat) (meaning : HexMeaning code value) :
    decodeHex code = some value := by
  cases meaning with
  | digit value bound =>
    have guard : 48 ≤ 48+value ∧ 48+value ≤ 57 := by omega
    simp [decodeHex,guard]
  | lower value bound =>
    have first : ¬(48 ≤ 97+value ∧ 97+value ≤ 57) := by omega
    have guard : 97 ≤ 97+value ∧ 97+value ≤ 102 := by omega
    simp only [decodeHex,if_neg first,if_pos guard,Option.some.injEq]; omega
  | upper value bound =>
    have first : ¬(48 ≤ 65+value ∧ 65+value ≤ 57) := by omega
    have second : ¬(97 ≤ 65+value ∧ 65+value ≤ 102) := by omega
    have guard : 65 ≤ 65+value ∧ 65+value ≤ 70 := by omega
    simp only [decodeHex,if_neg first,if_neg second,if_pos guard,Option.some.injEq]; omega

theorem decode_hex_exact (code value : Nat) :
    decodeHex code = some value ↔ HexMeaning code value :=
  ⟨decode_hex_sound code value,decode_hex_complete code value⟩

def decodeSimple (code : Nat) : Option Nat :=
  if code = 34 then some 34 else if code = 92 then some 92
  else if code = 47 then some 47 else if code = 98 then some 8
  else if code = 102 then some 12 else if code = 110 then some 10
  else if code = 114 then some 13 else if code = 116 then some 9 else none

theorem decode_simple_sound (code value : Nat) (decoded : decodeSimple code = some value) :
    SimpleEscape code value := by
  unfold decodeSimple at decoded
  repeat' first | split at decoded | subst code
  all_goals first | contradiction | (have same := Option.some.inj decoded; subst value; constructor)

theorem decode_simple_complete (code value : Nat) (meaning : SimpleEscape code value) :
    decodeSimple code = some value := by
  cases meaning <;> rfl

theorem decode_simple_exact (code value : Nat) :
    decodeSimple code = some value ↔ SimpleEscape code value :=
  ⟨decode_simple_sound code value,decode_simple_complete code value⟩

theorem simple_not_u (code value : Nat) (meaning : SimpleEscape code value) : code ≠ 117 := by
  cases meaning <;> decide

def decodeFour (a b c d : Nat) : Option Nat :=
  (decodeHex a).bind fun va => (decodeHex b).bind fun vb =>
    (decodeHex c).bind fun vc => (decodeHex d).bind fun vd =>
      some (va*4096+vb*256+vc*16+vd)

def FourMeaning (a b c d value : Nat) : Prop :=
  ∃ va vb vc vd, HexMeaning a va ∧ HexMeaning b vb ∧ HexMeaning c vc ∧ HexMeaning d vd ∧
    value = va*4096+vb*256+vc*16+vd

theorem decode_four_exact (a b c d value : Nat) :
    decodeFour a b c d = some value ↔ FourMeaning a b c d value := by
  simp only [decodeFour,Option.bind_eq_some_iff,Option.some.injEq,decode_hex_exact,FourMeaning]
  constructor
  · rintro ⟨va,ha,vb,hb,vc,hc,vd,hd,same⟩
    exact ⟨va,vb,vc,vd,ha,hb,hc,hd,same.symm⟩
  · rintro ⟨va,vb,vc,vd,ha,hb,hc,hd,same⟩
    exact ⟨va,ha,vb,hb,vc,hc,vd,hd,same.symm⟩

#print axioms decode_hex_sound
#print axioms decode_hex_complete
#print axioms decode_hex_exact
#print axioms decode_simple_sound
#print axioms decode_simple_complete
#print axioms decode_simple_exact
#print axioms simple_not_u
#print axioms decode_four_exact
end RelationalSuccessor.CandidateJsonStrings
