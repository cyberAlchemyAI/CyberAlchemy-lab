import ActualRecursive_03dbde6e4f92e8535324_Typed
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Successor.Runtime.Actual
open Inference Inference.Extension
theorem complete_closure : checkClosure after facts C [steps] = true := by decide
end Successor.Runtime.Actual
