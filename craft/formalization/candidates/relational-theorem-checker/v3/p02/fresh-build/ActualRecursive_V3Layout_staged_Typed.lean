import ActualRecursive_V3Layout_staged_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Successor.Runtime.Actual
open Inference Inference.Extension
theorem before_valid : TheoryValid before := by decide
theorem after_valid : TheoryValid after := by decide
theorem initial_valid : InitialValid after facts := by decide
theorem lineage_valid : checkLineage after facts = true := by decide
theorem sealed_heads : Producer.checkHeads after sealed = true := by decide
end Successor.Runtime.Actual
