import MappingStatements
import StressCheckers
namespace Successor.MappingRuntime
open Successor
instance (g : Stress.Graph) (f : Stress.Fact) (es : List Evaluation) (k : EvaluationKey) : Decidable (ActiveNorm g f es k) := by
  unfold ActiveNorm PotentialNorm StressRefEquals
  infer_instance
instance (g : Stress.Graph) (f h : Stress.Fact) (es : List Evaluation) (kf kh : EvaluationKey) : Decidable (ActiveConflict g f h es kf kh) := by
  unfold ActiveConflict
  infer_instance
end Successor.MappingRuntime
