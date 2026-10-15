import BodyStringProfiles
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateLessonSource
open CandidateTypedBodies

structure TLessonApplication_payload where
  applicability_assessment_ref : String
  application_posture : String
  conflict_refs : List (String)
  intended_influence : String
  lesson_revision_ref : String
  override_refs : List (String)
  session_ref : String
  deriving DecidableEq, Repr

def TLessonApplication_payload.fields : CandidateBindingAst.Fields TLessonApplication_payload :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 0 none false) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 0 none false) (CandidateBindingAst.cons (stringProfile 1 none none none) CandidateBindingAst.empty)))))))
    (fun p => TLessonApplication_payload.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1 p.2.2.2.2.2.1 p.2.2.2.2.2.2.1)
def TLessonApplication_payload.rawDecoder : CandidateBindingAst.Decoder TLessonApplication_payload :=
  CandidateBindingAst.object ["applicability_assessment_ref","application_posture","conflict_refs","intended_influence","lesson_revision_ref","override_refs","session_ref"] TLessonApplication_payload.fields
def TLessonApplication_payload.Conditions (_value : TLessonApplication_payload) : Prop := True
instance : DecidablePred TLessonApplication_payload.Conditions := fun value => by
  unfold TLessonApplication_payload.Conditions
  infer_instance
def TLessonApplication_payload.decoder : CandidateBindingAst.Decoder TLessonApplication_payload :=
  constrained TLessonApplication_payload.rawDecoder TLessonApplication_payload.Conditions
def TLessonApplication_payload.Meaning (value : CandidateBindingAst.J) (output : TLessonApplication_payload) : Prop :=
  CandidateBindingAst.ObjectMeaning ["applicability_assessment_ref","application_posture","conflict_refs","intended_influence","lesson_revision_ref","override_refs","session_ref"] TLessonApplication_payload.fields value output ∧ TLessonApplication_payload.Conditions output
def TLessonApplication_payload.toAst (value : TLessonApplication_payload) : CandidateBindingAst.J :=
  .object [("applicability_assessment_ref",CandidateJsonSource.Value.string value.applicability_assessment_ref),("application_posture",CandidateJsonSource.Value.string value.application_posture),("conflict_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.conflict_refs),("intended_influence",CandidateJsonSource.Value.string value.intended_influence),("lesson_revision_ref",CandidateJsonSource.Value.string value.lesson_revision_ref),("override_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.override_refs),("session_ref",CandidateJsonSource.Value.string value.session_ref)]

structure TLessonApplication_relation_refs_items where
  counterpart_kind : String
  counterpart_ref : String
  direction : String
  relation_kind_ref : String
  deriving DecidableEq, Repr

def TLessonApplication_relation_refs_items.fields : CandidateBindingAst.Fields TLessonApplication_relation_refs_items :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 0 none (some ["agent-action","challenge-event","lesson-application","lesson-outcome-assessment","operational-lesson"]) none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 0 none (some ["source","target"]) none) (CandidateBindingAst.cons (stringProfile 0 none (some ["relation.applies-lesson","relation.challenges","relation.evaluates","relation.produces","relation.successor-of"]) none) CandidateBindingAst.empty))))
    (fun p => TLessonApplication_relation_refs_items.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1)
def TLessonApplication_relation_refs_items.rawDecoder : CandidateBindingAst.Decoder TLessonApplication_relation_refs_items :=
  CandidateBindingAst.object ["counterpart_kind","counterpart_ref","direction","relation_kind_ref"] TLessonApplication_relation_refs_items.fields
def TLessonApplication_relation_refs_items.Conditions (_value : TLessonApplication_relation_refs_items) : Prop := True
instance : DecidablePred TLessonApplication_relation_refs_items.Conditions := fun value => by
  unfold TLessonApplication_relation_refs_items.Conditions
  infer_instance
def TLessonApplication_relation_refs_items.decoder : CandidateBindingAst.Decoder TLessonApplication_relation_refs_items :=
  constrained TLessonApplication_relation_refs_items.rawDecoder TLessonApplication_relation_refs_items.Conditions
def TLessonApplication_relation_refs_items.Meaning (value : CandidateBindingAst.J) (output : TLessonApplication_relation_refs_items) : Prop :=
  CandidateBindingAst.ObjectMeaning ["counterpart_kind","counterpart_ref","direction","relation_kind_ref"] TLessonApplication_relation_refs_items.fields value output ∧ TLessonApplication_relation_refs_items.Conditions output
def TLessonApplication_relation_refs_items.toAst (value : TLessonApplication_relation_refs_items) : CandidateBindingAst.J :=
  .object [("counterpart_kind",CandidateJsonSource.Value.string value.counterpart_kind),("counterpart_ref",CandidateJsonSource.Value.string value.counterpart_ref),("direction",CandidateJsonSource.Value.string value.direction),("relation_kind_ref",CandidateJsonSource.Value.string value.relation_kind_ref)]

structure TLessonApplication where
  authority_effect : String
  challenge_route : String
  claim_ceiling : String
  evidence_refs : List (String)
  kind : String
  lifecycle_state : String
  name : String
  node_id : String
  owner_ref : String
  payload : TLessonApplication_payload
  relation_refs : List (TLessonApplication_relation_refs_items)
  schema_version : String
  scope_ref : String
  successor_refs : List (String)
  deriving DecidableEq, Repr

def TLessonApplication.fields : CandidateBindingAst.Fields TLessonApplication :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 0 (some "none") none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 0 none true) (CandidateBindingAst.cons (stringProfile 0 (some "lesson-application") none none) (CandidateBindingAst.cons (stringProfile 0 none (some ["candidate","active","historical","retired"]) none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons TLessonApplication_payload.decoder (CandidateBindingAst.cons (boundedArray TLessonApplication_relation_refs_items.decoder 1 none false) (CandidateBindingAst.cons (stringProfile 0 (some "cyberalchemy-lab-lesson-application/v1") none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 0 none true) CandidateBindingAst.empty))))))))))))))
    (fun p => TLessonApplication.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1 p.2.2.2.2.2.1 p.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.1)
def TLessonApplication.rawDecoder : CandidateBindingAst.Decoder TLessonApplication :=
  CandidateBindingAst.object ["authority_effect","challenge_route","claim_ceiling","evidence_refs","kind","lifecycle_state","name","node_id","owner_ref","payload","relation_refs","schema_version","scope_ref","successor_refs"] TLessonApplication.fields
def TLessonApplication.Conditions (_value : TLessonApplication) : Prop := True
instance : DecidablePred TLessonApplication.Conditions := fun value => by
  unfold TLessonApplication.Conditions
  infer_instance
def TLessonApplication.decoder : CandidateBindingAst.Decoder TLessonApplication :=
  constrained TLessonApplication.rawDecoder TLessonApplication.Conditions
def TLessonApplication.Meaning (value : CandidateBindingAst.J) (output : TLessonApplication) : Prop :=
  CandidateBindingAst.ObjectMeaning ["authority_effect","challenge_route","claim_ceiling","evidence_refs","kind","lifecycle_state","name","node_id","owner_ref","payload","relation_refs","schema_version","scope_ref","successor_refs"] TLessonApplication.fields value output ∧ TLessonApplication.Conditions output
def TLessonApplication.toAst (value : TLessonApplication) : CandidateBindingAst.J :=
  .object [("authority_effect",CandidateJsonSource.Value.string value.authority_effect),("challenge_route",CandidateJsonSource.Value.string value.challenge_route),("claim_ceiling",CandidateJsonSource.Value.string value.claim_ceiling),("evidence_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.evidence_refs),("kind",CandidateJsonSource.Value.string value.kind),("lifecycle_state",CandidateJsonSource.Value.string value.lifecycle_state),("name",CandidateJsonSource.Value.string value.name),("node_id",CandidateJsonSource.Value.string value.node_id),("owner_ref",CandidateJsonSource.Value.string value.owner_ref),("payload",TLessonApplication_payload.toAst value.payload),("relation_refs",(fun values => CandidateJsonSource.Value.array (values.map TLessonApplication_relation_refs_items.toAst)) value.relation_refs),("schema_version",CandidateJsonSource.Value.string value.schema_version),("scope_ref",CandidateJsonSource.Value.string value.scope_ref),("successor_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.successor_refs)]

structure TOperationalLesson_payload where
  applicability : String
  classification_assignment_refs : List (String)
  counterevidence_refs : List (String)
  evidence_refs : List (String)
  exclusions : List (String)
  expires_at : String
  falsifier : String
  lesson_statement : String
  predicted_benefit : String
  retention_policy_ref : String
  scope_refs : List (String)
  status : String
  deriving DecidableEq, Repr

def TOperationalLesson_payload.fields : CandidateBindingAst.Fields TOperationalLesson_payload :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 0 none true) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 0 none false) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 0 none true) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 0 none true) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 0 none true) (CandidateBindingAst.cons (stringProfile 1 none none none) CandidateBindingAst.empty))))))))))))
    (fun p => TOperationalLesson_payload.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1 p.2.2.2.2.2.1 p.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.1)
def TOperationalLesson_payload.rawDecoder : CandidateBindingAst.Decoder TOperationalLesson_payload :=
  CandidateBindingAst.object ["applicability","classification_assignment_refs","counterevidence_refs","evidence_refs","exclusions","expires_at","falsifier","lesson_statement","predicted_benefit","retention_policy_ref","scope_refs","status"] TOperationalLesson_payload.fields
def TOperationalLesson_payload.Conditions (_value : TOperationalLesson_payload) : Prop := True
instance : DecidablePred TOperationalLesson_payload.Conditions := fun value => by
  unfold TOperationalLesson_payload.Conditions
  infer_instance
def TOperationalLesson_payload.decoder : CandidateBindingAst.Decoder TOperationalLesson_payload :=
  constrained TOperationalLesson_payload.rawDecoder TOperationalLesson_payload.Conditions
def TOperationalLesson_payload.Meaning (value : CandidateBindingAst.J) (output : TOperationalLesson_payload) : Prop :=
  CandidateBindingAst.ObjectMeaning ["applicability","classification_assignment_refs","counterevidence_refs","evidence_refs","exclusions","expires_at","falsifier","lesson_statement","predicted_benefit","retention_policy_ref","scope_refs","status"] TOperationalLesson_payload.fields value output ∧ TOperationalLesson_payload.Conditions output
def TOperationalLesson_payload.toAst (value : TOperationalLesson_payload) : CandidateBindingAst.J :=
  .object [("applicability",CandidateJsonSource.Value.string value.applicability),("classification_assignment_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.classification_assignment_refs),("counterevidence_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.counterevidence_refs),("evidence_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.evidence_refs),("exclusions",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.exclusions),("expires_at",CandidateJsonSource.Value.string value.expires_at),("falsifier",CandidateJsonSource.Value.string value.falsifier),("lesson_statement",CandidateJsonSource.Value.string value.lesson_statement),("predicted_benefit",CandidateJsonSource.Value.string value.predicted_benefit),("retention_policy_ref",CandidateJsonSource.Value.string value.retention_policy_ref),("scope_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.scope_refs),("status",CandidateJsonSource.Value.string value.status)]

structure TOperationalLesson_relation_refs_items where
  counterpart_kind : String
  counterpart_ref : String
  direction : String
  relation_kind_ref : String
  deriving DecidableEq, Repr

def TOperationalLesson_relation_refs_items.fields : CandidateBindingAst.Fields TOperationalLesson_relation_refs_items :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 0 none (some ["agent-action","agent-reflection","challenge-event","classification-value","decision","evidence-set","failure-assessment","feedback-record","finding","improvement-target","lesson-application","lesson-outcome-assessment","measurement-result","observation","operational-lesson","operational-observation","policy"]) none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 0 none (some ["source","target"]) none) (CandidateBindingAst.cons (stringProfile 0 none (some ["relation.applies-lesson","relation.challenges","relation.declares-effect-on","relation.derives-from","relation.evidence-bears-on","relation.governed-by","relation.instance-of","relation.produces","relation.successor-of"]) none) CandidateBindingAst.empty))))
    (fun p => TOperationalLesson_relation_refs_items.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1)
def TOperationalLesson_relation_refs_items.rawDecoder : CandidateBindingAst.Decoder TOperationalLesson_relation_refs_items :=
  CandidateBindingAst.object ["counterpart_kind","counterpart_ref","direction","relation_kind_ref"] TOperationalLesson_relation_refs_items.fields
def TOperationalLesson_relation_refs_items.Conditions (_value : TOperationalLesson_relation_refs_items) : Prop := True
instance : DecidablePred TOperationalLesson_relation_refs_items.Conditions := fun value => by
  unfold TOperationalLesson_relation_refs_items.Conditions
  infer_instance
def TOperationalLesson_relation_refs_items.decoder : CandidateBindingAst.Decoder TOperationalLesson_relation_refs_items :=
  constrained TOperationalLesson_relation_refs_items.rawDecoder TOperationalLesson_relation_refs_items.Conditions
def TOperationalLesson_relation_refs_items.Meaning (value : CandidateBindingAst.J) (output : TOperationalLesson_relation_refs_items) : Prop :=
  CandidateBindingAst.ObjectMeaning ["counterpart_kind","counterpart_ref","direction","relation_kind_ref"] TOperationalLesson_relation_refs_items.fields value output ∧ TOperationalLesson_relation_refs_items.Conditions output
def TOperationalLesson_relation_refs_items.toAst (value : TOperationalLesson_relation_refs_items) : CandidateBindingAst.J :=
  .object [("counterpart_kind",CandidateJsonSource.Value.string value.counterpart_kind),("counterpart_ref",CandidateJsonSource.Value.string value.counterpart_ref),("direction",CandidateJsonSource.Value.string value.direction),("relation_kind_ref",CandidateJsonSource.Value.string value.relation_kind_ref)]

structure TOperationalLesson where
  authority_effect : String
  challenge_route : String
  claim_ceiling : String
  evidence_refs : List (String)
  kind : String
  lifecycle_state : String
  name : String
  node_id : String
  owner_ref : String
  payload : TOperationalLesson_payload
  relation_refs : List (TOperationalLesson_relation_refs_items)
  schema_version : String
  scope_ref : String
  successor_refs : List (String)
  deriving DecidableEq, Repr

def TOperationalLesson.fields : CandidateBindingAst.Fields TOperationalLesson :=
  CandidateBindingAst.mapFields (CandidateBindingAst.cons (stringProfile 0 (some "none") none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 0 none true) (CandidateBindingAst.cons (stringProfile 0 (some "operational-lesson") none none) (CandidateBindingAst.cons (stringProfile 0 none (some ["candidate","active","historical","retired"]) none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons TOperationalLesson_payload.decoder (CandidateBindingAst.cons (boundedArray TOperationalLesson_relation_refs_items.decoder 1 none false) (CandidateBindingAst.cons (stringProfile 0 (some "cyberalchemy-lab-operational-lesson/v1") none none) (CandidateBindingAst.cons (stringProfile 1 none none none) (CandidateBindingAst.cons (boundedArray (stringProfile 1 none none none) 0 none true) CandidateBindingAst.empty))))))))))))))
    (fun p => TOperationalLesson.mk p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1 p.2.2.2.2.2.1 p.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2.2.2.2.2.2.1)
def TOperationalLesson.rawDecoder : CandidateBindingAst.Decoder TOperationalLesson :=
  CandidateBindingAst.object ["authority_effect","challenge_route","claim_ceiling","evidence_refs","kind","lifecycle_state","name","node_id","owner_ref","payload","relation_refs","schema_version","scope_ref","successor_refs"] TOperationalLesson.fields
def TOperationalLesson.Conditions (_value : TOperationalLesson) : Prop := True
instance : DecidablePred TOperationalLesson.Conditions := fun value => by
  unfold TOperationalLesson.Conditions
  infer_instance
def TOperationalLesson.decoder : CandidateBindingAst.Decoder TOperationalLesson :=
  constrained TOperationalLesson.rawDecoder TOperationalLesson.Conditions
def TOperationalLesson.Meaning (value : CandidateBindingAst.J) (output : TOperationalLesson) : Prop :=
  CandidateBindingAst.ObjectMeaning ["authority_effect","challenge_route","claim_ceiling","evidence_refs","kind","lifecycle_state","name","node_id","owner_ref","payload","relation_refs","schema_version","scope_ref","successor_refs"] TOperationalLesson.fields value output ∧ TOperationalLesson.Conditions output
def TOperationalLesson.toAst (value : TOperationalLesson) : CandidateBindingAst.J :=
  .object [("authority_effect",CandidateJsonSource.Value.string value.authority_effect),("challenge_route",CandidateJsonSource.Value.string value.challenge_route),("claim_ceiling",CandidateJsonSource.Value.string value.claim_ceiling),("evidence_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.evidence_refs),("kind",CandidateJsonSource.Value.string value.kind),("lifecycle_state",CandidateJsonSource.Value.string value.lifecycle_state),("name",CandidateJsonSource.Value.string value.name),("node_id",CandidateJsonSource.Value.string value.node_id),("owner_ref",CandidateJsonSource.Value.string value.owner_ref),("payload",TOperationalLesson_payload.toAst value.payload),("relation_refs",(fun values => CandidateJsonSource.Value.array (values.map TOperationalLesson_relation_refs_items.toAst)) value.relation_refs),("schema_version",CandidateJsonSource.Value.string value.schema_version),("scope_ref",CandidateJsonSource.Value.string value.scope_ref),("successor_refs",(fun values => CandidateJsonSource.Value.array (values.map CandidateJsonSource.Value.string)) value.successor_refs)]

inductive Kind where
  | lesson_application
  | operational_lesson
  deriving DecidableEq, Repr

inductive Body where
  | lesson_application (value : TLessonApplication)
  | operational_lesson (value : TOperationalLesson)
  deriving DecidableEq, Repr

def decoderForKind : Kind → CandidateBindingAst.Decoder Body
  | .lesson_application => mapped TLessonApplication.decoder Body.lesson_application
  | .operational_lesson => mapped TOperationalLesson.decoder Body.operational_lesson

def Body.toAst : Body → CandidateBindingAst.J
  | .lesson_application value => TLessonApplication.toAst value
  | .operational_lesson value => TOperationalLesson.toAst value

def Body.identity : Body → String
  | .lesson_application value => value.node_id
  | .operational_lesson value => value.node_id

theorem lesson_application_complete_record_exact (value : CandidateBindingAst.J) (output : TLessonApplication) :
    TLessonApplication.decoder.decode value = some output ↔ TLessonApplication.Meaning value output :=
  TLessonApplication.decoder.exact value output

theorem operational_lesson_complete_record_exact (value : CandidateBindingAst.J) (output : TOperationalLesson) :
    TOperationalLesson.decoder.decode value = some output ↔ TOperationalLesson.Meaning value output :=
  TOperationalLesson.decoder.exact value output

#print axioms lesson_application_complete_record_exact
#print axioms operational_lesson_complete_record_exact
end RelationalSuccessor.CandidateLessonSource
