import GrammarStarts
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonCompleteness
open CandidateJsonBytes CandidateJsonTokens CandidateJsonStrings CandidateJsonParser CandidateJsonSoundness

def ValueComplete (word : List Nat) (value : RawValue) : Prop :=
  ∀ remaining fuel, 2*word.length < fuel → FollowsValue remaining →
    parseValueFuel fuel (word++remaining) = some (value,remaining)

def ItemsComplete (word : List Nat) (values : List RawValue) : Prop :=
  ∀ left right remaining fuel allowEmpty, WhiteSpace left → WhiteSpace right →
    2*(left++word++right++[93]).length < fuel →
    parseArrayFuel fuel (left++word++right++[93]++remaining) allowEmpty = some (values,remaining)

def MembersComplete (word : List Nat) (entries : List (List Nat × RawValue)) : Prop :=
  ∀ left right remaining fuel allowEmpty, WhiteSpace left → WhiteSpace right →
    2*(left++word++right++[125]).length < fuel →
    parseObjectFuel fuel (left++word++right++[125]++remaining) allowEmpty = some (entries,remaining)

theorem primitive_complete (word : List Nat) (value : RawValue) (meaning : PrimitiveMeaning word value) :
    ValueComplete word value := by
  intro remaining fuel bound boundary
  cases fuel with
  | zero => omega
  | succ fuel =>
    have decoded := (decode_primitive_exact (word++remaining) value remaining).mpr ⟨word,rfl,meaning,boundary⟩
    rcases primitive_has_start word value meaning with ⟨first,tail,same,notArray,notObject⟩
    rw [same] at decoded ⊢
    simp only [List.cons_append] at decoded ⊢
    rw [primitive_value_dispatch fuel first (tail++remaining) notArray notObject]
    exact decoded

theorem empty_array_body_complete (space remaining : List Nat) (ws : WhiteSpace space)
    (fuel : Nat) (bound : 2*(space++[93]).length < fuel) :
    parseArrayFuel fuel (space++[93]++remaining) true = some ([],remaining) := by
  cases fuel with
  | zero => omega
  | succ fuel =>
    have scanned := scan_white_before_code space remaining 93 ws (by decide)
    simp only [List.append_assoc,List.cons_append,List.nil_append] at scanned ⊢
    simp [parseArrayFuel,scanned]

theorem empty_object_body_complete (space remaining : List Nat) (ws : WhiteSpace space)
    (fuel : Nat) (bound : 2*(space++[125]).length < fuel) :
    parseObjectFuel fuel (space++[125]++remaining) true = some ([],remaining) := by
  cases fuel with
  | zero => omega
  | succ fuel =>
    have scanned := scan_white_before_code space remaining 125 ws (by decide)
    simp only [List.append_assoc,List.cons_append,List.nil_append] at scanned ⊢
    simp [parseObjectFuel,scanned]

theorem empty_array_complete (space : List Nat) (ws : WhiteSpace space) :
    ValueComplete ([91]++space++[93]) (.array []) := by
  intro remaining fuel bound boundary
  cases fuel with
  | zero => omega
  | succ fuel =>
    have bodyBound : 2*(space++[93]).length < fuel := by
      simp only [List.length_append,List.length_singleton] at bound ⊢; omega
    have decoded := empty_array_body_complete space remaining ws fuel bodyBound
    simp only [List.cons_append,List.nil_append,parseValueFuel]
    apply (qualify_exact _ (.array []) remaining).mpr
    exact ⟨by rw [decoded]; rfl,boundary⟩

theorem empty_object_complete (space : List Nat) (ws : WhiteSpace space) :
    ValueComplete ([123]++space++[125]) (.object []) := by
  intro remaining fuel bound boundary
  cases fuel with
  | zero => omega
  | succ fuel =>
    have bodyBound : 2*(space++[125]).length < fuel := by
      simp only [List.length_append,List.length_singleton] at bound ⊢; omega
    have decoded := empty_object_body_complete space remaining ws fuel bodyBound
    simp only [List.cons_append,List.nil_append,parseValueFuel]
    apply (qualify_exact _ (.object []) remaining).mpr
    exact ⟨by rw [decoded]; rfl,boundary⟩

theorem array_complete (left text right : List Nat) (values : List RawValue)
    (wl : WhiteSpace left) (wr : WhiteSpace right) (items : ItemsComplete text values) :
    ValueComplete ([91]++left++text++right++[93]) (.array values) := by
  intro remaining fuel bound boundary
  cases fuel with
  | zero => omega
  | succ fuel =>
    have bodyBound : 2*(left++text++right++[93]).length < fuel := by
      simp only [List.length_append,List.length_singleton] at bound ⊢; omega
    have decoded := items left right remaining fuel true wl wr bodyBound
    simp only [List.cons_append,List.nil_append,parseValueFuel]
    apply (qualify_exact _ (.array values) remaining).mpr
    exact ⟨by rw [decoded]; rfl,boundary⟩

theorem object_complete (left text right : List Nat) (entries : List (List Nat × RawValue))
    (wl : WhiteSpace left) (wr : WhiteSpace right) (members : MembersComplete text entries) :
    ValueComplete ([123]++left++text++right++[125]) (.object entries) := by
  intro remaining fuel bound boundary
  cases fuel with
  | zero => omega
  | succ fuel =>
    have bodyBound : 2*(left++text++right++[125]).length < fuel := by
      simp only [List.length_append,List.length_singleton] at bound ⊢; omega
    have decoded := members left right remaining fuel true wl wr bodyBound
    simp only [List.cons_append,List.nil_append,parseValueFuel]
    apply (qualify_exact _ (.object entries) remaining).mpr
    exact ⟨by rw [decoded]; rfl,boundary⟩

theorem items_one_complete (word : List Nat) (value : RawValue) (meaning : ValueMeaning word value)
    (head : ValueComplete word value) : ItemsComplete word [value] := by
  intro left right remaining fuel allowEmpty wl wr bound
  cases fuel with
  | zero => omega
  | succ fuel =>
    have valueBound : 2*word.length < fuel := by
      simp only [List.length_append,List.length_singleton] at bound; omega
    have boundary := whitespace_value_boundary right remaining 93 wr (Or.inr (Or.inr (Or.inl rfl)))
    have parsed := head (right++[93]++remaining) fuel valueBound boundary
    have leading := scan_white_before_value left word (right++[93]++remaining) value wl meaning
    have trailing := scan_white_before_code right remaining 93 wr (by decide)
    rcases value_has_start word value meaning with ⟨first,tail,same,allowed⟩
    have noClose := (value_start_not_white_or_close first allowed).2.1
    rw [same] at parsed leading ⊢
    simp only [List.append_assoc,List.cons_append,List.nil_append] at parsed leading ⊢
    simp only [parseArrayFuel,leading,if_neg noClose]
    rw [parsed]
    simp only [Option.bind_some]
    simp only [List.append_assoc,List.cons_append,List.nil_append] at trailing
    rw [trailing]; rfl

theorem items_cons_complete (word before after tailWord : List Nat) (value : RawValue) (values : List RawValue)
    (meaning : ValueMeaning word value) (wb : WhiteSpace before) (wa : WhiteSpace after)
    (head : ValueComplete word value) (tailComplete : ItemsComplete tailWord values) :
    ItemsComplete (word++before++[44]++after++tailWord) (value::values) := by
  intro left right remaining fuel allowEmpty wl wr bound
  cases fuel with
  | zero => omega
  | succ fuel =>
    have valueBound : 2*word.length < fuel := by
      simp only [List.length_append,List.length_singleton] at bound; omega
    have tailBound : 2*(after++tailWord++right++[93]).length < fuel := by
      simp only [List.length_append,List.length_singleton] at bound ⊢; omega
    let suffix := after++tailWord++right++[93]++remaining
    have boundary := whitespace_value_boundary before suffix 44 wb (Or.inr (Or.inl rfl))
    have parsed := head (before++[44]++suffix) fuel valueBound boundary
    have leading := scan_white_before_value left word (before++[44]++suffix) value wl meaning
    have trailing := scan_white_before_code before suffix 44 wb (by decide)
    have tailParsed := tailComplete after right remaining fuel false wa wr tailBound
    change parseArrayFuel fuel suffix false = some (values,remaining) at tailParsed
    suffices result : parseArrayFuel (fuel+1) (left++word++before++[44]++suffix) allowEmpty = some (value::values,remaining) by
      simpa only [suffix,List.append_assoc] using result
    rcases value_has_start word value meaning with ⟨first,rest,same,allowed⟩
    have noClose := (value_start_not_white_or_close first allowed).2.1
    rw [same] at parsed leading ⊢
    simp only [List.append_assoc,List.cons_append,List.nil_append] at parsed leading ⊢
    simp only [parseArrayFuel,leading,if_neg noClose]
    rw [parsed]
    simp only [Option.bind_some]
    simp only [List.append_assoc,List.cons_append,List.nil_append] at trailing
    rw [trailing]
    simp only [show (44:Nat) ≠ 93 by decide,if_false]
    rw [tailParsed]; rfl

theorem object_member_prefix (fuel : Nat) (left key before after word suffix units : List Nat)
    (value : RawValue) (allowEmpty : Bool) (wl : WhiteSpace left) (name : StringMeaning key units)
    (wb : WhiteSpace before) (wa : WhiteSpace after) (meaning : ValueMeaning word value) :
    parseObjectFuel (fuel+1) (left++key++before++[58]++after++word++suffix) allowEmpty =
      (parseValueFuel fuel (word++suffix)).bind fun parsed =>
        match (scanWhitespace parsed.2).2 with
        | [] => none
        | delimiter::remaining =>
          if delimiter = 125 then some ([(units,parsed.1)],remaining)
          else if delimiter = 44 then (parseObjectFuel fuel remaining false).bind fun rest =>
            some ((units,parsed.1)::rest.1,rest.2)
          else none := by
  let afterKey := before++[58]++after++word++suffix
  let afterColon := after++word++suffix
  have leading := scan_white_before_string left key afterKey units wl name
  have quoted := (decode_quoted_exact (key++afterKey) units afterKey).mpr ⟨key,rfl,name⟩
  have beforeScan := scan_white_before_code before afterColon 58 wb (by decide)
  have afterScan := scan_white_before_value after word suffix value wa meaning
  rcases string_starts_quote key units name with ⟨tail,same⟩
  suffices result : parseObjectFuel (fuel+1) (left++key++afterKey) allowEmpty = _ by
    simpa only [afterKey,List.append_assoc] using result
  rw [same] at leading quoted ⊢
  simp only [List.append_assoc,List.cons_append] at leading quoted ⊢
  simp only [parseObjectFuel,leading,if_neg (by decide : (34:Nat) ≠ 125)]
  rw [quoted]
  simp only [Option.bind_some]
  have beforeScan' : scanWhitespace afterKey = (before,58::afterColon) := by
    simpa only [afterKey,afterColon,List.append_assoc] using beforeScan
  rw [beforeScan']
  simp only [takeWord,ite_true,Option.bind_some]
  rw [afterScan]
  rfl

theorem members_one_complete (key before after word units : List Nat) (value : RawValue)
    (name : StringMeaning key units) (wb : WhiteSpace before) (wa : WhiteSpace after)
    (meaning : ValueMeaning word value) (head : ValueComplete word value) :
    MembersComplete (key++before++[58]++after++word) [(units,value)] := by
  intro left right remaining fuel allowEmpty wl wr bound
  cases fuel with
  | zero => omega
  | succ fuel =>
    have valueBound : 2*word.length < fuel := by
      simp only [List.length_append,List.length_singleton] at bound; omega
    let suffix := right++[125]++remaining
    have boundary := whitespace_value_boundary right remaining 125 wr (Or.inr (Or.inr (Or.inr rfl)))
    have parsed := head suffix fuel valueBound boundary
    have trailing := scan_white_before_code right remaining 125 wr (by decide)
    suffices result : parseObjectFuel (fuel+1) (left++key++before++[58]++after++word++suffix) allowEmpty = some ([(units,value)],remaining) by
      simpa only [suffix,List.append_assoc] using result
    rw [object_member_prefix fuel left key before after word suffix units value allowEmpty wl name wb wa meaning,parsed]
    simp only [Option.bind_some]
    change scanWhitespace suffix = _ at trailing
    rw [trailing]; rfl

theorem members_cons_complete (key before after word beforeComma afterComma tailWord units : List Nat)
    (value : RawValue) (entries : List (List Nat × RawValue))
    (name : StringMeaning key units) (wb : WhiteSpace before) (wa : WhiteSpace after)
    (meaning : ValueMeaning word value) (wc : WhiteSpace beforeComma) (wt : WhiteSpace afterComma)
    (head : ValueComplete word value) (tailComplete : MembersComplete tailWord entries) :
    MembersComplete (key++before++[58]++after++word++beforeComma++[44]++afterComma++tailWord) ((units,value)::entries) := by
  intro left right remaining fuel allowEmpty wl wr bound
  cases fuel with
  | zero => omega
  | succ fuel =>
    have valueBound : 2*word.length < fuel := by
      simp only [List.length_append,List.length_singleton] at bound; omega
    have tailBound : 2*(afterComma++tailWord++right++[125]).length < fuel := by
      simp only [List.length_append,List.length_singleton] at bound ⊢; omega
    let tailInput := afterComma++tailWord++right++[125]++remaining
    let suffix := beforeComma++[44]++tailInput
    have boundary := whitespace_value_boundary beforeComma tailInput 44 wc (Or.inr (Or.inl rfl))
    have parsed := head suffix fuel valueBound boundary
    have trailing := scan_white_before_code beforeComma tailInput 44 wc (by decide)
    have tailParsed := tailComplete afterComma right remaining fuel false wt wr tailBound
    change parseObjectFuel fuel tailInput false = some (entries,remaining) at tailParsed
    suffices result : parseObjectFuel (fuel+1) (left++key++before++[58]++after++word++suffix) allowEmpty = some ((units,value)::entries,remaining) by
      simpa only [suffix,tailInput,List.append_assoc] using result
    rw [object_member_prefix fuel left key before after word suffix units value allowEmpty wl name wb wa meaning,parsed]
    simp only [Option.bind_some]
    change scanWhitespace suffix = _ at trailing
    rw [trailing]
    simp only [show (44:Nat) ≠ 125 by decide,if_false]
    rw [tailParsed]; rfl

#print axioms primitive_complete
#print axioms empty_array_body_complete
#print axioms empty_object_body_complete
#print axioms empty_array_complete
#print axioms empty_object_complete
#print axioms array_complete
#print axioms object_complete
#print axioms items_one_complete
#print axioms items_cons_complete
#print axioms object_member_prefix
#print axioms members_one_complete
#print axioms members_cons_complete
end RelationalSuccessor.CandidateJsonCompleteness
