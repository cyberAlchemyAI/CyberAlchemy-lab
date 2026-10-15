import PrefixScan
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonTokens
open CandidateJsonBytes

def takeWord : List Nat → List Nat → Option (List Nat)
  | [], input => some input
  | first::word, input =>
    match input with
    | [] => none
    | code::tail => if code = first then takeWord word tail else none

theorem take_word_exact (word input remaining : List Nat) :
    takeWord word input = some remaining ↔ input = word ++ remaining := by
  induction word generalizing input with
  | nil => simp [takeWord]
  | cons first word ih =>
    cases input with
    | nil => simp [takeWord]
    | cons code tail =>
      by_cases equal : code = first
      · subst code; simp [takeWord,ih]
      · simp [takeWord,equal]

def decodeLiteral (input : List Nat) : Option (RawValue × List Nat) :=
  match takeWord [110,117,108,108] input with
  | some remaining => some (.null,remaining)
  | none => match takeWord [102,97,108,115,101] input with
    | some remaining => some (.boolean false,remaining)
    | none => match takeWord [116,114,117,101] input with
      | some remaining => some (.boolean true,remaining)
      | none => none

theorem decode_literal_sound (input : List Nat) (value : RawValue) (remaining : List Nat)
    (decoded : decodeLiteral input = some (value,remaining)) : LiteralPrefixMeaning input value remaining := by
  cases hn : takeWord [110,117,108,108] input with
  | some rest =>
    simp only [decodeLiteral,hn] at decoded
    have same := Option.some.inj decoded
    have val : RawValue.null = value := congrArg Prod.fst same
    have rem : rest = remaining := congrArg Prod.snd same
    exact ⟨[110,117,108,108],by simpa only [rem] using (take_word_exact _ _ _).mp hn,by rw [←val]; constructor⟩
  | none =>
    cases hf : takeWord [102,97,108,115,101] input with
    | some rest =>
      simp only [decodeLiteral,hn,hf] at decoded
      have same := Option.some.inj decoded
      have val : RawValue.boolean false = value := congrArg Prod.fst same
      have rem : rest = remaining := congrArg Prod.snd same
      exact ⟨[102,97,108,115,101],by simpa only [rem] using (take_word_exact _ _ _).mp hf,by rw [←val]; constructor⟩
    | none =>
      cases ht : takeWord [116,114,117,101] input with
      | some rest =>
        simp only [decodeLiteral,hn,hf,ht] at decoded
        have same := Option.some.inj decoded
        have val : RawValue.boolean true = value := congrArg Prod.fst same
        have rem : rest = remaining := congrArg Prod.snd same
        exact ⟨[116,114,117,101],by simpa only [rem] using (take_word_exact _ _ _).mp ht,by rw [←val]; constructor⟩
      | none => simp [decodeLiteral,hn,hf,ht] at decoded

theorem decode_literal_word_complete (word : List Nat) (value : RawValue) (remaining : List Nat)
    (meaning : LiteralMeaning word value) : decodeLiteral (word ++ remaining) = some (value,remaining) := by
  cases meaning <;> simp [decodeLiteral,takeWord]

theorem decode_literal_exact (input : List Nat) (value : RawValue) (remaining : List Nat) :
    decodeLiteral input = some (value,remaining) ↔ LiteralPrefixMeaning input value remaining := by
  constructor
  · exact decode_literal_sound input value remaining
  · rintro ⟨word,same,meaning⟩
    rw [same]; exact decode_literal_word_complete word value remaining meaning

theorem literal_prefix_value_bridge (input : List Nat) (value : RawValue) (remaining : List Nat)
    (decoded : decodeLiteral input = some (value,remaining)) :
    ∃ word, input = word ++ remaining ∧ ValueMeaning word value := by
  rcases decode_literal_sound input value remaining decoded with ⟨word,same,meaning⟩
  exact ⟨word,same,literal_value_meaning word value meaning⟩

theorem literal_meaning_unique (input : List Nat) (value1 value2 : RawValue) (rest1 rest2 : List Nat)
    (first : LiteralPrefixMeaning input value1 rest1) (second : LiteralPrefixMeaning input value2 rest2) :
    value1 = value2 ∧ rest1 = rest2 := by
  have same := Option.some.inj (((decode_literal_exact input value1 rest1).mpr first).symm.trans
    ((decode_literal_exact input value2 rest2).mpr second))
  exact ⟨congrArg Prod.fst same,congrArg Prod.snd same⟩

theorem decoded_literal_progress (input : List Nat) (value : RawValue) (remaining : List Nat)
    (decoded : decodeLiteral input = some (value,remaining)) : remaining.length < input.length := by
  rcases decode_literal_sound input value remaining decoded with ⟨word,same,meaning⟩
  rw [same]
  cases meaning <;> simp <;> omega

#print axioms take_word_exact
#print axioms decode_literal_sound
#print axioms decode_literal_word_complete
#print axioms decode_literal_exact
#print axioms literal_prefix_value_bridge
#print axioms literal_meaning_unique
#print axioms decoded_literal_progress
end RelationalSuccessor.CandidateJsonTokens
