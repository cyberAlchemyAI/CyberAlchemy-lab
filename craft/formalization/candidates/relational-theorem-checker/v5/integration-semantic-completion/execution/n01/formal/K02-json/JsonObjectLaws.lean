import ClosedJsonObject

set_option autoImplicit false

namespace RelationalSuccessor.CandidateJsonSource

theorem required_field_present (entries : Entries) (required : List String)
    (values : List Value) (represented : FieldsMeaning entries required values)
    (key : String) (requiredKey : key ∈ required) : ∃ value, (key, value) ∈ entries := by
  induction required generalizing values with
  | nil => simp at requiredKey
  | cons first rest ih =>
    rcases represented with ⟨value, tail, member, meaning, same⟩
    simp only [List.mem_cons] at requiredKey
    rcases requiredKey with head | later
    · subst key; exact ⟨value, member⟩
    · exact ih tail meaning later

theorem missing_key_refuses (required : List String) (entries : Entries) (key : String)
    (requiredKey : key ∈ required) (missing : ∀ value, (key, value) ∉ entries) :
    decodeObject required (.object entries) = none := by
  cases found : decodeObject required (.object entries) with
  | none => rfl
  | some values =>
    rcases (decode_object_exact required (.object entries) values).mp found with
      ⟨actual, same, represented⟩
    cases same
    rcases required_field_present entries required values represented.fields key requiredKey with
      ⟨value, member⟩
    exact False.elim (missing value member)

def SameEntries (a b : Entries) : Prop :=
  ∀ key value, (key, value) ∈ a ↔ (key, value) ∈ b

theorem fields_meaning_transfer (a b : Entries) (same : SameEntries a b)
    (required : List String) (values : List Value) (represented : FieldsMeaning a required values) :
    FieldsMeaning b required values := by
  induction required generalizing values with
  | nil => exact represented
  | cons key keys ih =>
    rcases represented with ⟨value, rest, member, meaning, equal⟩
    exact ⟨value, rest, (same key value).mp member, ih rest meaning, equal⟩

theorem object_meaning_transfer (a b : Entries) (same : SameEntries a b)
    (unique : (b.map Prod.fst).Nodup) (required : List String) (values : List Value)
    (represented : ObjectMeaning required a values) : ObjectMeaning required b values := by
  refine ⟨represented.requiredUnique, unique, ?_,
    fields_meaning_transfer a b same required values represented.fields⟩
  intro entry member
  exact represented.closed entry ((same entry.1 entry.2).mpr member)

theorem reordering_preserves_decoding (a b : Entries) (same : SameEntries a b)
    (uniqueA : (a.map Prod.fst).Nodup) (uniqueB : (b.map Prod.fst).Nodup)
    (required : List String) (values : List Value) :
    decodeObject required (.object a) = some values ↔
      decodeObject required (.object b) = some values := by
  constructor
  · intro decoded
    rcases (decode_object_exact required (.object a) values).mp decoded with
      ⟨actual, equal, represented⟩
    cases equal
    exact (decode_object_exact required (.object b) values).mpr
      ⟨b, rfl, object_meaning_transfer a b same uniqueB required values represented⟩
  · intro decoded
    rcases (decode_object_exact required (.object b) values).mp decoded with
      ⟨actual, equal, represented⟩
    cases equal
    exact (decode_object_exact required (.object a) values).mpr
      ⟨a, rfl, object_meaning_transfer b a (fun key value => (same key value).symm)
        uniqueA required values represented⟩

#print axioms required_field_present
#print axioms missing_key_refuses
#print axioms fields_meaning_transfer
#print axioms object_meaning_transfer
#print axioms reordering_preserves_decoding
end RelationalSuccessor.CandidateJsonSource
