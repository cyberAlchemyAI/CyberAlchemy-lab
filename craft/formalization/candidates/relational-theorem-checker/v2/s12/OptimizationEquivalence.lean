import RecursiveExtension
namespace Successor.Optimization
open Inference Inference.Extension
-- No optimized evaluator is selected. This is the reference fallback's exact
-- grounding contract, not a claim of equivalence for an unimplemented optimization.
abbrev RequiredGrounding (ground : Theory → List GroundInstance) : Prop :=
  ∀ T i, i ∈ ground T ↔ ValidInstance T i
theorem reference_fallback_exact : RequiredGrounding groundInstances := by
  intro T i
  exact ⟨ground_instances_sound,ground_instances_complete⟩
#print axioms reference_fallback_exact
end Successor.Optimization
