import RecursiveExtension
namespace Successor.Recursive
open Inference Inference.Extension
theorem lift_atom {base expanded} (e : CheckedExtension base expanded) {a}
    (valid : AtomValid base a) : AtomValid expanded a := by
  rcases valid with ⟨p,hp,key,sorts,inside⟩
  exact ⟨p,by rw [e.predicates_append];exact List.mem_append_left _ hp,key,sorts,by simpa only [e.domain_same] using inside⟩
theorem lift_root {base expanded} (e : CheckedExtension base expanded) {a}
    (_old : Old base a) (root : RootPolicy base a) : RootPolicy expanded a := by
  intro p hp key role
  rw [e.predicates_append] at hp
  rcases List.mem_append.mp hp with hb | hf
  · simpa only [e.roots_same] using root p hb key role
  · have ordinary := e.fresh_ordinary p hf
    simp [ordinary,rootedRole] at role
theorem old_unchanged {base expanded} (e : CheckedExtension base expanded) {M a}
    (old : Old base a) : Relative e.added M a ↔ M a := by
  constructor
  · intro h
    cases h with
    | base hm => exact hm
    | apply i hi _ => exact False.elim (e.fresh_heads i hi old)
  · exact Relative.base
theorem expansion_valid {base expanded} (e : CheckedExtension base expanded) {F M}
    (model : SemanticModel base F M) : SemanticModel expanded F (Relative e.added M) := by
  refine ⟨?_,?_,?_⟩
  · intro a h
    cases h with
    | base hm =>
        have good := model.1 a hm
        exact ⟨lift_atom e good.1,lift_root e (valid_atom_is_old good.1) good.2⟩
    | apply i hi _ => exact ⟨e.head_typed i hi,e.head_roots i hi⟩
  · intro a ha
    exact Relative.base (model.2.1 a ha)
  · intro i valid body
    rcases e.cover i (ground_instances_complete valid) with old | fresh
    · apply Relative.base
      apply model.2.2 i (ground_instances_sound old)
      intro a ha
      exact (old_unchanged e (e.old_bodies i old a ha)).mp (body a ha)
    · exact Relative.apply i fresh body
theorem every_old_model_expands : RequiredConservativity := by
  intro base expanded e F M model
  exact ⟨Relative e.added M,expansion_valid e model,fun a old => old_unchanged e old⟩
theorem expansion_is_finite {base expanded} (e : CheckedExtension base expanded) {F M a}
    (model : SemanticModel base F M) (derived : Relative e.added M a) : a ∈ atomUniverse expanded :=
  finite_universe expanded a ((expansion_valid e model).1 a derived).1
theorem source_faithfulness_preserved {base expanded} (e : CheckedExtension base expanded)
    {M keys F} (source : SourceFaithful keys F M)
    (oldKeys : ∀ k ∈ keys, k ∈ base.predicates.map Predicate.key) :
    SourceFaithful keys F (Relative e.added M) := by
  intro a sealed
  exact (old_unchanged e (oldKeys a.predicate sealed)).trans (source a sealed)
#print axioms every_old_model_expands
#print axioms expansion_is_finite
#print axioms source_faithfulness_preserved
end Successor.Recursive
