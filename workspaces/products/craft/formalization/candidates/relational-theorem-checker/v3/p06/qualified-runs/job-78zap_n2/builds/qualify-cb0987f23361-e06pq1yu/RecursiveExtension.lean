import RuleConservativity
import SupportLineage
namespace Successor.Recursive
open Inference Inference.Extension
structure CheckedExtension (base expanded : Theory) where
  fresh : List Predicate
  addedRules : List Rule
  added : List GroundInstance
  domain_same : expanded.domain = base.domain
  predicates_append : expanded.predicates = base.predicates ++ fresh
  rules_append : expanded.rules = base.rules ++ addedRules
  roots_same : expanded.roots = base.roots
  epoch_same : expanded.epoch = base.epoch
  fresh_keys : ∀ p ∈ fresh, p.key ∉ base.predicates.map Predicate.key
  fresh_ordinary : ∀ p ∈ fresh, p.role = .ordinary
  cover : ∀ i ∈ groundInstances expanded, i ∈ groundInstances base ∨ i ∈ added
  old_bodies : ∀ i ∈ groundInstances base, ∀ a ∈ i.body, Old base a
  fresh_heads : ∀ i ∈ added, ¬ Old base i.head
  head_typed : ∀ i ∈ added, AtomValid expanded i.head
  head_roots : ∀ i ∈ added, RootPolicy expanded i.head
  added_valid : ∀ i ∈ added, ValidInstance expanded i
  producer_safe : ∀ i ∈ added, ∃ p ∈ fresh, p.key = i.head.predicate ∧ p.role = .ordinary
-- Positive recursive bodies may read old and fresh predicates. No model
-- expansion, closure result, or every-old-model conclusion is assumed here.
inductive Relative (added : List GroundInstance) (M : Atom → Prop) : Atom → Prop
  | base {a} : M a → Relative added M a
  | apply (i : GroundInstance) : i ∈ added →
      (∀ a ∈ i.body, Relative added M a) → Relative added M i.head
abbrev RequiredConservativity : Prop :=
  ∀ base expanded, CheckedExtension base expanded → ∀ F M,
    SemanticModel base F M → ∃ N, SemanticModel expanded F N ∧
      ∀ a, Old base a → (N a ↔ M a)
def atomUniverse (T : Theory) : List Atom :=
  (T.predicates.flatMap fun p =>
    ((choices T.domain p.sorts.length).map fun values => Atom.mk p.key values).filter fun a => decide (AtomValid T a)).eraseDups
theorem finite_universe : Required.FiniteUniverse atomUniverse := by
  intro T a valid
  rcases valid with ⟨p,hp,key,sorts,inside⟩
  have len : a.values.length = p.sorts.length := by
    have h := congrArg List.length sorts
    simpa using h
  have choice := choices_complete T.domain a.values inside
  rw [len] at choice
  apply List.mem_eraseDups.mpr
  apply List.mem_flatMap.mpr
  refine ⟨p,hp,List.mem_filter.mpr ⟨?_,?_⟩⟩
  · exact List.mem_map.mpr ⟨a.values,choice,by cases a; simp_all⟩
  · exact decide_eq_true ⟨p,hp,key,sorts,inside⟩
theorem no_unseeded_facts : Required.NoUnseededFacts := by
  intro T nonempty a proof
  induction proof with
  | base h => simp at h
  | apply i valid premises ih =>
      cases body : i.body with
      | nil => exact nonempty i valid body
      | cons b rest => exact ih b (by simp [body])
#print axioms finite_universe
#print axioms no_unseeded_facts
end Successor.Recursive
