import JsonElements
import IntentRecordShape

set_option autoImplicit false

namespace RelationalSuccessor.CandidateJsonSource
open RelationalSuccessor.CandidateIntentRecordShape

def referenceKeys : List String :=
  ["relation_kind_ref", "direction", "counterpart_kind", "counterpart_ref"]

def referenceValues (ref : RawRelationRef) : List Value :=
  [.string ref.relation_kind_ref, .string ref.direction,
   .string ref.counterpart_kind, .string ref.counterpart_ref]

def ReferenceMeaning (value : Value) (ref : RawRelationRef) : Prop :=
  ObjectValueMeaning referenceKeys value (referenceValues ref)

def decodeReferenceFields : List Value → Option RawRelationRef
  | [.string kind, .string direction, .string counterpartKind, .string counterpart] =>
      some ⟨kind, direction, counterpartKind, counterpart⟩
  | _ => none

theorem decode_reference_fields_exact (values : List Value) (ref : RawRelationRef) :
    decodeReferenceFields values = some ref ↔ values = referenceValues ref := by
  constructor
  · intro decoded
    unfold decodeReferenceFields at decoded
    split at decoded
    · cases decoded; rfl
    · cases decoded
  · intro same; rw [same]; rfl

def decodeReference (value : Value) : Option RawRelationRef :=
  match decodeObject referenceKeys value with
  | some values => decodeReferenceFields values
  | none => none

theorem decode_reference_exact (value : Value) (ref : RawRelationRef) :
    decodeReference value = some ref ↔ ReferenceMeaning value ref := by
  rw [ReferenceMeaning, ← decode_object_exact]
  cases found : decodeObject referenceKeys value with
  | none => simp [decodeReference, found]
  | some values => simp [decodeReference, found, decode_reference_fields_exact]

def ReferenceArrayMeaning (value : Value) (refs : List RawRelationRef) : Prop :=
  ∃ values, value = .array values ∧ ElementsMeaning ReferenceMeaning values refs

def decodeReferenceArray : Value → Option (List RawRelationRef)
  | .array values => decodeElements decodeReference values
  | _ => none

theorem decode_reference_array_exact (value : Value) (refs : List RawRelationRef) :
    decodeReferenceArray value = some refs ↔ ReferenceArrayMeaning value refs := by
  cases value with
  | array values =>
    simp only [decodeReferenceArray]
    rw [decode_elements_exact decodeReference ReferenceMeaning decode_reference_exact]
    constructor
    · intro represented; exact ⟨values, rfl, represented⟩
    · rintro ⟨actual, same, represented⟩; cases same; exact represented
  | null => simp [decodeReferenceArray, ReferenceArrayMeaning]
  | boolean value => simp [decodeReferenceArray, ReferenceArrayMeaning]
  | number token => simp [decodeReferenceArray, ReferenceArrayMeaning]
  | string value => simp [decodeReferenceArray, ReferenceArrayMeaning]
  | object entries => simp [decodeReferenceArray, ReferenceArrayMeaning]

#print axioms decode_reference_fields_exact
#print axioms decode_reference_exact
#print axioms decode_reference_array_exact
end RelationalSuccessor.CandidateJsonSource
