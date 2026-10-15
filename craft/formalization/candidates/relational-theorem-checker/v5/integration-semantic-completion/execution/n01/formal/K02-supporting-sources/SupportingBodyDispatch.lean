import DecisionBodyProfiles
import BodyKindDispatch
set_option autoImplicit false
namespace RelationalSuccessor.CandidateSupportingSources
open CandidateBindingAst (J Decoder)
abbrev EndpointBody := CandidateTypedBodies.Body

def DecisionTag (ast : J) : Prop :=
  ∃ entries, ast = .object entries ∧ (entries.map Prod.fst).Nodup ∧
    ("kind",CandidateJsonSource.Value.string "decision") ∈ entries

def decisionTagCheck : J → Bool
  | .object entries =>
    if (entries.map Prod.fst).Nodup then
      match CandidateJsonSource.lookup entries "kind" with
      | some (.string text) => decide (text = "decision")
      | _ => false
    else false
  | _ => false

theorem decision_tag_exact (ast : J) : decisionTagCheck ast = true ↔ DecisionTag ast := by
  cases ast with
  | object entries =>
    by_cases unique : (entries.map Prod.fst).Nodup
    · have field : ("kind",CandidateJsonSource.Value.string "decision") ∈ entries ↔
          CandidateJsonSource.lookup entries "kind" = some (.string "decision") :=
        ⟨CandidateJsonSource.lookup_complete _ _ _ unique,CandidateJsonSource.lookup_sound _ _ _⟩
      cases found : CandidateJsonSource.lookup entries "kind" with
      | none => simp [decisionTagCheck,unique,DecisionTag,field,found]
      | some value => cases value <;> simp [decisionTagCheck,unique,DecisionTag,field,found]
    · simp [decisionTagCheck,unique,DecisionTag]
  | null => simp [decisionTagCheck,DecisionTag]
  | boolean value => simp [decisionTagCheck,DecisionTag]
  | number token => simp [decisionTagCheck,DecisionTag]
  | string text => simp [decisionTagCheck,DecisionTag]
  | array values => simp [decisionTagCheck,DecisionTag]

theorem decision_tag_excludes_endpoint_selector (ast : J) (tag : DecisionTag ast) :
    CandidateBodyDispatch.selectKind ast = none := by
  rcases tag with ⟨entries,same,unique,member⟩
  subst ast
  have found := CandidateJsonSource.lookup_complete entries "kind" _ unique member
  simp [CandidateBodyDispatch.selectKind,unique,CandidateBodyDispatch.selectEntries,
    found,CandidateBodyDispatch.decodeKind]

inductive FamilyBody where
  | endpoint (value : EndpointBody)
  | decision (value : TDecision)
  deriving DecidableEq, Repr

def decisionAdapter : Decoder FamilyBody := CandidateTypedBodies.mapped TDecision.decoder FamilyBody.decision
def endpointAdapter : Decoder FamilyBody := CandidateTypedBodies.mapped CandidateBodyDispatch.bodyDecoder FamilyBody.endpoint

def FamilyMeaning (ast : J) (output : FamilyBody) : Prop :=
  (DecisionTag ast ∧ CandidateTypedBodies.MappedMeaning TDecision.decoder FamilyBody.decision ast output) ∨
    (¬ DecisionTag ast ∧ CandidateTypedBodies.MappedMeaning CandidateBodyDispatch.bodyDecoder FamilyBody.endpoint ast output)

def decodeFamily (ast : J) : Option FamilyBody :=
  if decisionTagCheck ast then decisionAdapter.decode ast else endpointAdapter.decode ast

theorem family_dispatch_exact (ast : J) (output : FamilyBody) :
    decodeFamily ast = some output ↔ FamilyMeaning ast output := by
  by_cases checked : decisionTagCheck ast = true
  · have tag := (decision_tag_exact _).mp checked
    simp only [decodeFamily,checked,if_true]
    rw [decisionAdapter.exact]
    simp [decisionAdapter,CandidateTypedBodies.mapped,FamilyMeaning,tag]
  · have tag : ¬ DecisionTag ast := fun meaning => checked ((decision_tag_exact _).mpr meaning)
    simp only [decodeFamily,if_neg checked]
    rw [endpointAdapter.exact]
    simp [endpointAdapter,CandidateTypedBodies.mapped,FamilyMeaning,tag]

def familyDecoder : Decoder FamilyBody := ⟨decodeFamily,FamilyMeaning,family_dispatch_exact⟩

theorem complete_endpoint_excludes_decision_tag (ast : J) (output : EndpointBody)
    (meaning : CandidateBodyDispatch.BodyMeaning ast output) : ¬ DecisionTag ast := by
  intro tag
  have missing := decision_tag_excludes_endpoint_selector ast tag
  rcases meaning with ⟨kind,selected,_⟩
  have found := (CandidateBodyDispatch.selector_exact _ _).mpr selected
  simp [missing] at found

theorem family_endpoint_exact (ast : J) (output : EndpointBody) :
    decodeFamily ast = some (.endpoint output) ↔ CandidateBodyDispatch.BodyMeaning ast output := by
  rw [family_dispatch_exact]
  simp only [FamilyMeaning,CandidateTypedBodies.MappedMeaning,
    reduceCtorEq,and_false,exists_false,false_or,FamilyBody.endpoint.injEq,exists_eq_right]
  constructor
  · rintro ⟨_,meaning⟩; exact meaning
  · intro meaning; exact ⟨complete_endpoint_excludes_decision_tag _ _ meaning,meaning⟩

theorem family_decision_exact (ast : J) (output : TDecision) :
    decodeFamily ast = some (.decision output) ↔ DecisionTag ast ∧ TDecision.Meaning ast output := by
  rw [family_dispatch_exact]
  simp [FamilyMeaning,CandidateTypedBodies.MappedMeaning,TDecision.decoder,
    CandidateTypedBodies.constrained,CandidateTypedBodies.ConstrainedMeaning,
    TDecision.rawDecoder,CandidateBindingAst.object,TDecision.Meaning]

def FamilyBody.sourceKind : FamilyBody → String
  | .endpoint value => CandidateBodyDispatch.kindName (CandidateBodyDispatch.bodyKind value)
  | .decision _ => "decision"
def FamilyBody.identity : FamilyBody → String
  | .endpoint value => CandidateTypedBodies.Body.identity value
  | .decision value => value.node_id

#print axioms decision_tag_exact
#print axioms decision_tag_excludes_endpoint_selector
#print axioms family_dispatch_exact
#print axioms complete_endpoint_excludes_decision_tag
#print axioms family_endpoint_exact
#print axioms family_decision_exact
end RelationalSuccessor.CandidateSupportingSources
