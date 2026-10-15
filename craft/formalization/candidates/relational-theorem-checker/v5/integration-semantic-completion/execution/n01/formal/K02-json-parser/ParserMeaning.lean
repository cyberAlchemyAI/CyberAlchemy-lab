import NumberPrefixDecoder
import QuotedStringDecoder
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonParser
open CandidateJsonBytes CandidateJsonTokens CandidateJsonStrings CandidateDecimal

-- These meanings use the pre-existing grammar, not parser outputs.
inductive PrimitiveMeaning : List Nat → RawValue → Prop
  | literal (word : List Nat) (value : RawValue) (meaning : LiteralMeaning word value) : PrimitiveMeaning word value
  | number (token : String) (grammar : NumberGrammar token.toList) :
      PrimitiveMeaning (token.toList.map Char.toNat) (.number token)
  | string (word units : List Nat) (meaning : StringMeaning word units) : PrimitiveMeaning word (.string units)

def PrimitivePrefixMeaning (input : List Nat) (value : RawValue) (remaining : List Nat) : Prop :=
  ∃ word, input = word ++ remaining ∧ PrimitiveMeaning word value ∧ FollowsValue remaining

-- Body modes consume their closing delimiter. Ordered entries and duplicate keys remain raw syntax.
inductive ArrayBodyMeaning : List Nat → List RawValue → List Nat → Prop
  | empty (space remaining : List Nat) (ws : WhiteSpace space) :
      ArrayBodyMeaning (space ++ [93] ++ remaining) [] remaining
  | nonempty (left text right remaining : List Nat) (values : List RawValue)
      (wl : WhiteSpace left) (items : ItemsMeaning text values) (wr : WhiteSpace right) :
      ArrayBodyMeaning (left ++ text ++ right ++ [93] ++ remaining) values remaining

inductive ObjectBodyMeaning : List Nat → List (List Nat × RawValue) → List Nat → Prop
  | empty (space remaining : List Nat) (ws : WhiteSpace space) :
      ObjectBodyMeaning (space ++ [125] ++ remaining) [] remaining
  | nonempty (left text right remaining : List Nat) (entries : List (List Nat × RawValue))
      (wl : WhiteSpace left) (members : MembersMeaning text entries) (wr : WhiteSpace right) :
      ObjectBodyMeaning (left ++ text ++ right ++ [125] ++ remaining) entries remaining

-- An internal fuel budget is a termination device. Its completeness bound must be proved separately.
def RecursionBudget (input : List Nat) : Nat := 2*input.length+1

theorem primitive_value_bridge (word : List Nat) (value : RawValue) (meaning : PrimitiveMeaning word value) :
    ValueMeaning word value := by
  cases meaning with
  | literal word value meaning => exact literal_value_meaning word value meaning
  | number token grammar => exact .number token grammar
  | string word units meaning => exact .string word units meaning

theorem primitive_prefix_value_bridge (input : List Nat) (value : RawValue) (remaining : List Nat)
    (meaning : PrimitivePrefixMeaning input value remaining) : BoundedValuePrefixMeaning input value remaining := by
  rcases meaning with ⟨word,same,primitive,boundary⟩
  exact ⟨word,same,primitive_value_bridge word value primitive,boundary⟩

theorem number_code_not_dispatch (code : Nat) (allowed : NumberCode code) :
    code ≠ 34 ∧ code ≠ 110 ∧ code ≠ 102 ∧ code ≠ 116 := by
  simp [NumberCode] at allowed
  rcases allowed with h|h|h|h|h|h|h|h|h|h|h|h|h|h|h <;> subst code <;> decide

theorem primitive_word_nonempty (word : List Nat) (value : RawValue) (meaning : PrimitiveMeaning word value) :
    word ≠ [] := by
  cases meaning with
  | literal word value meaning => cases meaning <;> simp
  | number token grammar =>
    have nonempty := grammar_word_nonempty token.toList grammar
    cases chars : token.toList with
    | nil => exact False.elim (nonempty chars)
    | cons first rest => simp
  | string word units meaning => rcases meaning with ⟨content,same,_⟩; simp [same]

theorem array_body_value_bridge (input : List Nat) (values : List RawValue) (remaining : List Nat)
    (meaning : ArrayBodyMeaning input values remaining) :
    ∃ word, 91::input = word ++ remaining ∧ ValueMeaning word (.array values) := by
  cases meaning with
  | empty space remaining ws =>
    exact ⟨[91]++space++[93],by simp [List.append_assoc],.emptyArray space ws⟩
  | nonempty left text right remaining values wl items wr =>
    exact ⟨[91]++left++text++right++[93],by simp [List.append_assoc],.array left text right values wl items wr⟩

theorem object_body_value_bridge (input : List Nat) (entries : List (List Nat × RawValue)) (remaining : List Nat)
    (meaning : ObjectBodyMeaning input entries remaining) :
    ∃ word, 123::input = word ++ remaining ∧ ValueMeaning word (.object entries) := by
  cases meaning with
  | empty space remaining ws =>
    exact ⟨[123]++space++[125],by simp [List.append_assoc],.emptyObject space ws⟩
  | nonempty left text right remaining entries wl members wr =>
    exact ⟨[123]++left++text++right++[125],by simp [List.append_assoc],.object left text right entries wl members wr⟩

#print axioms primitive_value_bridge
#print axioms primitive_prefix_value_bridge
#print axioms number_code_not_dispatch
#print axioms primitive_word_nonempty
#print axioms array_body_value_bridge
#print axioms object_body_value_bridge
end RelationalSuccessor.CandidateJsonParser
