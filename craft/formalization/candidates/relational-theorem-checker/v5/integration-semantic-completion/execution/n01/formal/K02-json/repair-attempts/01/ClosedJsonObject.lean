set_option autoImplicit false

namespace RelationalSuccessor.CandidateJsonSource

-- Objects retain their raw ordered entries, including duplicate keys. Numbers
-- retain a lexical token; syntax validation belongs to the byte-parser premise.
-- No object-map conversion may erase duplicate keys before this adapter.
inductive Value where
  | null
  | boolean (value : Bool)
  | number (token : String)
  | string (value : String)
  | array (values : List Value)
  | object (entries : List (String × Value))
  deriving Repr

abbrev Entries := List (String × Value)

def lookup : Entries → String → Option Value
  | [], _ => none
  | (key, value) :: rest, wanted =>
      if key = wanted then some value else lookup rest wanted

theorem lookup_sound (entries : Entries) (key : String) (value : Value)
    (found : lookup entries key = some value) : (key, value) ∈ entries := by
  induction entries with
  | nil => simp [lookup] at found
  | cons first rest ih =>
    rcases first with ⟨firstKey, firstValue⟩
    unfold lookup at found
    split at found
    · rename_i same; cases found; simp [same]
    · exact List.mem_cons_of_mem _ (ih found)

theorem lookup_complete (entries : Entries) (key : String) (value : Value)
    (unique : (entries.map Prod.fst).Nodup) (member : (key, value) ∈ entries) :
    lookup entries key = some value := by
  induction entries with
  | nil => simp at member
  | cons first rest ih =>
    rcases first with ⟨firstKey, firstValue⟩
    simp only [List.map_cons, List.nodup_cons] at unique
    simp only [List.mem_cons] at member
    rcases member with head | tail
    · cases head; simp [lookup]
    · have notHead : firstKey ≠ key := by
        intro same
        have mapped : key ∈ rest.map Prod.fst := List.mem_map_of_mem tail
        exact unique.1 (by simpa [same] using mapped)
      simp only [lookup, if_neg notHead]
      exact ih unique.2 tail

-- Independent denotation: required keys select exact values from retained raw
-- entries in schema order. This proposition does not call lookup or decoding.
def FieldsMeaning (entries : Entries) : List String → List Value → Prop
  | [], values => values = []
  | key :: keys, values => ∃ value rest,
      (key, value) ∈ entries ∧ FieldsMeaning entries keys rest ∧ values = value :: rest

def decodeFields (entries : Entries) : List String → Option (List Value)
  | [] => some []
  | key :: keys =>
      match lookup entries key, decodeFields entries keys with
      | some value, some rest => some (value :: rest)
      | _, _ => none

theorem decode_fields_exact (entries : Entries) (keys : List String) (values : List Value)
    (unique : (entries.map Prod.fst).Nodup) :
    decodeFields entries keys = some values ↔ FieldsMeaning entries keys values := by
  induction keys generalizing values with
  | nil => simp [decodeFields, FieldsMeaning, eq_comm]
  | cons key keys ih =>
    constructor
    · intro decoded
      unfold decodeFields at decoded
      cases head : lookup entries key with
      | none => simp [head] at decoded
      | some value =>
        cases tail : decodeFields entries keys with
        | none => simp [head, tail] at decoded
        | some rest =>
          have equal : value :: rest = values := by simpa [head, tail] using decoded
          exact ⟨value, rest, lookup_sound entries key value head,
            (ih rest).mp tail, equal.symm⟩
    · rintro ⟨value, rest, member, meaning, equal⟩
      have head := lookup_complete entries key value unique member
      have tail := (ih rest).mpr meaning
      simp [decodeFields, head, tail, equal]

structure ObjectMeaning (required : List String) (entries : Entries) (values : List Value) : Prop where
  requiredUnique : required.Nodup
  keysUnique : (entries.map Prod.fst).Nodup
  closed : ∀ entry ∈ entries, entry.1 ∈ required
  fields : FieldsMeaning entries required values

def keysCheck (required : List String) (entries : Entries) : Bool :=
  decide required.Nodup && decide (entries.map Prod.fst).Nodup &&
  entries.all (fun entry => decide (entry.1 ∈ required))

theorem keys_check_exact (required : List String) (entries : Entries) :
    keysCheck required entries = true ↔
      required.Nodup ∧ (entries.map Prod.fst).Nodup ∧
      (∀ entry ∈ entries, entry.1 ∈ required) := by
  simp only [keysCheck, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, and_assoc]

def decodeObject (required : List String) (value : Value) : Option (List Value) :=
  match value with
  | .object entries => if keysCheck required entries then decodeFields entries required else none
  | _ => none

def ObjectValueMeaning (required : List String) (value : Value) (values : List Value) : Prop :=
  ∃ entries, value = .object entries ∧ ObjectMeaning required entries values

theorem decode_object_exact (required : List String) (value : Value) (values : List Value) :
    decodeObject required value = some values ↔ ObjectValueMeaning required value values := by
  cases value with
  | object entries =>
    have representation : ObjectValueMeaning required (.object entries) values ↔
        ObjectMeaning required entries values := by
      constructor
      · rintro ⟨actual, same, meaning⟩; cases same; exact meaning
      · intro meaning; exact ⟨entries, rfl, meaning⟩
    rw [representation]
    unfold decodeObject
    split
    · rename_i checked
      have keys := (keys_check_exact required entries).mp checked
      rw [decode_fields_exact entries required values keys.2.1]
      exact ⟨fun fields => ⟨keys.1, keys.2.1, keys.2.2, fields⟩,
        fun meaning => meaning.fields⟩
    · rename_i unchecked
      constructor
      · intro impossible; cases impossible
      · intro meaning
        exact False.elim (unchecked ((keys_check_exact required entries).mpr
          ⟨meaning.requiredUnique, meaning.keysUnique, meaning.closed⟩))
  | null => simp [decodeObject, ObjectValueMeaning]
  | boolean value => simp [decodeObject, ObjectValueMeaning]
  | number token => simp [decodeObject, ObjectValueMeaning]
  | string value => simp [decodeObject, ObjectValueMeaning]
  | array values => simp [decodeObject, ObjectValueMeaning]

theorem duplicate_keys_refuse (required : List String) (entries : Entries)
    (duplicates : ¬ (entries.map Prod.fst).Nodup) :
    decodeObject required (.object entries) = none := by
  have rejected : keysCheck required entries ≠ true :=
    fun checked => duplicates ((keys_check_exact required entries).mp checked).2.1
  simp [decodeObject, rejected]

theorem extra_key_refuses (required : List String) (entries : Entries) (entry : String × Value)
    (member : entry ∈ entries) (extra : entry.1 ∉ required) :
    decodeObject required (.object entries) = none := by
  have rejected : keysCheck required entries ≠ true :=
    fun checked => extra (((keys_check_exact required entries).mp checked).2.2 entry member)
  simp [decodeObject, rejected]

theorem fields_meaning_length (entries : Entries) (keys : List String) (values : List Value)
    (meaning : FieldsMeaning entries keys values) : values.length = keys.length := by
  induction keys generalizing values with
  | nil => simp [FieldsMeaning] at meaning; simp [meaning]
  | cons key keys ih =>
    rcases meaning with ⟨value, rest, member, tail, equal⟩
    simp [equal, ih rest tail]

#print axioms lookup_sound
#print axioms lookup_complete
#print axioms decode_fields_exact
#print axioms keys_check_exact
#print axioms decode_object_exact
#print axioms duplicate_keys_refuse
#print axioms extra_key_refuses
#print axioms fields_meaning_length
end RelationalSuccessor.CandidateJsonSource
