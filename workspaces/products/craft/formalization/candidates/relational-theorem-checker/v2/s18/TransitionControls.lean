import BaselineTransition
import SourceInterpretation
import RequirementControls
namespace Successor.Transition.Controls
open Relational Successor.Controls
def extra : Node := ⟨⟨"new-contract","v2"⟩,.contract,"content-new"⟩
def nextGraph : Graph := {graph with nodes := graph.nodes ++ [extra]}
def e : AppendGraph graph nextGraph := {
 newNodes := [extra], newAssessments := [],newAssertions := []
 nodes_append := rfl,assessments_append := by simp [nextGraph]
 assertions_append := by simp [nextGraph]
 after_valid := by decide
 references_stable := by unfold Baseline.StableReferences; decide }
theorem richer_initial_view : InitialViewRelation graph nextGraph := initial_view_preserved e
theorem richer_new_kind : MemberKind nextGraph extra.ref .contract := by
  exact ⟨by decide,extra,by simp [nextGraph,extra],rfl,rfl⟩
theorem old_unary_view : observed.subject ∈ Projection.projectUnary nextGraph := by decide
def multiEdge : Assertion := {edge with qualifiers := .conformance "scope-A" "v1" "assessment,second"}
def multiGraph : Graph := {graph with assertions := [multiEdge]}
theorem multiple_unresolved_tokens_invalid : ¬ Relational.InstanceValid multiGraph multiEdge := by decide
theorem unsupported_pair_not_f0 : ¬ Relational.InstanceValid graph {edge with source := targetA} := by decide
theorem opaque_token_not_guessed : ¬ Source.BoundConformanceToken graph edge "scope-A" "v1" "assessment#v1" := by decide
#print axioms richer_initial_view
end Successor.Transition.Controls
