import GrammarReconstruction
set_option autoImplicit false
set_option maxHeartbeats 2000000
namespace RelationalSuccessor.CandidateJsonSoundness
open CandidateJsonBytes CandidateJsonTokens CandidateJsonStrings CandidateJsonParser

def ValueSound (fuel : Nat) : Prop := ∀ input value remaining,
  parseValueFuel fuel input = some (value,remaining) → BoundedValuePrefixMeaning input value remaining

def ArraySound (fuel : Nat) : Prop := ∀ input values remaining allowEmpty,
  parseArrayFuel fuel input allowEmpty = some (values,remaining) →
    ArrayBodyMeaning input values remaining ∧ (allowEmpty = false → values ≠ [])

def ObjectSound (fuel : Nat) : Prop := ∀ input entries remaining allowEmpty,
  parseObjectFuel fuel input allowEmpty = some (entries,remaining) →
    ObjectBodyMeaning input entries remaining ∧ (allowEmpty = false → entries ≠ [])

theorem value_step_sound (fuel : Nat) (array : ArraySound fuel) (object : ObjectSound fuel) : ValueSound (fuel+1) := by
  intro input value remaining decoded
  cases input with
  | nil => simp [parseValueFuel] at decoded
  | cons first tail =>
    simp only [parseValueFuel] at decoded
    split at decoded
    · subst first
      rcases (qualify_exact _ value remaining).mp decoded with ⟨bodyDecode,boundary⟩
      rcases Option.bind_eq_some_iff.mp bodyDecode with ⟨body,parsed,pair⟩
      have same := Option.some.inj pair
      have val : RawValue.array body.1 = value := congrArg Prod.fst same
      have rem : body.2 = remaining := congrArg Prod.snd same
      have meaning := (array tail body.1 body.2 true parsed).1
      rcases array_body_value_bridge tail body.1 body.2 meaning with ⟨word,inputEq,wordMeaning⟩
      exact ⟨word,by simpa only [rem] using inputEq,by simpa only [val] using wordMeaning,boundary⟩
    · split at decoded
      · subst first
        rcases (qualify_exact _ value remaining).mp decoded with ⟨bodyDecode,boundary⟩
        rcases Option.bind_eq_some_iff.mp bodyDecode with ⟨body,parsed,pair⟩
        have same := Option.some.inj pair
        have val : RawValue.object body.1 = value := congrArg Prod.fst same
        have rem : body.2 = remaining := congrArg Prod.snd same
        have meaning := (object tail body.1 body.2 true parsed).1
        rcases object_body_value_bridge tail body.1 body.2 meaning with ⟨word,inputEq,wordMeaning⟩
        exact ⟨word,by simpa only [rem] using inputEq,by simpa only [val] using wordMeaning,boundary⟩
      · exact primitive_prefix_value_bridge (first::tail) value remaining
          ((decode_primitive_exact (first::tail) value remaining).mp decoded)

theorem array_step_sound (fuel : Nat) (valueSound : ValueSound fuel) (arraySound : ArraySound fuel) : ArraySound (fuel+1) := by
  intro input values remaining allowEmpty decoded
  let left := (scanWhitespace input).1
  have wl : WhiteSpace left := (whitespace_reconstruction input).2
  cases hs : (scanWhitespace input).2 with
  | nil => simp [parseArrayFuel,hs] at decoded
  | cons first tail =>
    have leftEq : input = left ++ (first::tail) := by simpa only [hs] using (whitespace_reconstruction input).1
    simp only [parseArrayFuel,hs] at decoded
    split at decoded
    · subst first
      split at decoded
      · rename_i enabled
        have same := Option.some.inj decoded
        have vals : [] = values := congrArg Prod.fst same
        have rem : tail = remaining := congrArg Prod.snd same
        refine ⟨?_,?_⟩
        · have assembled : input = left ++ [93] ++ remaining := by rw [leftEq,rem]; simp only [List.append_assoc,List.cons_append,List.nil_append]
          rw [←vals,assembled]; exact .empty left remaining wl
        · intro disabled; simp [disabled] at enabled
      · contradiction
    · rcases Option.bind_eq_some_iff.mp decoded with ⟨value,parsed,afterValue⟩
      rcases valueSound (first::tail) value.1 value.2 parsed with ⟨word,valueEq,head,_⟩
      let right := (scanWhitespace value.2).1
      have wr : WhiteSpace right := (whitespace_reconstruction value.2).2
      cases hr : (scanWhitespace value.2).2 with
      | nil => simp [hr] at afterValue
      | cons delimiter after =>
        have rightEq : value.2 = right ++ (delimiter::after) := by
          simpa only [hr] using (whitespace_reconstruction value.2).1
        simp only [hr] at afterValue
        split at afterValue
        · subst delimiter
          have same := Option.some.inj afterValue
          have vals : [value.1] = values := congrArg Prod.fst same
          have rem : after = remaining := congrArg Prod.snd same
          have assembled : input = left ++ word ++ right ++ [93] ++ remaining := by
            rw [leftEq,valueEq,rightEq,rem]
            simp only [List.append_assoc,List.cons_append,List.nil_append]
          refine ⟨?_,?_⟩
          · rw [←vals]; exact array_single_reconstruction input left word right remaining value.1 assembled wl head wr
          · intro _; rw [←vals]; simp
        · split at afterValue
          · subst delimiter
            rcases Option.bind_eq_some_iff.mp afterValue with ⟨rest,tailParsed,pair⟩
            have same := Option.some.inj pair
            have vals : value.1::rest.1 = values := congrArg Prod.fst same
            have rem : rest.2 = remaining := congrArg Prod.snd same
            have tailMeaning := arraySound after rest.1 rest.2 false tailParsed
            have nonempty := tailMeaning.2 rfl
            have tailMeaning' : ArrayBodyMeaning after rest.1 remaining := by rw [←rem]; exact tailMeaning.1
            have assembled : input = left ++ word ++ right ++ [44] ++ after := by
              rw [leftEq,valueEq,rightEq]
              simp only [List.append_assoc,List.cons_append,List.nil_append]
            refine ⟨?_,?_⟩
            · rw [←vals]
              exact array_cons_reconstruction input left word right after remaining value.1 rest.1
                assembled wl head wr tailMeaning' nonempty
            · intro _; rw [←vals]; simp
          · contradiction

theorem object_step_sound (fuel : Nat) (valueSound : ValueSound fuel) (objectSound : ObjectSound fuel) : ObjectSound (fuel+1) := by
  intro input entries remaining allowEmpty decoded
  let left := (scanWhitespace input).1
  have wl : WhiteSpace left := (whitespace_reconstruction input).2
  cases hs : (scanWhitespace input).2 with
  | nil => simp [parseObjectFuel,hs] at decoded
  | cons first tail =>
    have leftEq : input = left ++ (first::tail) := by simpa only [hs] using (whitespace_reconstruction input).1
    simp only [parseObjectFuel,hs] at decoded
    split at decoded
    · subst first
      split at decoded
      · rename_i enabled
        have same := Option.some.inj decoded
        have vals : [] = entries := congrArg Prod.fst same
        have rem : tail = remaining := congrArg Prod.snd same
        refine ⟨?_,?_⟩
        · have assembled : input = left ++ [125] ++ remaining := by rw [leftEq,rem]; simp only [List.append_assoc,List.cons_append,List.nil_append]
          rw [←vals,assembled]; exact .empty left remaining wl
        · intro disabled; simp [disabled] at enabled
      · contradiction
    · rcases Option.bind_eq_some_iff.mp decoded with ⟨key,keyParsed,afterKey⟩
      rcases (decode_quoted_exact (first::tail) key.1 key.2).mp keyParsed with ⟨keyWord,keyEq,name⟩
      rcases Option.bind_eq_some_iff.mp afterKey with ⟨afterColon,colonParsed,afterSeparator⟩
      let before := (scanWhitespace key.2).1
      have wb : WhiteSpace before := (whitespace_reconstruction key.2).2
      have beforeEq : key.2 = before ++ [58] ++ afterColon := by
        calc key.2 = before ++ (scanWhitespace key.2).2 := (whitespace_reconstruction key.2).1
             _ = before ++ ([58] ++ afterColon) := congrArg (fun rest => before ++ rest) ((take_word_exact _ _ _).mp colonParsed)
             _ = before ++ [58] ++ afterColon := (List.append_assoc _ _ _).symm
      rcases Option.bind_eq_some_iff.mp afterSeparator with ⟨value,valueParsed,afterValue⟩
      rcases valueSound (scanWhitespace afterColon).2 value.1 value.2 valueParsed with ⟨word,valueEq,head,_⟩
      let afterSpace := (scanWhitespace afterColon).1
      have wa : WhiteSpace afterSpace := (whitespace_reconstruction afterColon).2
      have afterEq : afterColon = afterSpace ++ word ++ value.2 := by
        calc afterColon = afterSpace ++ (scanWhitespace afterColon).2 := (whitespace_reconstruction afterColon).1
             _ = afterSpace ++ (word ++ value.2) := congrArg (fun rest => afterSpace ++ rest) valueEq
             _ = afterSpace ++ word ++ value.2 := (List.append_assoc _ _ _).symm
      let right := (scanWhitespace value.2).1
      have wr : WhiteSpace right := (whitespace_reconstruction value.2).2
      cases hr : (scanWhitespace value.2).2 with
      | nil => simp [hr] at afterValue
      | cons delimiter after =>
        have rightEq : value.2 = right ++ (delimiter::after) := by
          simpa only [hr] using (whitespace_reconstruction value.2).1
        simp only [hr] at afterValue
        split at afterValue
        · subst delimiter
          have same := Option.some.inj afterValue
          have vals : [(key.1,value.1)] = entries := congrArg Prod.fst same
          have rem : after = remaining := congrArg Prod.snd same
          have assembled : input = left ++ keyWord ++ before ++ [58] ++ afterSpace ++ word ++ right ++ [125] ++ remaining := by
            rw [leftEq,keyEq,beforeEq,afterEq,rightEq,rem]
            simp only [List.append_assoc,List.cons_append,List.nil_append]
          refine ⟨?_,?_⟩
          · rw [←vals]
            exact object_single_reconstruction input left keyWord before afterSpace word right remaining key.1 value.1
              assembled wl name wb wa head wr
          · intro _; rw [←vals]; simp
        · split at afterValue
          · subst delimiter
            rcases Option.bind_eq_some_iff.mp afterValue with ⟨rest,tailParsed,pair⟩
            have same := Option.some.inj pair
            have vals : (key.1,value.1)::rest.1 = entries := congrArg Prod.fst same
            have rem : rest.2 = remaining := congrArg Prod.snd same
            have tailMeaning := objectSound after rest.1 rest.2 false tailParsed
            have nonempty := tailMeaning.2 rfl
            have tailMeaning' : ObjectBodyMeaning after rest.1 remaining := by rw [←rem]; exact tailMeaning.1
            have assembled : input = left ++ keyWord ++ before ++ [58] ++ afterSpace ++ word ++ right ++ [44] ++ after := by
              rw [leftEq,keyEq,beforeEq,afterEq,rightEq]
              simp only [List.append_assoc,List.cons_append,List.nil_append]
            refine ⟨?_,?_⟩
            · rw [←vals]
              exact object_cons_reconstruction input left keyWord before afterSpace word right after remaining key.1 value.1 rest.1
                assembled wl name wb wa head wr tailMeaning' nonempty
            · intro _; rw [←vals]; simp
          · contradiction

theorem all_modes_sound (fuel : Nat) : ValueSound fuel ∧ ArraySound fuel ∧ ObjectSound fuel := by
  induction fuel with
  | zero =>
    refine ⟨?_,?_,?_⟩
    · intro input value remaining decoded; simp [parseValueFuel] at decoded
    · intro input values remaining allowEmpty decoded; simp [parseArrayFuel] at decoded
    · intro input entries remaining allowEmpty decoded; simp [parseObjectFuel] at decoded
  | succ fuel ih =>
    exact ⟨value_step_sound fuel ih.2.1 ih.2.2,array_step_sound fuel ih.1 ih.2.1,
      object_step_sound fuel ih.1 ih.2.2⟩

theorem recursive_value_sound (fuel : Nat) (input : List Nat) (value : RawValue) (remaining : List Nat)
    (decoded : parseValueFuel fuel input = some (value,remaining)) : BoundedValuePrefixMeaning input value remaining :=
  (all_modes_sound fuel).1 input value remaining decoded

theorem recursive_array_sound (fuel : Nat) (input : List Nat) (values : List RawValue) (remaining : List Nat) (allowEmpty : Bool)
    (decoded : parseArrayFuel fuel input allowEmpty = some (values,remaining)) :
    ArrayBodyMeaning input values remaining ∧ (allowEmpty = false → values ≠ []) :=
  (all_modes_sound fuel).2.1 input values remaining allowEmpty decoded

theorem recursive_object_sound (fuel : Nat) (input : List Nat) (entries : List (List Nat × RawValue)) (remaining : List Nat) (allowEmpty : Bool)
    (decoded : parseObjectFuel fuel input allowEmpty = some (entries,remaining)) :
    ObjectBodyMeaning input entries remaining ∧ (allowEmpty = false → entries ≠ []) :=
  (all_modes_sound fuel).2.2 input entries remaining allowEmpty decoded

#print axioms value_step_sound
#print axioms array_step_sound
#print axioms object_step_sound
#print axioms all_modes_sound
#print axioms recursive_value_sound
#print axioms recursive_array_sound
#print axioms recursive_object_sound
end RelationalSuccessor.CandidateJsonSoundness
