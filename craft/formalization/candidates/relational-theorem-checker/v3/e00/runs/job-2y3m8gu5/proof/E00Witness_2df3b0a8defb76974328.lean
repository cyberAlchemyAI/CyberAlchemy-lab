import ExpressionSemantics
set_option maxRecDepth 2048
open RelationalExtensions.Expression
namespace ExpressionInstance
def frame : Frame := ⟨"b45aa742c6d009f2960d216464bfb50895a6282f76b5eb27482cb7891daecf5b", ⟨"snapshot", "v1"⟩, ⟨"agent", "v1"⟩, ⟨"contract", "v1"⟩, "repo", 5⟩
def expression : Expr := (Expr.atom ⟨"always", "condition-v1"⟩)
def root_condition : Ref := ⟨"always", "condition-v1"⟩
def entries : List (Key × Truth) := [(⟨frame, ⟨"always", "condition-v1"⟩⟩, Truth.yes)]
def env : Key → Truth := lookup entries
def potentials : List String := ["{\"edge\":{\"binding\":{\"id\":\"binding\",\"version\":\"v1\"},\"condition\":\"always\",\"contract\":{\"id\":\"contract\",\"version\":\"v1\"},\"id\":\"inherits-1\",\"scope\":\"repo\",\"subject\":{\"id\":\"agent\",\"version\":\"v1\"}},\"norm\":{\"action\":\"receipt\",\"mode\":\"require\"}}", "{\"edge\":{\"binding\":{\"id\":\"binding\",\"version\":\"v1\"},\"condition\":\"always\",\"contract\":{\"id\":\"contract\",\"version\":\"v1\"},\"id\":\"inherits-1\",\"scope\":\"repo\",\"subject\":{\"id\":\"agent\",\"version\":\"v1\"}},\"norm\":{\"action\":\"receipt\",\"mode\":\"forbid\"}}"]
theorem evaluated : evaluate frame env expression = Truth.yes := by decide
theorem activated : active frame env expression potentials = ["{\"edge\":{\"binding\":{\"id\":\"binding\",\"version\":\"v1\"},\"condition\":\"always\",\"contract\":{\"id\":\"contract\",\"version\":\"v1\"},\"id\":\"inherits-1\",\"scope\":\"repo\",\"subject\":{\"id\":\"agent\",\"version\":\"v1\"}},\"norm\":{\"action\":\"receipt\",\"mode\":\"require\"}}", "{\"edge\":{\"binding\":{\"id\":\"binding\",\"version\":\"v1\"},\"condition\":\"always\",\"contract\":{\"id\":\"contract\",\"version\":\"v1\"},\"id\":\"inherits-1\",\"scope\":\"repo\",\"subject\":{\"id\":\"agent\",\"version\":\"v1\"}},\"norm\":{\"action\":\"receipt\",\"mode\":\"forbid\"}}"] := by decide
theorem independent_activation (origin : String) : origin ∈ active frame env expression potentials ↔ origin ∈ potentials ∧ (meaning frame env expression).1 = true := activation_exact frame env expression potentials origin
#print axioms evaluated
#print axioms activated
#print axioms independent_activation
def source_frame : Frame := ⟨"b45aa742c6d009f2960d216464bfb50895a6282f76b5eb27482cb7891daecf5b", ⟨"snapshot", "v1"⟩, ⟨"agent", "v1"⟩, ⟨"contract", "v1"⟩, "repo", 5⟩
def source_condition : Ref := ⟨"always", "condition-v1"⟩
theorem mapped_frame_exact : frame = source_frame := by decide
theorem mapped_condition_exact : root_condition = source_condition := by decide
#print axioms mapped_frame_exact
#print axioms mapped_condition_exact
end ExpressionInstance
