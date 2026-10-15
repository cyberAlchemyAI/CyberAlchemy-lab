import ActualRecursive_cde073b3587d8e19cd68_Closure
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Successor.Runtime.Actual
open Inference Inference.Extension
def added := (groundInstances after).filter fun i => decide (¬ Old before i.head)
def extension : Recursive.CheckedExtension before after := {
fresh := after.predicates.drop 6, addedRules := after.rules.drop 1, added := added,domain_same := by decide,predicates_append := by decide,rules_append := by decide,roots_same := by decide,epoch_same := by decide,fresh_keys := by decide,fresh_ordinary := by decide,cover := by decide,old_bodies := by decide,fresh_heads := by decide,head_typed := by decide,head_roots := by decide,added_valid := by decide,producer_safe := by decide }
theorem actual_expansion : ∀ F M, SemanticModel before F M → ∃ N, SemanticModel after F N ∧ ∀ a, Old before a → (N a ↔ M a) := Recursive.every_old_model_expands before after extension
theorem closure_exact : ∀ a, a ∈ C ↔ Derivable after facts a := checked_closure_exact complete_closure
#print axioms before_valid
#print axioms after_valid
#print axioms initial_valid
#print axioms lineage_valid
#print axioms sealed_heads
#print axioms complete_closure
#print axioms actual_expansion
#print axioms closure_exact
end Successor.Runtime.Actual
