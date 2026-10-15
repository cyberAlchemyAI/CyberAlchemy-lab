import RequiredStatements
import DelegationSemantics

namespace Successor.Controls
open Relational Successor
instance (g : Relational.Graph) (r : NodeRef) (k : NodeKind) : Decidable (MemberKind g r k) := by
  unfold MemberKind; infer_instance

def subject : NodeRef := ⟨"subject","v1"⟩
def targetA : NodeRef := ⟨"contract-A","v1"⟩
def targetB : NodeRef := ⟨"contract-B","v1"⟩
def assessment : Assessment := ⟨"assessment",.conformance,subject,targetA,"scope-A","","",true⟩
def edge : Assertion := ⟨"edge",.conformsTo,subject,targetA,.conformance "scope-A" "v1" "assessment"⟩
def nodes : List Node := [⟨subject,.capabilityInstance,"content-subject"⟩,
  ⟨targetA,.contract,"content-A"⟩,⟨targetB,.contract,"content-B"⟩]
def graph : Relational.Graph := ⟨nodes,[assessment],[edge],[]⟩
def observed : ConformanceTuple := ⟨subject,targetA,"scope-A"⟩
def wrongScope : Assertion := {edge with qualifiers := .conformance "scope-B" "v1" "assessment"}
def wrongTarget : Assertion := {edge with target := targetB}
def wrongVersion : Assertion := {edge with qualifiers := .conformance "scope-A" "v2" "assessment"}
def rejectedEvidence : Relational.Graph := {graph with assessments := [{assessment with accepted := false}]}
def missingEvidence : Relational.Graph := {graph with assessments := []}
def noMember : Relational.Graph := {graph with assertions := []}
def duplicateIdentity : Relational.Graph := {graph with assessments := [assessment, {assessment with target := targetB}]}
def duplicateEdge : Relational.Graph := {graph with assertions := [edge,edge]}
def duplicateNode : Relational.Graph := {graph with nodes := nodes ++ [⟨targetA,.governedModel,"changed-content"⟩]}

-- Mutants are independent weakened semantic conditions, not checker output flags.
abbrev MutantNoMembership (g : Relational.Graph) (e : Assertion) : Prop := InstanceValid g e
abbrev MutantNoScope (g : Relational.Graph) (e : Assertion) : Prop :=
  ∃ a ∈ g.assessments, a.accepted = true ∧ a.subject = e.source ∧ a.target = e.target
abbrev MutantNoTarget (g : Relational.Graph) (e : Assertion) : Prop :=
  ∃ a ∈ g.assessments, a.accepted = true ∧ a.subject = e.source
abbrev MutantNoVersion (g : Relational.Graph) (e : Assertion) : Prop :=
  EndpointValid g e ∧ MutantNoScope g e
abbrev MutantNoAccepted (g : Relational.Graph) (e : Assertion) : Prop :=
  ∃ a ∈ g.assessments, a.subject = e.source ∧ a.target = e.target
abbrev MutantNoTokenUniqueness (g : Relational.Graph) : Prop :=
  (∀ n ∈ g.nodes, NodeValid n) ∧ (g.nodes.map Node.ref).Nodup ∧
  (∀ a ∈ g.assessments, AssessmentValid g a) ∧
  (∀ e ∈ g.assertions, InstanceValid g e)
instance (g : Relational.Graph) (e : Assertion) : Decidable (MutantNoScope g e) := by unfold MutantNoScope; infer_instance
instance (g : Relational.Graph) (e : Assertion) : Decidable (MutantNoTarget g e) := by unfold MutantNoTarget; infer_instance
instance (g : Relational.Graph) (e : Assertion) : Decidable (MutantNoVersion g e) := by unfold MutantNoVersion; infer_instance
instance (g : Relational.Graph) (e : Assertion) : Decidable (MutantNoAccepted g e) := by unfold MutantNoAccepted; infer_instance
instance (g : Relational.Graph) : Decidable (MutantNoTokenUniqueness g) := by unfold MutantNoTokenUniqueness; infer_instance

theorem positive_member : MemberConformance graph observed := by
  exact ⟨by decide, edge, by decide, "v1", "assessment", by decide, rfl, rfl⟩
theorem wrong_scope_rejected : ¬ InstanceValid graph wrongScope := by decide
theorem wrong_target_rejected : ¬ InstanceValid graph wrongTarget := by decide
theorem wrong_version_rejected : ¬ InstanceValid graph wrongVersion := by decide
theorem rejected_assessment_rejected : ¬ InstanceValid rejectedEvidence edge := by decide
theorem missing_assessment_rejected : ¬ InstanceValid missingEvidence edge := by decide
theorem valid_nonmember_not_observed : InstanceValid noMember edge ∧ ¬ MemberConformance noMember observed := by
  exact ⟨by decide, by simp [MemberConformance, noMember]⟩
theorem duplicate_assessment_rejected : ¬ Inv duplicateIdentity := by decide
theorem duplicate_edge_rejected : ¬ Inv duplicateEdge := by decide
theorem duplicate_node_rejected : ¬ Inv duplicateNode := by decide
theorem wrong_kind_not_observed : ¬ MemberKind graph targetA .governedModel := by decide
theorem no_membership_mutant_exposed : MutantNoMembership noMember edge ∧ ¬ MemberConformance noMember observed := by
  exact ⟨by decide, by simp [MemberConformance, noMember]⟩
theorem no_scope_mutant_exposed : MutantNoScope graph wrongScope ∧ ¬ InstanceValid graph wrongScope := by decide
theorem no_target_mutant_exposed : MutantNoTarget graph wrongTarget ∧ ¬ InstanceValid graph wrongTarget := by decide
theorem no_version_mutant_exposed : MutantNoVersion graph wrongVersion ∧ ¬ InstanceValid graph wrongVersion := by decide
theorem no_acceptance_mutant_exposed : MutantNoAccepted rejectedEvidence edge ∧ ¬ InstanceValid rejectedEvidence edge := by decide
theorem no_uniqueness_mutant_exposed : MutantNoTokenUniqueness duplicateIdentity ∧ ¬ Inv duplicateIdentity := by decide

def delegation : Stress.Delegation := {
  ref := ⟨"delegation","v1"⟩, agent := ⟨"agent","v1"⟩, principal := ⟨"principal","v1"⟩,
  scopes := ["repo"], actions := ["read"], period := ⟨0,10⟩, revokedAt := some 5,
  policies := [], gates := [], redelegationAllowed := false }
def acts : Stress.ActsEdge := ⟨"acts",delegation.agent,delegation.principal,delegation.ref,"repo",delegation.period,some 5⟩
def snapshot : Stress.Snapshot := ⟨⟨"context","v1"⟩,5,[],[]⟩
def ignoreRevocation : Stress.Delegation := {delegation with revokedAt := none}
def ignoreRevocationEdge : Stress.ActsEdge := {acts with revokedAt := none}
theorem revocation_premise_is_needed :
    ¬ Stress.Effective delegation snapshot acts "read" false ∧
      Stress.Effective ignoreRevocation snapshot ignoreRevocationEdge "read" false := by decide

#print axioms positive_member
#print axioms no_membership_mutant_exposed
#print axioms no_scope_mutant_exposed
#print axioms no_target_mutant_exposed
#print axioms no_version_mutant_exposed
#print axioms no_acceptance_mutant_exposed
#print axioms no_uniqueness_mutant_exposed
#print axioms revocation_premise_is_needed
end Successor.Controls
