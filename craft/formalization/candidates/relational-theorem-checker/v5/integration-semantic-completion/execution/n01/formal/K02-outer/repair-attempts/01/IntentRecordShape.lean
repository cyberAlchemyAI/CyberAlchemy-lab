import RawIntentPayload

set_option autoImplicit false

namespace RelationalSuccessor.CandidateIntentRecordShape
open RelationalSuccessor.CandidateIntentSource

-- This complete typed projection requires all source fields. Raw JSON parsing,
-- missing/extra fields, duplicate object keys and byte correspondence are later
-- adapter obligations; this carrier does not claim to check them.
structure RawRelationRef where
  relation_kind_ref : String
  direction : String
  counterpart_kind : String
  counterpart_ref : String
  deriving DecidableEq, Repr

structure RawRecord where
  schema_version : String
  node_id : String
  kind : String
  name : String
  lifecycle_state : String
  authority_effect : String
  owner_ref : String
  scope_ref : String
  evidence_refs : List String
  challenge_route : String
  successor_refs : List String
  relation_refs : List RawRelationRef
  payload : RawPayload
  claim_ceiling : String
  deriving DecidableEq, Repr

def NonemptyStrings (values : List String) : Prop :=
  ∀ value ∈ values, value ≠ ""

def stringListCheck (values : List String) : Bool :=
  values.all (fun value => decide (value ≠ ""))

theorem string_list_check_exact (values : List String) :
    stringListCheck values = true ↔ NonemptyStrings values := by
  simp only [stringListCheck, NonemptyStrings, List.all_eq_true, decide_eq_true_eq]

def RelationShape (ref : RawRelationRef) : Prop :=
  ref.relation_kind_ref ∈ ["relation.challenges", "relation.declares-effect-on", "relation.successor-of"] ∧
  ref.direction ∈ ["source", "target"] ∧
  ref.counterpart_kind ∈ ["challenge-event", "decision", "intent-resolution"] ∧
  ref.counterpart_ref ≠ ""

def relationShapeCheck (ref : RawRelationRef) : Bool :=
  decide (ref.relation_kind_ref ∈ ["relation.challenges", "relation.declares-effect-on", "relation.successor-of"]) &&
  decide (ref.direction ∈ ["source", "target"]) &&
  decide (ref.counterpart_kind ∈ ["challenge-event", "decision", "intent-resolution"]) &&
  decide (ref.counterpart_ref ≠ "")

theorem relation_shape_check_exact (ref : RawRelationRef) :
    relationShapeCheck ref = true ↔ RelationShape ref := by
  simp only [relationShapeCheck, RelationShape, Bool.and_eq_true, decide_eq_true_eq, and_assoc]

structure PayloadShape (raw : RawPayload) : Prop where
  intent : raw.intent_ref ≠ ""
  decision : raw.owner_decision_ref ≠ ""
  selected : NonemptyStrings raw.selected_subject_refs
  selectedDistinct : raw.selected_subject_refs.Nodup
  tests : NonemptyStrings raw.satisfaction_test_refs
  testsDistinct : raw.satisfaction_test_refs.Nodup
  excluded : NonemptyStrings raw.excluded_subject_refs
  excludedDistinct : raw.excluded_subject_refs.Nodup

def payloadShapeCheck (raw : RawPayload) : Bool :=
  decide (raw.intent_ref ≠ "") && decide (raw.owner_decision_ref ≠ "") &&
  stringListCheck raw.selected_subject_refs && decide raw.selected_subject_refs.Nodup &&
  stringListCheck raw.satisfaction_test_refs && decide raw.satisfaction_test_refs.Nodup &&
  stringListCheck raw.excluded_subject_refs && decide raw.excluded_subject_refs.Nodup

theorem payload_shape_check_exact (raw : RawPayload) :
    payloadShapeCheck raw = true ↔ PayloadShape raw := by
  have fields : PayloadShape raw ↔
      raw.intent_ref ≠ "" ∧ raw.owner_decision_ref ≠ "" ∧
      NonemptyStrings raw.selected_subject_refs ∧ raw.selected_subject_refs.Nodup ∧
      NonemptyStrings raw.satisfaction_test_refs ∧ raw.satisfaction_test_refs.Nodup ∧
      NonemptyStrings raw.excluded_subject_refs ∧ raw.excluded_subject_refs.Nodup := by
    constructor
    · intro h; exact ⟨h.intent, h.decision, h.selected, h.selectedDistinct,
        h.tests, h.testsDistinct, h.excluded, h.excludedDistinct⟩
    · rintro ⟨a, b, c, d, e, f, g, h⟩; exact ⟨a, b, c, d, e, f, g, h⟩
  rw [fields]
  simp only [payloadShapeCheck, Bool.and_eq_true, decide_eq_true_eq,
    string_list_check_exact, and_assoc]

structure RecordShape (raw : RawRecord) : Prop where
  schema : raw.schema_version = "cyberalchemy-lab-intent-resolution/v1"
  identity : raw.node_id ≠ ""
  kind : raw.kind = "intent-resolution"
  name : raw.name ≠ ""
  lifecycle : raw.lifecycle_state ∈ ["candidate", "active", "historical", "retired"]
  authority : raw.authority_effect = "none"
  owner : raw.owner_ref ≠ ""
  scope : raw.scope_ref ≠ ""
  evidence : NonemptyStrings raw.evidence_refs
  evidenceDistinct : raw.evidence_refs.Nodup
  challenge : raw.challenge_route ≠ ""
  successors : NonemptyStrings raw.successor_refs
  successorsDistinct : raw.successor_refs.Nodup
  relations : raw.relation_refs ≠ []
  relationShapes : ∀ ref ∈ raw.relation_refs, RelationShape ref
  payload : PayloadShape raw.payload
  ceiling : raw.claim_ceiling ≠ ""

def recordShapeCheck (raw : RawRecord) : Bool :=
  decide (raw.schema_version = "cyberalchemy-lab-intent-resolution/v1") &&
  decide (raw.node_id ≠ "") && decide (raw.kind = "intent-resolution") &&
  decide (raw.name ≠ "") &&
  decide (raw.lifecycle_state ∈ ["candidate", "active", "historical", "retired"]) &&
  decide (raw.authority_effect = "none") && decide (raw.owner_ref ≠ "") &&
  decide (raw.scope_ref ≠ "") && stringListCheck raw.evidence_refs &&
  decide raw.evidence_refs.Nodup && decide (raw.challenge_route ≠ "") &&
  stringListCheck raw.successor_refs && decide raw.successor_refs.Nodup &&
  decide (raw.relation_refs ≠ []) && raw.relation_refs.all relationShapeCheck &&
  payloadShapeCheck raw.payload && decide (raw.claim_ceiling ≠ "")

theorem record_shape_check_exact (raw : RawRecord) :
    recordShapeCheck raw = true ↔ RecordShape raw := by
  have fields : RecordShape raw ↔
      raw.schema_version = "cyberalchemy-lab-intent-resolution/v1" ∧
      raw.node_id ≠ "" ∧ raw.kind = "intent-resolution" ∧ raw.name ≠ "" ∧
      raw.lifecycle_state ∈ ["candidate", "active", "historical", "retired"] ∧
      raw.authority_effect = "none" ∧ raw.owner_ref ≠ "" ∧ raw.scope_ref ≠ "" ∧
      NonemptyStrings raw.evidence_refs ∧ raw.evidence_refs.Nodup ∧
      raw.challenge_route ≠ "" ∧ NonemptyStrings raw.successor_refs ∧
      raw.successor_refs.Nodup ∧ raw.relation_refs ≠ [] ∧
      (∀ ref ∈ raw.relation_refs, RelationShape ref) ∧ PayloadShape raw.payload ∧
      raw.claim_ceiling ≠ "" := by
    constructor
    · intro h; exact ⟨h.schema, h.identity, h.kind, h.name, h.lifecycle, h.authority,
        h.owner, h.scope, h.evidence, h.evidenceDistinct, h.challenge, h.successors,
        h.successorsDistinct, h.relations, h.relationShapes, h.payload, h.ceiling⟩
    · rintro ⟨a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q⟩
      exact ⟨a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q⟩
  rw [fields]
  simp only [recordShapeCheck, Bool.and_eq_true, decide_eq_true_eq,
    string_list_check_exact, List.all_eq_true, relation_shape_check_exact,
    payload_shape_check_exact, and_assoc]

-- Preserve the entire record. This gate neither resolves tokens nor issues an
-- authenticated semantic object. In particular it does not supply an owner.
def admit (raw : RawRecord) : Option RawRecord :=
  if recordShapeCheck raw then some raw else none

theorem admit_exact (raw accepted : RawRecord) :
    admit raw = some accepted ↔ RecordShape raw ∧ raw = accepted := by
  unfold admit
  split
  · rename_i checked
    simp only [Option.some.injEq]
    exact ⟨fun same => ⟨(record_shape_check_exact raw).mp checked, same⟩,
      fun h => h.2⟩
  · rename_i rejected
    constructor
    · intro impossible; cases impossible
    · intro valid; exact False.elim (rejected ((record_shape_check_exact raw).mpr valid.1))

theorem invalid_shape_refuses (raw : RawRecord) (invalid : ¬ RecordShape raw) :
    admit raw = none := by
  have rejected : recordShapeCheck raw ≠ true :=
    fun checked => invalid ((record_shape_check_exact raw).mp checked)
  simp [admit, rejected]

theorem successful_admission_preserves_every_field (raw accepted : RawRecord)
    (admitted : admit raw = some accepted) : accepted = raw :=
  ((admit_exact raw accepted).mp admitted).2.symm

theorem changed_authority_refuses (raw : RawRecord) (changed : raw.authority_effect ≠ "none") :
    admit raw = none := invalid_shape_refuses raw (fun valid => changed valid.authority)

theorem empty_owner_refuses (raw : RawRecord) (empty : raw.owner_ref = "") :
    admit raw = none := invalid_shape_refuses raw (fun valid => valid.owner empty)

theorem empty_relations_refuse (raw : RawRecord) (empty : raw.relation_refs = []) :
    admit raw = none := invalid_shape_refuses raw (fun valid => valid.relations empty)

theorem duplicate_selected_tokens_refuse (raw : RawRecord)
    (duplicates : ¬ raw.payload.selected_subject_refs.Nodup) :
    admit raw = none := invalid_shape_refuses raw (fun valid => duplicates valid.payload.selectedDistinct)

#print axioms string_list_check_exact
#print axioms relation_shape_check_exact
#print axioms payload_shape_check_exact
#print axioms record_shape_check_exact
#print axioms admit_exact
#print axioms invalid_shape_refuses
#print axioms successful_admission_preserves_every_field
#print axioms changed_authority_refuses
#print axioms empty_owner_refuses
#print axioms empty_relations_refuse
#print axioms duplicate_selected_tokens_refuse
end RelationalSuccessor.CandidateIntentRecordShape
