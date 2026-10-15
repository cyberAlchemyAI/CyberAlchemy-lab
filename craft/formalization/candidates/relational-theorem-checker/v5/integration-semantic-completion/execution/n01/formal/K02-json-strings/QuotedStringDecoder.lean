import StringUnitDecoder
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonStrings
open CandidateJsonBytes

def scanFuel : Nat → List Nat → Option (List Nat × List Nat)
  | 0, _ => none
  | fuel+1, input =>
    match input with
    | [] => none
    | code::suffix =>
      if code = 34 then some ([],suffix)
      else (decodeUnit (code::suffix)).bind fun first =>
        (scanFuel fuel first.2).bind fun tail => some (first.1 ++ tail.1,tail.2)

def ContentPrefixMeaning (input units remaining : List Nat) : Prop :=
  ∃ content, input = content ++ [34] ++ remaining ∧ StringContentMeaning content units

theorem scan_sound (fuel : Nat) (input units remaining : List Nat)
    (decoded : scanFuel fuel input = some (units,remaining)) : ContentPrefixMeaning input units remaining := by
  induction fuel generalizing input units remaining with
  | zero => simp [scanFuel] at decoded
  | succ fuel ih =>
    cases input with
    | nil => simp [scanFuel] at decoded
    | cons code suffix =>
      simp only [scanFuel] at decoded
      split at decoded
      · subst code
        have same := Option.some.inj decoded
        have empty : [] = units := congrArg Prod.fst same
        have rest : suffix = remaining := congrArg Prod.snd same
        exact ⟨[],by simp [rest],by rw [←empty]; exact .nil⟩
      · rcases Option.bind_eq_some_iff.mp decoded with ⟨first,head,tailDecode⟩
        rcases Option.bind_eq_some_iff.mp tailDecode with ⟨tail,tailMeaning,pair⟩
        have same := Option.some.inj pair
        have sameUnits : first.1 ++ tail.1 = units := congrArg Prod.fst same
        have sameRest : tail.2 = remaining := congrArg Prod.snd same
        rcases decode_unit_sound (code::suffix) first.1 first.2 head with ⟨word,inputEq,wordMeaning⟩
        rcases ih first.2 tail.1 tail.2 tailMeaning with ⟨content,tailEq,contentMeaning⟩
        exact ⟨word++content,by rw [inputEq,tailEq,sameRest]; simp only [List.append_assoc],by
          rw [←sameUnits]; exact .cons word content first.1 tail.1 wordMeaning contentMeaning⟩

theorem scan_content_complete (content units remaining : List Nat)
    (meaning : StringContentMeaning content units) :
    ∀ fuel, content.length < fuel → scanFuel fuel (content ++ [34] ++ remaining) = some (units,remaining) := by
  induction meaning with
  | nil =>
    intro fuel bound
    cases fuel with
    | zero => omega
    | succ fuel => rfl
  | cons word content units tailUnits head tail ih =>
    intro fuel bound
    cases fuel with
    | zero => omega
    | succ fuel =>
      have positive : 0 < word.length := by
        have nonempty := unit_word_nonempty word units head
        cases word <;> simp_all
      have tailBound : content.length < fuel := by simp only [List.length_append] at bound; omega
      have tailDecoded := ih fuel tailBound
      have unitDecoded := decode_unit_word_complete word units (content ++ [34] ++ remaining) head
      have noQuote := unit_word_no_quote word units head
      cases word with
      | nil => simp at positive
      | cons code rest =>
        have nq : code ≠ 34 := by intro same; apply noQuote rest; simp only [same]
        simp only [List.cons_append,List.append_assoc] at unitDecoded ⊢
        simp only [scanFuel,if_neg nq]
        rw [unitDecoded]
        simp only [Option.bind_some]
        simp only [List.append_assoc,List.cons_append,List.nil_append] at tailDecoded ⊢
        rw [tailDecoded]
        rfl

def scan (input : List Nat) : Option (List Nat × List Nat) := scanFuel (input.length+1) input

theorem scan_complete (input units remaining : List Nat) (meaning : ContentPrefixMeaning input units remaining) :
    scan input = some (units,remaining) := by
  rcases meaning with ⟨content,same,contentMeaning⟩
  unfold scan
  rw [same]
  apply scan_content_complete content units remaining contentMeaning
  simp only [List.length_append,List.length_singleton]; omega

theorem scan_exact (input units remaining : List Nat) :
    scan input = some (units,remaining) ↔ ContentPrefixMeaning input units remaining :=
  ⟨scan_sound (input.length+1) input units remaining,scan_complete input units remaining⟩

def decodeQuoted (input : List Nat) : Option (List Nat × List Nat) :=
  match input with
  | [] => none
  | code::content => if code = 34 then scan content else none

def QuotedPrefixMeaning (input units remaining : List Nat) : Prop :=
  ∃ word, input = word ++ remaining ∧ StringMeaning word units

theorem decode_quoted_exact (input units remaining : List Nat) :
    decodeQuoted input = some (units,remaining) ↔ QuotedPrefixMeaning input units remaining := by
  constructor
  · intro decoded
    cases input with
    | nil => simp [decodeQuoted] at decoded
    | cons code content =>
      simp only [decodeQuoted] at decoded
      split at decoded
      · subst code
        rcases (scan_exact content units remaining).mp decoded with ⟨text,same,meaning⟩
        exact ⟨[34]++text++[34],by simp [same,List.append_assoc],text,rfl,meaning⟩
      · contradiction
  · rintro ⟨word,same,text,wordEq,meaning⟩
    rw [same,wordEq]
    simp only [List.cons_append,List.nil_append,decodeQuoted]
    apply scan_complete
    exact ⟨text,by simp only [List.append_assoc],meaning⟩

def decodeString (input : List Nat) : Option (List Nat) :=
  (decodeQuoted input).bind fun decoded => if decoded.2 = [] then some decoded.1 else none

theorem decode_string_exact (input units : List Nat) :
    decodeString input = some units ↔ StringMeaning input units := by
  constructor
  · intro decoded
    unfold decodeString at decoded
    rcases Option.bind_eq_some_iff.mp decoded with ⟨pair,quoted,whole⟩
    split at whole
    · rename_i empty
      have same := Option.some.inj whole
      rcases (decode_quoted_exact input pair.1 pair.2).mp quoted with ⟨word,inputEq,meaning⟩
      rw [inputEq,empty,List.append_nil,←same]
      exact meaning
    · contradiction
  · intro meaning
    unfold decodeString
    have quoted := (decode_quoted_exact input units []).mpr ⟨input,by simp,meaning⟩
    rw [quoted]; rfl

theorem quoted_meaning_unique (input units1 units2 rest1 rest2 : List Nat)
    (first : QuotedPrefixMeaning input units1 rest1) (second : QuotedPrefixMeaning input units2 rest2) :
    units1 = units2 ∧ rest1 = rest2 := by
  have same := Option.some.inj ((decode_quoted_exact input units1 rest1).mpr first |>.symm.trans
    ((decode_quoted_exact input units2 rest2).mpr second))
  exact ⟨congrArg Prod.fst same,congrArg Prod.snd same⟩

theorem decode_quoted_units_bounded (input units remaining : List Nat)
    (decoded : decodeQuoted input = some (units,remaining)) : ∀ unit ∈ units, unit < 65536 := by
  rcases (decode_quoted_exact input units remaining).mp decoded with ⟨word,_,content,_,meaning⟩
  exact string_content_units_bounded content units meaning

theorem decode_quoted_progress (input units remaining : List Nat)
    (decoded : decodeQuoted input = some (units,remaining)) : remaining.length < input.length := by
  rcases (decode_quoted_exact input units remaining).mp decoded with ⟨word,same,content,wordEq,_⟩
  rw [same,wordEq]
  simp only [List.length_append,List.length_singleton]; omega

def decodeStringBytes (bytes : Bytes) : Option (List Nat) :=
  (decodeUtf8 bytes).bind decodeString

def ByteStringMeaning (bytes : Bytes) (units : List Nat) : Prop :=
  ∃ text, StreamMeaning bytes text ∧ StringMeaning text units

theorem decode_string_bytes_exact (bytes : Bytes) (units : List Nat) :
    decodeStringBytes bytes = some units ↔ ByteStringMeaning bytes units := by
  simp only [decodeStringBytes,Option.bind_eq_some_iff,decode_utf8_exact,decode_string_exact,ByteStringMeaning]

theorem string_meaning_unique (text units1 units2 : List Nat)
    (first : StringMeaning text units1) (second : StringMeaning text units2) : units1 = units2 := by
  exact Option.some.inj (((decode_string_exact text units1).mpr first).symm.trans
    ((decode_string_exact text units2).mpr second))

theorem byte_string_units_bounded (bytes : Bytes) (units : List Nat)
    (decoded : decodeStringBytes bytes = some units) : ∀ unit ∈ units, unit < 65536 := by
  rcases (decode_string_bytes_exact bytes units).mp decoded with ⟨text,_,content,_,meaning⟩
  exact string_content_units_bounded content units meaning

#print axioms scan_sound
#print axioms scan_content_complete
#print axioms scan_complete
#print axioms scan_exact
#print axioms decode_quoted_exact
#print axioms decode_string_exact
#print axioms quoted_meaning_unique
#print axioms decode_quoted_units_bounded
#print axioms decode_quoted_progress
#print axioms decode_string_bytes_exact
#print axioms string_meaning_unique
#print axioms byte_string_units_bounded
end RelationalSuccessor.CandidateJsonStrings
