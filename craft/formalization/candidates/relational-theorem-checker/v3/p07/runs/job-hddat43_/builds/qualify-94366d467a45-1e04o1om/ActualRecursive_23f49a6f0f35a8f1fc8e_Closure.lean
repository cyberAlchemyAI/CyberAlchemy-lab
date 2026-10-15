import ActualRecursive_23f49a6f0f35a8f1fc8e_Typed
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Successor.Runtime.Actual
open Inference Inference.Extension
theorem complete_closure : checkClosure after facts C [steps] = true := by decide
end Successor.Runtime.Actual
