import ActsForCandidate

set_option autoImplicit false

namespace RelationalSuccessor.CandidateScopedImpact
open RelationalSuccessor

inductive SourceKind where
  | failureOccurrence | incident | other
  deriving DecidableEq, Repr
inductive TargetKind where
  | agentCapability | agentSession | artifactType | generatedOutput | implementation
  | ontology | personReference | product | productCapability | project | work | other
  deriving DecidableEq, Repr

def allowedSources : List SourceKind := [.failureOccurrence, .incident]
def allowedTargets : List TargetKind := [.agentCapability, .agentSession, .artifactType,
  .generatedOutput, .implementation, .ontology, .personReference, .product,
  .productCapability, .project, .work]

structure Source where
  ref : RevisionRef
  kind : SourceKind
  accountablePrincipal : RevisionRef
  deriving DecidableEq, Repr
structure Target where
  ref : RevisionRef
  kind : TargetKind
  deriving DecidableEq, Repr
structure Scope where
  ref : RevisionRef
  participants : List RevisionRef
  start : Nat
  finish : Nat
  timeDomain : String
  deriving DecidableEq, Repr
inductive Posture where
  | observed | predicted | declared
  deriving DecidableEq, Repr
inductive Direction where
  | increase | decrease | change
  deriving DecidableEq, Repr
structure ImpactPolicy where
  ref : RevisionRef
  code : String
  sourceKind : SourceKind
  targetKind : TargetKind
  scopes : List RevisionRef
  observers : List RevisionRef
  methods : List RevisionRef
  metric : RevisionRef
  unit : RevisionRef
  direction : Direction
  maxAge : Nat
  deriving DecidableEq, Repr

-- Numeric changes are a synthetic measurement profile. Raw datum interpretation,
-- units and proof of physical truth are not supplied by these typed values.
structure Measurement where
  ref : RevisionRef
  subject : RevisionRef
  metric : RevisionRef
  unit : RevisionRef
  baseline : Nat
  observed : Nat
  observedAt : Nat
  timeDomain : String
  observer : RevisionRef
  method : RevisionRef
  deriving DecidableEq, Repr
structure Provenance where
  ref : RevisionRef
  measurement : RevisionRef
  action : RevisionRef
  output : RevisionRef
  sourceEvidence : RevisionRef
  frame : Frame
  deriving DecidableEq, Repr
structure Observation where
  ref : RevisionRef
  source : RevisionRef
  affectedSubject : RevisionRef
  scope : RevisionRef
  policy : RevisionRef
  posture : Posture
  measurement : RevisionRef
  provenance : RevisionRef
  frame : Frame
  deriving DecidableEq, Repr

inductive Equation where
  | direct | commonCause
  deriving DecidableEq, Repr

def evaluateEquation (equation : Equation) (intervenedSource common : Bool) : Bool :=
  match equation with
  | .direct => intervenedSource
  | .commonCause => common

structure CausalModel where
  ref : RevisionRef
  source : RevisionRef
  target : RevisionRef
  equation : Equation
  common : Bool
  frame : Frame
  deriving DecidableEq, Repr

inductive Grade where
  | minor | moderate | major
  deriving DecidableEq, Repr
structure SeverityPolicy where
  ref : RevisionRef
  metric : RevisionRef
  unit : RevisionRef
  moderateAt : Nat
  majorAt : Nat
  deriving DecidableEq, Repr
structure SeverityAssessment where
  ref : RevisionRef
  source : RevisionRef
  target : RevisionRef
  measurement : RevisionRef
  policy : RevisionRef
  grade : Grade
  frame : Frame
  deriving DecidableEq, Repr
structure Duty where
  ref : RevisionRef
  actor : RevisionRef
  subject : RevisionRef
  metric : RevisionRef
  unit : RevisionRef
  maximum : Nat
  deriving DecidableEq, Repr
structure ResponsibilityAssessment where
  ref : RevisionRef
  source : RevisionRef
  target : RevisionRef
  actor : RevisionRef
  duty : RevisionRef
  measurement : RevisionRef
  justification : RevisionRef
  frame : Frame
  deriving DecidableEq, Repr
structure Ownership where
  ref : RevisionRef
  owner : RevisionRef
  artifact : RevisionRef
  frame : Frame
  deriving DecidableEq, Repr

structure World where
  profile : RevisionRef
  context : RevisionRef
  snapshot : RevisionRef
  epoch : Nat
  timeDomain : String
  sources : List Source := []
  targets : List Target := []
  scopes : List Scope := []
  policies : List ImpactPolicy := []
  observations : List Observation := []
  measurements : List Measurement := []
  -- These are independently captured admissible roots, not proposal approval flags.
  provenanceRoots : List Provenance := []
  evidenceRoots : List RevisionRef := []
  actions : List RevisionRef := []
  outputs : List RevisionRef := []
  causalModels : List CausalModel := []
  severityPolicies : List SeverityPolicy := []
  severityAssessments : List SeverityAssessment := []
  duties : List Duty := []
  responsibilityAssessments : List ResponsibilityAssessment := []
  justificationRoots : List RevisionRef := []
  ownershipRecords : List Ownership := []

structure Claim where
  source : Source
  target : Target
  scope : Scope
  policy : ImpactPolicy
  observation : Observation
  measurement : Measurement
  provenance : Provenance
  scopeQualifier : RevisionRef
  postureQualifier : String
  deriving DecidableEq, Repr

def ImpactChange (policy : ImpactPolicy) (measurement : Measurement) : Prop :=
  match policy.direction with
  | .increase => measurement.baseline < measurement.observed
  | .decrease => measurement.observed < measurement.baseline
  | .change => measurement.baseline ≠ measurement.observed

structure Affects (w : World) (c : Claim) : Prop where
  sourceKind : c.source.kind ∈ allowedSources
  targetKind : c.target.kind ∈ allowedTargets
  sourceOwned : c.source ∈ w.sources
  targetOwned : c.target ∈ w.targets
  scopeOwned : c.scope ∈ w.scopes
  policyOwned : c.policy ∈ w.policies
  observationOwned : c.observation ∈ w.observations
  measurementOwned : c.measurement ∈ w.measurements
  provenanceOwned : c.provenance ∈ w.provenanceRoots
  scopeQualifier : c.scopeQualifier = c.scope.ref
  postureQualifier : c.postureQualifier = c.policy.code
  policyNonempty : c.policy.code ≠ ""
  policySource : c.policy.sourceKind = c.source.kind
  policyTarget : c.policy.targetKind = c.target.kind
  permittedScope : c.scope.ref ∈ c.policy.scopes
  scopedSource : c.source.ref ∈ c.scope.participants
  scopedTarget : c.target.ref ∈ c.scope.participants
  scopeOrdered : c.scope.start ≤ c.scope.finish
  scopeStart : c.scope.start ≤ c.observation.frame.epoch
  scopeFinish : c.observation.frame.epoch ≤ c.scope.finish
  scopeTime : c.scope.timeDomain = w.timeDomain
  observed : c.observation.posture = .observed
  source : c.observation.source = c.source.ref
  target : c.observation.affectedSubject = c.target.ref
  scope : c.observation.scope = c.scope.ref
  policy : c.observation.policy = c.policy.ref
  measurement : c.observation.measurement = c.measurement.ref
  provenance : c.observation.provenance = c.provenance.ref
  measuredSubject : c.measurement.subject = c.target.ref
  metric : c.measurement.metric = c.policy.metric
  unit : c.measurement.unit = c.policy.unit
  observer : c.measurement.observer ∈ c.policy.observers
  method : c.measurement.method ∈ c.policy.methods
  measurementTime : c.measurement.timeDomain = w.timeDomain
  notFuture : c.measurement.observedAt ≤ c.observation.frame.epoch
  fresh : c.observation.frame.epoch ≤ c.measurement.observedAt + c.policy.maxAge
  impact : ImpactChange c.policy c.measurement
  provenanceMeasurement : c.provenance.measurement = c.measurement.ref
  evidenceRoot : c.provenance.sourceEvidence ∈ w.evidenceRoots
  actionOwned : c.provenance.action ∈ w.actions
  outputOwned : c.provenance.output ∈ w.outputs
  provenanceFrame : c.provenance.frame = c.observation.frame
  frameSource : c.observation.frame.subject = c.source.ref
  frameTarget : c.observation.frame.target = c.target.ref
  frameScope : c.observation.frame.scope = c.scope.ref
  frameProfile : c.observation.frame.profile = w.profile
  frameContext : c.observation.frame.context = w.context
  frameSnapshot : c.observation.frame.snapshot = w.snapshot
  frameEpoch : c.observation.frame.epoch = w.epoch
  frameTime : c.observation.frame.timeDomain = w.timeDomain

-- Intervention dependence is separate from the observed association. This finite
-- deterministic profile is not a general causal identification procedure.
def Causes (w : World) (c : Claim) : Prop :=
  ∃ model ∈ w.causalModels, model.source = c.source.ref ∧ model.target = c.target.ref ∧
    model.frame = c.observation.frame ∧
    evaluateEquation model.equation true model.common ≠ evaluateEquation model.equation false model.common

def delta (m : Measurement) : Nat :=
  if m.baseline ≤ m.observed then m.observed - m.baseline else m.baseline - m.observed

def classify (p : SeverityPolicy) (m : Measurement) : Grade :=
  if p.majorAt ≤ delta m then .major else if p.moderateAt ≤ delta m then .moderate else .minor

def AssessedSeverity (w : World) (c : Claim) : Prop :=
  ∃ assessment ∈ w.severityAssessments, ∃ policy ∈ w.severityPolicies,
    assessment.source = c.source.ref ∧ assessment.target = c.target.ref ∧
    assessment.measurement = c.measurement.ref ∧ assessment.frame = c.observation.frame ∧
    assessment.policy = policy.ref ∧ policy.metric = c.measurement.metric ∧
    policy.unit = c.measurement.unit ∧ policy.moderateAt < policy.majorAt ∧
    assessment.grade = classify policy c.measurement

def Blamed (w : World) (c : Claim) : Prop :=
  ∃ assessment ∈ w.responsibilityAssessments, ∃ duty ∈ w.duties,
    assessment.source = c.source.ref ∧ assessment.target = c.target.ref ∧
    assessment.actor = c.source.accountablePrincipal ∧ assessment.duty = duty.ref ∧
    duty.actor = assessment.actor ∧ duty.subject = c.target.ref ∧
    assessment.measurement = c.measurement.ref ∧ assessment.frame = c.observation.frame ∧
    assessment.justification ∈ w.justificationRoots ∧
    duty.metric = c.measurement.metric ∧ duty.unit = c.measurement.unit ∧
    duty.maximum < c.measurement.observed

def HasOwnership (w : World) (c : Claim) : Prop :=
  ∃ record ∈ w.ownershipRecords, record.owner = c.source.accountablePrincipal ∧
    record.artifact = c.target.ref ∧ record.frame = c.observation.frame

theorem predicted_impact_refuses (w : World) (c : Claim)
    (predicted : c.observation.posture = .predicted) : ¬ Affects w c := by
  intro h
  have clash := predicted.symm.trans h.observed
  cases clash

theorem unowned_measurement_refuses (w : World) (c : Claim)
    (unowned : c.measurement ∉ w.measurements) : ¬ Affects w c := by
  intro h; exact unowned h.measurementOwned

theorem scope_widening_refuses (w : World) (c : Claim)
    (outside : c.target.ref ∉ c.scope.participants) : ¬ Affects w c := by
  intro h; exact outside h.scopedTarget

theorem unsupported_provenance_refuses (w : World) (c : Claim)
    (missing : c.provenance ∉ w.provenanceRoots) : ¬ Affects w c := by
  intro h; exact missing h.provenanceOwned

theorem arbitrary_posture_code_refuses (w : World) (c : Claim)
    (wrong : c.postureQualifier ≠ c.policy.code) : ¬ Affects w c := by
  intro h; exact wrong h.postureQualifier

theorem no_impact_change_refuses (w : World) (c : Claim)
    (unchanged : ¬ ImpactChange c.policy c.measurement) : ¬ Affects w c := by
  intro h; exact unchanged h.impact

theorem stale_measurement_refuses (w : World) (c : Claim)
    (stale : c.measurement.observedAt + c.policy.maxAge < c.observation.frame.epoch) : ¬ Affects w c := by
  intro h; exact Nat.not_le_of_gt stale h.fresh

theorem future_measurement_refuses (w : World) (c : Claim)
    (future : c.observation.frame.epoch < c.measurement.observedAt) : ¬ Affects w c := by
  intro h; exact Nat.not_le_of_gt future h.notFuture

theorem wrong_snapshot_refuses (w : World) (c : Claim)
    (wrong : c.observation.frame.snapshot ≠ w.snapshot) : ¬ Affects w c := by
  intro h; exact wrong h.frameSnapshot

theorem common_cause_has_no_source_intervention_effect (common : Bool) :
    evaluateEquation .commonCause true common = evaluateEquation .commonCause false common := rfl

theorem direct_equation_has_source_intervention_effect (common : Bool) :
    evaluateEquation .direct true common ≠ evaluateEquation .direct false common := by decide

structure State where
  causalModels : List CausalModel
  severityAssessments : List SeverityAssessment
  responsibilityAssessments : List ResponsibilityAssessment
  ownershipRecords : List Ownership
  protectedState : CandidateActsFor.ProtectedState
  records : List Observation
  deriving DecidableEq, Repr

def record (state : State) (observation : Observation) : State :=
  { state with records := state.records ++ [observation] }

theorem record_preserves_causal_models (state : State) (observation : Observation) :
    (record state observation).causalModels = state.causalModels := rfl
theorem record_preserves_severity (state : State) (observation : Observation) :
    (record state observation).severityAssessments = state.severityAssessments := rfl
theorem record_preserves_responsibility (state : State) (observation : Observation) :
    (record state observation).responsibilityAssessments = state.responsibilityAssessments := rfl
theorem record_preserves_ownership (state : State) (observation : Observation) :
    (record state observation).ownershipRecords = state.ownershipRecords := rfl
theorem record_preserves_protected_state (state : State) (observation : Observation) :
    (record state observation).protectedState = state.protectedState := rfl

#print axioms predicted_impact_refuses
#print axioms unowned_measurement_refuses
#print axioms scope_widening_refuses
#print axioms unsupported_provenance_refuses
#print axioms arbitrary_posture_code_refuses
#print axioms no_impact_change_refuses
#print axioms stale_measurement_refuses
#print axioms future_measurement_refuses
#print axioms wrong_snapshot_refuses
#print axioms common_cause_has_no_source_intervention_effect
#print axioms direct_equation_has_source_intervention_effect
#print axioms record_preserves_causal_models
#print axioms record_preserves_severity
#print axioms record_preserves_responsibility
#print axioms record_preserves_ownership
#print axioms record_preserves_protected_state
end RelationalSuccessor.CandidateScopedImpact
