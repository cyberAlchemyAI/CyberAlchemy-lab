import ClosureAdequacy

namespace Inference

-- A supplied semantic model may contain more than the least closure. It must
-- satisfy every Horn rule and the captured exact-root interpretation policy.
abbrev ModelValid (T : Theory) (F M : List Atom) : Prop :=
  TheoryValid T ∧ InitialValid T F ∧ InitialValid T M ∧
    (∀ a ∈ F, a ∈ M) ∧ Saturated T M
instance (T : Theory) (F M : List Atom) : Decidable (ModelValid T F M) := by unfold ModelValid; infer_instance
def checkModel (T : Theory) (F M : List Atom) : Bool := decide (ModelValid T F M)
theorem model_checker_iff (T : Theory) (F M : List Atom) :
    checkModel T F M = true ↔ ModelValid T F M := by simp [checkModel]
theorem checked_model_is_closed {T : Theory} {F M : List Atom}
    (checked : checkModel T F M = true) : Closed T F M := by
  have model := (model_checker_iff T F M).mp checked
  refine ⟨model.2.2.2.1, ?_⟩
  intro i valid body
  exact model.2.2.2.2 i (ground_instances_complete valid) body
abbrev Countermodel (T : Theory) (F M : List Atom) (premise conclusion : Atom) : Prop :=
  ModelValid T F M ∧ AtomValid T premise ∧ AtomValid T conclusion ∧
    premise ∈ M ∧ conclusion ∉ M
instance (T : Theory) (F M : List Atom) (premise conclusion : Atom) :
    Decidable (Countermodel T F M premise conclusion) := by unfold Countermodel; infer_instance
def checkCountermodel (T : Theory) (F M : List Atom) (premise conclusion : Atom) : Bool :=
  decide (Countermodel T F M premise conclusion)
theorem countermodel_checker_iff (T : Theory) (F M : List Atom) (premise conclusion : Atom) :
    checkCountermodel T F M premise conclusion = true ↔ Countermodel T F M premise conclusion := by
  simp [checkCountermodel]
-- This denies the implication even over all closed Horn models, rather than
-- weakening the claim to the additional root-constrained validation profile.
theorem checked_countermodel_non_entailment {T : Theory} {F M : List Atom} {premise conclusion : Atom}
    (checked : checkCountermodel T F M premise conclusion = true) :
    ¬ (∀ model : List Atom, Closed T F model → premise ∈ model → conclusion ∈ model) := by
  have counter := (countermodel_checker_iff T F M premise conclusion).mp checked
  have model : Closed T F M := by
    apply checked_model_is_closed
    exact (model_checker_iff T F M).mpr counter.1
  intro implication
  exact counter.2.2.2.2 (implication M model counter.2.2.2.1)

abbrev RequiredCountermodelSoundness : Prop :=
  ∀ (T : Theory) (F M : List Atom) (premise conclusion : Atom),
    checkCountermodel T F M premise conclusion = true →
    ¬ (∀ model : List Atom, Closed T F model → premise ∈ model → conclusion ∈ model)
theorem audited_countermodel_soundness : RequiredCountermodelSoundness := by
  intro T F M premise conclusion checked
  exact checked_countermodel_non_entailment checked

end Inference
