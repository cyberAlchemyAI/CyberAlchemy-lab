import LiteralDecoder
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonTokens
open CandidateJsonBytes CandidateDecimal CandidateNumberParser

def decodeNumber (input : List Nat) : Option (String × List Nat) :=
  let run := scanRun NumberCode input
  let chars := run.1.map Char.ofNat
  match parseChars chars with
  | none => none
  | some _ => some (String.ofList chars,run.2)

theorem decode_number_sound (input : List Nat) (token : String) (remaining : List Nat)
    (decoded : decodeNumber input = some (token,remaining)) : NumberPrefixMeaning input token remaining := by
  have run := scanned_run_meaning NumberCode input
  cases parsed : parseChars ((scanRun NumberCode input).1.map Char.ofNat) with
  | none => simp [decodeNumber,parsed] at decoded
  | some parts =>
    simp only [decodeNumber,parsed] at decoded
    have same := Option.some.inj decoded
    have tokenEq : String.ofList ((scanRun NumberCode input).1.map Char.ofNat) = token := congrArg Prod.fst same
    have remEq : (scanRun NumberCode input).2 = remaining := congrArg Prod.snd same
    have grammar := (parser_covers_exact_JSON_grammar ((scanRun NumberCode input).1.map Char.ofNat)).mp ⟨parts,parsed⟩
    refine ⟨?_,?_,?_⟩
    · rw [←tokenEq,String.toList_ofList]; exact grammar
    · rw [←tokenEq,String.toList_ofList,numeric_word_roundtrip _ run.2.1,←remEq]
      exact run.1
    · simpa only [remEq] using run.2.2

theorem decode_number_complete (input : List Nat) (token : String) (remaining : List Nat)
    (meaning : NumberPrefixMeaning input token remaining) : decodeNumber input = some (token,remaining) := by
  have allowed := grammar_number_codes token.toList meaning.1
  have scanned := scan_run_inverse NumberCode (token.toList.map Char.toNat) remaining allowed meaning.2.2
  rcases (parser_covers_exact_JSON_grammar token.toList).mpr meaning.1 with ⟨parts,parsed⟩
  unfold decodeNumber
  rw [meaning.2.1,scanned]
  simp only [scalar_word_roundtrip,parsed,String.ofList_toList]

theorem decode_number_exact (input : List Nat) (token : String) (remaining : List Nat) :
    decodeNumber input = some (token,remaining) ↔ NumberPrefixMeaning input token remaining :=
  ⟨decode_number_sound input token remaining,decode_number_complete input token remaining⟩

theorem number_prefix_value_bridge (input : List Nat) (token : String) (remaining : List Nat)
    (decoded : decodeNumber input = some (token,remaining)) :
    ∃ word, input = word ++ remaining ∧ ValueMeaning word (.number token) := by
  have meaning := decode_number_sound input token remaining decoded
  exact ⟨token.toList.map Char.toNat,meaning.2.1,ValueMeaning.number token meaning.1⟩

theorem number_prefix_unique (input : List Nat) (token1 token2 : String) (rest1 rest2 : List Nat)
    (first : NumberPrefixMeaning input token1 rest1) (second : NumberPrefixMeaning input token2 rest2) :
    token1 = token2 ∧ rest1 = rest2 := by
  have same := Option.some.inj (((decode_number_exact input token1 rest1).mpr first).symm.trans
    ((decode_number_exact input token2 rest2).mpr second))
  exact ⟨congrArg Prod.fst same,congrArg Prod.snd same⟩

theorem decoded_number_progress (input : List Nat) (token : String) (remaining : List Nat)
    (decoded : decodeNumber input = some (token,remaining)) : remaining.length < input.length := by
  have meaning := decode_number_sound input token remaining decoded
  have nonempty := grammar_word_nonempty token.toList meaning.1
  have positive : 0 < token.toList.length := by
    cases chars : token.toList with
    | nil => exact False.elim (nonempty chars)
    | cons first rest => simp
  rw [meaning.2.1]
  simp only [List.length_append,List.length_map]; omega

def decodeWholeNumber (input : List Nat) : Option String :=
  (decodeNumber input).bind fun decoded => if decoded.2 = [] then some decoded.1 else none

def WholeNumberMeaning (input : List Nat) (token : String) : Prop :=
  NumberGrammar token.toList ∧ input = token.toList.map Char.toNat

theorem decode_whole_number_exact (input : List Nat) (token : String) :
    decodeWholeNumber input = some token ↔ WholeNumberMeaning input token := by
  constructor
  · intro decoded
    unfold decodeWholeNumber at decoded
    rcases Option.bind_eq_some_iff.mp decoded with ⟨pair,number,whole⟩
    split at whole
    · rename_i empty
      have same := Option.some.inj whole
      have meaning := decode_number_sound input pair.1 pair.2 number
      exact ⟨by simpa only [same] using meaning.1,by simpa only [same,empty,List.append_nil] using meaning.2.1⟩
    · contradiction
  · rintro ⟨grammar,same⟩
    have decoded := (decode_number_exact input token []).mpr ⟨grammar,by simp [same],Or.inl rfl⟩
    unfold decodeWholeNumber
    rw [decoded]; rfl

theorem decode_number_at_value_boundary (token : String) (remaining : List Nat)
    (grammar : NumberGrammar token.toList) (boundary : FollowsValue remaining) :
    decodeNumber (token.toList.map Char.toNat ++ remaining) = some (token,remaining) := by
  apply decode_number_complete
  exact ⟨grammar,rfl,value_boundary_stops_number remaining boundary⟩

#print axioms decode_number_sound
#print axioms decode_number_complete
#print axioms decode_number_exact
#print axioms number_prefix_value_bridge
#print axioms number_prefix_unique
#print axioms decoded_number_progress
#print axioms decode_whole_number_exact
#print axioms decode_number_at_value_boundary
end RelationalSuccessor.CandidateJsonTokens
