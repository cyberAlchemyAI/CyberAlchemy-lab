import IntentAddressingCandidate

set_option autoImplicit false

namespace RelationalSuccessor.CandidateIntentAddressing.Witnesses
open RelationalSuccessor

def ref (name : String) : RevisionRef := ⟨⟨"fixture", name, "1"⟩, name⟩
def kindName : SubjectKind → String
  | .agentAssignment => "agent-assignment"
  | .goal => "goal"
  | .product => "product"
  | .productCapability => "product-capability"
  | .project => "project"
  | .researchInquiry => "research-inquiry"
  | .other => "other"
def subject (kind : SubjectKind) : Subject :=
  ⟨ref ("subject:" ++ kindName kind), kind, ref "holder"⟩
def intent : Intent := ⟨ref "intent", "Establish a sound bounded relation checker"⟩
def resolution (kind : SubjectKind) : Resolution :=
  ⟨ref ("resolution:" ++ kindName kind), ref "scope", intent.ref, ref "owner-decision",
    [(subject kind).ref], [ref "excluded-output"], [ref "Q1", ref "Q2"]⟩
def role (kind : SubjectKind) : Role :=
  ⟨ref ("role:" ++ kindName kind), "intent-carrier", kind⟩
def frame (kind : SubjectKind) : Frame := ⟨ref "profile", (subject kind).ref, intent.ref,
  ref "context", ref "scope", ref "snapshot", 5, "fixture-time"⟩
def selection (kind : SubjectKind) : Selection :=
  ⟨ref ("selection:" ++ kindName kind), (resolution kind).ref, (subject kind).ref,
    ref "owner-decision", (role kind).ref, frame kind⟩
def right : CandidateActsFor.Right := ⟨"modify-checker", ref "checker", ref "scope"⟩
def emptyAuthority : CandidateActsFor.World :=
  ⟨[], [], [], [], [], [], [], [], (fun _ _ => .unknown), [right]⟩
def world (kind : SubjectKind) : World :=
  ⟨ref "profile", ref "context", ref "scope", ref "snapshot", "fixture-time",
    [subject kind], [intent], [resolution kind], [ref "owner-decision"],
    [ref "Q1", ref "Q2"], [role kind], [selection kind], [], [], [], [], [], [], [],
    emptyAuthority⟩
def claim (kind : SubjectKind) : Claim :=
  ⟨subject kind, intent, resolution kind, role kind, selection kind,
    (resolution kind).ref, (role kind).code⟩

theorem legitimate_addressing (kind : SubjectKind) (allowed : kind ∈ allowedSources) :
    Addresses (world kind) (claim kind) := by
  refine {
    sourcePair := allowed
    subjectOwned := by simp [world, claim]
    intentOwned := by simp [world, claim]
    resolutionOwned := by simp [world, claim]
    resolutionScope := rfl
    target := rfl
    selected := by simp [claim, resolution]
    notExcluded := ?_
    selectedDistinct := by simp [claim, resolution]
    excludedDistinct := by simp [claim, resolution]
    testsDistinct := ?_
    decisionOwned := by simp [world, claim, resolution]
    testsOwned := ?_
    selectionOwned := by simp [world, claim]
    selectionResolution := rfl
    selectionSubject := rfl
    selectionDecision := rfl
    roleOwned := by simp [world, claim]
    roleKind := rfl
    selectionRole := rfl
    roleNonempty := by decide
    resolutionQualifier := rfl
    roleQualifier := rfl
    frameSubject := rfl
    frameTarget := rfl
    frameProfile := rfl
    frameContext := rfl
    frameScope := rfl
    frameSnapshot := rfl
    frameTimeDomain := rfl
  }
  · cases kind <;> decide
  · change ([ref "Q1", ref "Q2"] : List RevisionRef).Nodup
    decide
  · intro test h; exact h

theorem legitimate_agent_assignment_branch : Addresses (world .agentAssignment) (claim .agentAssignment) :=
  legitimate_addressing .agentAssignment (by decide)
theorem legitimate_goal_branch : Addresses (world .goal) (claim .goal) :=
  legitimate_addressing .goal (by decide)
theorem legitimate_product_branch : Addresses (world .product) (claim .product) :=
  legitimate_addressing .product (by decide)
theorem legitimate_product_capability_branch : Addresses (world .productCapability) (claim .productCapability) :=
  legitimate_addressing .productCapability (by decide)
theorem legitimate_project_branch : Addresses (world .project) (claim .project) :=
  legitimate_addressing .project (by decide)
theorem legitimate_research_inquiry_branch : Addresses (world .researchInquiry) (claim .researchInquiry) :=
  legitimate_addressing .researchInquiry (by decide)

theorem selection_does_not_satisfy_intent (kind : SubjectKind) :
    ¬ Satisfied (world kind) (claim kind) := by
  intro h
  rcases (h.2.2 (ref "Q1") (by decide)).1 with ⟨assessment, captured, _⟩
  simp [world] at captured

theorem selection_does_not_complete_work (kind : SubjectKind) :
    ¬ Completed (world kind) (claim kind) := by
  rintro ⟨contract, captured, _⟩
  simp [world] at captured

theorem selection_does_not_authorize_changes (kind : SubjectKind) :
    ¬ Authorized (world kind) (claim kind) right := by
  rintro ⟨delegation, captured, _⟩
  simp [world, emptyAuthority] at captured

theorem selection_does_not_create_membership (kind : SubjectKind) :
    ¬ HasMembership (world kind) (claim kind) := by
  rintro ⟨membership, captured, _⟩
  simp [world] at captured

theorem satisfaction_non_entailment_all_six (kind : SubjectKind) (allowed : kind ∈ allowedSources) :
    Addresses (world kind) (claim kind) ∧ ¬ Satisfied (world kind) (claim kind) :=
  ⟨legitimate_addressing kind allowed, selection_does_not_satisfy_intent kind⟩
theorem completion_non_entailment_all_six (kind : SubjectKind) (allowed : kind ∈ allowedSources) :
    Addresses (world kind) (claim kind) ∧ ¬ Completed (world kind) (claim kind) :=
  ⟨legitimate_addressing kind allowed, selection_does_not_complete_work kind⟩
theorem authority_non_entailment_all_six (kind : SubjectKind) (allowed : kind ∈ allowedSources) :
    Addresses (world kind) (claim kind) ∧ ¬ Authorized (world kind) (claim kind) right :=
  ⟨legitimate_addressing kind allowed, selection_does_not_authorize_changes kind⟩
theorem membership_non_entailment_all_six (kind : SubjectKind) (allowed : kind ∈ allowedSources) :
    Addresses (world kind) (claim kind) ∧ ¬ HasMembership (world kind) (claim kind) :=
  ⟨legitimate_addressing kind allowed, selection_does_not_create_membership kind⟩

theorem selected_and_excluded_subject_refuses :
    ¬ Addresses (world .project) { claim .project with resolution :=
      { resolution .project with excludedSubjects := [(subject .project).ref] } } := by
  apply excluded_subject_refuses
  decide

theorem unselected_subject_refuses_example :
    ¬ Addresses (world .project) { claim .project with resolution :=
      { resolution .project with selectedSubjects := [] } } := by
  apply unselected_subject_refuses
  decide

theorem other_kind_refuses_example : ¬ Addresses (world .other) (claim .other) :=
  other_source_kind_refuses _ _ rfl

theorem wrong_intent_refuses_example :
    ¬ Addresses (world .project) { claim .project with resolution :=
      { resolution .project with intent := ref "different-intent" } } := by
  apply wrong_intent_refuses
  decide

theorem wrong_resolution_qualifier_refuses_example :
    ¬ Addresses (world .project) { claim .project with resolutionQualifier := ref "other-resolution" } := by
  apply wrong_resolution_qualifier_refuses
  decide

theorem wrong_endpoint_role_refuses_example :
    ¬ Addresses (world .project) { claim .project with role :=
      { role .project with subjectKind := .researchInquiry } } := by
  apply wrong_role_kind_refuses
  decide

theorem missing_owner_decision_refuses_example :
    ¬ Addresses { world .project with decisions := [] } (claim .project) := by
  apply missing_owner_decision_refuses
  simp

theorem stale_snapshot_refuses_example :
    ¬ Addresses (world .project) { claim .project with selection :=
      { selection .project with frame := { frame .project with snapshot := ref "stale" } } } := by
  apply wrong_snapshot_refuses
  decide

theorem empty_tests_cannot_satisfy_example :
    ¬ Satisfied (world .project) { claim .project with resolution :=
      { resolution .project with satisfactionTests := [] } } :=
  empty_tests_do_not_establish_satisfaction _ _ rfl

def assessment (test : RevisionRef) (value : Truth) : TestAssessment :=
  ⟨(resolution .project).ref, intent.ref, test, frame .project, value⟩
def satisfiedWorld : World := { world .project with testAssessments :=
  [assessment (ref "Q1") .yes, assessment (ref "Q2") .yes] }
def partialWorld : World := { world .project with testAssessments := [assessment (ref "Q1") .yes] }
def conflictWorld : World := { satisfiedWorld with testAssessments :=
  satisfiedWorld.testAssessments ++ [assessment (ref "Q2") .no] }

theorem independent_tests_satisfy_intent : Satisfied satisfiedWorld (claim .project) := by
  refine ⟨by decide, by decide, ?_⟩
  intro test h
  have choices : test = ref "Q1" ∨ test = ref "Q2" := by simpa [claim, resolution] using h
  constructor
  · rcases choices with first | second
    · subst test; exact ⟨assessment (ref "Q1") .yes, by decide, by unfold ExactTest; decide, rfl⟩
    · subst test; exact ⟨assessment (ref "Q2") .yes, by decide, by unfold ExactTest; decide, rfl⟩
  · intro observed captured _
    have choices : observed = assessment (ref "Q1") .yes ∨
        observed = assessment (ref "Q2") .yes := by simpa [satisfiedWorld] using captured
    rcases choices with first | second
    · subst observed; decide
    · subst observed; decide

theorem incomplete_tests_do_not_satisfy_intent : ¬ Satisfied partialWorld (claim .project) := by
  intro h
  rcases (h.2.2 (ref "Q2") (by decide)).1 with ⟨observed, captured, exactTest, _⟩
  have same : observed = assessment (ref "Q1") .yes := by simpa [partialWorld] using captured
  subst observed
  have mismatch : (assessment (ref "Q1") .yes).test ≠ ref "Q2" := by decide
  exact mismatch exactTest.2.2.1

theorem conflicting_tests_do_not_satisfy_intent : ¬ Satisfied conflictWorld (claim .project) := by
  intro h
  have noNegative := (h.2.2 (ref "Q2") (by decide)).2
  exact noNegative (assessment (ref "Q2") .no) (by decide) (by unfold ExactTest; decide) rfl

theorem addressing_with_independent_satisfaction : Addresses satisfiedWorld (claim .project) := by
  cases legitimate_project_branch
  constructor <;> assumption

theorem satisfaction_can_coexist_with_addressing :
    Addresses satisfiedWorld (claim .project) ∧ Satisfied satisfiedWorld (claim .project) :=
  ⟨addressing_with_independent_satisfaction, independent_tests_satisfy_intent⟩

theorem satisfaction_does_not_complete_work_example :
    Satisfied satisfiedWorld (claim .project) ∧ ¬ Completed satisfiedWorld (claim .project) := by
  refine ⟨independent_tests_satisfy_intent, ?_⟩
  rintro ⟨contract, captured, _⟩
  simp [satisfiedWorld, world] at captured

def projectContainer : Container := ⟨ref "container-project", .project⟩
def inquiryMembership : Membership := ⟨subject .researchInquiry, projectContainer, frame .researchInquiry⟩
def membershipWorld : World := { world .researchInquiry with
  containers := [projectContainer], memberships := [inquiryMembership] }

theorem independent_membership_coexists_with_addressing :
    Addresses membershipWorld (claim .researchInquiry) ∧ HasMembership membershipWorld (claim .researchInquiry) := by
  constructor
  · cases legitimate_research_inquiry_branch
    constructor <;> assumption
  · exact ⟨inquiryMembership, by decide, rfl, by decide, rfl, by unfold AllowedMembership; decide⟩

#print axioms legitimate_addressing
#print axioms legitimate_agent_assignment_branch
#print axioms legitimate_goal_branch
#print axioms legitimate_product_branch
#print axioms legitimate_product_capability_branch
#print axioms legitimate_project_branch
#print axioms legitimate_research_inquiry_branch
#print axioms selection_does_not_satisfy_intent
#print axioms selection_does_not_complete_work
#print axioms selection_does_not_authorize_changes
#print axioms selection_does_not_create_membership
#print axioms satisfaction_non_entailment_all_six
#print axioms completion_non_entailment_all_six
#print axioms authority_non_entailment_all_six
#print axioms membership_non_entailment_all_six
#print axioms selected_and_excluded_subject_refuses
#print axioms unselected_subject_refuses_example
#print axioms other_kind_refuses_example
#print axioms wrong_intent_refuses_example
#print axioms wrong_resolution_qualifier_refuses_example
#print axioms wrong_endpoint_role_refuses_example
#print axioms missing_owner_decision_refuses_example
#print axioms stale_snapshot_refuses_example
#print axioms empty_tests_cannot_satisfy_example
#print axioms independent_tests_satisfy_intent
#print axioms incomplete_tests_do_not_satisfy_intent
#print axioms conflicting_tests_do_not_satisfy_intent
#print axioms addressing_with_independent_satisfaction
#print axioms satisfaction_can_coexist_with_addressing
#print axioms satisfaction_does_not_complete_work_example
#print axioms independent_membership_coexists_with_addressing
end RelationalSuccessor.CandidateIntentAddressing.Witnesses
