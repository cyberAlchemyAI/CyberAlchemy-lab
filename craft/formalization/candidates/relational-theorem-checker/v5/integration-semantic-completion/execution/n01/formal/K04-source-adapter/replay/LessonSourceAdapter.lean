import LessonBodyProfiles
import LessonUseCandidate

set_option autoImplicit false

namespace RelationalSuccessor.CandidateLessonSource
open CandidateBindingAst (Decoder J)
open CandidateTypedBodies

structure Qualifiers where
  lesson_revision_ref : String
  application_posture : String
  applicability_assessment_ref : String
  instruction_precedence : String
  deriving DecidableEq, Repr

def qualifierString : Decoder String := stringProfile 1 none none none
def qualifierFields : CandidateBindingAst.Fields Qualifiers :=
  CandidateBindingAst.mapFields
    (CandidateBindingAst.cons qualifierString
      (CandidateBindingAst.cons qualifierString
        (CandidateBindingAst.cons qualifierString
          (CandidateBindingAst.cons qualifierString CandidateBindingAst.empty))))
    (fun fields => ⟨fields.1, fields.2.1, fields.2.2.1, fields.2.2.2.1⟩)
def qualifierNames : List String :=
  ["lesson_revision_ref", "application_posture", "applicability_assessment_ref", "instruction_precedence"]
def qualifierDecoder : Decoder Qualifiers := CandidateBindingAst.object qualifierNames qualifierFields
def QualifierMeaning (raw : J) (q : Qualifiers) : Prop :=
  CandidateBindingAst.ObjectMeaning qualifierNames qualifierFields raw q

theorem qualifiers_exact (raw : J) (q : Qualifiers) :
    qualifierDecoder.decode raw = some q ↔ QualifierMeaning raw q := qualifierDecoder.exact raw q

structure SourceBundle where
  application : TLessonApplication
  lesson : TOperationalLesson
  qualifiers : Qualifiers
  deriving DecidableEq, Repr

def sourceFields : CandidateBindingAst.Fields SourceBundle :=
  CandidateBindingAst.mapFields
    (CandidateBindingAst.cons TLessonApplication.decoder
      (CandidateBindingAst.cons TOperationalLesson.decoder
        (CandidateBindingAst.cons qualifierDecoder CandidateBindingAst.empty)))
    (fun fields => ⟨fields.1, fields.2.1, fields.2.2.1⟩)
def sourceNames : List String := ["application", "lesson", "qualifiers"]
def sourceDecoder : Decoder SourceBundle := CandidateBindingAst.object sourceNames sourceFields
def SourceBodyMeaning (raw : J) (output : SourceBundle) : Prop :=
  CandidateBindingAst.ObjectMeaning sourceNames sourceFields raw output

structure Resolution where
  references : List (String × CandidateLessonUse.Ref)
  postures : List (String × CandidateLessonUse.Posture)
  deriving DecidableEq, Repr

def resolveRef (r : Resolution) (token : String) : Option CandidateLessonUse.Ref :=
  (r.references.find? (fun entry => entry.1 == token)).map Prod.snd
def resolvePosture (r : Resolution) (token : String) : Option CandidateLessonUse.Posture :=
  (r.postures.find? (fun entry => entry.1 == token)).map Prod.snd
def resolveRefs (r : Resolution) (tokens : List String) : Option (List CandidateLessonUse.Ref) :=
  tokens.mapM (resolveRef r)

def ResolutionConsistent (r : Resolution) : Prop :=
  (r.references.map Prod.fst).Nodup ∧ (r.postures.map Prod.fst).Nodup
instance (r : Resolution) : Decidable (ResolutionConsistent r) :=
  inferInstanceAs (Decidable ((_ : Prop) ∧ (_ : Prop)))

-- The token map is supplied by an independently owned catalog. Neither a prefix
-- nor the spelling "applied" installs a mapping or authenticates a record.
def SourceJoins (r : Resolution) (c : CandidateLessonUse.Claim) (b : SourceBundle) : Prop :=
  ResolutionConsistent r ∧
  resolveRef r b.application.node_id = some c.application.ref ∧
  resolveRef r b.lesson.node_id = some c.target ∧
  resolveRef r b.application.owner_ref = some c.frame.owner ∧
  resolveRef r b.application.scope_ref = some c.frame.scope ∧
  resolveRef r b.application.payload.lesson_revision_ref = some c.application.lesson ∧
  resolveRef r b.application.payload.session_ref = some c.frame.session ∧
  resolvePosture r b.application.payload.application_posture = some c.application.posture ∧
  resolveRef r b.application.payload.applicability_assessment_ref = some c.application.assessment ∧
  resolveRefs r b.application.payload.conflict_refs = some c.application.conflicts ∧
  resolveRefs r b.application.payload.override_refs = some c.application.overrides ∧
  resolveRef r b.qualifiers.lesson_revision_ref = some c.lessonQualifier ∧
  resolvePosture r b.qualifiers.application_posture = some c.postureQualifier ∧
  resolveRef r b.qualifiers.applicability_assessment_ref = some c.assessmentQualifier ∧
  resolveRef r b.qualifiers.instruction_precedence = some c.precedenceQualifier ∧
  (∃ link ∈ b.application.relation_refs,
    link.relation_kind_ref = "relation.applies-lesson" ∧ link.direction = "source" ∧
    link.counterpart_kind = "operational-lesson" ∧
    resolveRef r link.counterpart_ref = some c.target)

instance (r : Resolution) (c : CandidateLessonUse.Claim) : DecidablePred (SourceJoins r c) :=
  fun _b => inferInstanceAs (Decidable ((_ : Prop) ∧ (_ : Prop)))

def SourceMeaning (r : Resolution) (w : CandidateLessonUse.World)
    (c : CandidateLessonUse.Claim) (raw : J) (b : SourceBundle) : Prop :=
  SourceBodyMeaning raw b ∧ SourceJoins r c b ∧ CandidateLessonUse.AppliesLesson w c

def qualifiedDecoder (r : Resolution) (w : CandidateLessonUse.World)
    (c : CandidateLessonUse.Claim) : Decoder SourceBundle :=
  constrained sourceDecoder (fun b => SourceJoins r c b ∧ CandidateLessonUse.AppliesLesson w c)

theorem source_adapter_exact (r : Resolution) (w : CandidateLessonUse.World)
    (c : CandidateLessonUse.Claim) (raw : J) (b : SourceBundle) :
    (qualifiedDecoder r w c).decode raw = some b ↔ SourceMeaning r w c raw b := by
  exact (qualifiedDecoder r w c).exact raw b

theorem source_success_requires_meaning (r : Resolution) (w : CandidateLessonUse.World)
    (c : CandidateLessonUse.Claim) (raw : J) (b : SourceBundle)
    (h : (qualifiedDecoder r w c).decode raw = some b) : CandidateLessonUse.AppliesLesson w c :=
  ((source_adapter_exact r w c raw b).mp h).2.2

theorem source_success_requires_unique_tokens (r : Resolution) (w : CandidateLessonUse.World)
    (c : CandidateLessonUse.Claim) (raw : J) (b : SourceBundle)
    (h : (qualifiedDecoder r w c).decode raw = some b) : ResolutionConsistent r :=
  ((source_adapter_exact r w c raw b).mp h).2.1.1

theorem source_success_requires_body (r : Resolution) (w : CandidateLessonUse.World)
    (c : CandidateLessonUse.Claim) (raw : J) (b : SourceBundle)
    (h : (qualifiedDecoder r w c).decode raw = some b) : SourceBodyMeaning raw b :=
  ((source_adapter_exact r w c raw b).mp h).1

theorem missing_policy_not_qualified (r : Resolution) (w : CandidateLessonUse.World)
    (c : CandidateLessonUse.Claim) (raw : J) (b : SourceBundle)
    (missing : resolveRef r b.qualifiers.instruction_precedence = none) :
    (qualifiedDecoder r w c).decode raw ≠ some b := by
  intro accepted
  have joins := ((source_adapter_exact r w c raw b).mp accepted).2.1
  have policyJoin := joins.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1
  rw [missing] at policyJoin
  cases policyJoin

def sourceCheck (r : Resolution) (w : CandidateLessonUse.World)
    (c : CandidateLessonUse.Claim) (raw : J) : Bool :=
  ((qualifiedDecoder r w c).decode raw).isSome

theorem source_check_exact (r : Resolution) (w : CandidateLessonUse.World)
    (c : CandidateLessonUse.Claim) (raw : J) :
    sourceCheck r w c raw = true ↔ ∃ b, SourceMeaning r w c raw b := by
  cases decoded : (qualifiedDecoder r w c).decode raw with
  | none => simp [sourceCheck, ← source_adapter_exact, decoded]
  | some b => simp [sourceCheck, ← source_adapter_exact, decoded]

#print axioms qualifiers_exact
#print axioms source_adapter_exact
#print axioms source_success_requires_meaning
#print axioms source_success_requires_unique_tokens
#print axioms source_success_requires_body
#print axioms missing_policy_not_qualified
#print axioms source_check_exact
end RelationalSuccessor.CandidateLessonSource
