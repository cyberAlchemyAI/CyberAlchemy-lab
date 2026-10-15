import BodyStringProfiles
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateTypedBodies

structure TIntent_current_output_hypothesis where
  artifact_type_ref : String
  description : String
  deriving DecidableEq, Repr

def TIntent_current_output_hypothesis.fields : CandidateBindingAst.Fields TIntent_current_output_hypothesis :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) CandidateBindingAst.empty))
    (fun p => TIntent_current_output_hypothesis.mk p.1 p.2.1)
def TIntent_current_output_hypothesis.rawDecoder : CandidateBindingAst.Decoder TIntent_current_output_hypothesis :=
  CandidateBindingAst.object ["artifact_type_ref","description"] TIntent_current_output_hypothesis.fields
def TIntent_current_output_hypothesis.Conditions (_value : TIntent_current_output_hypothesis) : Prop := True
instance : DecidablePred TIntent_current_output_hypothesis.Conditions := fun value => by
  unfold TIntent_current_output_hypothesis.Conditions
  infer_instance
def TIntent_current_output_hypothesis.decoder : CandidateBindingAst.Decoder TIntent_current_output_hypothesis :=
  constrained TIntent_current_output_hypothesis.rawDecoder TIntent_current_output_hypothesis.Conditions
def TIntent_current_output_hypothesis.Meaning (value : CandidateBindingAst.J) (output : TIntent_current_output_hypothesis) : Prop :=
  CandidateBindingAst.ObjectMeaning ["artifact_type_ref","description"] TIntent_current_output_hypothesis.fields value output ∧ TIntent_current_output_hypothesis.Conditions output
def TIntent_current_output_hypothesis.toAst (value : TIntent_current_output_hypothesis) : CandidateBindingAst.J :=
  .object [("artifact_type_ref",CandidateJsonSource.Value.string value.artifact_type_ref),("description",CandidateJsonSource.Value.string value.description)]

structure TIntent_revision_history_items where
  change_kind : String
  decision_ref : String
  rationale : String
  resulting_intent_refs : List (String)
  revision_id : String
  deriving DecidableEq, Repr

def TIntent_revision_history_items.fields : CandidateBindingAst.Fields TIntent_revision_history_items :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 0 none (some ["refined","split","renamed","rejected","reactivated"]) none) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 0 (some 100) true) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) CandidateBindingAst.empty)))))
    (fun p => TIntent_revision_history_items.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1)
def TIntent_revision_history_items.rawDecoder : CandidateBindingAst.Decoder TIntent_revision_history_items :=
  CandidateBindingAst.object ["change_kind","decision_ref","rationale","resulting_intent_refs","revision_id"] TIntent_revision_history_items.fields
def TIntent_revision_history_items.Conditions (_value : TIntent_revision_history_items) : Prop := True
instance : DecidablePred TIntent_revision_history_items.Conditions := fun value => by
  unfold TIntent_revision_history_items.Conditions
  infer_instance
def TIntent_revision_history_items.decoder : CandidateBindingAst.Decoder TIntent_revision_history_items :=
  constrained TIntent_revision_history_items.rawDecoder TIntent_revision_history_items.Conditions
def TIntent_revision_history_items.Meaning (value : CandidateBindingAst.J) (output : TIntent_revision_history_items) : Prop :=
  CandidateBindingAst.ObjectMeaning ["change_kind","decision_ref","rationale","resulting_intent_refs","revision_id"] TIntent_revision_history_items.fields value output ∧ TIntent_revision_history_items.Conditions output
def TIntent_revision_history_items.toAst (value : TIntent_revision_history_items) : CandidateBindingAst.J :=
  .object [("change_kind",CandidateJsonSource.Value.string value.change_kind),("decision_ref",CandidateJsonSource.Value.string value.decision_ref),("rationale",CandidateJsonSource.Value.string value.rationale),("resulting_intent_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.resulting_intent_refs),("revision_id",CandidateJsonSource.Value.string value.revision_id)]

structure TIntent where
  attributed_to : String
  authority_effect : String
  constraints : List (String)
  current_output_hypothesis : TIntent_current_output_hypothesis
  direction : String
  intent_state : String
  kind : String
  motivation : String
  node_id : String
  owner_ref : String
  review_route : String
  revision_history : List (TIntent_revision_history_items)
  revision_route : String
  satisfaction_refs : List (String)
  scope_ref : String
  status : String
  successor_refs : List (String)
  target_pressure : String
  deriving DecidableEq, Repr

def TIntent.fields : CandidateBindingAst.Fields TIntent :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 (some "none") none none) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 1 (some 100) true) (CandidateBindingAst.cons TIntent_current_output_hypothesis.decoder (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none (some ["proposed","active","satisfied","superseded","rejected"]) none) (CandidateBindingAst.cons (stringProfile 0 (some "intent") none none) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (boundedArray TIntent_revision_history_items.decoder 0 (some 100) false) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 0 (some 100) true) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 (some "candidate-unadmitted") none none) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 0 (some 100) true) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) CandidateBindingAst.empty))))))))))))))))))
    (fun p => TIntent.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1 p.2.2.2.2.2.1 p.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1)
def TIntent.rawDecoder : CandidateBindingAst.Decoder TIntent :=
  CandidateBindingAst.object ["attributed_to","authority_effect","constraints","current_output_hypothesis","direction","intent_state","kind","motivation","node_id","owner_ref","review_route","revision_history","revision_route","satisfaction_refs","scope_ref","status","successor_refs","target_pressure"] TIntent.fields
def TIntent.Conditions (value : TIntent) : Prop := (value.intent_state = "satisfied" → 1 ≤ value.satisfaction_refs.length) ∧ (value.intent_state = "superseded" → 1 ≤ value.successor_refs.length)
instance : DecidablePred TIntent.Conditions := fun value => by
  unfold TIntent.Conditions
  infer_instance
def TIntent.decoder : CandidateBindingAst.Decoder TIntent :=
  constrained TIntent.rawDecoder TIntent.Conditions
def TIntent.Meaning (value : CandidateBindingAst.J) (output : TIntent) : Prop :=
  CandidateBindingAst.ObjectMeaning ["attributed_to","authority_effect","constraints","current_output_hypothesis","direction","intent_state","kind","motivation","node_id","owner_ref","review_route","revision_history","revision_route","satisfaction_refs","scope_ref","status","successor_refs","target_pressure"] TIntent.fields value output ∧ TIntent.Conditions output
def TIntent.toAst (value : TIntent) : CandidateBindingAst.J :=
  .object [("attributed_to",CandidateJsonSource.Value.string value.attributed_to),("authority_effect",CandidateJsonSource.Value.string value.authority_effect),("constraints",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.constraints),("current_output_hypothesis",TIntent_current_output_hypothesis.toAst value.current_output_hypothesis),("direction",CandidateJsonSource.Value.string value.direction),("intent_state",CandidateJsonSource.Value.string value.intent_state),("kind",CandidateJsonSource.Value.string value.kind),("motivation",CandidateJsonSource.Value.string value.motivation),("node_id",CandidateJsonSource.Value.string value.node_id),("owner_ref",CandidateJsonSource.Value.string value.owner_ref),("review_route",CandidateJsonSource.Value.string value.review_route),("revision_history",(fun values => CandidateJsonSource.Value.array (values.map TIntent_revision_history_items.toAst)) value.revision_history),("revision_route",CandidateJsonSource.Value.string value.revision_route),("satisfaction_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.satisfaction_refs),("scope_ref",CandidateJsonSource.Value.string value.scope_ref),("status",CandidateJsonSource.Value.string value.status),("successor_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.successor_refs),("target_pressure",CandidateJsonSource.Value.string value.target_pressure)]

structure TAgentAssignment_payload where
  eligible_agent_ref : String
  expected_output_refs : List (String)
  intent_ref : String
  owner_ref : String
  period : String
  project_ref : String
  stop_conditions : List (String)
  work_ref : String
  deriving DecidableEq, Repr

def TAgentAssignment_payload.fields : CandidateBindingAst.Fields TAgentAssignment_payload :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 0 none true) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 0 none true) (CandidateBindingAst.cons (stringProfile 1 none none none) CandidateBindingAst.empty))))))))
    (fun p => TAgentAssignment_payload.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1 p.2.2.2.2.2.1 p.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.1)
def TAgentAssignment_payload.rawDecoder : CandidateBindingAst.Decoder TAgentAssignment_payload :=
  CandidateBindingAst.object ["eligible_agent_ref","expected_output_refs","intent_ref","owner_ref","period","project_ref","stop_conditions","work_ref"] TAgentAssignment_payload.fields
def TAgentAssignment_payload.Conditions (_value : TAgentAssignment_payload) : Prop := True
instance : DecidablePred TAgentAssignment_payload.Conditions := fun value => by
  unfold TAgentAssignment_payload.Conditions
  infer_instance
def TAgentAssignment_payload.decoder : CandidateBindingAst.Decoder TAgentAssignment_payload :=
  constrained TAgentAssignment_payload.rawDecoder TAgentAssignment_payload.Conditions
def TAgentAssignment_payload.Meaning (value : CandidateBindingAst.J) (output : TAgentAssignment_payload) : Prop :=
  CandidateBindingAst.ObjectMeaning ["eligible_agent_ref","expected_output_refs","intent_ref","owner_ref","period","project_ref","stop_conditions","work_ref"] TAgentAssignment_payload.fields value output ∧ TAgentAssignment_payload.Conditions output
def TAgentAssignment_payload.toAst (value : TAgentAssignment_payload) : CandidateBindingAst.J :=
  .object [("eligible_agent_ref",CandidateJsonSource.Value.string value.eligible_agent_ref),("expected_output_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.expected_output_refs),("intent_ref",CandidateJsonSource.Value.string value.intent_ref),("owner_ref",CandidateJsonSource.Value.string value.owner_ref),("period",CandidateJsonSource.Value.string value.period),("project_ref",CandidateJsonSource.Value.string value.project_ref),("stop_conditions",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.stop_conditions),("work_ref",CandidateJsonSource.Value.string value.work_ref)]

structure TAgentAssignment_relation_refs_items where
  counterpart_kind : String
  counterpart_ref : String
  direction : String
  relation_kind_ref : String
  deriving DecidableEq, Repr

def TAgentAssignment_relation_refs_items.fields : CandidateBindingAst.Fields TAgentAssignment_relation_refs_items :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 0 none (some ["agent-assignment","challenge-event","intent","project"]) none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 0 none (some ["source","target"]) none) (CandidateBindingAst.cons (stringProfile 0 none (some ["relation.addresses-intent","relation.challenges","relation.member-of","relation.successor-of"]) none) CandidateBindingAst.empty))))
    (fun p => TAgentAssignment_relation_refs_items.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1)
def TAgentAssignment_relation_refs_items.rawDecoder : CandidateBindingAst.Decoder TAgentAssignment_relation_refs_items :=
  CandidateBindingAst.object ["counterpart_kind","counterpart_ref","direction","relation_kind_ref"] TAgentAssignment_relation_refs_items.fields
def TAgentAssignment_relation_refs_items.Conditions (_value : TAgentAssignment_relation_refs_items) : Prop := True
instance : DecidablePred TAgentAssignment_relation_refs_items.Conditions := fun value => by
  unfold TAgentAssignment_relation_refs_items.Conditions
  infer_instance
def TAgentAssignment_relation_refs_items.decoder : CandidateBindingAst.Decoder TAgentAssignment_relation_refs_items :=
  constrained TAgentAssignment_relation_refs_items.rawDecoder TAgentAssignment_relation_refs_items.Conditions
def TAgentAssignment_relation_refs_items.Meaning (value : CandidateBindingAst.J) (output : TAgentAssignment_relation_refs_items) : Prop :=
  CandidateBindingAst.ObjectMeaning ["counterpart_kind","counterpart_ref","direction","relation_kind_ref"] TAgentAssignment_relation_refs_items.fields value output ∧ TAgentAssignment_relation_refs_items.Conditions output
def TAgentAssignment_relation_refs_items.toAst (value : TAgentAssignment_relation_refs_items) : CandidateBindingAst.J :=
  .object [("counterpart_kind",CandidateJsonSource.Value.string value.counterpart_kind),("counterpart_ref",CandidateJsonSource.Value.string value.counterpart_ref),("direction",CandidateJsonSource.Value.string value.direction),("relation_kind_ref",CandidateJsonSource.Value.string value.relation_kind_ref)]

structure TAgentAssignment where
  authority_effect : String
  challenge_route : String
  claim_ceiling : String
  evidence_refs : List (String)
  kind : String
  lifecycle_state : String
  name : String
  node_id : String
  owner_ref : String
  payload : TAgentAssignment_payload
  relation_refs : List (TAgentAssignment_relation_refs_items)
  schema_version : String
  scope_ref : String
  successor_refs : List (String)
  deriving DecidableEq, Repr

def TAgentAssignment.fields : CandidateBindingAst.Fields TAgentAssignment :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 0 (some "none") none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 0 none true) (CandidateBindingAst.cons (stringProfile 0 (some "agent-assignment") none none) (CandidateBindingAst.cons (stringProfile 0 none (some ["candidate","active","historical","retired"]) none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons TAgentAssignment_payload.decoder (CandidateBindingAst.cons (boundedArray TAgentAssignment_relation_refs_items.decoder 1 none false) (CandidateBindingAst.cons (stringProfile 0 (some "cyberalchemy-lab-agent-assignment/v1") none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 0 none true) CandidateBindingAst.empty))))))))))))))
    (fun p => TAgentAssignment.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1 p.2.2.2.2.2.1 p.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.1)
def TAgentAssignment.rawDecoder : CandidateBindingAst.Decoder TAgentAssignment :=
  CandidateBindingAst.object ["authority_effect","challenge_route","claim_ceiling","evidence_refs","kind","lifecycle_state","name","node_id","owner_ref","payload","relation_refs","schema_version","scope_ref","successor_refs"] TAgentAssignment.fields
def TAgentAssignment.Conditions (_value : TAgentAssignment) : Prop := True
instance : DecidablePred TAgentAssignment.Conditions := fun value => by
  unfold TAgentAssignment.Conditions
  infer_instance
def TAgentAssignment.decoder : CandidateBindingAst.Decoder TAgentAssignment :=
  constrained TAgentAssignment.rawDecoder TAgentAssignment.Conditions
def TAgentAssignment.Meaning (value : CandidateBindingAst.J) (output : TAgentAssignment) : Prop :=
  CandidateBindingAst.ObjectMeaning ["authority_effect","challenge_route","claim_ceiling","evidence_refs","kind","lifecycle_state","name","node_id","owner_ref","payload","relation_refs","schema_version","scope_ref","successor_refs"] TAgentAssignment.fields value output ∧ TAgentAssignment.Conditions output
def TAgentAssignment.toAst (value : TAgentAssignment) : CandidateBindingAst.J :=
  .object [("authority_effect",CandidateJsonSource.Value.string value.authority_effect),("challenge_route",CandidateJsonSource.Value.string value.challenge_route),("claim_ceiling",CandidateJsonSource.Value.string value.claim_ceiling),("evidence_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.evidence_refs),("kind",CandidateJsonSource.Value.string value.kind),("lifecycle_state",CandidateJsonSource.Value.string value.lifecycle_state),("name",CandidateJsonSource.Value.string value.name),("node_id",CandidateJsonSource.Value.string value.node_id),("owner_ref",CandidateJsonSource.Value.string value.owner_ref),("payload",TAgentAssignment_payload.toAst value.payload),("relation_refs",(fun values => CandidateJsonSource.Value.array (values.map TAgentAssignment_relation_refs_items.toAst)) value.relation_refs),("schema_version",CandidateJsonSource.Value.string value.schema_version),("scope_ref",CandidateJsonSource.Value.string value.scope_ref),("successor_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.successor_refs)]

structure TGoal where
  schema_version : String
  goal_id : String
  version : String
  name : String
  status : String
  authority_effect : String
  semantic_definition_refs : List (String)
  outcome : String
  rationale : String
  success_conditions : List (String)
  evidence_requirements : List (String)
  accountable_owner_ref : String
  challenge_route : String
  claim_ceiling : String
  deriving DecidableEq, Repr

def TGoal.fields : CandidateBindingAst.Fields TGoal :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 0 (some "cyberalchemy-lab-goal/v1") none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 0 (some "candidate-unadmitted") none none) (CandidateBindingAst.cons (stringProfile 0 (some "none") none none) (CandidateBindingAst.cons (constrained (boundedArray (stringProfile 0 none none none) 0 none false) (fun values => values = ["CAV2-D59@1.0.0-candidate.1","cal.definition.identity-carrier@1.0.0-candidate.1"])) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 1 none true) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 1 none true) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) CandidateBindingAst.empty))))))))))))))
    (fun p => TGoal.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1 p.2.2.2.2.2.1 p.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.1)
def TGoal.rawDecoder : CandidateBindingAst.Decoder TGoal :=
  CandidateBindingAst.object ["schema_version","goal_id","version","name","status","authority_effect","semantic_definition_refs","outcome","rationale","success_conditions","evidence_requirements","accountable_owner_ref","challenge_route","claim_ceiling"] TGoal.fields
def TGoal.Conditions (_value : TGoal) : Prop := True
instance : DecidablePred TGoal.Conditions := fun value => by
  unfold TGoal.Conditions
  infer_instance
def TGoal.decoder : CandidateBindingAst.Decoder TGoal :=
  constrained TGoal.rawDecoder TGoal.Conditions
def TGoal.Meaning (value : CandidateBindingAst.J) (output : TGoal) : Prop :=
  CandidateBindingAst.ObjectMeaning ["schema_version","goal_id","version","name","status","authority_effect","semantic_definition_refs","outcome","rationale","success_conditions","evidence_requirements","accountable_owner_ref","challenge_route","claim_ceiling"] TGoal.fields value output ∧ TGoal.Conditions output
def TGoal.toAst (value : TGoal) : CandidateBindingAst.J :=
  .object [("schema_version",CandidateJsonSource.Value.string value.schema_version),("goal_id",CandidateJsonSource.Value.string value.goal_id),("version",CandidateJsonSource.Value.string value.version),("name",CandidateJsonSource.Value.string value.name),("status",CandidateJsonSource.Value.string value.status),("authority_effect",CandidateJsonSource.Value.string value.authority_effect),("semantic_definition_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.semantic_definition_refs),("outcome",CandidateJsonSource.Value.string value.outcome),("rationale",CandidateJsonSource.Value.string value.rationale),("success_conditions",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.success_conditions),("evidence_requirements",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.evidence_requirements),("accountable_owner_ref",CandidateJsonSource.Value.string value.accountable_owner_ref),("challenge_route",CandidateJsonSource.Value.string value.challenge_route),("claim_ceiling",CandidateJsonSource.Value.string value.claim_ceiling)]

structure TProduct where
  authority_effect : String
  identity_boundary : String
  kind : String
  name : String
  node_id : String
  owner_ref : String
  owner_route : String
  purpose : String
  scope_ref : String
  status : String
  deriving DecidableEq, Repr

def TProduct.fields : CandidateBindingAst.Fields TProduct :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 0 (some "none") none none) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 (some "product") none none) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 (some "candidate-unadmitted") none none) CandidateBindingAst.empty))))))))))
    (fun p => TProduct.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1 p.2.2.2.2.2.1 p.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.1)
def TProduct.rawDecoder : CandidateBindingAst.Decoder TProduct :=
  CandidateBindingAst.object ["authority_effect","identity_boundary","kind","name","node_id","owner_ref","owner_route","purpose","scope_ref","status"] TProduct.fields
def TProduct.Conditions (_value : TProduct) : Prop := True
instance : DecidablePred TProduct.Conditions := fun value => by
  unfold TProduct.Conditions
  infer_instance
def TProduct.decoder : CandidateBindingAst.Decoder TProduct :=
  constrained TProduct.rawDecoder TProduct.Conditions
def TProduct.Meaning (value : CandidateBindingAst.J) (output : TProduct) : Prop :=
  CandidateBindingAst.ObjectMeaning ["authority_effect","identity_boundary","kind","name","node_id","owner_ref","owner_route","purpose","scope_ref","status"] TProduct.fields value output ∧ TProduct.Conditions output
def TProduct.toAst (value : TProduct) : CandidateBindingAst.J :=
  .object [("authority_effect",CandidateJsonSource.Value.string value.authority_effect),("identity_boundary",CandidateJsonSource.Value.string value.identity_boundary),("kind",CandidateJsonSource.Value.string value.kind),("name",CandidateJsonSource.Value.string value.name),("node_id",CandidateJsonSource.Value.string value.node_id),("owner_ref",CandidateJsonSource.Value.string value.owner_ref),("owner_route",CandidateJsonSource.Value.string value.owner_route),("purpose",CandidateJsonSource.Value.string value.purpose),("scope_ref",CandidateJsonSource.Value.string value.scope_ref),("status",CandidateJsonSource.Value.string value.status)]

structure TProductCapability_lifecycle_posture where
  commitment_ref : Option String
  evidence_refs : List (String)
  kind : String
  owner_ref : String
  provenance_refs : List (String)
  residue_refs : List (String)
  status : String
  status_vocabulary_ref : String
  deriving DecidableEq, Repr

def TProductCapability_lifecycle_posture.fields : CandidateBindingAst.Fields TProductCapability_lifecycle_posture :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (nullable (stringProfile 0 none none (some .nonWhitespace))) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 0 (some 100) true) (CandidateBindingAst.cons (stringProfile 0 (some "product-capability") none none) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 1 (some 100) true) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 0 (some 100) true) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) CandidateBindingAst.empty))))))))
    (fun p => TProductCapability_lifecycle_posture.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1 p.2.2.2.2.2.1 p.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.1)
def TProductCapability_lifecycle_posture.rawDecoder : CandidateBindingAst.Decoder TProductCapability_lifecycle_posture :=
  CandidateBindingAst.object ["commitment_ref","evidence_refs","kind","owner_ref","provenance_refs","residue_refs","status","status_vocabulary_ref"] TProductCapability_lifecycle_posture.fields
def TProductCapability_lifecycle_posture.Conditions (_value : TProductCapability_lifecycle_posture) : Prop := True
instance : DecidablePred TProductCapability_lifecycle_posture.Conditions := fun value => by
  unfold TProductCapability_lifecycle_posture.Conditions
  infer_instance
def TProductCapability_lifecycle_posture.decoder : CandidateBindingAst.Decoder TProductCapability_lifecycle_posture :=
  constrained TProductCapability_lifecycle_posture.rawDecoder TProductCapability_lifecycle_posture.Conditions
def TProductCapability_lifecycle_posture.Meaning (value : CandidateBindingAst.J) (output : TProductCapability_lifecycle_posture) : Prop :=
  CandidateBindingAst.ObjectMeaning ["commitment_ref","evidence_refs","kind","owner_ref","provenance_refs","residue_refs","status","status_vocabulary_ref"] TProductCapability_lifecycle_posture.fields value output ∧ TProductCapability_lifecycle_posture.Conditions output
def TProductCapability_lifecycle_posture.toAst (value : TProductCapability_lifecycle_posture) : CandidateBindingAst.J :=
  .object [("commitment_ref",(fun value => match value with | none => CandidateJsonSource.Value.null | some text => CandidateJsonSource.Value.string text) value.commitment_ref),("evidence_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.evidence_refs),("kind",CandidateJsonSource.Value.string value.kind),("owner_ref",CandidateJsonSource.Value.string value.owner_ref),("provenance_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.provenance_refs),("residue_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.residue_refs),("status",CandidateJsonSource.Value.string value.status),("status_vocabulary_ref",CandidateJsonSource.Value.string value.status_vocabulary_ref)]

structure TProductCapability_revision_history_items where
  changed_anchors : List (String)
  decision_ref : String
  rationale : String
  revision_id : String
  deriving DecidableEq, Repr

def TProductCapability_revision_history_items.fields : CandidateBindingAst.Fields TProductCapability_revision_history_items :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (boundedArray (stringProfile 0 none (some ["product_ref","outcome","scope_ref","owner_routes"]) none) 1 none true) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) CandidateBindingAst.empty))))
    (fun p => TProductCapability_revision_history_items.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1)
def TProductCapability_revision_history_items.rawDecoder : CandidateBindingAst.Decoder TProductCapability_revision_history_items :=
  CandidateBindingAst.object ["changed_anchors","decision_ref","rationale","revision_id"] TProductCapability_revision_history_items.fields
def TProductCapability_revision_history_items.Conditions (_value : TProductCapability_revision_history_items) : Prop := True
instance : DecidablePred TProductCapability_revision_history_items.Conditions := fun value => by
  unfold TProductCapability_revision_history_items.Conditions
  infer_instance
def TProductCapability_revision_history_items.decoder : CandidateBindingAst.Decoder TProductCapability_revision_history_items :=
  constrained TProductCapability_revision_history_items.rawDecoder TProductCapability_revision_history_items.Conditions
def TProductCapability_revision_history_items.Meaning (value : CandidateBindingAst.J) (output : TProductCapability_revision_history_items) : Prop :=
  CandidateBindingAst.ObjectMeaning ["changed_anchors","decision_ref","rationale","revision_id"] TProductCapability_revision_history_items.fields value output ∧ TProductCapability_revision_history_items.Conditions output
def TProductCapability_revision_history_items.toAst (value : TProductCapability_revision_history_items) : CandidateBindingAst.J :=
  .object [("changed_anchors",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.changed_anchors),("decision_ref",CandidateJsonSource.Value.string value.decision_ref),("rationale",CandidateJsonSource.Value.string value.rationale),("revision_id",CandidateJsonSource.Value.string value.revision_id)]

structure TProductCapability where
  acceptance_conditions : List (String)
  authority_effect : String
  challenge_route : String
  consumer_refs : List (String)
  context_policy_refs : List (String)
  evidence_refs : List (String)
  exclusions : List (String)
  input_contract_refs : List (String)
  kind : String
  lifecycle_posture : TProductCapability_lifecycle_posture
  name : String
  node_id : String
  outcome : String
  output_contract_refs : List (String)
  owner_ref : String
  owner_routes : List (String)
  participant_refs : List (String)
  product_ref : String
  product_thesis_ref : String
  realization_binding_refs : List (String)
  revision_history : List (TProductCapability_revision_history_items)
  scope_ref : String
  status : String
  successor_refs : List (String)
  thesis_outcome_refs : List (String)
  deriving DecidableEq, Repr

def TProductCapability.fields : CandidateBindingAst.Fields TProductCapability :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 1 (some 100) true) (CandidateBindingAst.cons (stringProfile 0 (some "none") none none) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 1 (some 100) true) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 0 (some 100) true) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 0 (some 100) true) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 1 (some 100) true) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 0 (some 100) true) (CandidateBindingAst.cons (stringProfile 0 (some "product-capability") none none) (CandidateBindingAst.cons TProductCapability_lifecycle_posture.decoder (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 1 (some 100) true) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 1 (some 100) true) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 1 (some 100) true) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 0 (some 100) true) (CandidateBindingAst.cons (boundedArray TProductCapability_revision_history_items.decoder 0 (some 100) false) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 (some "candidate-unadmitted") none none) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 0 (some 100) true) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 1 (some 100) true) CandidateBindingAst.empty)))))))))))))))))))))))))
    (fun p => TProductCapability.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1 p.2.2.2.2.2.1 p.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1)
def TProductCapability.rawDecoder : CandidateBindingAst.Decoder TProductCapability :=
  CandidateBindingAst.object ["acceptance_conditions","authority_effect","challenge_route","consumer_refs","context_policy_refs","evidence_refs","exclusions","input_contract_refs","kind","lifecycle_posture","name","node_id","outcome","output_contract_refs","owner_ref","owner_routes","participant_refs","product_ref","product_thesis_ref","realization_binding_refs","revision_history","scope_ref","status","successor_refs","thesis_outcome_refs"] TProductCapability.fields
def TProductCapability.Conditions (_value : TProductCapability) : Prop := True
instance : DecidablePred TProductCapability.Conditions := fun value => by
  unfold TProductCapability.Conditions
  infer_instance
def TProductCapability.decoder : CandidateBindingAst.Decoder TProductCapability :=
  constrained TProductCapability.rawDecoder TProductCapability.Conditions
def TProductCapability.Meaning (value : CandidateBindingAst.J) (output : TProductCapability) : Prop :=
  CandidateBindingAst.ObjectMeaning ["acceptance_conditions","authority_effect","challenge_route","consumer_refs","context_policy_refs","evidence_refs","exclusions","input_contract_refs","kind","lifecycle_posture","name","node_id","outcome","output_contract_refs","owner_ref","owner_routes","participant_refs","product_ref","product_thesis_ref","realization_binding_refs","revision_history","scope_ref","status","successor_refs","thesis_outcome_refs"] TProductCapability.fields value output ∧ TProductCapability.Conditions output
def TProductCapability.toAst (value : TProductCapability) : CandidateBindingAst.J :=
  .object [("acceptance_conditions",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.acceptance_conditions),("authority_effect",CandidateJsonSource.Value.string value.authority_effect),("challenge_route",CandidateJsonSource.Value.string value.challenge_route),("consumer_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.consumer_refs),("context_policy_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.context_policy_refs),("evidence_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.evidence_refs),("exclusions",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.exclusions),("input_contract_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.input_contract_refs),("kind",CandidateJsonSource.Value.string value.kind),("lifecycle_posture",TProductCapability_lifecycle_posture.toAst value.lifecycle_posture),("name",CandidateJsonSource.Value.string value.name),("node_id",CandidateJsonSource.Value.string value.node_id),("outcome",CandidateJsonSource.Value.string value.outcome),("output_contract_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.output_contract_refs),("owner_ref",CandidateJsonSource.Value.string value.owner_ref),("owner_routes",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.owner_routes),("participant_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.participant_refs),("product_ref",CandidateJsonSource.Value.string value.product_ref),("product_thesis_ref",CandidateJsonSource.Value.string value.product_thesis_ref),("realization_binding_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.realization_binding_refs),("revision_history",(fun values => CandidateJsonSource.Value.array (values.map TProductCapability_revision_history_items.toAst)) value.revision_history),("scope_ref",CandidateJsonSource.Value.string value.scope_ref),("status",CandidateJsonSource.Value.string value.status),("successor_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.successor_refs),("thesis_outcome_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.thesis_outcome_refs)]

structure TProject where
  authority_effect : String
  identity_boundary : String
  kind : String
  name : String
  node_id : String
  owner_ref : String
  owner_route : String
  purpose : String
  scope_ref : String
  status : String
  deriving DecidableEq, Repr

def TProject.fields : CandidateBindingAst.Fields TProject :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 0 (some "none") none none) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 (some "project") none none) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 (some "candidate-unadmitted") none none) CandidateBindingAst.empty))))))))))
    (fun p => TProject.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1 p.2.2.2.2.2.1 p.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.1)
def TProject.rawDecoder : CandidateBindingAst.Decoder TProject :=
  CandidateBindingAst.object ["authority_effect","identity_boundary","kind","name","node_id","owner_ref","owner_route","purpose","scope_ref","status"] TProject.fields
def TProject.Conditions (_value : TProject) : Prop := True
instance : DecidablePred TProject.Conditions := fun value => by
  unfold TProject.Conditions
  infer_instance
def TProject.decoder : CandidateBindingAst.Decoder TProject :=
  constrained TProject.rawDecoder TProject.Conditions
def TProject.Meaning (value : CandidateBindingAst.J) (output : TProject) : Prop :=
  CandidateBindingAst.ObjectMeaning ["authority_effect","identity_boundary","kind","name","node_id","owner_ref","owner_route","purpose","scope_ref","status"] TProject.fields value output ∧ TProject.Conditions output
def TProject.toAst (value : TProject) : CandidateBindingAst.J :=
  .object [("authority_effect",CandidateJsonSource.Value.string value.authority_effect),("identity_boundary",CandidateJsonSource.Value.string value.identity_boundary),("kind",CandidateJsonSource.Value.string value.kind),("name",CandidateJsonSource.Value.string value.name),("node_id",CandidateJsonSource.Value.string value.node_id),("owner_ref",CandidateJsonSource.Value.string value.owner_ref),("owner_route",CandidateJsonSource.Value.string value.owner_route),("purpose",CandidateJsonSource.Value.string value.purpose),("scope_ref",CandidateJsonSource.Value.string value.scope_ref),("status",CandidateJsonSource.Value.string value.status)]

structure TResearchInquiry_source_policy where
  allowed_source_kinds : List (String)
  conflict_handling : String
  freshness_rule : String
  selection_criteria : List (String)
  deriving DecidableEq, Repr

def TResearchInquiry_source_policy.fields : CandidateBindingAst.Fields TResearchInquiry_source_policy :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 1 (some 100) true) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 1 (some 100) true) CandidateBindingAst.empty))))
    (fun p => TResearchInquiry_source_policy.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1)
def TResearchInquiry_source_policy.rawDecoder : CandidateBindingAst.Decoder TResearchInquiry_source_policy :=
  CandidateBindingAst.object ["allowed_source_kinds","conflict_handling","freshness_rule","selection_criteria"] TResearchInquiry_source_policy.fields
def TResearchInquiry_source_policy.Conditions (_value : TResearchInquiry_source_policy) : Prop := True
instance : DecidablePred TResearchInquiry_source_policy.Conditions := fun value => by
  unfold TResearchInquiry_source_policy.Conditions
  infer_instance
def TResearchInquiry_source_policy.decoder : CandidateBindingAst.Decoder TResearchInquiry_source_policy :=
  constrained TResearchInquiry_source_policy.rawDecoder TResearchInquiry_source_policy.Conditions
def TResearchInquiry_source_policy.Meaning (value : CandidateBindingAst.J) (output : TResearchInquiry_source_policy) : Prop :=
  CandidateBindingAst.ObjectMeaning ["allowed_source_kinds","conflict_handling","freshness_rule","selection_criteria"] TResearchInquiry_source_policy.fields value output ∧ TResearchInquiry_source_policy.Conditions output
def TResearchInquiry_source_policy.toAst (value : TResearchInquiry_source_policy) : CandidateBindingAst.J :=
  .object [("allowed_source_kinds",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.allowed_source_kinds),("conflict_handling",CandidateJsonSource.Value.string value.conflict_handling),("freshness_rule",CandidateJsonSource.Value.string value.freshness_rule),("selection_criteria",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.selection_criteria)]

structure TResearchInquiry where
  authority_effect : String
  challenge_route : String
  claim_ceiling : String
  counterevidence_refs : List (String)
  created_at : String
  evidence_aggregate_refs : List (String)
  exclusions : List (String)
  finding_refs : List (String)
  goal_refs : List (String)
  inclusions : List (String)
  kind : String
  last_updated_at : String
  limitations : List (String)
  method_ref : String
  node_id : String
  owner_ref : String
  owner_route : String
  project_ref : String
  question : String
  scope_ref : String
  source_policy : TResearchInquiry_source_policy
  source_refs : List (String)
  status : String
  stop_conditions : List (String)
  deriving DecidableEq, Repr

def TResearchInquiry.fields : CandidateBindingAst.Fields TResearchInquiry :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 0 (some "none") none none) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 0 (some 100) true) (CandidateBindingAst.cons (stringProfile 0 none none (some .timestamp)) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 0 (some 100) true) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 1 (some 100) true) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 0 (some 100) true) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 1 (some 100) true) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 1 (some 100) true) (CandidateBindingAst.cons (stringProfile 0 (some "research-inquiry") none none) (CandidateBindingAst.cons (stringProfile 0 none none (some .timestamp)) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 1 (some 100) true) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons (stringProfile 0 none none (some .nonWhitespace)) (CandidateBindingAst.cons TResearchInquiry_source_policy.decoder (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 0 (some 100) true) (CandidateBindingAst.cons (stringProfile 0 (some "candidate-unadmitted") none none) (CandidateBindingAst.cons (boundedArray (stringProfile 0 none none (some .nonWhitespace)) 1 (some 100) true) CandidateBindingAst.empty))))))))))))))))))))))))
    (fun p => TResearchInquiry.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1 p.2.2.2.2.2.1 p.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1)
def TResearchInquiry.rawDecoder : CandidateBindingAst.Decoder TResearchInquiry :=
  CandidateBindingAst.object ["authority_effect","challenge_route","claim_ceiling","counterevidence_refs","created_at","evidence_aggregate_refs","exclusions","finding_refs","goal_refs","inclusions","kind","last_updated_at","limitations","method_ref","node_id","owner_ref","owner_route","project_ref","question","scope_ref","source_policy","source_refs","status","stop_conditions"] TResearchInquiry.fields
def TResearchInquiry.Conditions (_value : TResearchInquiry) : Prop := True
instance : DecidablePred TResearchInquiry.Conditions := fun value => by
  unfold TResearchInquiry.Conditions
  infer_instance
def TResearchInquiry.decoder : CandidateBindingAst.Decoder TResearchInquiry :=
  constrained TResearchInquiry.rawDecoder TResearchInquiry.Conditions
def TResearchInquiry.Meaning (value : CandidateBindingAst.J) (output : TResearchInquiry) : Prop :=
  CandidateBindingAst.ObjectMeaning ["authority_effect","challenge_route","claim_ceiling","counterevidence_refs","created_at","evidence_aggregate_refs","exclusions","finding_refs","goal_refs","inclusions","kind","last_updated_at","limitations","method_ref","node_id","owner_ref","owner_route","project_ref","question","scope_ref","source_policy","source_refs","status","stop_conditions"] TResearchInquiry.fields value output ∧ TResearchInquiry.Conditions output
def TResearchInquiry.toAst (value : TResearchInquiry) : CandidateBindingAst.J :=
  .object [("authority_effect",CandidateJsonSource.Value.string value.authority_effect),("challenge_route",CandidateJsonSource.Value.string value.challenge_route),("claim_ceiling",CandidateJsonSource.Value.string value.claim_ceiling),("counterevidence_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.counterevidence_refs),("created_at",CandidateJsonSource.Value.string value.created_at),("evidence_aggregate_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.evidence_aggregate_refs),("exclusions",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.exclusions),("finding_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.finding_refs),("goal_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.goal_refs),("inclusions",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.inclusions),("kind",CandidateJsonSource.Value.string value.kind),("last_updated_at",CandidateJsonSource.Value.string value.last_updated_at),("limitations",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.limitations),("method_ref",CandidateJsonSource.Value.string value.method_ref),("node_id",CandidateJsonSource.Value.string value.node_id),("owner_ref",CandidateJsonSource.Value.string value.owner_ref),("owner_route",CandidateJsonSource.Value.string value.owner_route),("project_ref",CandidateJsonSource.Value.string value.project_ref),("question",CandidateJsonSource.Value.string value.question),("scope_ref",CandidateJsonSource.Value.string value.scope_ref),("source_policy",TResearchInquiry_source_policy.toAst value.source_policy),("source_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.source_refs),("status",CandidateJsonSource.Value.string value.status),("stop_conditions",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.stop_conditions)]

inductive Kind where
  | intent
  | agent_assignment
  | goal
  | product
  | product_capability
  | project
  | research_inquiry
  deriving DecidableEq, Repr

inductive Body where
  | intent (value : TIntent)
  | agent_assignment (value : TAgentAssignment)
  | goal (value : TGoal)
  | product (value : TProduct)
  | product_capability (value : TProductCapability)
  | project (value : TProject)
  | research_inquiry (value : TResearchInquiry)
  deriving DecidableEq, Repr

def decoderForKind : Kind → CandidateBindingAst.Decoder Body
  | .intent => mapped TIntent.decoder Body.intent
  | .agent_assignment => mapped TAgentAssignment.decoder Body.agent_assignment
  | .goal => mapped TGoal.decoder Body.goal
  | .product => mapped TProduct.decoder Body.product
  | .product_capability => mapped TProductCapability.decoder Body.product_capability
  | .project => mapped TProject.decoder Body.project
  | .research_inquiry => mapped TResearchInquiry.decoder Body.research_inquiry

def Body.toAst : Body → CandidateBindingAst.J
  | .intent value => TIntent.toAst value
  | .agent_assignment value => TAgentAssignment.toAst value
  | .goal value => TGoal.toAst value
  | .product value => TProduct.toAst value
  | .product_capability value => TProductCapability.toAst value
  | .project value => TProject.toAst value
  | .research_inquiry value => TResearchInquiry.toAst value

def Body.identity : Body → String
  | .intent value => value.node_id
  | .agent_assignment value => value.node_id
  | .goal value => value.goal_id
  | .product value => value.node_id
  | .product_capability value => value.node_id
  | .project value => value.node_id
  | .research_inquiry value => value.node_id

theorem intent_complete_record_exact (value : CandidateBindingAst.J) (output : TIntent) :
    TIntent.decoder.decode value = some output ↔ TIntent.Meaning value output :=
  TIntent.decoder.exact value output

theorem agent_assignment_complete_record_exact (value : CandidateBindingAst.J) (output : TAgentAssignment) :
    TAgentAssignment.decoder.decode value = some output ↔ TAgentAssignment.Meaning value output :=
  TAgentAssignment.decoder.exact value output

theorem goal_complete_record_exact (value : CandidateBindingAst.J) (output : TGoal) :
    TGoal.decoder.decode value = some output ↔ TGoal.Meaning value output :=
  TGoal.decoder.exact value output

theorem product_complete_record_exact (value : CandidateBindingAst.J) (output : TProduct) :
    TProduct.decoder.decode value = some output ↔ TProduct.Meaning value output :=
  TProduct.decoder.exact value output

theorem product_capability_complete_record_exact (value : CandidateBindingAst.J) (output : TProductCapability) :
    TProductCapability.decoder.decode value = some output ↔ TProductCapability.Meaning value output :=
  TProductCapability.decoder.exact value output

theorem project_complete_record_exact (value : CandidateBindingAst.J) (output : TProject) :
    TProject.decoder.decode value = some output ↔ TProject.Meaning value output :=
  TProject.decoder.exact value output

theorem research_inquiry_complete_record_exact (value : CandidateBindingAst.J) (output : TResearchInquiry) :
    TResearchInquiry.decoder.decode value = some output ↔ TResearchInquiry.Meaning value output :=
  TResearchInquiry.decoder.exact value output

#print axioms intent_complete_record_exact
#print axioms agent_assignment_complete_record_exact
#print axioms goal_complete_record_exact
#print axioms product_complete_record_exact
#print axioms product_capability_complete_record_exact
#print axioms project_complete_record_exact
#print axioms research_inquiry_complete_record_exact
end RelationalSuccessor.CandidateTypedBodies
