import Std
namespace RelationalExtensions.Fulfillment
structure Ref where
  id : String
  version : String
  deriving DecidableEq, Repr
inductive Truth where
  | yes | no | unknown
  deriving DecidableEq, Repr
structure Frame where
  context : Ref
  scope : String
  epoch : Nat
  deriving DecidableEq, Repr
structure Action where
  ref : Ref
  request : Ref
  requirement : Ref
  frame : Frame
  outputs : List Ref
  accepted : Bool
  deriving DecidableEq, Repr
structure Output where
  ref : Ref
  action : Ref
  accepted : Bool
  deriving DecidableEq, Repr
structure Evaluation where
  ref : Ref
  criterion : Ref
  request : Ref
  requirement : Ref
  action : Ref
  output : Ref
  frame : Frame
  value : Truth
  deriving DecidableEq, Repr
structure Source where
  request : Ref
  requirement : Ref
  frame : Frame
  linked : Bool
  criteria : List Ref
  actions : List Action
  outputs : List Output
  evaluations : List Evaluation
  deriving DecidableEq, Repr
def exactEvidence (s : Source) (c : Ref) (e : Evaluation) : Bool :=
  decide (e.criterion = c ∧ e.request = s.request ∧ e.requirement = s.requirement ∧ e.frame = s.frame) &&
  s.actions.any (fun a => decide (a.ref = e.action ∧ a.request = s.request ∧ a.requirement = s.requirement ∧ a.frame = s.frame) && a.accepted && a.outputs.contains e.output) &&
  s.outputs.any (fun o => decide (o.ref = e.output ∧ o.action = e.action) && o.accepted)
def satisfies (s : Source) (c : Ref) : Bool :=
  s.evaluations.any (fun e => exactEvidence s c e && decide (e.value = .yes))
def fulfilled (s : Source) : Bool := s.linked && !s.criteria.isEmpty && s.criteria.all (satisfies s)
-- Independent quantified target requires an exact supported assessment per criterion.
def Meaning (s : Source) : Prop := s.linked = true ∧ s.criteria ≠ [] ∧
  ∀ c ∈ s.criteria, ∃ e ∈ s.evaluations, exactEvidence s c e = true ∧ e.value = .yes
theorem satisfaction_exact (s : Source) (c : Ref) : satisfies s c = true ↔
    ∃ e ∈ s.evaluations, exactEvidence s c e = true ∧ e.value = .yes := by
  simp [satisfies, List.any_eq_true]
theorem fulfillment_exact (s : Source) : fulfilled s = true ↔ Meaning s := by
  simp [fulfilled, Meaning, List.all_eq_true, satisfaction_exact, and_assoc]
theorem every_named_criterion (s : Source) (h : fulfilled s = true) :
    ∀ c ∈ s.criteria, ∃ e ∈ s.evaluations, exactEvidence s c e = true ∧ e.value = .yes :=
  ((fulfillment_exact s).mp h).2.2
def criterionTruth (s : Source) (c : Ref) : Truth :=
  if satisfies s c then .yes
  else if s.evaluations.any (fun e => decide (e.criterion = c ∧ e.value = .no)) then .no else .unknown
def verdict (s : Source) : Truth :=
  if fulfilled s then .yes
  else if !s.linked || s.criteria.any (fun c => decide (criterionTruth s c = .no)) then .no else .unknown
def linkedOnly : Source := ⟨⟨"request", "v1"⟩, ⟨"requirement", "v1"⟩,
  ⟨⟨"context", "v1"⟩, "review", 0⟩, true, [⟨"criterion", "v1"⟩], [], [], []⟩
theorem linkage_alone_is_not_fulfillment : linkedOnly.linked = true ∧ fulfilled linkedOnly = false := by decide
#print axioms satisfaction_exact
#print axioms fulfillment_exact
#print axioms every_named_criterion
#print axioms linkage_alone_is_not_fulfillment
end RelationalExtensions.Fulfillment
