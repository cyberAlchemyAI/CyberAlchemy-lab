import ActsForCandidate

set_option autoImplicit false

namespace RelationalSuccessor.CandidateIntentAddressing
open RelationalSuccessor

inductive SubjectKind where
  | agentAssignment | goal | product | productCapability | project | researchInquiry | other
  deriving DecidableEq, Repr

def allowedSources : List SubjectKind :=
  [.agentAssignment, .goal, .product, .productCapability, .project, .researchInquiry]

structure Subject where
  ref : RevisionRef
  kind : SubjectKind
  accountableHolder : RevisionRef
  deriving DecidableEq, Repr

structure Intent where
  ref : RevisionRef
  direction : String
  deriving DecidableEq, Repr

structure Resolution where
  ref : RevisionRef
  scope : RevisionRef
  intent : RevisionRef
  ownerDecision : RevisionRef
  selectedSubjects : List RevisionRef
  excludedSubjects : List RevisionRef
  satisfactionTests : List RevisionRef
  deriving DecidableEq, Repr

structure Role where
  ref : RevisionRef
  code : String
  subjectKind : SubjectKind
  deriving DecidableEq, Repr

-- This owned primary witness supplies the role mapping absent from the raw
-- Intent Resolution carrier. Its capture/source refinement remains to be proved.
structure Selection where
  ref : RevisionRef
  resolution : RevisionRef
  subject : RevisionRef
  ownerDecision : RevisionRef
  role : RevisionRef
  frame : Frame
  deriving DecidableEq, Repr

structure TestAssessment where
  resolution : RevisionRef
  intent : RevisionRef
  test : RevisionRef
  frame : Frame
  value : Truth
  deriving DecidableEq, Repr

structure WorkContract where
  ref : RevisionRef
  subject : RevisionRef
  requirements : List RevisionRef
  deriving DecidableEq, Repr

inductive ContainerKind where
  | project | product
  deriving DecidableEq, Repr

structure Container where
  ref : RevisionRef
  kind : ContainerKind
  deriving DecidableEq, Repr

structure Membership where
  subject : Subject
  container : Container
  frame : Frame
  deriving DecidableEq, Repr

def AllowedMembership (source : SubjectKind) (target : ContainerKind) : Prop :=
  (source = .agentAssignment ∧ target = .project) ∨
  (source = .goal ∧ target = .project) ∨
  (source = .product ∧ target = .product) ∨
  (source = .productCapability ∧ target = .product) ∨
  (source = .researchInquiry ∧ target = .project)

-- Each catalog is independently captured typed context. Authenticity, exact
-- catalog consistency and full source decoding are explicit future premises.
structure World where
  profile : RevisionRef
  context : RevisionRef
  scope : RevisionRef
  snapshot : RevisionRef
  timeDomain : String
  subjects : List Subject
  intents : List Intent
  resolutions : List Resolution
  decisions : List RevisionRef
  tests : List RevisionRef
  roles : List Role
  selections : List Selection
  testAssessments : List TestAssessment
  workContracts : List WorkContract
  requirementRoots : List Definition
  requirementCatalog : Catalog
  fulfillmentAssessments : List Assessment
  containers : List Container
  memberships : List Membership
  authority : CandidateActsFor.World

structure Claim where
  subject : Subject
  intent : Intent
  resolution : Resolution
  role : Role
  selection : Selection
  resolutionQualifier : RevisionRef
  addressingRole : String
  deriving DecidableEq, Repr

structure Addresses (w : World) (c : Claim) : Prop where
  sourcePair : c.subject.kind ∈ allowedSources
  subjectOwned : c.subject ∈ w.subjects
  intentOwned : c.intent ∈ w.intents
  resolutionOwned : c.resolution ∈ w.resolutions
  resolutionScope : c.resolution.scope = w.scope
  target : c.resolution.intent = c.intent.ref
  selected : c.subject.ref ∈ c.resolution.selectedSubjects
  notExcluded : c.subject.ref ∉ c.resolution.excludedSubjects
  selectedDistinct : c.resolution.selectedSubjects.Nodup
  excludedDistinct : c.resolution.excludedSubjects.Nodup
  testsDistinct : c.resolution.satisfactionTests.Nodup
  decisionOwned : c.resolution.ownerDecision ∈ w.decisions
  testsOwned : ∀ test ∈ c.resolution.satisfactionTests, test ∈ w.tests
  selectionOwned : c.selection ∈ w.selections
  selectionResolution : c.selection.resolution = c.resolution.ref
  selectionSubject : c.selection.subject = c.subject.ref
  selectionDecision : c.selection.ownerDecision = c.resolution.ownerDecision
  roleOwned : c.role ∈ w.roles
  roleKind : c.role.subjectKind = c.subject.kind
  selectionRole : c.selection.role = c.role.ref
  roleNonempty : c.role.code ≠ ""
  resolutionQualifier : c.resolutionQualifier = c.resolution.ref
  roleQualifier : c.addressingRole = c.role.code
  frameSubject : c.selection.frame.subject = c.subject.ref
  frameTarget : c.selection.frame.target = c.intent.ref
  frameProfile : c.selection.frame.profile = w.profile
  frameContext : c.selection.frame.context = w.context
  frameScope : c.selection.frame.scope = w.scope
  frameSnapshot : c.selection.frame.snapshot = w.snapshot
  frameTimeDomain : c.selection.frame.timeDomain = w.timeDomain

def ExactTest (c : Claim) (test : RevisionRef) (assessment : TestAssessment) : Prop :=
  assessment.resolution = c.resolution.ref ∧ assessment.intent = c.intent.ref ∧
  assessment.test = test ∧ assessment.frame = c.selection.frame

def Satisfied (w : World) (c : Claim) : Prop :=
  c.resolution.satisfactionTests ≠ [] ∧ c.resolution.satisfactionTests.Nodup ∧
  ∀ test ∈ c.resolution.satisfactionTests,
    (∃ assessment ∈ w.testAssessments, ExactTest c test assessment ∧ assessment.value = .yes) ∧
    (∀ assessment ∈ w.testAssessments, ExactTest c test assessment → assessment.value ≠ .no)

-- This uses independently owned complete requirements, not caller-selected
-- criteria or a "completed" flag. Raw WorkContract/E03 bridging remains pending.
def Completed (w : World) (c : Claim) : Prop :=
  ∃ contract ∈ w.workContracts, contract.subject = c.subject.ref ∧
    contract.requirements ≠ [] ∧ contract.requirements.Nodup ∧
    ∀ required ∈ contract.requirements, ∃ criteria,
      FulfillmentMeaning w.requirementRoots w.requirementCatalog required
        c.selection.frame w.fulfillmentAssessments criteria

def Authorized (w : World) (c : Claim) (right : CandidateActsFor.Right) : Prop :=
  CandidateActsFor.DelegatedRight w.authority c.selection.frame c.subject.accountableHolder right

def HasMembership (w : World) (c : Claim) : Prop :=
  ∃ membership ∈ w.memberships,
    membership.subject = c.subject ∧ membership.container ∈ w.containers ∧
    membership.frame = c.selection.frame ∧
    AllowedMembership membership.subject.kind membership.container.kind

theorem excluded_subject_refuses (w : World) (c : Claim)
    (excluded : c.subject.ref ∈ c.resolution.excludedSubjects) : ¬ Addresses w c := by
  intro h; exact h.notExcluded excluded

theorem unselected_subject_refuses (w : World) (c : Claim)
    (unselected : c.subject.ref ∉ c.resolution.selectedSubjects) : ¬ Addresses w c := by
  intro h; exact unselected h.selected

theorem other_source_kind_refuses (w : World) (c : Claim)
    (other : c.subject.kind = .other) : ¬ Addresses w c := by
  intro h
  have source := h.sourcePair
  simp [other, allowedSources] at source

theorem wrong_intent_refuses (w : World) (c : Claim)
    (wrong : c.resolution.intent ≠ c.intent.ref) : ¬ Addresses w c := by
  intro h; exact wrong h.target

theorem wrong_resolution_qualifier_refuses (w : World) (c : Claim)
    (wrong : c.resolutionQualifier ≠ c.resolution.ref) : ¬ Addresses w c := by
  intro h; exact wrong h.resolutionQualifier

theorem wrong_role_kind_refuses (w : World) (c : Claim)
    (wrong : c.role.subjectKind ≠ c.subject.kind) : ¬ Addresses w c := by
  intro h; exact wrong h.roleKind

theorem missing_owner_decision_refuses (w : World) (c : Claim)
    (missing : c.resolution.ownerDecision ∉ w.decisions) : ¬ Addresses w c := by
  intro h; exact missing h.decisionOwned

theorem wrong_snapshot_refuses (w : World) (c : Claim)
    (wrong : c.selection.frame.snapshot ≠ w.snapshot) : ¬ Addresses w c := by
  intro h; exact wrong h.frameSnapshot

theorem empty_tests_do_not_establish_satisfaction (w : World) (c : Claim)
    (empty : c.resolution.satisfactionTests = []) : ¬ Satisfied w c := by
  intro h; exact h.1 empty

theorem project_cannot_gain_membership_from_selection (container : ContainerKind) :
    ¬ AllowedMembership .project container := by
  simp [AllowedMembership]

structure State where
  testAssessments : List TestAssessment
  fulfillmentAssessments : List Assessment
  memberships : List Membership
  protectedState : CandidateActsFor.ProtectedState
  records : List Selection
  deriving DecidableEq, Repr

def record (state : State) (selection : Selection) : State :=
  { state with records := state.records ++ [selection] }

theorem record_preserves_tests (state : State) (selection : Selection) :
    (record state selection).testAssessments = state.testAssessments := rfl
theorem record_preserves_fulfillment (state : State) (selection : Selection) :
    (record state selection).fulfillmentAssessments = state.fulfillmentAssessments := rfl
theorem record_preserves_membership (state : State) (selection : Selection) :
    (record state selection).memberships = state.memberships := rfl
theorem record_preserves_protected_state (state : State) (selection : Selection) :
    (record state selection).protectedState = state.protectedState := rfl

#print axioms excluded_subject_refuses
#print axioms unselected_subject_refuses
#print axioms other_source_kind_refuses
#print axioms wrong_intent_refuses
#print axioms wrong_resolution_qualifier_refuses
#print axioms wrong_role_kind_refuses
#print axioms missing_owner_decision_refuses
#print axioms wrong_snapshot_refuses
#print axioms empty_tests_do_not_establish_satisfaction
#print axioms project_cannot_gain_membership_from_selection
#print axioms record_preserves_tests
#print axioms record_preserves_fulfillment
#print axioms record_preserves_membership
#print axioms record_preserves_protected_state
end RelationalSuccessor.CandidateIntentAddressing
