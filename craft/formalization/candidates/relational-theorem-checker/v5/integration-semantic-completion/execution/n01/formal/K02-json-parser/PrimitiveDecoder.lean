import ParserMeaning
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonParser
open CandidateJsonBytes CandidateJsonTokens CandidateJsonStrings
instance (code : Nat) : Decidable (ValueBoundaryCode code) :=
  inferInstanceAs (Decidable (WhiteCode code ∨ code = 44 ∨ code = 93 ∨ code = 125))

def boundaryCheck : List Nat → Bool
  | [] => true
  | first::_ => decide (ValueBoundaryCode first)

theorem boundary_check_exact (remaining : List Nat) : boundaryCheck remaining = true ↔ FollowsValue remaining := by
  cases remaining with
  | nil => simp [boundaryCheck,FollowsValue]
  | cons first tail => simp [boundaryCheck,FollowsValue]

def qualify (parsed : Option (RawValue × List Nat)) : Option (RawValue × List Nat) :=
  parsed.bind fun pair => if boundaryCheck pair.2 = true then some pair else none

theorem qualify_exact (parsed : Option (RawValue × List Nat)) (value : RawValue) (remaining : List Nat) :
    qualify parsed = some (value,remaining) ↔ parsed = some (value,remaining) ∧ FollowsValue remaining := by
  constructor
  · intro decoded
    rcases Option.bind_eq_some_iff.mp decoded with ⟨pair,prepared,result⟩
    split at result
    · rename_i checked
      have same := Option.some.inj result
      rw [same] at prepared checked
      exact ⟨prepared,(boundary_check_exact remaining).mp checked⟩
    · contradiction
  · rintro ⟨prepared,boundary⟩
    simp [qualify,prepared,(boundary_check_exact remaining).mpr boundary]

def rawPrimitive (input : List Nat) : Option (RawValue × List Nat) :=
  match input with
  | [] => none
  | first::_ =>
    if first = 34 then (decodeQuoted input).bind fun pair => some (.string pair.1,pair.2)
    else if first = 110 ∨ first = 102 ∨ first = 116 then decodeLiteral input
    else (decodeNumber input).bind fun pair => some (.number pair.1,pair.2)

def decodePrimitive (input : List Nat) : Option (RawValue × List Nat) := qualify (rawPrimitive input)

theorem raw_primitive_sound (input : List Nat) (value : RawValue) (remaining : List Nat)
    (decoded : rawPrimitive input = some (value,remaining)) :
    ∃ word, input = word ++ remaining ∧ PrimitiveMeaning word value := by
  cases input with
  | nil => simp [rawPrimitive] at decoded
  | cons first tail =>
    simp only [rawPrimitive] at decoded
    split at decoded
    · rcases Option.bind_eq_some_iff.mp decoded with ⟨pair,quoted,result⟩
      have same := Option.some.inj result
      have val : RawValue.string pair.1 = value := congrArg Prod.fst same
      have rem : pair.2 = remaining := congrArg Prod.snd same
      rcases (decode_quoted_exact (first::tail) pair.1 pair.2).mp quoted with ⟨word,inputEq,meaning⟩
      exact ⟨word,by simpa only [rem] using inputEq,by rw [←val]; exact .string word pair.1 meaning⟩
    · split at decoded
      · rcases decode_literal_sound (first::tail) value remaining decoded with ⟨word,inputEq,meaning⟩
        exact ⟨word,inputEq,.literal word value meaning⟩
      · rcases Option.bind_eq_some_iff.mp decoded with ⟨pair,number,result⟩
        have same := Option.some.inj result
        have val : RawValue.number pair.1 = value := congrArg Prod.fst same
        have rem : pair.2 = remaining := congrArg Prod.snd same
        have meaning := decode_number_sound (first::tail) pair.1 pair.2 number
        exact ⟨pair.1.toList.map Char.toNat,by simpa only [rem] using meaning.2.1,by
          rw [←val]; exact .number pair.1 meaning.1⟩

theorem raw_primitive_word_complete (word : List Nat) (value : RawValue) (remaining : List Nat)
    (meaning : PrimitiveMeaning word value) (boundary : FollowsValue remaining) :
    rawPrimitive (word ++ remaining) = some (value,remaining) := by
  cases meaning with
  | literal word value meaning => cases meaning <;> simp [rawPrimitive,decodeLiteral,takeWord]
  | string word units meaning =>
    have decoded := (decode_quoted_exact (word ++ remaining) units remaining).mpr ⟨word,rfl,meaning⟩
    rcases meaning with ⟨content,wordEq,_⟩
    rw [wordEq] at decoded ⊢
    simp only [List.cons_append,List.nil_append,List.append_assoc] at decoded ⊢
    simp only [rawPrimitive]
    rw [decoded]; rfl
  | number token grammar =>
    have decoded := decode_number_at_value_boundary token remaining grammar boundary
    have nonempty := grammar_word_nonempty token.toList grammar
    have codes := grammar_number_codes token.toList grammar
    cases chars : token.toList with
    | nil => exact False.elim (nonempty chars)
    | cons first rest =>
      have allowed : NumberCode first.toNat := codes first.toNat (by simp [chars])
      have noDispatch := number_code_not_dispatch first.toNat allowed
      have noLiteral : ¬ (first.toNat = 110 ∨ first.toNat = 102 ∨ first.toNat = 116) := by
        intro literal; rcases literal with hn|hf|ht
        · exact noDispatch.2.1 hn
        · exact noDispatch.2.2.1 hf
        · exact noDispatch.2.2.2 ht
      simp only [chars,List.map_cons,List.cons_append,rawPrimitive,if_neg noDispatch.1,if_neg noLiteral] at decoded ⊢
      rw [decoded]; rfl

theorem decode_primitive_exact (input : List Nat) (value : RawValue) (remaining : List Nat) :
    decodePrimitive input = some (value,remaining) ↔ PrimitivePrefixMeaning input value remaining := by
  constructor
  · intro decoded
    rcases (qualify_exact (rawPrimitive input) value remaining).mp decoded with ⟨raw,boundary⟩
    rcases raw_primitive_sound input value remaining raw with ⟨word,inputEq,meaning⟩
    exact ⟨word,inputEq,meaning,boundary⟩
  · rintro ⟨word,inputEq,meaning,boundary⟩
    apply (qualify_exact (rawPrimitive input) value remaining).mpr
    rw [inputEq]
    exact ⟨raw_primitive_word_complete word value remaining meaning boundary,boundary⟩

theorem primitive_prefix_unique (input : List Nat) (value1 value2 : RawValue) (rest1 rest2 : List Nat)
    (first : PrimitivePrefixMeaning input value1 rest1) (second : PrimitivePrefixMeaning input value2 rest2) :
    value1 = value2 ∧ rest1 = rest2 := by
  have same := Option.some.inj (((decode_primitive_exact input value1 rest1).mpr first).symm.trans
    ((decode_primitive_exact input value2 rest2).mpr second))
  exact ⟨congrArg Prod.fst same,congrArg Prod.snd same⟩

theorem decoded_primitive_progress (input : List Nat) (value : RawValue) (remaining : List Nat)
    (decoded : decodePrimitive input = some (value,remaining)) : remaining.length < input.length := by
  rcases (decode_primitive_exact input value remaining).mp decoded with ⟨word,same,meaning,_⟩
  have nonempty := primitive_word_nonempty word value meaning
  have positive : 0 < word.length := by cases word <;> simp_all
  rw [same]
  simp only [List.length_append]; omega

#print axioms boundary_check_exact
#print axioms qualify_exact
#print axioms raw_primitive_sound
#print axioms raw_primitive_word_complete
#print axioms decode_primitive_exact
#print axioms primitive_prefix_unique
#print axioms decoded_primitive_progress
end RelationalSuccessor.CandidateJsonParser
