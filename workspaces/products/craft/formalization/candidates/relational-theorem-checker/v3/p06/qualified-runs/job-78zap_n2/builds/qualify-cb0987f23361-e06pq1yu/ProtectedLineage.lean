import ClosureAdequacy

namespace Inference

abbrev Rooted (T : Theory) (a : Atom) : Prop :=
  ∃ p ∈ T.predicates, p.key = a.predicate ∧ rootedRole p.role = true
instance (T : Theory) (a : Atom) : Decidable (Rooted T a) := by unfold Rooted; infer_instance
abbrev Justification (T : Theory) (a : Atom) : Prop :=
  ∃ p ∈ T.predicates, p.key = a.predicate ∧ (p.role = .checkedRoot ∨ p.role = .rootCarrier)
instance (T : Theory) (a : Atom) : Decidable (Justification T a) := by unfold Justification; infer_instance
abbrev SafeGround (T : Theory) (i : GroundInstance) : Prop :=
  Rooted T i.head → ∃ a ∈ i.body, Justification T a ∧ a.values = i.head.values
instance (T : Theory) (i : GroundInstance) : Decidable (SafeGround T i) := by unfold SafeGround; infer_instance
abbrev SafeRules (T : Theory) : Prop := ∀ i ∈ groundInstances T, SafeGround T i
instance (T : Theory) : Decidable (SafeRules T) := by unfold SafeRules; infer_instance
def checkLineage (T : Theory) (F : List Atom) : Bool :=
  decide (TheoryValid T ∧ InitialValid T F ∧ SafeRules T)

theorem lineage_checker_iff (T : Theory) (F : List Atom) :
    checkLineage T F = true ↔ TheoryValid T ∧ InitialValid T F ∧ SafeRules T := by simp [checkLineage]
theorem justification_is_rooted {T : Theory} {a : Atom} (justified : Justification T a) : Rooted T a := by
  rcases justified with ⟨p, member, key, role⟩
  refine ⟨p, member, key, ?_⟩
  rcases role with checked | carrier
  · simp [rootedRole, checked]
  · simp [rootedRole, carrier]
theorem initial_root_lineage {T : Theory} {F : List Atom} {a : Atom}
    (initial : InitialValid T F) (member : a ∈ F) (rooted : Rooted T a) : a.values ∈ T.roots := by
  rcases rooted with ⟨p, hp, key, role⟩
  exact (initial.2 a member).2 p hp key role

theorem protected_lineage {T : Theory} {F : List Atom} {a : Atom}
    (initial : InitialValid T F) (safe : SafeRules T) (derived : Derivable T F a) :
    Rooted T a → a.values ∈ T.roots := by
  induction derived with
  | base member => exact initial_root_lineage initial member
  | apply i valid _ ih =>
      intro rooted
      rcases safe i (ground_instances_complete valid) rooted with ⟨premise, member, justified, same_tuple⟩
      have existing := ih premise member (justification_is_rooted justified)
      rw [same_tuple] at existing
      exact existing

theorem checked_protected_lineage (T : Theory) (F : List Atom) (a : Atom)
    (checked : checkLineage T F = true) (derived : Derivable T F a) (rooted : Rooted T a) :
    a.values ∈ T.roots := by
  have safe := (lineage_checker_iff T F).mp checked
  exact protected_lineage safe.2.1 safe.2.2 derived rooted

theorem no_unrooted_protected_derivation {T : Theory} {F : List Atom} {a : Atom}
    (checked : checkLineage T F = true) (rooted : Rooted T a) (absent : a.values ∉ T.roots) :
    ¬ Derivable T F a := by
  intro derived
  exact absent (checked_protected_lineage T F a checked derived rooted)

-- This is exact tuple equality, not merely equal artifact IDs. All coordinates
-- (including the version inside Value.reference) are retained in the theorem.
abbrev RequiredProtectedLineage : Prop :=
  ∀ (T : Theory) (F : List Atom) (a : Atom), checkLineage T F = true →
    Derivable T F a → Rooted T a → a.values ∈ T.roots
theorem audited_protected_lineage : RequiredProtectedLineage := checked_protected_lineage

end Inference
