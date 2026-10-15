import DocumentSoundness
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonCompleteness
open CandidateJsonBytes CandidateJsonTokens CandidateJsonStrings CandidateJsonParser CandidateJsonSoundness

def ValueStartCode (code : Nat) : Prop := code ∈ [110,102,116,34,91,123] ∨ NumberCode code

theorem number_code_not_white_or_bracket (code : Nat) (allowed : NumberCode code) :
    ¬ WhiteCode code ∧ code ≠ 91 ∧ code ≠ 123 := by
  simp [NumberCode] at allowed
  rcases allowed with h|h|h|h|h|h|h|h|h|h|h|h|h|h|h <;> subst code <;> decide

theorem value_start_not_white_or_close (code : Nat) (allowed : ValueStartCode code) :
    ¬ WhiteCode code ∧ code ≠ 93 ∧ code ≠ 125 := by
  rcases allowed with literal | number
  · simp at literal
    rcases literal with h|h|h|h|h|h <;> subst code <;> decide
  · simp [NumberCode] at number
    rcases number with h|h|h|h|h|h|h|h|h|h|h|h|h|h|h <;> subst code <;> decide

theorem string_starts_quote (word units : List Nat) (meaning : StringMeaning word units) :
    ∃ tail, word = 34::tail := by
  rcases meaning with ⟨content,same,_⟩
  exact ⟨content++[34],by simpa only [List.cons_append,List.nil_append] using same⟩

theorem value_has_start (word : List Nat) (value : RawValue) (meaning : ValueMeaning word value) :
    ∃ first tail, word = first::tail ∧ ValueStartCode first := by
  cases meaning with
  | null => exact ⟨110,[117,108,108],rfl,Or.inl (by simp)⟩
  | false => exact ⟨102,[97,108,115,101],rfl,Or.inl (by simp)⟩
  | true => exact ⟨116,[114,117,101],rfl,Or.inl (by simp)⟩
  | number token grammar =>
    have nonempty := grammar_word_nonempty token.toList grammar
    have codes := grammar_number_codes token.toList grammar
    cases chars : token.toList with
    | nil => exact False.elim (nonempty chars)
    | cons first rest => exact ⟨first.toNat,rest.map Char.toNat,rfl,Or.inr (codes first.toNat (by simp [chars]))⟩
  | string text units meaning =>
    rcases string_starts_quote _ units meaning with ⟨tail,same⟩
    exact ⟨34,tail,same,Or.inl (by simp)⟩
  | emptyArray space ws => exact ⟨91,space++[93],by simp,Or.inl (by simp)⟩
  | array left text right values wl items wr =>
    exact ⟨91,left++text++right++[93],by simp,Or.inl (by simp)⟩
  | emptyObject space ws => exact ⟨123,space++[125],by simp,Or.inl (by simp)⟩
  | object left text right entries wl members wr =>
    exact ⟨123,left++text++right++[125],by simp,Or.inl (by simp)⟩

theorem primitive_has_start (word : List Nat) (value : RawValue) (meaning : PrimitiveMeaning word value) :
    ∃ first tail, word = first::tail ∧ first ≠ 91 ∧ first ≠ 123 := by
  cases meaning with
  | literal word value meaning => cases meaning <;> exact ⟨_,_,rfl,by decide,by decide⟩
  | number token grammar =>
    have nonempty := grammar_word_nonempty token.toList grammar
    have codes := grammar_number_codes token.toList grammar
    cases chars : token.toList with
    | nil => exact False.elim (nonempty chars)
    | cons first rest =>
      have code := number_code_not_white_or_bracket first.toNat (codes first.toNat (by simp [chars]))
      exact ⟨first.toNat,rest.map Char.toNat,rfl,code.2.1,code.2.2⟩
  | string word units meaning =>
    rcases string_starts_quote word units meaning with ⟨tail,same⟩
    exact ⟨34,tail,same,by decide,by decide⟩

theorem items_have_start (word : List Nat) (values : List RawValue) (meaning : ItemsMeaning word values) :
    ∃ first tail, word = first::tail ∧ ValueStartCode first := by
  cases meaning with
  | one text value head => exact value_has_start _ value head
  | cons text left right remaining value values head wl wr tail =>
    rcases value_has_start text value head with ⟨first,rest,same,allowed⟩
    exact ⟨first,rest++left++[44]++right++remaining,by simp [same],allowed⟩

theorem members_start_quote (word : List Nat) (entries : List (List Nat × RawValue))
    (meaning : MembersMeaning word entries) : ∃ tail, word = 34::tail := by
  cases meaning with
  | one key left right text units value name wl wr head =>
    rcases string_starts_quote key units name with ⟨tail,same⟩
    exact ⟨tail++left++[58]++right++text,by simp [same]⟩
  | cons key left right text before after remaining units value entries name wl wr head wb wa tail =>
    rcases string_starts_quote key units name with ⟨rest,same⟩
    exact ⟨rest++left++[58]++right++text++before++[44]++after++remaining,by simp [same]⟩

theorem scan_white_prefix (space input : List Nat) (ws : WhiteSpace space) (stop : Stops WhiteCode input) :
    scanWhitespace (space ++ input) = (space,input) := scan_run_inverse WhiteCode space input ws stop

theorem scan_white_before_value (space word remaining : List Nat) (value : RawValue)
    (ws : WhiteSpace space) (meaning : ValueMeaning word value) :
    scanWhitespace (space ++ word ++ remaining) = (space,word ++ remaining) := by
  rcases value_has_start word value meaning with ⟨first,tail,same,allowed⟩
  have denied := (value_start_not_white_or_close first allowed).1
  simpa only [List.append_assoc] using scan_white_prefix space (word++remaining) ws
    (Or.inr ⟨first,tail++remaining,by simp [same],denied⟩)

theorem scan_white_before_code (space remaining : List Nat) (code : Nat)
    (ws : WhiteSpace space) (denied : ¬ WhiteCode code) :
    scanWhitespace (space ++ [code] ++ remaining) = (space,code::remaining) := by
  simpa only [List.append_assoc,List.cons_append,List.nil_append] using
    scan_white_prefix space (code::remaining) ws (Or.inr ⟨code,remaining,rfl,denied⟩)

theorem scan_white_before_string (space word remaining units : List Nat)
    (ws : WhiteSpace space) (meaning : StringMeaning word units) :
    scanWhitespace (space ++ word ++ remaining) = (space,word++remaining) := by
  rcases string_starts_quote word units meaning with ⟨tail,same⟩
  simpa only [List.append_assoc] using scan_white_prefix space (word++remaining) ws
    (Or.inr ⟨34,tail++remaining,by simp [same],by decide⟩)

theorem whitespace_value_boundary (space remaining : List Nat) (code : Nat)
    (ws : WhiteSpace space) (boundary : ValueBoundaryCode code) : FollowsValue (space ++ [code] ++ remaining) := by
  cases space with
  | nil => exact Or.inr ⟨code,remaining,rfl,boundary⟩
  | cons first rest =>
    exact Or.inr ⟨first,rest++[code]++remaining,rfl,Or.inl (ws first (by simp))⟩

#print axioms number_code_not_white_or_bracket
#print axioms value_start_not_white_or_close
#print axioms string_starts_quote
#print axioms value_has_start
#print axioms primitive_has_start
#print axioms items_have_start
#print axioms members_start_quote
#print axioms scan_white_prefix
#print axioms scan_white_before_value
#print axioms scan_white_before_code
#print axioms scan_white_before_string
#print axioms whitespace_value_boundary
end RelationalSuccessor.CandidateJsonCompleteness
