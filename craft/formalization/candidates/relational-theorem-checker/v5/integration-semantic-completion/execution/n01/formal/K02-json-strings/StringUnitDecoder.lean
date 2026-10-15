import StringEscapes
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonStrings
open CandidateJsonBytes

def decodeUnit (input : List Nat) : Option (List Nat × List Nat) :=
  match input with
  | [] => none
  | code::tail =>
    if code = 92 then
      match tail with
      | [] => none
      | encoded::rest =>
        if encoded = 117 then
          match rest with
          | a::b::c::d::remaining =>
            (decodeFour a b c d).bind fun value => some ([value],remaining)
          | _ => none
        else (decodeSimple encoded).bind fun value => some ([value],rest)
    else if Scalar code ∧ 32 ≤ code ∧ code ≠ 34 then some (scalarUnits code,tail)
    else none

def UnitPrefixMeaning (input units remaining : List Nat) : Prop :=
  ∃ word, input = word ++ remaining ∧ StringUnitMeaning word units

theorem decode_unit_sound (input units remaining : List Nat)
    (decoded : decodeUnit input = some (units,remaining)) : UnitPrefixMeaning input units remaining := by
  cases input with
  | nil => simp [decodeUnit] at decoded
  | cons code tail =>
    simp only [decodeUnit] at decoded
    split at decoded
    · subst code
      cases tail with
      | nil => simp at decoded
      | cons encoded rest =>
        dsimp only at decoded
        split at decoded
        · subst encoded
          cases rest with
          | nil => simp at decoded
          | cons a afterA =>
            cases afterA with
            | nil => simp at decoded
            | cons b afterB =>
              cases afterB with
              | nil => simp at decoded
              | cons c afterC =>
                cases afterC with
                | nil => simp at decoded
                | cons d suffix =>
                  dsimp only at decoded
                  rcases Option.bind_eq_some_iff.mp decoded with ⟨value,four,pair⟩
                  have same := Option.some.inj pair
                  have sameUnits : [value] = units := congrArg Prod.fst same
                  have sameRest : suffix = remaining := congrArg Prod.snd same
                  rcases (decode_four_exact a b c d value).mp four with ⟨va,vb,vc,vd,ha,hb,hc,hd,equal⟩
                  subst value
                  exact ⟨[92,117,a,b,c,d],by simp [sameRest],by
                    rw [←sameUnits]; exact StringUnitMeaning.hexadecimal a b c d va vb vc vd ha hb hc hd⟩
        · rcases Option.bind_eq_some_iff.mp decoded with ⟨value,simple,pair⟩
          have same := Option.some.inj pair
          have sameUnits : [value] = units := congrArg Prod.fst same
          have sameRest : rest = remaining := congrArg Prod.snd same
          exact ⟨[92,encoded],by simp [sameRest],by
            rw [←sameUnits]; exact StringUnitMeaning.simple encoded value (decode_simple_sound encoded value simple)⟩
    · split at decoded
      · rename_i notSlash allowed
        have same := Option.some.inj decoded
        have sameUnits : scalarUnits code = units := congrArg Prod.fst same
        have sameRest : tail = remaining := congrArg Prod.snd same
        exact ⟨[code],by simp [sameRest],by
          rw [←sameUnits]; exact StringUnitMeaning.raw code allowed.1 allowed.2.1 allowed.2.2 notSlash⟩
      · contradiction

theorem decode_unit_word_complete (word units remaining : List Nat)
    (meaning : StringUnitMeaning word units) : decodeUnit (word ++ remaining) = some (units,remaining) := by
  cases meaning with
  | raw code scalar printable notQuote notSlash =>
    simp only [List.cons_append,List.nil_append,decodeUnit,if_neg notSlash]
    simp [scalar,printable,notQuote]
  | simple encoded value escape =>
    have notU := simple_not_u encoded value escape
    have decoded := decode_simple_complete encoded value escape
    simp [decodeUnit,notU,decoded]
  | hexadecimal a b c d va vb vc vd ha hb hc hd =>
    have four := (decode_four_exact a b c d (va*4096+vb*256+vc*16+vd)).mpr
      ⟨va,vb,vc,vd,ha,hb,hc,hd,rfl⟩
    simp [decodeUnit,four]

theorem decode_unit_exact (input units remaining : List Nat) :
    decodeUnit input = some (units,remaining) ↔ UnitPrefixMeaning input units remaining := by
  constructor
  · exact decode_unit_sound input units remaining
  · rintro ⟨word,same,meaning⟩
    rw [same]; exact decode_unit_word_complete word units remaining meaning

theorem unit_word_nonempty (word units : List Nat) (meaning : StringUnitMeaning word units) :
    word ≠ [] := by
  cases meaning <;> simp

theorem unit_word_no_quote (word units : List Nat) (meaning : StringUnitMeaning word units) :
    ∀ suffix, word ≠ 34::suffix := by
  cases meaning with
  | raw code scalar printable nq ns => intro suffix equal; cases equal; exact nq rfl
  | simple encoded decoded escape => intro suffix equal; cases equal
  | hexadecimal a b c d va vb vc vd ha hb hc hd => intro suffix equal; cases equal

theorem decoded_unit_progress (input units remaining : List Nat)
    (decoded : decodeUnit input = some (units,remaining)) : remaining.length < input.length := by
  rcases decode_unit_sound input units remaining decoded with ⟨word,same,meaning⟩
  have nonempty := unit_word_nonempty word units meaning
  have positive : 0 < word.length := by cases word <;> simp_all
  simp only [same,List.length_append]; omega

theorem decoded_units_bounded (input units remaining : List Nat)
    (decoded : decodeUnit input = some (units,remaining)) : ∀ unit ∈ units, unit < 65536 := by
  rcases decode_unit_sound input units remaining decoded with ⟨word,_,meaning⟩
  exact string_units_bounded word units meaning

#print axioms decode_unit_sound
#print axioms decode_unit_word_complete
#print axioms decode_unit_exact
#print axioms unit_word_nonempty
#print axioms unit_word_no_quote
#print axioms decoded_unit_progress
#print axioms decoded_units_bounded
end RelationalSuccessor.CandidateJsonStrings
