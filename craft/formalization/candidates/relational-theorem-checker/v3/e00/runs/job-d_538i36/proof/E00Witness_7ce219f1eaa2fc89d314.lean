import ExpressionSemantics
open RelationalExtensions.Expression
namespace ExpressionInstance
def frame : Frame := ⟨(String.ofList [Char.ofNat 101, Char.ofNat 120, Char.ofNat 112, Char.ofNat 114, Char.ofNat 101, Char.ofNat 115, Char.ofNat 115, Char.ofNat 105, Char.ofNat 111, Char.ofNat 110, Char.ofNat 45, Char.ofNat 102, Char.ofNat 105, Char.ofNat 120, Char.ofNat 116, Char.ofNat 117, Char.ofNat 114, Char.ofNat 101]), ⟨(String.ofList [Char.ofNat 99, Char.ofNat 111, Char.ofNat 110, Char.ofNat 116, Char.ofNat 101, Char.ofNat 120, Char.ofNat 116]), (String.ofList [Char.ofNat 118, Char.ofNat 49])⟩, ⟨(String.ofList [Char.ofNat 114, Char.ofNat 101, Char.ofNat 118, Char.ofNat 105, Char.ofNat 101, Char.ofNat 119, Char.ofNat 101, Char.ofNat 114]), (String.ofList [Char.ofNat 118, Char.ofNat 49])⟩, ⟨(String.ofList [Char.ofNat 99, Char.ofNat 111, Char.ofNat 110, Char.ofNat 116, Char.ofNat 114, Char.ofNat 97, Char.ofNat 99, Char.ofNat 116]), (String.ofList [Char.ofNat 118, Char.ofNat 49])⟩, (String.ofList [Char.ofNat 115, Char.ofNat 116, Char.ofNat 97, Char.ofNat 116, Char.ofNat 105, Char.ofNat 99]), 0⟩
def expression : Expr := (Expr.atom ⟨(String.ofList [Char.ofNat 108, Char.ofNat 101, Char.ofNat 97, Char.ofNat 102]), (String.ofList [Char.ofNat 118, Char.ofNat 49])⟩)
def entries : List (Key × Truth) := [(⟨frame, ⟨(String.ofList [Char.ofNat 108, Char.ofNat 101, Char.ofNat 97, Char.ofNat 102]), (String.ofList [Char.ofNat 118, Char.ofNat 49])⟩⟩, Truth.yes)]
def env : Key → Truth := lookup entries
def potentials : List String := []
theorem evaluated : evaluate frame env expression = Truth.yes := by decide
theorem activated : active frame env expression potentials = [] := by decide
theorem independent_activation (origin : String) : origin ∈ active frame env expression potentials ↔ origin ∈ potentials ∧ (meaning frame env expression).1 = true := activation_exact frame env expression potentials origin
#print axioms evaluated
#print axioms activated
#print axioms independent_activation
end ExpressionInstance
