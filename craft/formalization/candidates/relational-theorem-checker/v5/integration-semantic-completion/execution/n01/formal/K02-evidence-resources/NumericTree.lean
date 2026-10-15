import NumericWork
set_option autoImplicit false
namespace RelationalSuccessor.CandidateEvidenceResources
abbrev J := CandidateJsonSource.Value
mutual
  def numberTokens : J → List String
    | .number token=>[token]
    | .array values=>numberTokensValues values
    | .object entries=>numberTokensEntries entries
    | _=>[]
  termination_by value=>sizeOf value
  def numberTokensValues : List J → List String
    | []=>[]
    | value::values=>numberTokens value++numberTokensValues values
  termination_by values=>sizeOf values
  def numberTokensEntries : List (String × J) → List String
    | []=>[]
    | (_,value)::entries=>numberTokens value++numberTokensEntries entries
  termination_by entries=>sizeOf entries
end
mutual
  def NumberOccurs (token : String) : J → Prop
    | .number actual=>actual=token
    | .array values=>NumberOccursValues token values
    | .object entries=>NumberOccursEntries token entries
    | _=>False
  termination_by value=>sizeOf value
  def NumberOccursValues (token : String) : List J → Prop
    | []=>False
    | value::values=>NumberOccurs token value ∨ NumberOccursValues token values
  termination_by values=>sizeOf values
  def NumberOccursEntries (token : String) : List (String × J) → Prop
    | []=>False
    | (_,value)::entries=>NumberOccurs token value ∨ NumberOccursEntries token entries
  termination_by entries=>sizeOf entries
end
mutual
theorem number_tokens_exact (value : J) (token : String) : token∈numberTokens value ↔ NumberOccurs token value := by
  cases value with
  | number actual=>simp [numberTokens,NumberOccurs,eq_comm]
  | array values=>simpa only [numberTokens,NumberOccurs] using number_tokens_values_exact values token
  | object entries=>simpa only [numberTokens,NumberOccurs] using number_tokens_entries_exact entries token
  | null=>simp [numberTokens,NumberOccurs]
  | boolean flag=>simp [numberTokens,NumberOccurs]
  | string text=>simp [numberTokens,NumberOccurs]
  termination_by sizeOf value
theorem number_tokens_values_exact (values : List J) (token : String) : token∈numberTokensValues values ↔ NumberOccursValues token values := by
  cases values with
  | nil=>simp [numberTokensValues,NumberOccursValues]
  | cons value values=>simp only [numberTokensValues,NumberOccursValues,List.mem_append,number_tokens_exact value token,number_tokens_values_exact values token]
  termination_by sizeOf values
theorem number_tokens_entries_exact (entries : List (String × J)) (token : String) : token∈numberTokensEntries entries ↔ NumberOccursEntries token entries := by
  cases entries with
  | nil=>simp [numberTokensEntries,NumberOccursEntries]
  | cons pair entries=>
    cases pair with
    | mk name value=>simp only [numberTokensEntries,NumberOccursEntries,List.mem_append,number_tokens_exact value token,number_tokens_entries_exact entries token]
  termination_by sizeOf entries
  decreasing_by all_goals simp_all [List.cons.sizeOf_spec,Prod.mk.sizeOf_spec];omega
end

def NumericTreeMeaning (limits : NumericLimits) (value : J) : Prop := ∀ token,NumberOccurs token value → TokenWorkMeaning limits token
theorem numeric_tree_tokens_exact (limits : NumericLimits) (value : J) :
    TokensWorkMeaning limits (numberTokens value) ↔ NumericTreeMeaning limits value := by
  simp only [TokensWorkMeaning,NumericTreeMeaning,number_tokens_exact]
theorem numeric_tree_none_exact (limits : NumericLimits) (value : J) :
    firstUnsupported limits (numberTokens value)=none ↔ NumericTreeMeaning limits value :=
  (first_unsupported_none_exact limits (numberTokens value)).trans (numeric_tree_tokens_exact limits value)
theorem numeric_tree_refusal_has_actual_occurrence (limits : NumericLimits) (value : J) (token : String)
    (found : firstUnsupported limits (numberTokens value)=some token) : NumberOccurs token value ∧ ¬TokenWorkMeaning limits token := by
  have actual:=first_unsupported_is_actual_token limits (numberTokens value) token found
  exact ⟨(number_tokens_exact value token).mp actual.1,actual.2⟩
#print axioms number_tokens_exact
#print axioms number_tokens_values_exact
#print axioms number_tokens_entries_exact
#print axioms numeric_tree_tokens_exact
#print axioms numeric_tree_none_exact
#print axioms numeric_tree_refusal_has_actual_occurrence
end RelationalSuccessor.CandidateEvidenceResources
