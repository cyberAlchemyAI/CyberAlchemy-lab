import JsonElements
import IntentRecordShape

set_option autoImplicit false

namespace RelationalSuccessor.CandidateJsonSource
open RelationalSuccessor.CandidateIntentSource (RawPayload)

def payloadKeys : List String :=
  ["intent_ref", "owner_decision_ref", "selected_subject_refs",
   "satisfaction_test_refs", "excluded_subject_refs"]

def PayloadFieldsMeaning (values : List Value) (raw : RawPayload) : Prop :=
  ∃ selected tests excluded,
    values = [.string raw.intent_ref, .string raw.owner_decision_ref, selected, tests, excluded] ∧
    StringArrayMeaning selected raw.selected_subject_refs ∧
    StringArrayMeaning tests raw.satisfaction_test_refs ∧
    StringArrayMeaning excluded raw.excluded_subject_refs

def decodePayloadFields : List Value → Option RawPayload
  | [.string intent, .string decision, selected, tests, excluded] =>
      match decodeStringArray selected, decodeStringArray tests, decodeStringArray excluded with
      | some selectedRefs, some testRefs, some excludedRefs =>
          some ⟨intent, decision, selectedRefs, testRefs, excludedRefs⟩
      | _, _, _ => none
  | _ => none

theorem decode_payload_fields_exact (values : List Value) (raw : RawPayload) :
    decodePayloadFields values = some raw ↔ PayloadFieldsMeaning values raw := by
  constructor
  · intro decoded
    unfold decodePayloadFields at decoded
    split at decoded
    · rename_i intent decision selected tests excluded
      cases hs : decodeStringArray selected with
      | none => simp [hs] at decoded
      | some selectedRefs =>
        cases ht : decodeStringArray tests with
        | none => simp [hs, ht] at decoded
        | some testRefs =>
          cases he : decodeStringArray excluded with
          | none => simp [hs, ht, he] at decoded
          | some excludedRefs =>
            have equal : (⟨intent, decision, selectedRefs, testRefs, excludedRefs⟩ : RawPayload) = raw :=
              by simpa [hs, ht, he] using decoded
            cases equal
            exact ⟨selected, tests, excluded, rfl,
              (decode_string_array_exact selected selectedRefs).mp hs,
              (decode_string_array_exact tests testRefs).mp ht,
              (decode_string_array_exact excluded excludedRefs).mp he⟩
    · cases decoded
  · rintro ⟨selected, tests, excluded, same, hs, ht, he⟩
    have selectedDecoded := (decode_string_array_exact selected raw.selected_subject_refs).mpr hs
    have testsDecoded := (decode_string_array_exact tests raw.satisfaction_test_refs).mpr ht
    have excludedDecoded := (decode_string_array_exact excluded raw.excluded_subject_refs).mpr he
    simp [decodePayloadFields, same, selectedDecoded, testsDecoded, excludedDecoded]

def PayloadAstMeaning (value : Value) (raw : RawPayload) : Prop :=
  ∃ values, ObjectValueMeaning payloadKeys value values ∧ PayloadFieldsMeaning values raw

def decodePayload (value : Value) : Option RawPayload :=
  match decodeObject payloadKeys value with
  | some values => decodePayloadFields values
  | none => none

theorem decode_payload_ast_exact (value : Value) (raw : RawPayload) :
    decodePayload value = some raw ↔ PayloadAstMeaning value raw := by
  cases found : decodeObject payloadKeys value with
  | none =>
    constructor
    · simp [decodePayload, found]
    · rintro ⟨values, represented, fields⟩
      have contradiction := (decode_object_exact payloadKeys value values).mpr represented
      simp [found] at contradiction
  | some values =>
    constructor
    · intro decoded
      have fields : decodePayloadFields values = some raw := by simpa [decodePayload, found] using decoded
      exact ⟨values, (decode_object_exact payloadKeys value values).mp found,
        (decode_payload_fields_exact values raw).mp fields⟩
    · rintro ⟨actual, represented, fields⟩
      have equal := (decode_object_exact payloadKeys value actual).mpr represented
      rw [found] at equal
      cases equal
      simpa [decodePayload, found] using (decode_payload_fields_exact values raw).mpr fields

#print axioms decode_payload_fields_exact
#print axioms decode_payload_ast_exact
end RelationalSuccessor.CandidateJsonSource
