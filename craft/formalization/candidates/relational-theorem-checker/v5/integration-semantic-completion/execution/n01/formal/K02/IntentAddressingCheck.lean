import IntentAddressingCandidate

set_option autoImplicit false

namespace RelationalSuccessor.CandidateIntentAddressing.Checker
open RelationalSuccessor

-- False means unqualified in this resolved fragment, not factual falsehood.
-- Raw decoding, unknown/unsupported classification and catalog authenticity are pending.
inductive Diagnostic where
  | sourcePair
  | subjectOwned
  | intentOwned
  | resolutionOwned
  | resolutionScope
  | target
  | selected
  | notExcluded
  | selectedDistinct
  | excludedDistinct
  | testsDistinct
  | decisionOwned
  | testsOwned
  | selectionOwned
  | selectionResolution
  | selectionSubject
  | selectionDecision
  | roleOwned
  | roleKind
  | selectionRole
  | roleNonempty
  | resolutionQualifier
  | roleQualifier
  | frameSubject
  | frameTarget
  | frameProfile
  | frameContext
  | frameScope
  | frameSnapshot
  | frameTimeDomain
  deriving DecidableEq, Repr

def checks (w : World) (c : Claim) : List (Diagnostic × Bool) :=
  [
    (.sourcePair, decide (c.subject.kind ∈ allowedSources)),
    (.subjectOwned, decide (c.subject ∈ w.subjects)),
    (.intentOwned, decide (c.intent ∈ w.intents)),
    (.resolutionOwned, decide (c.resolution ∈ w.resolutions)),
    (.resolutionScope, decide (c.resolution.scope = w.scope)),
    (.target, decide (c.resolution.intent = c.intent.ref)),
    (.selected, decide (c.subject.ref ∈ c.resolution.selectedSubjects)),
    (.notExcluded, decide (c.subject.ref ∉ c.resolution.excludedSubjects)),
    (.selectedDistinct, decide (c.resolution.selectedSubjects.Nodup)),
    (.excludedDistinct, decide (c.resolution.excludedSubjects.Nodup)),
    (.testsDistinct, decide (c.resolution.satisfactionTests.Nodup)),
    (.decisionOwned, decide (c.resolution.ownerDecision ∈ w.decisions)),
    (.testsOwned, c.resolution.satisfactionTests.all (fun test => decide (test ∈ w.tests))),
    (.selectionOwned, decide (c.selection ∈ w.selections)),
    (.selectionResolution, decide (c.selection.resolution = c.resolution.ref)),
    (.selectionSubject, decide (c.selection.subject = c.subject.ref)),
    (.selectionDecision, decide (c.selection.ownerDecision = c.resolution.ownerDecision)),
    (.roleOwned, decide (c.role ∈ w.roles)),
    (.roleKind, decide (c.role.subjectKind = c.subject.kind)),
    (.selectionRole, decide (c.selection.role = c.role.ref)),
    (.roleNonempty, decide (c.role.code ≠ "")),
    (.resolutionQualifier, decide (c.resolutionQualifier = c.resolution.ref)),
    (.roleQualifier, decide (c.addressingRole = c.role.code)),
    (.frameSubject, decide (c.selection.frame.subject = c.subject.ref)),
    (.frameTarget, decide (c.selection.frame.target = c.intent.ref)),
    (.frameProfile, decide (c.selection.frame.profile = w.profile)),
    (.frameContext, decide (c.selection.frame.context = w.context)),
    (.frameScope, decide (c.selection.frame.scope = w.scope)),
    (.frameSnapshot, decide (c.selection.frame.snapshot = w.snapshot)),
    (.frameTimeDomain, decide (c.selection.frame.timeDomain = w.timeDomain))
  ]

def check (w : World) (c : Claim) : Bool := (checks w c).all (fun item => item.2)

def failed : List (Diagnostic × Bool) → List Diagnostic
  | [] => []
  | (code, passed) :: rest => if passed then failed rest else code :: failed rest

def diagnostics (w : World) (c : Claim) : List Diagnostic := failed (checks w c)

theorem check_exact (w : World) (c : Claim) : check w c = true ↔ Addresses w c := by
  have parts : check w c = true ↔
    (c.subject.kind ∈ allowedSources) ∧
    (c.subject ∈ w.subjects) ∧
    (c.intent ∈ w.intents) ∧
    (c.resolution ∈ w.resolutions) ∧
    (c.resolution.scope = w.scope) ∧
    (c.resolution.intent = c.intent.ref) ∧
    (c.subject.ref ∈ c.resolution.selectedSubjects) ∧
    (c.subject.ref ∉ c.resolution.excludedSubjects) ∧
    (c.resolution.selectedSubjects.Nodup) ∧
    (c.resolution.excludedSubjects.Nodup) ∧
    (c.resolution.satisfactionTests.Nodup) ∧
    (c.resolution.ownerDecision ∈ w.decisions) ∧
    (∀ test ∈ c.resolution.satisfactionTests, test ∈ w.tests) ∧
    (c.selection ∈ w.selections) ∧
    (c.selection.resolution = c.resolution.ref) ∧
    (c.selection.subject = c.subject.ref) ∧
    (c.selection.ownerDecision = c.resolution.ownerDecision) ∧
    (c.role ∈ w.roles) ∧
    (c.role.subjectKind = c.subject.kind) ∧
    (c.selection.role = c.role.ref) ∧
    (c.role.code ≠ "") ∧
    (c.resolutionQualifier = c.resolution.ref) ∧
    (c.addressingRole = c.role.code) ∧
    (c.selection.frame.subject = c.subject.ref) ∧
    (c.selection.frame.target = c.intent.ref) ∧
    (c.selection.frame.profile = w.profile) ∧
    (c.selection.frame.context = w.context) ∧
    (c.selection.frame.scope = w.scope) ∧
    (c.selection.frame.snapshot = w.snapshot) ∧
    (c.selection.frame.timeDomain = w.timeDomain) := by
    simp [check, checks, List.all_eq_true]
  constructor
  · intro h
    rcases parts.mp h with ⟨h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14, h15, h16, h17, h18, h19, h20, h21, h22, h23, h24, h25, h26, h27, h28, h29⟩
    exact ⟨h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14, h15, h16, h17, h18, h19, h20, h21, h22, h23, h24, h25, h26, h27, h28, h29⟩
  · intro h
    exact parts.mpr ⟨h.sourcePair, h.subjectOwned, h.intentOwned, h.resolutionOwned, h.resolutionScope, h.target, h.selected, h.notExcluded, h.selectedDistinct, h.excludedDistinct, h.testsDistinct, h.decisionOwned, h.testsOwned, h.selectionOwned, h.selectionResolution, h.selectionSubject, h.selectionDecision, h.roleOwned, h.roleKind, h.selectionRole, h.roleNonempty, h.resolutionQualifier, h.roleQualifier, h.frameSubject, h.frameTarget, h.frameProfile, h.frameContext, h.frameScope, h.frameSnapshot, h.frameTimeDomain⟩

theorem failed_empty_exact (items : List (Diagnostic × Bool)) :
    failed items = [] ↔ items.all (fun item => item.2) = true := by
  induction items with
  | nil => simp [failed]
  | cons item rest ih =>
    rcases item with ⟨code, passed⟩
    cases passed <;> simp [failed, ih]

theorem diagnostics_empty_exact (w : World) (c : Claim) :
    diagnostics w c = [] ↔ Addresses w c :=
  (failed_empty_exact (checks w c)).trans (check_exact w c)

theorem refusal_has_diagnostic (w : World) (c : Claim) (refused : ¬ Addresses w c) :
    diagnostics w c ≠ [] := by
  intro empty
  exact refused ((diagnostics_empty_exact w c).mp empty)

#print axioms check_exact
#print axioms failed_empty_exact
#print axioms diagnostics_empty_exact
#print axioms refusal_has_diagnostic
end RelationalSuccessor.CandidateIntentAddressing.Checker
