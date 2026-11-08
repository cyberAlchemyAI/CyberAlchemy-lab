import EvidenceSemantics

namespace RelationalV3.Shadow

structure Head where
  generation : Nat
  baseline : String
  deriving DecidableEq, Repr

structure Review where
  generation : Nat
  before : String
  after : String
  deriving DecidableEq, Repr

def Matches (h : Head) (r : Review) : Prop :=
  h.generation = r.generation ∧ h.baseline = r.before

def successor (h : Head) (r : Review) : Head :=
  ⟨h.generation + 1, r.after⟩

-- The implementation's commit guard must additionally establish two live
-- qualifications: the proposal and an independent identity-extension check
-- of the exact successor baseline. JSON flags are not premises of this rule.
def Authorized (h : Head) (r : Review) (proposalFresh registrationFresh : Prop) : Prop :=
  Matches h r ∧ proposalFresh ∧ registrationFresh

theorem authorized_requires_both_live_checks (h : Head) (r : Review)
    (proposalFresh registrationFresh : Prop)
    (accepted : Authorized h r proposalFresh registrationFresh) :
    proposalFresh ∧ registrationFresh := accepted.2

-- Index the live judgments by the exact source and successor, rather than
-- treating any previous baseline registration as the required successor.
-- These judgments are supplied by P00's FreshQualified verifier boundary,
-- with the implementation's exact checked-request identity correspondence.
def ExactAuthorized (h : Head) (r : Review)
    (proposalFresh : String → String → Prop)
    (registrationFresh : String → Prop) : Prop :=
  Matches h r ∧ proposalFresh r.before r.after ∧ registrationFresh r.after

theorem exact_guard_has_fresh_registered_successor (h : Head) (r : Review)
    (proposalFresh : String → String → Prop)
    (registrationFresh : String → Prop)
    (accepted : ExactAuthorized h r proposalFresh registrationFresh) :
    proposalFresh h.baseline r.after ∧ registrationFresh (successor h r).baseline := by
  constructor
  · rw [accepted.1.2]
    exact accepted.2.1
  · exact accepted.2.2

theorem previous_baseline_is_not_changed_successor (h : Head) (r : Review)
    (matching : Matches h r) (changed : r.before ≠ r.after) :
    h.baseline ≠ (successor h r).baseline := by
  simpa [successor, matching.2] using changed

theorem one_reviewed_generation_cannot_commit_twice (h : Head) (a b : Review)
    (first : Matches h a) (sameReviewedGeneration : a.generation = b.generation) :
    ¬ Matches (successor h a) b := by
  intro second
  have eq : h.generation + 1 = h.generation := by
    calc
      h.generation + 1 = b.generation := second.1
      _ = a.generation := sameReviewedGeneration.symm
      _ = h.generation := first.1.symm
  exact Nat.ne_of_gt (Nat.lt_succ_self h.generation) eq

inductive Recovery where
  | headCurrent | abortedPrepared | repairedMirror | reconciliationRequired
  deriving DecidableEq, Repr

-- Recovery classification depends on authoritative transactional metadata,
-- exact artifact bindings and the explicitly recorded mirror-write window.
-- It does not infer filesystem atomicity or durability from graph theorems.
def classifyRecovery (committed artifactsCurrent mirrorCurrent
    recordedMirrorWindow oldMirrorExact : Bool) : Recovery :=
  if !artifactsCurrent then .reconciliationRequired
  else if mirrorCurrent then if committed then .headCurrent else .abortedPrepared
  else if committed && recordedMirrorWindow && oldMirrorExact then .repairedMirror
  else .reconciliationRequired

theorem conflicting_artifacts_require_reconciliation (c m w o : Bool) :
    classifyRecovery c false m w o = .reconciliationRequired := by
  simp [classifyRecovery]

theorem completed_head_cannot_repair_an_unrecorded_mirror (o : Bool) :
    classifyRecovery true true false false o = .reconciliationRequired := by
  simp [classifyRecovery]

end RelationalV3.Shadow

#print axioms RelationalV3.Shadow.authorized_requires_both_live_checks
#print axioms RelationalV3.Shadow.exact_guard_has_fresh_registered_successor
#print axioms RelationalV3.Shadow.previous_baseline_is_not_changed_successor
#print axioms RelationalV3.Shadow.one_reviewed_generation_cannot_commit_twice
#print axioms RelationalV3.Shadow.conflicting_artifacts_require_reconciliation
#print axioms RelationalV3.Shadow.completed_head_cannot_repair_an_unrecorded_mirror
