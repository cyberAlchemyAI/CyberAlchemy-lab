import ScalarStringMeaning
set_option autoImplicit false
namespace RelationalSuccessor.CandidateScalarConversion

def decodeChars : List Nat → Option (List Char)
  | [] => some []
  | unit::tail =>
      if BmpUnit unit then (decodeChars tail).map (Char.ofNat unit :: ·)
      else if HighUnit unit then
        match tail with
        | [] => none
        | low::rest => if LowUnit low then
            (decodeChars rest).map (Char.ofNat (pairScalar unit low) :: ·)
          else none
      else none

theorem decode_chars_cons (unit : Nat) (tail : List Nat) :
    decodeChars (unit::tail) =
      if BmpUnit unit then (decodeChars tail).map (Char.ofNat unit :: ·)
      else if HighUnit unit then
        match tail with
        | [] => none
        | low::rest => if LowUnit low then
            (decodeChars rest).map (Char.ofNat (pairScalar unit low) :: ·)
          else none
      else none := by
  cases tail <;> rfl

def decodeString (units : List Nat) : Option String := (decodeChars units).map String.ofList

theorem decode_chars_sound (units : List Nat) (chars : List Char)
    (parsed : decodeChars units = some chars) : UnitCharsMeaning units chars := by
  cases units with
  | nil => simp only [decodeChars,Option.some.injEq] at parsed; subst chars; exact .nil
  | cons unit tail =>
      simp only [decode_chars_cons] at parsed
      split at parsed
      · rename_i bmp
        cases decoded : decodeChars tail with
        | none => simp [decoded] at parsed
        | some restChars =>
            simp only [decoded,Option.map_some,Option.some.injEq] at parsed
            subst chars
            have exactChar := of_nat_scalar_exact unit (bmp_is_scalar unit bmp)
            simpa only [exactChar] using (UnitCharsMeaning.bmp (Char.ofNat unit) tail restChars
              (by rw [exactChar]; exact bmp.1) (decode_chars_sound tail restChars decoded))
      · rename_i notBmp
        split at parsed
        · rename_i high
          cases tail with
          | nil => cases parsed
          | cons low rest =>
              change (if LowUnit low then (decodeChars rest).map (Char.ofNat (pairScalar unit low) :: ·) else none) = some chars at parsed
              split at parsed
              · rename_i lowBound
                cases decoded : decodeChars rest with
                | none => simp [decoded] at parsed
                | some restChars =>
                    simp only [decoded,Option.map_some,Option.some.injEq] at parsed
                    subst chars
                    exact .pair unit low (Char.ofNat (pairScalar unit low)) rest restChars high lowBound
                      (of_nat_scalar_exact _ (pair_is_scalar unit low high lowBound))
                      (decode_chars_sound rest restChars decoded)
              · cases parsed
        · cases parsed
termination_by units.length

theorem decode_chars_complete (units : List Nat) (chars : List Char)
    (meaning : UnitCharsMeaning units chars) : decodeChars units = some chars := by
  induction meaning with
  | nil => rfl
  | bmp char units chars bound tail ih =>
      simp only [decode_chars_cons,if_pos (bmp_char_unit char bound),ih,Option.map_some,Char.ofNat_toNat]
  | pair high low char units chars hb lb scalar tail ih =>
      simp only [decode_chars_cons,if_neg (high_not_bmp high hb),if_pos hb,if_pos lb,ih,Option.map_some]
      rw [← scalar,Char.ofNat_toNat]

theorem decode_chars_exact (units : List Nat) (chars : List Char) :
    decodeChars units = some chars ↔ UnitCharsMeaning units chars :=
  ⟨decode_chars_sound units chars,decode_chars_complete units chars⟩

theorem chars_meaning_unique (units : List Nat) (first second : List Char)
    (a : UnitCharsMeaning units first) (b : UnitCharsMeaning units second) : first = second :=
  Option.some.inj ((decode_chars_complete units first a).symm.trans (decode_chars_complete units second b))

theorem decode_chars_none_exact (units : List Nat) :
    decodeChars units = none ↔ ¬ ∃ chars, UnitCharsMeaning units chars := by
  constructor
  · intro refused; rintro ⟨chars,meaning⟩
    have accepted := decode_chars_complete units chars meaning
    rw [refused] at accepted; contradiction
  · intro invalid
    cases parsed : decodeChars units with
    | none => rfl
    | some chars => exact False.elim (invalid ⟨chars,decode_chars_sound units chars parsed⟩)

theorem decode_string_sound (units : List Nat) (text : String)
    (parsed : decodeString units = some text) : StringMeaning units text := by
  unfold decodeString at parsed
  cases decoded : decodeChars units with
  | none => simp [decoded] at parsed
  | some chars =>
      simp only [decoded,Option.map_some,Option.some.injEq] at parsed
      subst text
      unfold StringMeaning
      rw [String.toList_ofList]
      exact decode_chars_sound units chars decoded

theorem decode_string_complete (units : List Nat) (text : String)
    (meaning : StringMeaning units text) : decodeString units = some text := by
  have parsed := decode_chars_complete units text.toList meaning
  simp only [decodeString,parsed,Option.map_some,String.ofList_toList]

theorem decode_string_exact (units : List Nat) (text : String) :
    decodeString units = some text ↔ StringMeaning units text :=
  ⟨decode_string_sound units text,decode_string_complete units text⟩

theorem string_meaning_unique (units : List Nat) (first second : String)
    (a : StringMeaning units first) (b : StringMeaning units second) : first = second :=
  Option.some.inj ((decode_string_complete units first a).symm.trans (decode_string_complete units second b))

theorem decode_string_none_exact (units : List Nat) :
    decodeString units = none ↔ ¬ ∃ text, StringMeaning units text := by
  constructor
  · intro refused; rintro ⟨text,meaning⟩
    have accepted := decode_string_complete units text meaning
    rw [refused] at accepted; contradiction
  · intro invalid
    cases parsed : decodeString units with
    | none => rfl
    | some text => exact False.elim (invalid ⟨text,decode_string_sound units text parsed⟩)

theorem characters_do_not_expand (units : List Nat) (chars : List Char)
    (meaning : UnitCharsMeaning units chars) : chars.length ≤ units.length := by
  induction meaning with
  | nil => simp
  | bmp char units chars bound tail ih => simp only [List.length_cons]; omega
  | pair high low char units chars hb lb scalar tail ih => simp only [List.length_cons]; omega

theorem leading_low_refused (low : Nat) (tail : List Nat) (bound : LowUnit low) :
    decodeChars (low::tail) = none := by
  have notHigh : ¬ HighUnit low := by unfold LowUnit at bound; unfold HighUnit; omega
  simp only [decode_chars_cons,if_neg (low_not_bmp low bound),if_neg notHigh]

theorem lone_high_refused (high : Nat) (bound : HighUnit high) : decodeChars [high] = none := by
  simp only [decode_chars_cons,if_neg (high_not_bmp high bound),if_pos bound]

theorem above_unit_range_refused (unit : Nat) (tail : List Nat) (bound : 65536 ≤ unit) :
    decodeChars (unit::tail) = none := by
  have notBmp : ¬ BmpUnit unit := by unfold BmpUnit; omega
  have notHigh : ¬ HighUnit unit := by unfold HighUnit; omega
  simp only [decode_chars_cons,if_neg notBmp,if_neg notHigh]

#print axioms decode_chars_cons
#print axioms decode_chars_sound
#print axioms decode_chars_complete
#print axioms decode_chars_exact
#print axioms chars_meaning_unique
#print axioms decode_chars_none_exact
#print axioms decode_string_sound
#print axioms decode_string_complete
#print axioms decode_string_exact
#print axioms string_meaning_unique
#print axioms decode_string_none_exact
#print axioms characters_do_not_expand
#print axioms leading_low_refused
#print axioms lone_high_refused
#print axioms above_unit_range_refused
end RelationalSuccessor.CandidateScalarConversion
