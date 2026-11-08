import Init

namespace Relational

inductive RelationKind where
  | conformsTo | declaresEffectOn | materializesConsequence
  deriving DecidableEq, Repr

inductive NodeKind where
  | admissionTransaction
  | agentCapability
  | agentProfile
  | artifactType
  | capabilityInstance
  | capabilityRealizationBinding
  | challengeEvent
  | classificationAssignment
  | communicationPreference
  | context
  | contextProfile
  | contract
  | decision
  | definition
  | delegation
  | effect
  | failureAssessment
  | failureControlBinding
  | failureMode
  | failureOccurrence
  | generatedOutput
  | governedModel
  | improvementTarget
  | incident
  | intentResolution
  | operationalLesson
  | productCapability
  | projectGovernanceEventHistory
  | projectSemanticEventHistory
  | projectState
  | relationKind
  deriving DecidableEq, Repr

structure NodeRef where
  id : String
  version : String
  deriving DecidableEq, Repr

structure Node where
  ref : NodeRef
  kind : NodeKind
  contentIdentity : String
  deriving DecidableEq, Repr

inductive Qualifiers where
  | conformance (scope exactVersion evidenceRef : String)
  | effect (effectKind exactTargetVersion : String)
  | materialization (receiptRef role outputDigest : String)
  deriving DecidableEq, Repr

structure Assertion where
  id : String
  kind : RelationKind
  source : NodeRef
  target : NodeRef
  qualifiers : Qualifiers
  deriving DecidableEq, Repr

inductive AssessmentMode where
  | conformance | applicationReceipt
  deriving DecidableEq, Repr

structure Assessment where
  ref : String
  mode : AssessmentMode
  subject : NodeRef
  target : NodeRef
  scope : String
  role : String
  outputDigest : String
  accepted : Bool
  deriving DecidableEq, Repr

structure AdmissionRoot where
  subject : NodeRef
  decision : NodeRef
  authorityEvidence : String
  deriving DecidableEq, Repr

-- This describes a proposed rule; F0 has no inference execution function.
structure InferenceRule where
  id : String
  premiseKinds : List RelationKind
  conclusionKind : RelationKind
  deriving DecidableEq, Repr

structure Graph where
  nodes : List Node
  assessments : List Assessment
  assertions : List Assertion
  admissionRoots : List AdmissionRoot
  deriving DecidableEq, Repr

def applyAddition (g : Graph) (e : Assertion) : Graph :=
  { g with assertions := g.assertions ++ [e] }

end Relational
