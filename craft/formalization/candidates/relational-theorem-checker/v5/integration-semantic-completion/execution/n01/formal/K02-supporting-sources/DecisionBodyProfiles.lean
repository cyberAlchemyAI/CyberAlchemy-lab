import BodyStringProfiles
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateSupportingSources
open CandidateTypedBodies

structure TDecision_payload where
  decision_maker_ref : String
  declared_effect_refs : List (String)
  evidence_basis_refs : List (String)
  selected_outcome : String
  subject_refs : List (String)
  deriving DecidableEq, Repr

def TDecision_payload.fields : CandidateBindingAst.Fields TDecision_payload :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 1 none true) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 1 none true) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 1 none true) CandidateBindingAst.empty)))))
    (fun p => TDecision_payload.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1)
def TDecision_payload.rawDecoder : CandidateBindingAst.Decoder TDecision_payload :=
  CandidateBindingAst.object ["decision_maker_ref","declared_effect_refs","evidence_basis_refs","selected_outcome","subject_refs"] TDecision_payload.fields
def TDecision_payload.Conditions (_value : TDecision_payload) : Prop := True
instance : DecidablePred TDecision_payload.Conditions := fun value => by
  unfold TDecision_payload.Conditions
  infer_instance
def TDecision_payload.decoder : CandidateBindingAst.Decoder TDecision_payload :=
  constrained TDecision_payload.rawDecoder TDecision_payload.Conditions
def TDecision_payload.Meaning (value : CandidateBindingAst.J) (output : TDecision_payload) : Prop :=
  CandidateBindingAst.ObjectMeaning ["decision_maker_ref","declared_effect_refs","evidence_basis_refs","selected_outcome","subject_refs"] TDecision_payload.fields value output ∧ TDecision_payload.Conditions output
def TDecision_payload.toAst (value : TDecision_payload) : CandidateBindingAst.J :=
  .object [("decision_maker_ref",CandidateJsonSource.Value.string value.decision_maker_ref),("declared_effect_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.declared_effect_refs),("evidence_basis_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.evidence_basis_refs),("selected_outcome",CandidateJsonSource.Value.string value.selected_outcome),("subject_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.subject_refs)]

structure TDecision_relation_refs_items where
  counterpart_kind : String
  counterpart_ref : String
  direction : String
  relation_kind_ref : String
  deriving DecidableEq, Repr

def TDecision_relation_refs_items.fields : CandidateBindingAst.Fields TDecision_relation_refs_items :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 0 none (some ["artifact-type","capability-realization-binding","definition","effect","governed-model","product-capability","relation-kind"]) none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 0 none (some ["source"]) none) (CandidateBindingAst.cons (stringProfile 0 none (some ["relation.declares-effect-on"]) none) CandidateBindingAst.empty))))
    (fun p => TDecision_relation_refs_items.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1)
def TDecision_relation_refs_items.rawDecoder : CandidateBindingAst.Decoder TDecision_relation_refs_items :=
  CandidateBindingAst.object ["counterpart_kind","counterpart_ref","direction","relation_kind_ref"] TDecision_relation_refs_items.fields
def TDecision_relation_refs_items.Conditions (_value : TDecision_relation_refs_items) : Prop := True
instance : DecidablePred TDecision_relation_refs_items.Conditions := fun value => by
  unfold TDecision_relation_refs_items.Conditions
  infer_instance
def TDecision_relation_refs_items.decoder : CandidateBindingAst.Decoder TDecision_relation_refs_items :=
  constrained TDecision_relation_refs_items.rawDecoder TDecision_relation_refs_items.Conditions
def TDecision_relation_refs_items.Meaning (value : CandidateBindingAst.J) (output : TDecision_relation_refs_items) : Prop :=
  CandidateBindingAst.ObjectMeaning ["counterpart_kind","counterpart_ref","direction","relation_kind_ref"] TDecision_relation_refs_items.fields value output ∧ TDecision_relation_refs_items.Conditions output
def TDecision_relation_refs_items.toAst (value : TDecision_relation_refs_items) : CandidateBindingAst.J :=
  .object [("counterpart_kind",CandidateJsonSource.Value.string value.counterpart_kind),("counterpart_ref",CandidateJsonSource.Value.string value.counterpart_ref),("direction",CandidateJsonSource.Value.string value.direction),("relation_kind_ref",CandidateJsonSource.Value.string value.relation_kind_ref)]

structure TDecision where
  authority_effect : String
  challenge_route : String
  claim_ceiling : String
  evidence_refs : List (String)
  kind : String
  lifecycle_state : String
  name : String
  node_id : String
  owner_ref : String
  payload : TDecision_payload
  relation_refs : List (TDecision_relation_refs_items)
  schema_version : String
  scope_ref : String
  successor_refs : List (String)
  deriving DecidableEq, Repr

def TDecision.fields : CandidateBindingAst.Fields TDecision :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 0 (some "none") none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 0 none true) (CandidateBindingAst.cons (stringProfile 0 (some "decision") none none) (CandidateBindingAst.cons (stringProfile 0 none (some ["candidate","active","historical","retired"]) none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons TDecision_payload.decoder (CandidateBindingAst.cons (boundedArray TDecision_relation_refs_items.decoder 1 none false) (CandidateBindingAst.cons (stringProfile 0 (some "cyberalchemy-lab-decision/v1") none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 0 none true) CandidateBindingAst.empty))))))))))))))
    (fun p => TDecision.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1 p.2.2.2.2.2.1 p.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.1)
def TDecision.rawDecoder : CandidateBindingAst.Decoder TDecision :=
  CandidateBindingAst.object ["authority_effect","challenge_route","claim_ceiling","evidence_refs","kind","lifecycle_state","name","node_id","owner_ref","payload","relation_refs","schema_version","scope_ref","successor_refs"] TDecision.fields
def TDecision.Conditions (_value : TDecision) : Prop := True
instance : DecidablePred TDecision.Conditions := fun value => by
  unfold TDecision.Conditions
  infer_instance
def TDecision.decoder : CandidateBindingAst.Decoder TDecision :=
  constrained TDecision.rawDecoder TDecision.Conditions
def TDecision.Meaning (value : CandidateBindingAst.J) (output : TDecision) : Prop :=
  CandidateBindingAst.ObjectMeaning ["authority_effect","challenge_route","claim_ceiling","evidence_refs","kind","lifecycle_state","name","node_id","owner_ref","payload","relation_refs","schema_version","scope_ref","successor_refs"] TDecision.fields value output ∧ TDecision.Conditions output
def TDecision.toAst (value : TDecision) : CandidateBindingAst.J :=
  .object [("authority_effect",CandidateJsonSource.Value.string value.authority_effect),("challenge_route",CandidateJsonSource.Value.string value.challenge_route),("claim_ceiling",CandidateJsonSource.Value.string value.claim_ceiling),("evidence_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.evidence_refs),("kind",CandidateJsonSource.Value.string value.kind),("lifecycle_state",CandidateJsonSource.Value.string value.lifecycle_state),("name",CandidateJsonSource.Value.string value.name),("node_id",CandidateJsonSource.Value.string value.node_id),("owner_ref",CandidateJsonSource.Value.string value.owner_ref),("payload",TDecision_payload.toAst value.payload),("relation_refs",(fun values => CandidateJsonSource.Value.array (values.map TDecision_relation_refs_items.toAst)) value.relation_refs),("schema_version",CandidateJsonSource.Value.string value.schema_version),("scope_ref",CandidateJsonSource.Value.string value.scope_ref),("successor_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.successor_refs)]

theorem decision_complete_record_exact (value : CandidateBindingAst.J) (output : TDecision) :
    TDecision.decoder.decode value = some output ↔ TDecision.Meaning value output :=
  TDecision.decoder.exact value output

#print axioms decision_complete_record_exact
end RelationalSuccessor.CandidateSupportingSources
