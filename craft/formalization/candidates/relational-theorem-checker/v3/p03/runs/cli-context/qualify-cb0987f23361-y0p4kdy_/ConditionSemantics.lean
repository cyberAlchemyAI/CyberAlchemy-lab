import RequiredStatements
import StressLaws

namespace Successor.Conditions
open Successor
instance (r : Relational.NodeRef) : Decidable (RefValid r) := by unfold RefValid; infer_instance
instance (k : EvaluationKey) : Decidable (EvaluationKeyValid k) := by unfold EvaluationKeyValid; infer_instance
instance (e : Evaluation) : Decidable (EvaluationValid e) := by unfold EvaluationValid; infer_instance
instance (es : List Evaluation) (k : EvaluationKey) : Decidable (EvaluationConsistent es k) := by unfold EvaluationConsistent; infer_instance
instance (es : List Evaluation) (k : EvaluationKey) : Decidable (CheckedHolds es k) := by unfold CheckedHolds; infer_instance
abbrev InventoryValid (es : List Evaluation) : Prop :=
  (∀ e ∈ es, EvaluationValid e) ∧ (es.map Evaluation.id).Nodup
instance (es : List Evaluation) : Decidable (InventoryValid es) := by unfold InventoryValid; infer_instance
abbrev HasStatus (es : List Evaluation) (k : EvaluationKey) (status : ConditionStatus) : Prop :=
  ∃ e ∈ es, e.key = k ∧ e.status = status
instance (es : List Evaluation) (k : EvaluationKey) (status : ConditionStatus) : Decidable (HasStatus es k status) := by unfold HasStatus; infer_instance

def checkCondition (es : List Evaluation) (k : EvaluationKey) : Stress.Verdict :=
  if InventoryValid es ∧ EvaluationKeyValid k then
    if EvaluationConsistent es k then
      if HasStatus es k .holds then .yes
      else if HasStatus es k .doesNotHold then .no else .unknown
    else .invalid
  else .invalid

theorem condition_yes_iff (es : List Evaluation) (k : EvaluationKey) :
    checkCondition es k = .yes ↔ InventoryValid es ∧ CheckedHolds es k := by
  unfold checkCondition
  split
  · rename_i valid
    split
    · rename_i consistent
      split
      · rename_i holds
        exact ⟨fun _ => ⟨valid.1,valid.2,valid.1.1,consistent,holds⟩,fun _ => rfl⟩
      · rename_i absent
        split <;> constructor
        all_goals
          intro h
          first | contradiction | exact False.elim (absent h.2.2.2.2)
    · rename_i inconsistent
      constructor
      · intro h; cases h
      · intro h; exact False.elim (inconsistent h.2.2.2.1)
  · rename_i invalid
    constructor
    · intro h; cases h
    · intro h; exact False.elim (invalid ⟨h.1,h.2.1⟩)

theorem contradictory_status_blocks_holds : Successor.Required.ConflictBlocksHolds := by
  intro es k a b ha hb hak hbk different holds
  exact different (holds.2.2.1 a ha b hb hak hbk)

theorem activation_has_origin : Successor.Required.ActivationHasOrigin := by
  intro g f es k h; exact h.1

theorem activation_needs_holds : Successor.Required.ActivationNeedsHolds := by
  intro g f es k h; exact h.2.2.2.2.2

theorem potential_independent_of_conformance : Successor.Required.PotentialIndependentOfConformance := by
  intro g rows f; rfl

theorem no_active_without_holds (g : Stress.Graph) (f : Stress.Fact) (es : List Evaluation)
    (k : EvaluationKey) (absent : ¬ CheckedHolds es k) : ¬ ActiveNorm g f es k := by
  intro active; exact absent (activation_needs_holds g f es k active)

theorem active_conflict_has_two_active (g : Stress.Graph) (f h : Stress.Fact) (es : List Evaluation)
    (kf kh : EvaluationKey) (conflict : ActiveConflict g f h es kf kh) :
    ActiveNorm g f es kf ∧ ActiveNorm g h es kh ∧ Stress.ConflictPair f h :=
  ⟨conflict.1,conflict.2.1,conflict.2.2.2.2.2⟩

#print axioms condition_yes_iff
#print axioms contradictory_status_blocks_holds
#print axioms activation_has_origin
#print axioms activation_needs_holds
#print axioms potential_independent_of_conformance
#print axioms active_conflict_has_two_active
end Successor.Conditions
