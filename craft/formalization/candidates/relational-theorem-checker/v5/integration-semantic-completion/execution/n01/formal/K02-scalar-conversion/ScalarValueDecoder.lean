import ScalarValueMeaning
set_option autoImplicit false
namespace RelationalSuccessor.CandidateScalarConversion
open CandidateJsonBytes (RawValue)

mutual
  def convertValue : RawValue → Option CandidateJsonSource.Value
    | .null => some .null
    | .boolean value => some (.boolean value)
    | .number token => some (.number token)
    | .string units => (decodeString units).map CandidateJsonSource.Value.string
    | .array values => (convertValues values).map CandidateJsonSource.Value.array
    | .object entries => (convertEntries entries).map CandidateJsonSource.Value.object
  termination_by raw => sizeOf raw
  def convertValues : List RawValue → Option (List CandidateJsonSource.Value)
    | [] => some []
    | raw::raws => (convertValue raw).bind (fun value =>
        (convertValues raws).bind (fun values => some (value::values)))
  termination_by raws => sizeOf raws
  def convertEntries : List (List Nat × RawValue) → Option CandidateJsonSource.Entries
    | [] => some []
    | (units,raw)::raws => (decodeString units).bind (fun key =>
        (convertValue raw).bind (fun value =>
          (convertEntries raws).bind (fun entries => some ((key,value)::entries))))
  termination_by raws => sizeOf raws
end

mutual
theorem convert_value_sound (raw : RawValue) (value : CandidateJsonSource.Value)
      (parsed : convertValue raw = some value) : ValueMeaning raw value := by
    cases raw with
    | null => simp only [convertValue,Option.some.injEq] at parsed; subst value; exact .null
    | boolean flag => simp only [convertValue,Option.some.injEq] at parsed; subst value; exact .boolean flag
    | number token => simp only [convertValue,Option.some.injEq] at parsed; subst value; exact .number token
    | string units =>
        simp only [convertValue] at parsed
        cases decoded : decodeString units with
        | none => simp [decoded] at parsed
        | some text =>
            simp only [decoded,Option.map_some,Option.some.injEq] at parsed; subst value
            exact .string units text (decode_string_sound units text decoded)
    | array raws =>
        simp only [convertValue] at parsed
        cases decoded : convertValues raws with
        | none => simp [decoded] at parsed
        | some values =>
            simp only [decoded,Option.map_some,Option.some.injEq] at parsed; subst value
            exact .array raws values (convert_values_sound raws values decoded)
    | object raws =>
        simp only [convertValue] at parsed
        cases decoded : convertEntries raws with
        | none => simp [decoded] at parsed
        | some entries =>
            simp only [decoded,Option.map_some,Option.some.injEq] at parsed; subst value
            exact .object raws entries (convert_entries_sound raws entries decoded)
  termination_by sizeOf raw
theorem convert_values_sound (raws : List RawValue) (values : List CandidateJsonSource.Value)
      (parsed : convertValues raws = some values) : ValuesMeaning raws values := by
    cases raws with
    | nil => simp only [convertValues,Option.some.injEq] at parsed; subst values; exact .nil
    | cons raw raws =>
        simp only [convertValues] at parsed
        cases head : convertValue raw with
        | none => simp [head] at parsed
        | some value =>
            simp only [head,Option.bind_some] at parsed
            cases tail : convertValues raws with
            | none => simp [tail] at parsed
            | some rest =>
                simp only [tail,Option.bind_some,Option.some.injEq] at parsed; subst values
                exact .cons raw value raws rest (convert_value_sound raw value head)
                  (convert_values_sound raws rest tail)
  termination_by sizeOf raws
theorem convert_entries_sound (raws : List (List Nat × RawValue)) (entries : CandidateJsonSource.Entries)
      (parsed : convertEntries raws = some entries) : EntriesMeaning raws entries := by
    cases raws with
    | nil => simp only [convertEntries,Option.some.injEq] at parsed; subst entries; exact .nil
    | cons first raws =>
        cases pairEq : first
        rename_i units raw
        rw [pairEq] at parsed
        simp only [convertEntries] at parsed
        cases name : decodeString units with
        | none => simp [name] at parsed
        | some key =>
            simp only [name,Option.bind_some] at parsed
            cases head : convertValue raw with
            | none => simp [head] at parsed
            | some value =>
                simp only [head,Option.bind_some] at parsed
                cases tail : convertEntries raws with
                | none => simp [tail] at parsed
                | some rest =>
                    simp only [tail,Option.bind_some,Option.some.injEq] at parsed; subst entries
                    exact .cons units key raw value raws rest (decode_string_sound units key name)
                      (convert_value_sound raw value head) (convert_entries_sound raws rest tail)
  termination_by sizeOf raws
  decreasing_by all_goals simp_all [List.cons.sizeOf_spec, Prod.mk.sizeOf_spec]; omega
end

mutual
theorem convert_value_complete (raw : RawValue) (value : CandidateJsonSource.Value)
      (meaning : ValueMeaning raw value) : convertValue raw = some value := by
    cases meaning with
    | null => simp only [convertValue]
    | boolean flag => simp only [convertValue]
    | number token => simp only [convertValue]
    | string units text meaning => simp only [convertValue,decode_string_complete units text meaning,Option.map_some]
    | array raws values meaning => simp only [convertValue,convert_values_complete raws values meaning,Option.map_some]
    | object raws entries meaning => simp only [convertValue,convert_entries_complete raws entries meaning,Option.map_some]
  termination_by sizeOf raw
theorem convert_values_complete (raws : List RawValue) (values : List CandidateJsonSource.Value)
      (meaning : ValuesMeaning raws values) : convertValues raws = some values := by
    cases meaning with
    | nil => simp only [convertValues]
    | cons raw value raws values head tail =>
        simp only [convertValues,convert_value_complete raw value head,Option.bind_some,
          convert_values_complete raws values tail]
  termination_by sizeOf raws
theorem convert_entries_complete (raws : List (List Nat × RawValue)) (entries : CandidateJsonSource.Entries)
      (meaning : EntriesMeaning raws entries) : convertEntries raws = some entries := by
    cases meaning with
    | nil => simp only [convertEntries]
    | cons units key raw value raws entries name head tail =>
        simp only [convertEntries,decode_string_complete units key name,Option.bind_some,
          convert_value_complete raw value head,convert_entries_complete raws entries tail]
  termination_by sizeOf raws
end

theorem convert_value_exact (raw : RawValue) (value : CandidateJsonSource.Value) :
    convertValue raw = some value ↔ ValueMeaning raw value :=
  ⟨convert_value_sound raw value,convert_value_complete raw value⟩

theorem convert_values_exact (raws : List RawValue) (values : List CandidateJsonSource.Value) :
    convertValues raws = some values ↔ ValuesMeaning raws values :=
  ⟨convert_values_sound raws values,convert_values_complete raws values⟩

theorem convert_entries_exact (raws : List (List Nat × RawValue)) (entries : CandidateJsonSource.Entries) :
    convertEntries raws = some entries ↔ EntriesMeaning raws entries :=
  ⟨convert_entries_sound raws entries,convert_entries_complete raws entries⟩

theorem converted_value_unique (raw : RawValue) (first second : CandidateJsonSource.Value)
    (a : ValueMeaning raw first) (b : ValueMeaning raw second) : first = second :=
  Option.some.inj ((convert_value_complete raw first a).symm.trans (convert_value_complete raw second b))

theorem conversion_none_exact (raw : RawValue) : convertValue raw = none ↔ ¬ ∃ value, ValueMeaning raw value := by
  constructor
  · intro refused; rintro ⟨value,meaning⟩
    have accepted := convert_value_complete raw value meaning
    rw [refused] at accepted; contradiction
  · intro invalid
    cases parsed : convertValue raw with
    | none => rfl
    | some value => exact False.elim (invalid ⟨value,convert_value_sound raw value parsed⟩)

theorem converted_array_length (raws : List RawValue) (values : List CandidateJsonSource.Value)
    (parsed : convertValues raws = some values) : raws.length = values.length :=
  values_meaning_length raws values (convert_values_sound raws values parsed)

theorem converted_entries_length (raws : List (List Nat × RawValue)) (entries : CandidateJsonSource.Entries)
    (parsed : convertEntries raws = some entries) : raws.length = entries.length :=
  entries_meaning_length raws entries (convert_entries_sound raws entries parsed)

theorem number_lexeme_preserved (token : String) : convertValue (.number token) = some (.number token) := by simp only [convertValue]

#print axioms convert_value_sound
#print axioms convert_values_sound
#print axioms convert_entries_sound
#print axioms convert_value_complete
#print axioms convert_values_complete
#print axioms convert_entries_complete
#print axioms convert_value_exact
#print axioms convert_values_exact
#print axioms convert_entries_exact
#print axioms converted_value_unique
#print axioms conversion_none_exact
#print axioms converted_array_length
#print axioms converted_entries_length
#print axioms number_lexeme_preserved
end RelationalSuccessor.CandidateScalarConversion
