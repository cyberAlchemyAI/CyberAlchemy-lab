import ActualRecursive_0519f7371842e57ecba7_Typed
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Successor.Runtime.Actual
open Inference Inference.Extension
theorem complete_closure : checkClosure after facts C [steps] = true := by decide
end Successor.Runtime.Actual
