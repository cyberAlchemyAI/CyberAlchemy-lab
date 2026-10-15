import ActualRecursive_4dcb781f90dd10646662_Typed
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Successor.Runtime.Actual
open Inference Inference.Extension
theorem complete_closure : checkClosure after facts C [steps] = true := by decide
end Successor.Runtime.Actual
