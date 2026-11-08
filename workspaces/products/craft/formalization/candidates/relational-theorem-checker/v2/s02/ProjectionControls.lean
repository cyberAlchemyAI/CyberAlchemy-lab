import ProjectionProofs
import RequirementControls

namespace Successor.Projection.Controls
open Relational Successor
instance (g : Relational.Graph) (x : ConformanceTuple) (s : Support) : Decidable (Supports g x s) := by
  unfold Supports SupportValid Relational.Logic.ConformsAt; infer_instance

def duplicateSupport : Relational.Graph := {Successor.Controls.graph with assertions := [Successor.Controls.edge,{Successor.Controls.edge with id := "second-edge"}]}
def wrongKind : Relational.Graph := {Successor.Controls.graph with nodes := Successor.Controls.nodes.map fun n =>
  if n.ref = Successor.Controls.targetA then {n with kind := .governedModel} else n}
def changedScope : Relational.Graph := {Successor.Controls.graph with assertions := [Successor.Controls.wrongScope]}
def changedVersion : Relational.Graph := {Successor.Controls.graph with assertions := [Successor.Controls.wrongVersion]}
def changedTarget : Relational.Graph := {Successor.Controls.graph with assertions := [Successor.Controls.wrongTarget]}

theorem positive_projection : Successor.Controls.observed ∈ project Successor.Controls.graph := by decide
theorem wrong_contract_absent : (⟨Successor.Controls.subject,Successor.Controls.targetB,"scope-A"⟩ : ConformanceTuple) ∉ project Successor.Controls.graph := by decide
theorem wrong_scope_absent : (⟨Successor.Controls.subject,Successor.Controls.targetA,"scope-B"⟩ : ConformanceTuple) ∉ project Successor.Controls.graph := by decide
theorem wrong_revision_absent : (⟨Successor.Controls.subject,⟨"contract-A","v2"⟩,"scope-A"⟩ : ConformanceTuple) ∉ project Successor.Controls.graph := by decide
theorem nonmember_absent : project Successor.Controls.noMember = [] := by decide
theorem invalid_scope_graph_projects_nothing : project changedScope = [] := by decide
theorem invalid_version_graph_projects_nothing : project changedVersion = [] := by decide
theorem invalid_target_graph_projects_nothing : project changedTarget = [] := by decide
theorem wrong_kind_conformance_is_general : Successor.Controls.observed ∈ project wrongKind := by decide
theorem wrong_kind_cannot_be_contract : (Successor.Controls.targetA,NodeKind.contract) ∉ projectKinds wrongKind := by decide
theorem wrong_kind_reported_exactly : (Successor.Controls.targetA,NodeKind.governedModel) ∈ projectKinds wrongKind := by decide
theorem duplicate_support_deduplicates_atom : project duplicateSupport = [Successor.Controls.observed] := by decide
theorem both_supports_retained :
    Supports duplicateSupport Successor.Controls.observed ⟨Successor.Controls.edge,"v1","assessment"⟩ ∧
    Supports duplicateSupport Successor.Controls.observed ⟨{Successor.Controls.edge with id := "second-edge"},"v1","assessment"⟩ := by decide
theorem rejected_assessment_projects_nothing : project Successor.Controls.rejectedEvidence = [] := by decide
theorem missing_assessment_projects_nothing : project Successor.Controls.missingEvidence = [] := by decide
theorem unary_exact_observation : projectUnary Successor.Controls.graph = [Successor.Controls.subject] := by decide
theorem ambiguous_node_projects_nothing : project Successor.Controls.duplicateNode = [] := by decide

#print axioms positive_projection
#print axioms wrong_kind_cannot_be_contract
#print axioms both_supports_retained
end Successor.Projection.Controls
