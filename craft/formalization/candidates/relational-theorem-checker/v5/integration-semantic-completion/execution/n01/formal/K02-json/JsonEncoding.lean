import JsonRecord

set_option autoImplicit false

namespace RelationalSuccessor.CandidateJsonSource
open RelationalSuccessor.CandidateIntentRecordShape
open RelationalSuccessor.CandidateIntentSource (RawPayload)

theorem decode_elements_encoding {α : Type} (decode : Value → Option α) (encode : α → Value)
    (inverse : ∀ output, decode (encode output) = some output) (outputs : List α) :
    decodeElements decode (outputs.map encode) = some outputs := by
  induction outputs with
  | nil => rfl
  | cons output outputs ih => simp [decodeElements, inverse output, ih]

def encodeStringArray (values : List String) : Value := .array (values.map Value.string)

theorem decode_string_array_encoding (values : List String) :
    decodeStringArray (encodeStringArray values) = some values :=
  decode_elements_encoding decodeString Value.string (fun _ => rfl) values

def encodeReference (ref : RawRelationRef) : Value := .object
  [("relation_kind_ref", .string ref.relation_kind_ref), ("direction", .string ref.direction),
   ("counterpart_kind", .string ref.counterpart_kind), ("counterpart_ref", .string ref.counterpart_ref)]

theorem decode_reference_encoding (ref : RawRelationRef) :
    decodeReference (encodeReference ref) = some ref := by rfl

def encodeReferenceArray (refs : List RawRelationRef) : Value := .array (refs.map encodeReference)

theorem decode_reference_array_encoding (refs : List RawRelationRef) :
    decodeReferenceArray (encodeReferenceArray refs) = some refs :=
  decode_elements_encoding decodeReference encodeReference decode_reference_encoding refs

def encodePayload (raw : RawPayload) : Value := .object
  [("intent_ref", .string raw.intent_ref), ("owner_decision_ref", .string raw.owner_decision_ref),
   ("selected_subject_refs", encodeStringArray raw.selected_subject_refs),
   ("satisfaction_test_refs", encodeStringArray raw.satisfaction_test_refs),
   ("excluded_subject_refs", encodeStringArray raw.excluded_subject_refs)]

theorem decode_payload_encoding (raw : RawPayload) :
    decodePayload (encodePayload raw) = some raw := by
  change decodePayloadFields [.string raw.intent_ref, .string raw.owner_decision_ref,
    encodeStringArray raw.selected_subject_refs, encodeStringArray raw.satisfaction_test_refs,
    encodeStringArray raw.excluded_subject_refs] = some raw
  simp only [decodePayloadFields, decode_string_array_encoding]

def encodeRecord (raw : RawRecord) : Value := .object
  [("schema_version", .string raw.schema_version), ("node_id", .string raw.node_id),
   ("kind", .string raw.kind), ("name", .string raw.name),
   ("lifecycle_state", .string raw.lifecycle_state), ("authority_effect", .string raw.authority_effect),
   ("owner_ref", .string raw.owner_ref), ("scope_ref", .string raw.scope_ref),
   ("evidence_refs", encodeStringArray raw.evidence_refs), ("challenge_route", .string raw.challenge_route),
   ("successor_refs", encodeStringArray raw.successor_refs), ("relation_refs", encodeReferenceArray raw.relation_refs),
   ("payload", encodePayload raw.payload), ("claim_ceiling", .string raw.claim_ceiling)]

theorem decode_record_carrier_encoding (raw : RawRecord) :
    decodeRecordCarrier (encodeRecord raw) = some raw := by
  change decodeRecordFields [.string raw.schema_version, .string raw.node_id,
    .string raw.kind, .string raw.name, .string raw.lifecycle_state,
    .string raw.authority_effect, .string raw.owner_ref, .string raw.scope_ref,
    encodeStringArray raw.evidence_refs, .string raw.challenge_route,
    encodeStringArray raw.successor_refs, encodeReferenceArray raw.relation_refs,
    encodePayload raw.payload, .string raw.claim_ceiling] = some raw
  simp only [decodeRecordFields, decode_string_array_encoding,
    decode_reference_array_encoding, decode_payload_encoding]

theorem decode_schema_record_encoding (raw : RawRecord) (shape : RecordShape raw) :
    decodeRecord (encodeRecord raw) = some raw := by
  simpa only [decodeRecord, decode_record_carrier_encoding] using
    (check_carrier_exact raw raw).mpr ⟨shape, rfl⟩

#print axioms decode_elements_encoding
#print axioms decode_string_array_encoding
#print axioms decode_reference_encoding
#print axioms decode_reference_array_encoding
#print axioms decode_payload_encoding
#print axioms decode_record_carrier_encoding
#print axioms decode_schema_record_encoding
end RelationalSuccessor.CandidateJsonSource
