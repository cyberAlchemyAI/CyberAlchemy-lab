import ModelSemantics

namespace Inference.Extension

abbrev Old (base : Theory) (a : Atom) : Prop := a.predicate ∈ base.predicates.map Predicate.key
instance (base : Theory) (a : Atom) : Decidable (Old base a) := by unfold Old; infer_instance
abbrev RootPolicy (T : Theory) (a : Atom) : Prop :=
  ∀ p ∈ T.predicates, p.key = a.predicate → rootedRole p.role = true → a.values ∈ T.roots
instance (T : Theory) (a : Atom) : Decidable (RootPolicy T a) := by unfold RootPolicy; infer_instance
abbrev SemanticModel (T : Theory) (F : List Atom) (M : Atom → Prop) : Prop :=
  (∀ a, M a → AtomValid T a ∧ RootPolicy T a) ∧ (∀ a ∈ F, M a) ∧
  ∀ i, ValidInstance T i → (∀ a ∈ i.body, M a) → M i.head

-- These are finite structural/grounding assumptions, not conservativity as an
-- assumption. Captured instances must independently check every field.
structure FreshHeadExtension (base expanded : Theory) where
  fresh : List Predicate
  added : List GroundInstance
  domain_same : expanded.domain = base.domain
  predicates_append : expanded.predicates = base.predicates ++ fresh
  roots_same : expanded.roots = base.roots
  fresh_keys : ∀ p ∈ fresh, p.key ∉ base.predicates.map Predicate.key
  cover : ∀ i ∈ groundInstances expanded, i ∈ groundInstances base ∨ i ∈ added
  old_bodies : ∀ i ∈ groundInstances base, ∀ a ∈ i.body, Old base a
  added_bodies : ∀ i ∈ added, ∀ a ∈ i.body, Old base a
  fresh_heads : ∀ i ∈ added, ¬ Old base i.head
  head_typed : ∀ i ∈ added, AtomValid expanded i.head
  head_roots : ∀ i ∈ added, (∀ a ∈ i.body, RootPolicy base a) → RootPolicy expanded i.head

theorem ground_rule_output_valid {T : Theory} {r : Rule} {values : List Value} {i : GroundInstance}
    (member : r ∈ T.rules) (output : groundRule T r values = some i) : ValidInstance T i := by
  unfold groundRule at output
  split at output
  · rename_i valid
    have substitution : SubstitutionValid T r values := by simpa using valid
    cases head : instantiate values r.head with
    | none => simp [head] at output
    | some a =>
        cases body : instantiateBody values r.body with
        | none => simp [head, body] at output
        | some atoms =>
            simp [head, body] at output
            subst i
            exact ⟨r, member, rfl, substitution, head, body⟩
  · simp at output
theorem ground_instances_sound {T : Theory} {i : GroundInstance}
    (member : i ∈ groundInstances T) : ValidInstance T i := by
  rcases List.mem_flatMap.mp member with ⟨r, hr, hi⟩
  rcases List.mem_filterMap.mp hi with ⟨values, _, output⟩
  exact ground_rule_output_valid hr output

theorem valid_atom_is_old {T : Theory} {a : Atom} (valid : AtomValid T a) : Old T a := by
  rcases valid with ⟨p, member, key, _, _⟩
  exact List.mem_map.mpr ⟨p, member, key⟩
theorem lift_atom {base expanded : Theory} (extension : FreshHeadExtension base expanded)
    {a : Atom} (valid : AtomValid base a) : AtomValid expanded a := by
  rcases valid with ⟨p, member, key, sorts, values⟩
  refine ⟨p, ?_, key, sorts, ?_⟩
  · rw [extension.predicates_append]
    exact List.mem_append.mpr (Or.inl member)
  · simpa only [extension.domain_same] using values
theorem lift_root_policy {base expanded : Theory} (extension : FreshHeadExtension base expanded)
    {a : Atom} (old : Old base a) (roots : RootPolicy base a) : RootPolicy expanded a := by
  intro p member key role
  rw [extension.predicates_append] at member
  rcases List.mem_append.mp member with base_member | fresh_member
  · simpa only [extension.roots_same] using roots p base_member key role
  · have impossible : p.key ∈ base.predicates.map Predicate.key := by simpa only [key] using old
    exact False.elim (extension.fresh_keys p fresh_member impossible)

def expansion {base expanded : Theory} (extension : FreshHeadExtension base expanded)
    (M : Atom → Prop) (a : Atom) : Prop :=
  M a ∨ ∃ i ∈ extension.added, i.head = a ∧ ∀ b ∈ i.body, M b

theorem old_interpretation_unchanged {base expanded : Theory} (extension : FreshHeadExtension base expanded)
    (M : Atom → Prop) (a : Atom) (old : Old base a) : expansion extension M a ↔ M a := by
  constructor
  · intro expanded_fact
    rcases expanded_fact with existing | ⟨i, member, head, _⟩
    · exact existing
    · have impossible : Old base i.head := by simpa only [head] using old
      exact False.elim (extension.fresh_heads i member impossible)
  · exact Or.inl

theorem every_base_model_expands {base expanded : Theory} (extension : FreshHeadExtension base expanded)
    (F : List Atom) (M : Atom → Prop) (model : SemanticModel base F M) :
    SemanticModel expanded F (expansion extension M) := by
  refine ⟨?_, ?_, ?_⟩
  · intro a fact
    rcases fact with old | ⟨i, member, head, body⟩
    · have valid := model.1 a old
      exact ⟨lift_atom extension valid.1, lift_root_policy extension (valid_atom_is_old valid.1) valid.2⟩
    · subst a
      exact ⟨extension.head_typed i member,
        extension.head_roots i member (fun b hb => (model.1 b (body b hb)).2)⟩
  · intro a member
    exact Or.inl (model.2.1 a member)
  · intro i valid premises
    rcases extension.cover i (ground_instances_complete valid) with old_instance | fresh_instance
    · apply Or.inl
      apply model.2.2 i (ground_instances_sound old_instance)
      intro a member
      exact (old_interpretation_unchanged extension M a (extension.old_bodies i old_instance a member)).mp (premises a member)
    · apply Or.inr
      refine ⟨i, fresh_instance, rfl, ?_⟩
      intro a member
      exact (old_interpretation_unchanged extension M a (extension.added_bodies i fresh_instance a member)).mp (premises a member)

abbrev RequiredRuleConservativity : Prop :=
  ∀ (base expanded : Theory), FreshHeadExtension base expanded →
    ∀ (F : List Atom) (M : Atom → Prop), SemanticModel base F M →
      ∃ expandedModel, SemanticModel expanded F expandedModel ∧
        ∀ a, Old base a → (expandedModel a ↔ M a)
theorem audited_rule_conservativity : RequiredRuleConservativity := by
  intro base expanded extension F M model
  exact ⟨expansion extension M, every_base_model_expands extension F M model,
    old_interpretation_unchanged extension M⟩

theorem checked_list_model_is_semantic {T : Theory} {F M : List Atom}
    (checked : checkModel T F M = true) : SemanticModel T F (fun a => a ∈ M) := by
  have valid := (model_checker_iff T F M).mp checked
  have closed := checked_model_is_closed checked
  exact ⟨valid.2.2.1.2, closed.1, closed.2⟩

end Inference.Extension
