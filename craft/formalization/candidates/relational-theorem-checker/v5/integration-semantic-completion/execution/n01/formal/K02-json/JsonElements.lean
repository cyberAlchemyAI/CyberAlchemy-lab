import ClosedJsonObject

set_option autoImplicit false

namespace RelationalSuccessor.CandidateJsonSource

-- Internal structural helper. Public record adapters fix the element decoder
-- and bind its equivalence to an independently specified element denotation.
def ElementsMeaning {α : Type} (meaning : Value → α → Prop) : List Value → List α → Prop
  | [], outputs => outputs = []
  | value :: values, outputs => ∃ output rest,
      meaning value output ∧ ElementsMeaning meaning values rest ∧ outputs = output :: rest

def decodeElements {α : Type} (decode : Value → Option α) : List Value → Option (List α)
  | [] => some []
  | value :: values =>
      match decode value, decodeElements decode values with
      | some output, some rest => some (output :: rest)
      | _, _ => none

theorem decode_elements_exact {α : Type} (decode : Value → Option α)
    (meaning : Value → α → Prop)
    (exactElement : ∀ value output, decode value = some output ↔ meaning value output)
    (values : List Value) (outputs : List α) :
    decodeElements decode values = some outputs ↔ ElementsMeaning meaning values outputs := by
  induction values generalizing outputs with
  | nil => simp [decodeElements, ElementsMeaning, eq_comm]
  | cons value values ih =>
    constructor
    · intro decoded
      unfold decodeElements at decoded
      cases head : decode value with
      | none => simp [head] at decoded
      | some output =>
        cases tail : decodeElements decode values with
        | none => simp [head, tail] at decoded
        | some rest =>
          have equal : output :: rest = outputs := by simpa [head, tail] using decoded
          exact ⟨output, rest, (exactElement value output).mp head,
            (ih rest).mp tail, equal.symm⟩
    · rintro ⟨output, rest, headMeaning, tailMeaning, equal⟩
      have head := (exactElement value output).mpr headMeaning
      have tail := (ih rest).mpr tailMeaning
      simp [decodeElements, head, tail, equal]

theorem elements_meaning_length {α : Type} (meaning : Value → α → Prop)
    (values : List Value) (outputs : List α) (represented : ElementsMeaning meaning values outputs) :
    outputs.length = values.length := by
  induction values generalizing outputs with
  | nil => simp [ElementsMeaning] at represented; simp [represented]
  | cons value values ih =>
    rcases represented with ⟨output, rest, head, tail, equal⟩
    simp [equal, ih rest tail]

theorem failed_element_refuses {α : Type} (decode : Value → Option α) (value : Value)
    (values : List Value) (failed : decode value = none) :
    decodeElements decode (value :: values) = none := by
  simp [decodeElements, failed]

theorem failed_tail_refuses {α : Type} (decode : Value → Option α) (value : Value)
    (values : List Value) (failed : decodeElements decode values = none) :
    decodeElements decode (value :: values) = none := by
  simp only [decodeElements, failed]
  cases decode value <;> rfl

def StringMeaning (value : Value) (output : String) : Prop := value = .string output

def decodeString : Value → Option String
  | .string output => some output
  | _ => none

theorem decode_string_exact (value : Value) (output : String) :
    decodeString value = some output ↔ StringMeaning value output := by
  cases value <;> simp [decodeString, StringMeaning]

def StringArrayMeaning (value : Value) (outputs : List String) : Prop :=
  ∃ values, value = .array values ∧ ElementsMeaning StringMeaning values outputs

def decodeStringArray : Value → Option (List String)
  | .array values => decodeElements decodeString values
  | _ => none

theorem decode_string_array_exact (value : Value) (outputs : List String) :
    decodeStringArray value = some outputs ↔ StringArrayMeaning value outputs := by
  cases value with
  | array values =>
    simp only [decodeStringArray]
    rw [decode_elements_exact decodeString StringMeaning decode_string_exact]
    constructor
    · intro represented; exact ⟨values, rfl, represented⟩
    · rintro ⟨actual, same, represented⟩; cases same; exact represented
  | null => simp [decodeStringArray, StringArrayMeaning]
  | boolean value => simp [decodeStringArray, StringArrayMeaning]
  | number token => simp [decodeStringArray, StringArrayMeaning]
  | string value => simp [decodeStringArray, StringArrayMeaning]
  | object entries => simp [decodeStringArray, StringArrayMeaning]

theorem decoded_string_array_length (values : List Value) (outputs : List String)
    (decoded : decodeStringArray (.array values) = some outputs) : outputs.length = values.length := by
  have represented := (decode_elements_exact decodeString StringMeaning decode_string_exact values outputs).mp decoded
  exact elements_meaning_length StringMeaning values outputs represented

#print axioms decode_elements_exact
#print axioms elements_meaning_length
#print axioms failed_element_refuses
#print axioms failed_tail_refuses
#print axioms decode_string_exact
#print axioms decode_string_array_exact
#print axioms decoded_string_array_length
end RelationalSuccessor.CandidateJsonSource
