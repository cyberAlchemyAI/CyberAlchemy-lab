import ExpressionSemantics
set_option maxRecDepth 2048
open RelationalExtensions.Expression
namespace ExpressionInstance
def frame : Frame := ⟨"expression-fixture", ⟨"context", "v1"⟩, ⟨"reviewer", "v1"⟩, ⟨"contract", "v1"⟩, "static", 0⟩
def expression : Expr := (Expr.conj (Expr.atom ⟨"left", "v1"⟩) (Expr.neg (Expr.atom ⟨"right", "v1"⟩)))
def root_condition : Ref := ⟨"expression", "v1"⟩
def entries : List (Key × Truth) := [(⟨frame, ⟨"left", "v1"⟩⟩, Truth.yes), (⟨frame, ⟨"right", "v1"⟩⟩, Truth.no)]
def env : Key → Truth := lookup entries
def potentials : List String := []
theorem evaluated : evaluate frame env expression = Truth.yes := by decide
theorem activated : active frame env expression potentials = [] := by decide
theorem independent_activation (origin : String) : origin ∈ active frame env expression potentials ↔ origin ∈ potentials ∧ (meaning frame env expression).1 = true := activation_exact frame env expression potentials origin
#print axioms evaluated
#print axioms activated
#print axioms independent_activation
end ExpressionInstance
