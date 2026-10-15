import ScalarStringDecoder
set_option autoImplicit false
namespace RelationalSuccessor.CandidateScalarConversion
open CandidateJsonBytes (RawValue)

mutual
  inductive ValueMeaning : RawValue → CandidateJsonSource.Value → Prop
    | null : ValueMeaning .null .null
    | boolean (value : Bool) : ValueMeaning (.boolean value) (.boolean value)
    | number (token : String) : ValueMeaning (.number token) (.number token)
    | string (units : List Nat) (text : String) (meaning : StringMeaning units text) :
        ValueMeaning (.string units) (.string text)
    | array (raw : List RawValue) (values : List CandidateJsonSource.Value)
        (meaning : ValuesMeaning raw values) : ValueMeaning (.array raw) (.array values)
    | object (raw : List (List Nat × RawValue)) (entries : CandidateJsonSource.Entries)
        (meaning : EntriesMeaning raw entries) : ValueMeaning (.object raw) (.object entries)
  inductive ValuesMeaning : List RawValue → List CandidateJsonSource.Value → Prop
    | nil : ValuesMeaning [] []
    | cons (raw : RawValue) (value : CandidateJsonSource.Value)
        (raws : List RawValue) (values : List CandidateJsonSource.Value)
        (head : ValueMeaning raw value) (tail : ValuesMeaning raws values) :
        ValuesMeaning (raw::raws) (value::values)
  inductive EntriesMeaning : List (List Nat × RawValue) → CandidateJsonSource.Entries → Prop
    | nil : EntriesMeaning [] []
    | cons (units : List Nat) (key : String) (raw : RawValue) (value : CandidateJsonSource.Value)
        (raws : List (List Nat × RawValue)) (entries : CandidateJsonSource.Entries)
        (name : StringMeaning units key) (head : ValueMeaning raw value) (tail : EntriesMeaning raws entries) :
        EntriesMeaning ((units,raw)::raws) ((key,value)::entries)
end

theorem values_meaning_length (raw : List RawValue) (values : List CandidateJsonSource.Value)
    (meaning : ValuesMeaning raw values) : raw.length = values.length := by
  cases meaning with
  | nil => rfl
  | cons raw value raws values head tail => simp only [List.length_cons,values_meaning_length raws values tail]
termination_by raw.length

theorem entries_meaning_length (raw : List (List Nat × RawValue)) (entries : CandidateJsonSource.Entries)
    (meaning : EntriesMeaning raw entries) : raw.length = entries.length := by
  cases meaning with
  | nil => rfl
  | cons units key raw value raws entries name head tail => simp only [List.length_cons,entries_meaning_length raws entries tail]
termination_by raw.length

theorem entries_meaning_member (raw : List (List Nat × RawValue)) (entries : CandidateJsonSource.Entries)
    (meaning : EntriesMeaning raw entries) (key : String) (value : CandidateJsonSource.Value)
    (member : (key,value) ∈ entries) :
    ∃ units source, (units,source) ∈ raw ∧ StringMeaning units key ∧ ValueMeaning source value := by
  cases meaning with
  | nil => simp at member
  | cons units name raw headValue raws entries keyMeaning head tail =>
      rcases List.mem_cons.mp member with same | inside
      · cases same; exact ⟨units,raw,List.mem_cons_self,keyMeaning,head⟩
      · rcases entries_meaning_member raws entries tail key value inside with ⟨units,source,member,keyMeaning,meaning⟩
        exact ⟨units,source,List.mem_cons_of_mem _ member,keyMeaning,meaning⟩

termination_by raw.length

#print axioms values_meaning_length
#print axioms entries_meaning_length
#print axioms entries_meaning_member
end RelationalSuccessor.CandidateScalarConversion
