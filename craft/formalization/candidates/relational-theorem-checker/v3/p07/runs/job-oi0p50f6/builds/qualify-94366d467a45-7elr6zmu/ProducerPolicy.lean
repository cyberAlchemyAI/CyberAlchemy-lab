import RequiredStatements

namespace Successor.Producer
open Inference
abbrev RuleHeadsUnsealed (T : Theory) (keys : List Key) : Prop :=
  ∀ r ∈ T.rules, r.head.predicate ∉ keys
instance (T : Theory) (keys : List Key) : Decidable (RuleHeadsUnsealed T keys) := by
  unfold RuleHeadsUnsealed; infer_instance
def checkHeads (T : Theory) (keys : List Key) : Bool := decide (RuleHeadsUnsealed T keys)
theorem instantiated_predicate {vs p a} (h : instantiate vs p = some a) : a.predicate = p.predicate := by
  unfold instantiate at h
  cases args : p.terms.mapM (substitute vs) with
  | none => simp [args] at h
  | some values =>
      simp [args] at h
      subst a
      rfl
theorem checked_heads_sealed {T keys} (h : checkHeads T keys = true) : NoSealedHeads T keys := by
  have unsealed : RuleHeadsUnsealed T keys := by simpa [checkHeads] using h
  intro i hi hs
  rcases hi with ⟨r,hr,_,_,head,_⟩
  have eq := instantiated_predicate head
  exact unsealed r hr (by simpa only [Sealed,eq] using hs)
theorem observation_derivation_exact : Required.ObservationDerivationExact := by
  intro T F keys a policy sealed
  constructor
  · intro proof
    cases proof with
    | base h => exact h
    | apply i valid _ => exact False.elim (policy i valid sealed)
  · exact Derivable.base
#print axioms checked_heads_sealed
#print axioms observation_derivation_exact
end Successor.Producer
