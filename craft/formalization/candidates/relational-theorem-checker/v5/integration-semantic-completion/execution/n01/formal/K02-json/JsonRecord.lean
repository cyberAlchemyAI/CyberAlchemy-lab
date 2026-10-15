import JsonReference
import JsonPayload

set_option autoImplicit false

namespace RelationalSuccessor.CandidateJsonSource
open RelationalSuccessor.CandidateIntentRecordShape

def recordKeys : List String :=
  ["schema_version", "node_id", "kind", "name", "lifecycle_state", "authority_effect",
   "owner_ref", "scope_ref", "evidence_refs", "challenge_route", "successor_refs",
   "relation_refs", "payload", "claim_ceiling"]

-- Every scalar and container is represented independently. Nested objects may
-- reorder unique fields; arrays retain positional correspondence at every level.
def RecordFieldsMeaning (values : List Value) (raw : RawRecord) : Prop :=
  ∃ evidence successors relations payload,
    values = [.string raw.schema_version, .string raw.node_id, .string raw.kind,
      .string raw.name, .string raw.lifecycle_state, .string raw.authority_effect,
      .string raw.owner_ref, .string raw.scope_ref, evidence, .string raw.challenge_route,
      successors, relations, payload, .string raw.claim_ceiling] ∧
    StringArrayMeaning evidence raw.evidence_refs ∧
    StringArrayMeaning successors raw.successor_refs ∧
    ReferenceArrayMeaning relations raw.relation_refs ∧ PayloadAstMeaning payload raw.payload

def decodeRecordFields : List Value → Option RawRecord
  | [.string schema, .string identity, .string kind, .string name,
      .string lifecycle, .string authority, .string owner, .string scope,
      evidence, .string challenge, successors, relations, payload, .string ceiling] =>
      match decodeStringArray evidence, decodeStringArray successors,
            decodeReferenceArray relations, decodePayload payload with
      | some evidenceRefs, some successorRefs, some relationRefs, some rawPayload =>
          some ⟨schema, identity, kind, name, lifecycle, authority, owner, scope,
            evidenceRefs, challenge, successorRefs, relationRefs, rawPayload, ceiling⟩
      | _, _, _, _ => none
  | _ => none

theorem decode_record_fields_exact (values : List Value) (raw : RawRecord) :
    decodeRecordFields values = some raw ↔ RecordFieldsMeaning values raw := by
  constructor
  · intro decoded
    unfold decodeRecordFields at decoded
    split at decoded
    · rename_i schema identity kind name lifecycle authority owner scope evidence
        challenge successors relations payload ceiling
      cases he : decodeStringArray evidence with
      | none => simp [he] at decoded
      | some evidenceRefs =>
        cases hs : decodeStringArray successors with
        | none => simp [he, hs] at decoded
        | some successorRefs =>
          cases hr : decodeReferenceArray relations with
          | none => simp [he, hs, hr] at decoded
          | some relationRefs =>
            cases hp : decodePayload payload with
            | none => simp [he, hs, hr, hp] at decoded
            | some rawPayload =>
              have equal : (⟨schema, identity, kind, name, lifecycle, authority, owner,
                  scope, evidenceRefs, challenge, successorRefs, relationRefs,
                  rawPayload, ceiling⟩ : RawRecord) = raw := by
                simpa [he, hs, hr, hp] using decoded
              cases equal
              exact ⟨evidence, successors, relations, payload, rfl,
                (decode_string_array_exact evidence evidenceRefs).mp he,
                (decode_string_array_exact successors successorRefs).mp hs,
                (decode_reference_array_exact relations relationRefs).mp hr,
                (decode_payload_ast_exact payload rawPayload).mp hp⟩
    · cases decoded
  · rintro ⟨evidence, successors, relations, payload, same, he, hs, hr, hp⟩
    have evidenceDecoded := (decode_string_array_exact evidence raw.evidence_refs).mpr he
    have successorsDecoded := (decode_string_array_exact successors raw.successor_refs).mpr hs
    have relationsDecoded := (decode_reference_array_exact relations raw.relation_refs).mpr hr
    have payloadDecoded := (decode_payload_ast_exact payload raw.payload).mpr hp
    simp [decodeRecordFields, same, evidenceDecoded, successorsDecoded,
      relationsDecoded, payloadDecoded]

def RecordAstMeaning (value : Value) (raw : RawRecord) : Prop :=
  ∃ values, ObjectValueMeaning recordKeys value values ∧ RecordFieldsMeaning values raw

def decodeRecordCarrier (value : Value) : Option RawRecord :=
  match decodeObject recordKeys value with
  | some values => decodeRecordFields values
  | none => none

theorem decode_record_carrier_exact (value : Value) (raw : RawRecord) :
    decodeRecordCarrier value = some raw ↔ RecordAstMeaning value raw := by
  cases found : decodeObject recordKeys value with
  | none =>
    constructor
    · simp [decodeRecordCarrier, found]
    · rintro ⟨values, represented, fields⟩
      have contradiction := (decode_object_exact recordKeys value values).mpr represented
      simp [found] at contradiction
  | some values =>
    constructor
    · intro decoded
      have fields : decodeRecordFields values = some raw := by
        simpa [decodeRecordCarrier, found] using decoded
      exact ⟨values, (decode_object_exact recordKeys value values).mp found,
        (decode_record_fields_exact values raw).mp fields⟩
    · rintro ⟨actual, represented, fields⟩
      have equal := (decode_object_exact recordKeys value actual).mpr represented
      rw [found] at equal
      cases equal
      simpa [decodeRecordCarrier, found] using (decode_record_fields_exact values raw).mpr fields

def SchemaAstMeaning (value : Value) (raw : RawRecord) : Prop :=
  RecordAstMeaning value raw ∧ RecordShape raw

def decodeRecord (value : Value) : Option RawRecord :=
  match decodeRecordCarrier value with
  | some raw => checkCarrier raw
  | none => none

theorem decode_record_exact (value : Value) (raw : RawRecord) :
    decodeRecord value = some raw ↔ SchemaAstMeaning value raw := by
  cases found : decodeRecordCarrier value with
  | none =>
    constructor
    · simp [decodeRecord, found]
    · intro represented
      have contradiction := (decode_record_carrier_exact value raw).mpr represented.1
      simp [found] at contradiction
  | some actual =>
    constructor
    · intro decoded
      have checked : checkCarrier actual = some raw := by simpa [decodeRecord, found] using decoded
      have shapeAndSame := (check_carrier_exact actual raw).mp checked
      refine ⟨?_, ?_⟩
      · simpa only [shapeAndSame.2] using (decode_record_carrier_exact value actual).mp found
      · simpa only [shapeAndSame.2] using shapeAndSame.1
    · intro represented
      have equal := (decode_record_carrier_exact value raw).mpr represented.1
      have same : actual = raw := Option.some.inj (found.symm.trans equal)
      have checked := (check_carrier_exact actual raw).mpr
        ⟨by simpa only [same] using represented.2, same⟩
      simpa [decodeRecord, found] using checked

#print axioms decode_record_fields_exact
#print axioms decode_record_carrier_exact
#print axioms decode_record_exact
end RelationalSuccessor.CandidateJsonSource
