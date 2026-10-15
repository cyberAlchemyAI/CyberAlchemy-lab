import ActsForCandidate

set_option autoImplicit false

-- N01 candidate preparation. Raw schema refinement and complete rule closure
-- are not supplied by this resolved finite model or by the synthetic examples.
namespace RelationalSuccessor.CandidateImprovementAddressing
open RelationalSuccessor
namespace Delegated
abbrev World := CandidateActsFor.World
abbrev Right := CandidateActsFor.Right
end Delegated

structure SourcePolicy where
  ref : RevisionRef
  allowedKinds : List String
  selectionCriteria : List String
  freshnessRule : String
  conflictHandling : String
  deriving DecidableEq, Repr

structure Inquiry where
  ref : RevisionRef
  owner : RevisionRef
  project : RevisionRef
  goals : List RevisionRef
  scope : RevisionRef
  method : RevisionRef
  question : String
  sourcePolicy : SourcePolicy
  inclusions : List String
  exclusions : List String
  stoppingConditions : List String
  limitations : List String
  sources : List RevisionRef
  evidenceAggregates : List RevisionRef
  counterevidence : List RevisionRef
  findings : List RevisionRef
  createdAt : Nat
  updatedAt : Nat
  timeDomain : String
  ownerRoute : String
  challengeRoute : String
  claimCeiling : String
  deriving DecidableEq, Repr

-- Source success_measure_refs remain distinct from an E03 Requirement. A later
-- bridge must derive the complete target criteria from the owned measure policy.
structure Target where
  ref : RevisionRef
  statement : String
  affectedScopes : List RevisionRef
  basis : List RevisionRef
  priorityPosture : String
  researchRoute : RevisionRef
  successMeasures : List RevisionRef
  deriving DecidableEq, Repr

inductive ResearchPurpose where
  | investigate | compare | assessEvidence
  deriving DecidableEq, Repr

structure Role where
  ref : RevisionRef
  code : String
  purpose : ResearchPurpose
  deriving DecidableEq, Repr

structure IntentRecord where
  ref : RevisionRef
  inquiry : RevisionRef
  target : RevisionRef
  role : RevisionRef
  frame : Frame
  deriving DecidableEq, Repr

structure ResolutionAssessment where
  target : RevisionRef
  measure : RevisionRef
  frame : Frame
  value : Truth
  deriving DecidableEq, Repr

inductive Direction where
  | lower | higher
  deriving DecidableEq, Repr

structure Metric where
  ref : RevisionRef
  direction : Direction
  deriving DecidableEq, Repr

structure Comparison where
  target : RevisionRef
  metric : Metric
  frame : Frame
  beforeValue : Nat
  afterValue : Nat
  deriving DecidableEq, Repr

structure Prioritization where
  target : RevisionRef
  queue : RevisionRef
  policy : RevisionRef
  frame : Frame
  position : Nat
  deriving DecidableEq, Repr

-- Lists are independently verified typed context. They are not populated from
-- request flags. A source adapter must justify ownership, complete snapshots,
-- non-equivocation and the recorded posture; this model assumes that context.
structure World where
  profile : RevisionRef
  context : RevisionRef
  snapshot : RevisionRef
  timeDomain : String
  projects : List RevisionRef
  goals : List RevisionRef
  scopes : List RevisionRef
  methods : List RevisionRef
  sourcePolicies : List SourcePolicy
  inquiries : List Inquiry
  targets : List Target
  roles : List Role
  intentRecords : List IntentRecord
  resolutionAssessments : List ResolutionAssessment
  metrics : List Metric
  comparisons : List Comparison
  queues : List RevisionRef
  priorityPolicies : List RevisionRef
  prioritizations : List Prioritization
  authority : Delegated.World

def NonemptyDistinct (xs : List String) : Prop :=
  xs ≠ [] ∧ xs.Nodup ∧ ∀ text ∈ xs, text ≠ ""

-- This independent research predicate has no Improvement Target or relation
-- existence premise. The raw schema's Unicode/regex/byte bounds are not proved.
structure ValidInquiry (w : World) (i : Inquiry) : Prop where
  captured : i ∈ w.inquiries
  project : i.project ∈ w.projects
  goalsNonempty : i.goals ≠ []
  goalsDistinct : i.goals.Nodup
  goalsOwned : ∀ goal ∈ i.goals, goal ∈ w.goals
  scope : i.scope ∈ w.scopes
  method : i.method ∈ w.methods
  question : i.question ≠ ""
  sourcePolicy : i.sourcePolicy ∈ w.sourcePolicies
  sourceKinds : NonemptyDistinct i.sourcePolicy.allowedKinds
  selectionCriteria : NonemptyDistinct i.sourcePolicy.selectionCriteria
  freshness : i.sourcePolicy.freshnessRule ≠ ""
  conflicts : i.sourcePolicy.conflictHandling ≠ ""
  inclusions : NonemptyDistinct i.inclusions
  exclusions : NonemptyDistinct i.exclusions
  stops : NonemptyDistinct i.stoppingConditions
  limitations : NonemptyDistinct i.limitations
  ownerRoute : i.ownerRoute ≠ ""
  challengeRoute : i.challengeRoute ≠ ""
  ceiling : i.claimCeiling ≠ ""
  timeDomain : i.timeDomain = w.timeDomain
  timeOrder : i.createdAt ≤ i.updatedAt

structure Claim where
  inquiry : Inquiry
  target : Target
  role : Role
  witness : IntentRecord
  targetVersionRef : RevisionRef
  addressingRole : String
  deriving DecidableEq, Repr

structure Addresses (w : World) (c : Claim) : Prop where
  inquiry : ValidInquiry w c.inquiry
  ownedTarget : c.target ∈ w.targets
  ownedRole : c.role ∈ w.roles
  capturedIntent : c.witness ∈ w.intentRecords
  witnessInquiry : c.witness.inquiry = c.inquiry.ref
  witnessTarget : c.witness.target = c.target.ref
  witnessRole : c.witness.role = c.role.ref
  targetQualifier : c.targetVersionRef = c.target.ref
  roleQualifier : c.addressingRole = c.role.code
  frameSubject : c.witness.frame.subject = c.inquiry.ref
  frameTarget : c.witness.frame.target = c.target.ref
  frameScope : c.witness.frame.scope = c.inquiry.scope
  frameProfile : c.witness.frame.profile = w.profile
  frameContext : c.witness.frame.context = w.context
  frameSnapshot : c.witness.frame.snapshot = w.snapshot
  frameTimeDomain : c.witness.frame.timeDomain = w.timeDomain

-- These are independently supplied outcome predicates, not conclusion flags
-- copied out of an Addressing claim. They can hold through separate evidence.
def Resolved (w : World) (target : Target) (f : Frame) : Prop :=
  target.successMeasures ≠ [] ∧ target.successMeasures.Nodup ∧
  ∀ measure ∈ target.successMeasures,
    (∃ assessment ∈ w.resolutionAssessments,
      assessment.target = target.ref ∧ assessment.measure = measure ∧
      assessment.frame = f ∧ assessment.value = .yes) ∧
    (∀ assessment ∈ w.resolutionAssessments,
      assessment.target = target.ref → assessment.measure = measure →
      assessment.frame = f → assessment.value ≠ .no)

def Improved (w : World) (target : Target) (f : Frame) : Prop :=
  ∃ comparison ∈ w.comparisons,
    comparison.target = target.ref ∧ comparison.metric ∈ w.metrics ∧
    comparison.metric.ref ∈ target.successMeasures ∧ comparison.frame = f ∧
    match comparison.metric.direction with
    | .lower => comparison.afterValue < comparison.beforeValue
    | .higher => comparison.beforeValue < comparison.afterValue

def Prioritized (w : World) (target : Target) (f : Frame) : Prop :=
  ∃ ordering ∈ w.prioritizations,
    ordering.target = target.ref ∧ ordering.queue ∈ w.queues ∧
    ordering.policy ∈ w.priorityPolicies ∧ ordering.frame = f

def Authorized (w : World) (c : Claim) (right : Delegated.Right) : Prop :=
  CandidateActsFor.DelegatedRight w.authority c.witness.frame c.inquiry.owner right

-- Erasing improvement-related context leaves inquiry context intact. This is
-- candidate inquiry invariance, not yet the source schema or generator proof.
def withoutImprovementContext (w : World) : World :=
  { w with targets := [], roles := [], intentRecords := [] }

theorem inquiry_survives_no_improvement_context (w : World) (i : Inquiry)
    (h : ValidInquiry w i) : ValidInquiry (withoutImprovementContext w) i := by
  cases h
  constructor <;> assumption

theorem no_targets_no_addressing (w : World) (c : Claim) (none : w.targets = []) :
    ¬ Addresses w c := by
  intro h
  have captured := h.ownedTarget
  simp [none] at captured

theorem no_intent_record_no_addressing (w : World) (c : Claim)
    (none : w.intentRecords = []) : ¬ Addresses w c := by
  intro h
  have captured := h.capturedIntent
  simp [none] at captured

theorem mismatched_target_revision_refuses (w : World) (c : Claim)
    (mismatch : c.targetVersionRef ≠ c.target.ref) : ¬ Addresses w c := by
  intro h; exact mismatch h.targetQualifier

theorem mismatched_role_code_refuses (w : World) (c : Claim)
    (mismatch : c.addressingRole ≠ c.role.code) : ¬ Addresses w c := by
  intro h; exact mismatch h.roleQualifier

theorem mismatched_witness_target_refuses (w : World) (c : Claim)
    (mismatch : c.witness.target ≠ c.target.ref) : ¬ Addresses w c := by
  intro h; exact mismatch h.witnessTarget

theorem stale_intent_snapshot_refuses (w : World) (c : Claim)
    (mismatch : c.witness.frame.snapshot ≠ w.snapshot) : ¬ Addresses w c := by
  intro h; exact mismatch h.frameSnapshot

structure OutcomeState where
  resolutions : List ResolutionAssessment
  comparisons : List Comparison
  priorities : List Prioritization
  protectedState : CandidateActsFor.ProtectedState
  records : List IntentRecord
  deriving DecidableEq, Repr

def record (s : OutcomeState) (witness : IntentRecord) : OutcomeState :=
  { s with records := s.records ++ [witness] }

theorem recording_preserves_resolutions (s : OutcomeState) (witness : IntentRecord) :
    (record s witness).resolutions = s.resolutions := rfl

theorem recording_preserves_comparisons (s : OutcomeState) (witness : IntentRecord) :
    (record s witness).comparisons = s.comparisons := rfl

theorem recording_preserves_priorities (s : OutcomeState) (witness : IntentRecord) :
    (record s witness).priorities = s.priorities := rfl

theorem recording_preserves_protected_state (s : OutcomeState) (witness : IntentRecord) :
    (record s witness).protectedState = s.protectedState := rfl

#print axioms inquiry_survives_no_improvement_context
#print axioms no_targets_no_addressing
#print axioms no_intent_record_no_addressing
#print axioms mismatched_target_revision_refuses
#print axioms mismatched_role_code_refuses
#print axioms mismatched_witness_target_refuses
#print axioms stale_intent_snapshot_refuses
#print axioms recording_preserves_resolutions
#print axioms recording_preserves_comparisons
#print axioms recording_preserves_priorities
#print axioms recording_preserves_protected_state
end RelationalSuccessor.CandidateImprovementAddressing
