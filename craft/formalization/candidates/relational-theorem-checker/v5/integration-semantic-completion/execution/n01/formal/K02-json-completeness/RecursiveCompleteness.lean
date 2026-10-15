import CompletenessInterfaces
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonCompleteness
open CandidateJsonBytes CandidateJsonTokens CandidateJsonParser

theorem grammar_value_complete (word : List Nat) (value : RawValue) (meaning : ValueMeaning word value) : ValueComplete word value := by
  exact ValueMeaning.rec
    (motive_1 := fun word value _ => ValueComplete word value)
    (motive_2 := fun word values _ => ItemsComplete word values)
    (motive_3 := fun word entries _ => MembersComplete word entries)
    (primitive_complete _ .null (.literal _ .null .null))
    (primitive_complete _ (.boolean false) (.literal _ (.boolean false) .false))
    (primitive_complete _ (.boolean true) (.literal _ (.boolean true) .true))
    (fun token grammar => primitive_complete _ (.number token) (.number token grammar))
    (fun word units meaning => primitive_complete word (.string units) (.string word units meaning))
    (fun space ws => empty_array_complete space ws)
    (fun left text right values wl _ wr ih => array_complete left text right values wl wr ih)
    (fun space ws => empty_object_complete space ws)
    (fun left text right entries wl _ wr ih => object_complete left text right entries wl wr ih)
    (fun text value meaning ih => items_one_complete text value meaning ih)
    (fun text left right remaining value values head wl wr _ ihHead ihTail =>
      items_cons_complete text left right remaining value values head wl wr ihHead ihTail)
    (fun key left right text units value name wl wr meaning ih =>
      members_one_complete key left right text units value name wl wr meaning ih)
    (fun key left right text before after remaining units value entries name wl wr meaning wb wa _ ihHead ihTail =>
      members_cons_complete key left right text before after remaining units value entries name wl wr meaning wb wa ihHead ihTail)
    meaning

theorem grammar_items_complete (word : List Nat) (value : List RawValue) (meaning : ItemsMeaning word value) : ItemsComplete word value := by
  exact ItemsMeaning.rec
    (motive_1 := fun word value _ => ValueComplete word value)
    (motive_2 := fun word values _ => ItemsComplete word values)
    (motive_3 := fun word entries _ => MembersComplete word entries)
    (primitive_complete _ .null (.literal _ .null .null))
    (primitive_complete _ (.boolean false) (.literal _ (.boolean false) .false))
    (primitive_complete _ (.boolean true) (.literal _ (.boolean true) .true))
    (fun token grammar => primitive_complete _ (.number token) (.number token grammar))
    (fun word units meaning => primitive_complete word (.string units) (.string word units meaning))
    (fun space ws => empty_array_complete space ws)
    (fun left text right values wl _ wr ih => array_complete left text right values wl wr ih)
    (fun space ws => empty_object_complete space ws)
    (fun left text right entries wl _ wr ih => object_complete left text right entries wl wr ih)
    (fun text value meaning ih => items_one_complete text value meaning ih)
    (fun text left right remaining value values head wl wr _ ihHead ihTail =>
      items_cons_complete text left right remaining value values head wl wr ihHead ihTail)
    (fun key left right text units value name wl wr meaning ih =>
      members_one_complete key left right text units value name wl wr meaning ih)
    (fun key left right text before after remaining units value entries name wl wr meaning wb wa _ ihHead ihTail =>
      members_cons_complete key left right text before after remaining units value entries name wl wr meaning wb wa ihHead ihTail)
    meaning

theorem grammar_members_complete (word : List Nat) (value : List (List Nat × RawValue)) (meaning : MembersMeaning word value) : MembersComplete word value := by
  exact MembersMeaning.rec
    (motive_1 := fun word value _ => ValueComplete word value)
    (motive_2 := fun word values _ => ItemsComplete word values)
    (motive_3 := fun word entries _ => MembersComplete word entries)
    (primitive_complete _ .null (.literal _ .null .null))
    (primitive_complete _ (.boolean false) (.literal _ (.boolean false) .false))
    (primitive_complete _ (.boolean true) (.literal _ (.boolean true) .true))
    (fun token grammar => primitive_complete _ (.number token) (.number token grammar))
    (fun word units meaning => primitive_complete word (.string units) (.string word units meaning))
    (fun space ws => empty_array_complete space ws)
    (fun left text right values wl _ wr ih => array_complete left text right values wl wr ih)
    (fun space ws => empty_object_complete space ws)
    (fun left text right entries wl _ wr ih => object_complete left text right entries wl wr ih)
    (fun text value meaning ih => items_one_complete text value meaning ih)
    (fun text left right remaining value values head wl wr _ ihHead ihTail =>
      items_cons_complete text left right remaining value values head wl wr ihHead ihTail)
    (fun key left right text units value name wl wr meaning ih =>
      members_one_complete key left right text units value name wl wr meaning ih)
    (fun key left right text before after remaining units value entries name wl wr meaning wb wa _ ihHead ihTail =>
      members_cons_complete key left right text before after remaining units value entries name wl wr meaning wb wa ihHead ihTail)
    meaning

#print axioms grammar_value_complete
#print axioms grammar_items_complete
#print axioms grammar_members_complete
end RelationalSuccessor.CandidateJsonCompleteness
