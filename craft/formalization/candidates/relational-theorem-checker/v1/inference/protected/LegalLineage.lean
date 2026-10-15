import InferenceFixture
import ProtectedLineage
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
open Inference Inference.Captured
theorem checked_result : checkLineage theory facts = true := by decide
#print axioms checked_result
theorem exact_root_lineage : ∀ a, Derivable theory facts a → Rooted theory a → a.values ∈ theory.roots := fun a derived rooted => checked_protected_lineage theory facts a checked_result derived rooted
#print axioms exact_root_lineage
