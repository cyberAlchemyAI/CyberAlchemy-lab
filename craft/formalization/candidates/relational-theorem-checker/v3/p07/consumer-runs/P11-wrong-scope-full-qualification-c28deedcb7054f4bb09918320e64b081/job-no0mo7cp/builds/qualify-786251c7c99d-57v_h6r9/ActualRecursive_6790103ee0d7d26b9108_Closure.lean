import ActualRecursive_6790103ee0d7d26b9108_Typed
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Successor.Runtime.Actual
open Inference Inference.Extension
theorem complete_closure : checkClosure after facts C [steps] = true := by decide
end Successor.Runtime.Actual
