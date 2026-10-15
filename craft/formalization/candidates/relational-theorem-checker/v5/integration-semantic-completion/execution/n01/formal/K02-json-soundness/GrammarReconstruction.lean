import RecursiveJsonParser
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonSoundness
open CandidateJsonBytes CandidateJsonTokens CandidateJsonParser

theorem whitespace_reconstruction (input : List Nat) :
    input = (scanWhitespace input).1 ++ (scanWhitespace input).2 ∧ WhiteSpace (scanWhitespace input).1 := by
  have meaning := (scan_whitespace_exact input (scanWhitespace input).1 (scanWhitespace input).2).mp rfl
  exact ⟨meaning.1,meaning.2.1⟩

theorem items_nonempty (word : List Nat) (values : List RawValue) (meaning : ItemsMeaning word values) :
    values ≠ [] := by
  cases meaning <;> simp

theorem members_nonempty (word : List Nat) (entries : List (List Nat × RawValue))
    (meaning : MembersMeaning word entries) : entries ≠ [] := by
  cases meaning <;> simp

theorem array_single_reconstruction (input left word right remaining : List Nat) (value : RawValue)
    (same : input = left ++ word ++ right ++ [93] ++ remaining)
    (wl : WhiteSpace left) (head : ValueMeaning word value) (wr : WhiteSpace right) :
    ArrayBodyMeaning input [value] remaining := by
  rw [same]
  exact .nonempty left word right remaining [value] wl (.one word value head) wr

theorem array_cons_reconstruction (input left word between tailInput remaining : List Nat)
    (value : RawValue) (values : List RawValue)
    (same : input = left ++ word ++ between ++ [44] ++ tailInput)
    (wl : WhiteSpace left) (head : ValueMeaning word value) (wb : WhiteSpace between)
    (tail : ArrayBodyMeaning tailInput values remaining) (nonempty : values ≠ []) :
    ArrayBodyMeaning input (value::values) remaining := by
  cases tail with
  | empty space remaining ws => exact False.elim (nonempty rfl)
  | nonempty tailLeft text tailRight remaining values wtl items wtr =>
    rw [same]
    have combined := ItemsMeaning.cons word between tailLeft text value values head wb wtl items
    have result := ArrayBodyMeaning.nonempty left (word++between++[44]++tailLeft++text)
      tailRight remaining (value::values) wl combined wtr
    simpa only [List.append_assoc] using result

theorem object_single_reconstruction (input left key beforeColon afterColon word right remaining units : List Nat)
    (value : RawValue)
    (same : input = left ++ key ++ beforeColon ++ [58] ++ afterColon ++ word ++ right ++ [125] ++ remaining)
    (wl : WhiteSpace left) (name : StringMeaning key units) (wb : WhiteSpace beforeColon)
    (wa : WhiteSpace afterColon) (head : ValueMeaning word value) (wr : WhiteSpace right) :
    ObjectBodyMeaning input [(units,value)] remaining := by
  rw [same]
  have member := MembersMeaning.one key beforeColon afterColon word units value name wb wa head
  have result := ObjectBodyMeaning.nonempty left (key++beforeColon++[58]++afterColon++word)
    right remaining [(units,value)] wl member wr
  simpa only [List.append_assoc] using result

theorem object_cons_reconstruction
    (input left key beforeColon afterColon word between tailInput remaining units : List Nat)
    (value : RawValue) (entries : List (List Nat × RawValue))
    (same : input = left ++ key ++ beforeColon ++ [58] ++ afterColon ++ word ++ between ++ [44] ++ tailInput)
    (wl : WhiteSpace left) (name : StringMeaning key units) (wb : WhiteSpace beforeColon)
    (wa : WhiteSpace afterColon) (head : ValueMeaning word value) (wc : WhiteSpace between)
    (tail : ObjectBodyMeaning tailInput entries remaining) (nonempty : entries ≠ []) :
    ObjectBodyMeaning input ((units,value)::entries) remaining := by
  cases tail with
  | empty space remaining ws => exact False.elim (nonempty rfl)
  | nonempty tailLeft text tailRight remaining entries wtl members wtr =>
    rw [same]
    have combined := MembersMeaning.cons key beforeColon afterColon word between tailLeft text units value entries
      name wb wa head wc wtl members
    have result := ObjectBodyMeaning.nonempty left
      (key++beforeColon++[58]++afterColon++word++between++[44]++tailLeft++text)
      tailRight remaining ((units,value)::entries) wl combined wtr
    simpa only [List.append_assoc] using result

#print axioms whitespace_reconstruction
#print axioms items_nonempty
#print axioms members_nonempty
#print axioms array_single_reconstruction
#print axioms array_cons_reconstruction
#print axioms object_single_reconstruction
#print axioms object_cons_reconstruction
end RelationalSuccessor.CandidateJsonSoundness
