import SemanticLogic
import InferenceCore
import ObligationSemantics

namespace Successor
open Relational

-- Source meaning fixed independently from any runtime projector.
structure ConformanceTuple where
  subject : NodeRef
  target : NodeRef
  scope : String
  deriving DecidableEq, Repr
abbrev MemberConformance (g : Relational.Graph) (x : ConformanceTuple) : Prop :=
  Inv g ∧ ∃ e ∈ g.assertions, ∃ ver ev,
    Relational.Logic.ConformsAt g e x.scope ver ev ∧ e.source = x.subject ∧ e.target = x.target
abbrev MemberKind (g : Relational.Graph) (r : NodeRef) (k : NodeKind) : Prop :=
  Inv g ∧ ∃ n ∈ g.nodes, n.ref = r ∧ n.kind = k
structure Vocabulary where
  conformance : Inference.Key
  targetKind : Inference.Key
  unary : Inference.Key
  deriving DecidableEq, Repr
def referenceValue (r : NodeRef) : Inference.Value := .reference r.id r.version
def conformanceAtom (v : Vocabulary) (x : ConformanceTuple) : Inference.Atom :=
  ⟨v.conformance, [referenceValue x.subject, referenceValue x.target, .scope x.scope]⟩
def kindName : NodeKind → String
  | .admissionTransaction => "admission-transaction"
  | .agentCapability => "agent-capability"
  | .agentProfile => "agent-profile"
  | .artifactType => "artifact-type"
  | .capabilityInstance => "capability-instance"
  | .capabilityRealizationBinding => "capability-realization-binding"
  | .challengeEvent => "challenge-event"
  | .classificationAssignment => "classification-assignment"
  | .communicationPreference => "communication-preference"
  | .context => "context"
  | .contextProfile => "context-profile"
  | .contract => "contract"
  | .decision => "decision"
  | .definition => "definition"
  | .delegation => "delegation"
  | .effect => "effect"
  | .failureAssessment => "failure-assessment"
  | .failureControlBinding => "failure-control-binding"
  | .failureMode => "failure-mode"
  | .failureOccurrence => "failure-occurrence"
  | .generatedOutput => "generated-output"
  | .governedModel => "governed-model"
  | .improvementTarget => "improvement-target"
  | .incident => "incident"
  | .intentResolution => "intent-resolution"
  | .operationalLesson => "operational-lesson"
  | .productCapability => "product-capability"
  | .projectGovernanceEventHistory => "project-governance-event-history"
  | .projectSemanticEventHistory => "project-semantic-event-history"
  | .projectState => "project-state"
  | .relationKind => "relation-kind"
def kindAtom (v : Vocabulary) (r : NodeRef) (k : NodeKind) : Inference.Atom :=
  ⟨v.targetKind, [referenceValue r, .text (kindName k)]⟩
def unaryAtom (v : Vocabulary) (r : NodeRef) : Inference.Atom :=
  ⟨v.unary, [referenceValue r]⟩
inductive ProducerClass where
  | sealedObservation | derivedInformation | independentRoot | rootPreserving
  deriving DecidableEq, Repr
abbrev Sealed (keys : List Inference.Key) (a : Inference.Atom) : Prop := a.predicate ∈ keys
abbrev NoSealedHeads (T : Inference.Theory) (keys : List Inference.Key) : Prop :=
  ∀ i, Inference.ValidInstance T i → ¬ Sealed keys i.head
-- Strong source interpretation is distinct from generic Horn SemanticModel.
abbrev SourceFaithful (keys : List Inference.Key) (observed : List Inference.Atom)
    (M : Inference.Atom → Prop) : Prop :=
  ∀ a, Sealed keys a → (M a ↔ a ∈ observed)

inductive ConditionStatus where
  | holds | doesNotHold | unknown
  deriving DecidableEq, Repr
structure EvaluationKey where
  profile : String
  condition : NodeRef
  context : NodeRef
  subject : NodeRef
  target : NodeRef
  scope : String
  epoch : Option Nat
  deriving DecidableEq, Repr
structure Evaluation where
  id : String
  key : EvaluationKey
  status : ConditionStatus
  evidence : String
  deriving DecidableEq, Repr
abbrev RefValid (r : NodeRef) : Prop := r.id ≠ "" ∧ r.version ≠ ""
abbrev EvaluationKeyValid (k : EvaluationKey) : Prop :=
  k.profile ≠ "" ∧ RefValid k.condition ∧ RefValid k.context ∧
  RefValid k.subject ∧ RefValid k.target ∧ k.scope ≠ ""
abbrev EvaluationValid (e : Evaluation) : Prop :=
  e.id ≠ "" ∧ EvaluationKeyValid e.key ∧ e.evidence ≠ ""
abbrev EvaluationConsistent (es : List Evaluation) (k : EvaluationKey) : Prop :=
  ∀ a ∈ es, ∀ b ∈ es, a.key = k → b.key = k → a.status = b.status
abbrev CheckedHolds (es : List Evaluation) (k : EvaluationKey) : Prop :=
  EvaluationKeyValid k ∧ (∀ e ∈ es, EvaluationValid e) ∧
  EvaluationConsistent es k ∧ ∃ e ∈ es, e.key = k ∧ e.status = .holds
abbrev PotentialNorm (g : Stress.Graph) (f : Stress.Fact) : Prop := Stress.Origin g f
abbrev StressRefEquals (r : Stress.Ref) (s : NodeRef) : Prop := r.id = s.id ∧ r.version = s.version
-- Runtime source mapping must additionally bind condition revision to its interpretation record.
abbrev ActiveNorm (g : Stress.Graph) (f : Stress.Fact) (es : List Evaluation)
    (k : EvaluationKey) : Prop :=
  PotentialNorm g f ∧ k.condition.id = f.edge.condition ∧
  StressRefEquals f.edge.subject k.subject ∧ StressRefEquals f.edge.contract k.target ∧
  k.scope = f.edge.scope ∧ CheckedHolds es k
abbrev ActiveConflict (g : Stress.Graph) (f h : Stress.Fact) (es : List Evaluation)
    (kf kh : EvaluationKey) : Prop :=
  ActiveNorm g f es kf ∧ ActiveNorm g h es kh ∧
  kf.context = kh.context ∧ kf.epoch = kh.epoch ∧ kf.profile = kh.profile ∧
  Stress.ConflictPair f h
-- Separate requirement satisfaction remains deliberately uninterpreted/deferred.
inductive ClaimScope where
  | candidateValid | observed | derivation | completeClosure | countermodel
  | potentialNorm | activeNorm | activeConflict | shadowReady
  deriving DecidableEq, Repr
end Successor
