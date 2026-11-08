import RecursiveSaturation
namespace Successor.Recursive.Controls
open Inference Inference.Extension
def oldKey : Key := ⟨"Existing","v2","existing"⟩
def oldSignal : Key := ⟨"ExistingSignal","v2","existing-signal"⟩
def freshOne : Key := ⟨"FreshOne","v2","fresh-one"⟩
def freshTwo : Key := ⟨"FreshTwo","v2","fresh-two"⟩
def pred (k : Key) : Predicate := ⟨k,[],.ordinary⟩
def rule (name : String) (head body : Key) : Rule := ⟨⟨name,"v2",name⟩,[],⟨head,[]⟩,[⟨body,[]⟩]⟩
def oldRule := rule "old-rule" oldSignal oldKey
def addedRules := [rule "seed-cycle" freshOne oldSignal,rule "cycle-forward" freshTwo freshOne,rule "cycle-back" freshOne freshTwo]
def before : Theory := ⟨[.text "unit"],[pred oldKey,pred oldSignal],[oldRule],[],0⟩
def after : Theory := {before with predicates := before.predicates ++ [pred freshOne,pred freshTwo],rules := before.rules ++ addedRules}
def freshGround := (groundInstances after).filter fun i => decide (¬ Old before i.head)
def e : CheckedExtension before after := {
  fresh := [pred freshOne,pred freshTwo]
  addedRules := addedRules
  added := freshGround
  domain_same := rfl
  predicates_append := rfl
  rules_append := rfl
  roots_same := rfl
  epoch_same := rfl
  fresh_keys := by decide
  fresh_ordinary := by decide
  cover := by decide
  old_bodies := by decide
  fresh_heads := by decide
  head_typed := by decide
  head_roots := by decide
  added_valid := by decide
  producer_safe := by decide }
def F : List Atom := [⟨oldKey,[]⟩]
def M (a : Atom) : Prop := a = ⟨oldKey,[]⟩ ∨ a = ⟨oldSignal,[]⟩
theorem old_model_valid : SemanticModel before F M := by
  refine ⟨?_,?_,?_⟩
  · intro a ha
    rcases ha with eq | eq <;> subst a <;> decide
  · intro a ha
    have eq : a = ⟨oldKey,[]⟩ := by simpa [F] using ha
    exact Or.inl eq
  · intro i valid body
    have member := ground_instances_complete valid
    have eq : i = GroundInstance.mk oldRule.key [] ⟨oldSignal,[]⟩ [⟨oldKey,[]⟩] := by simpa [before,groundInstances,groundRule,choices,oldRule,rule,SubstitutionValid,instantiate,instantiateBody,substitute] using member
    subst i
    exact Or.inr (by decide)
theorem nonempty_before_valid : TheoryValid before := by decide
theorem after_valid : TheoryValid after := by decide
theorem nonempty_old_rules : before.rules ≠ [] := by decide
theorem actual_every_old_model : ∀ F M, SemanticModel before F M →
    ∃ N, SemanticModel after F N ∧ ∀ a, Old before a → (N a ↔ M a) :=
  every_old_model_expands before after e
def result := saturate (groundInstances after) F ((groundInstances after).map GroundInstance.head)
theorem multistep_seeded_cycle : result = [⟨oldKey,[]⟩,⟨oldSignal,[]⟩,⟨freshOne,[]⟩,⟨freshTwo,[]⟩] := by decide
theorem unseeded_cycle : saturate (groundInstances after) [] ((groundInstances after).map GroundInstance.head) = [] := by decide
theorem no_empty_body : ∀ i, ValidInstance after i → i.body ≠ [] := by
  intro i hi
  have mem := ground_instances_complete hi
  have body : ∀ i ∈ groundInstances after, i.body ≠ [] := by decide
  exact body i mem
theorem unseeded_not_derivable : ∀ a, ¬ Derivable after [] a := no_unseeded_facts after no_empty_body
theorem root_inventory_preserved : after.roots = before.roots := rfl
theorem old_head_not_fresh : Old before ⟨oldKey,[]⟩ := by decide
theorem protected_fresh_not_ordinary : rootedRole Role.protectedConclusion = true := rfl
theorem domain_growth_not_same : {before with domain := before.domain ++ [Value.text "new"]}.domain ≠ before.domain := by decide
theorem old_rule_mutation_not_append : ({after with rules := addedRules}).rules ≠ before.rules ++ addedRules := by decide
#print axioms actual_every_old_model
#print axioms unseeded_not_derivable
#print axioms multistep_seeded_cycle
end Successor.Recursive.Controls
