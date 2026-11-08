import BaselineContract
import SupportedObservations
namespace Successor.Transition
open Relational
structure AppendGraph (before after : Graph) where
  newNodes : List Node
  newAssessments : List Assessment
  newAssertions : List Assertion
  nodes_append : after.nodes = before.nodes ++ newNodes
  assessments_append : after.assessments = before.assessments ++ newAssessments
  assertions_append : after.assertions = before.assertions ++ newAssertions
  after_valid : Inv after
  references_stable : Baseline.StableReferences before after
-- A richer migration may grow the finite domain and observations. This target
-- preserves the old initial view; it is not every-old-model expansion.
abbrev InitialViewRelation (before after : Graph) : Prop :=
  (∀ x, MemberConformance before x → MemberConformance after x) ∧
  ∀ r k, MemberKind before r k → MemberKind after r k
theorem initial_view_preserved {before after} (e : AppendGraph before after) : InitialViewRelation before after := by
  constructor
  · intro x h
    rcases h with ⟨_,a,ha,ver,token,meaning,subject,target⟩
    have member : a ∈ after.assertions := by rw [e.assertions_append];exact List.mem_append.mpr (Or.inl ha)
    have valid := e.after_valid.2.1 a member
    exact ⟨e.after_valid,a,member,ver,token,⟨meaning.1,meaning.2.1,valid⟩,subject,target⟩
  · intro r k h
    rcases h with ⟨_,n,hn,ref,kind⟩
    exact ⟨e.after_valid,n,by rw [e.nodes_append];exact List.mem_append.mpr (Or.inl hn),ref,kind⟩
theorem observation_view_preserved {before after} (e : AppendGraph before after) (v : Vocabulary) :
    ∀ a ∈ Observation.observed v before, a ∈ Observation.observed v after := by
  intro a ha
  have meaning := (Observation.observation_exact v before a).mp ha
  apply (Observation.observation_exact v after a).mpr
  rcases meaning with ⟨x,hx,eq⟩ | ⟨r,k,hk,eq⟩ | ⟨x,hx,eq⟩
  · exact Or.inl ⟨x,(initial_view_preserved e).1 x hx,eq⟩
  · exact Or.inr (Or.inl ⟨r,k,(initial_view_preserved e).2 r k hk,eq⟩)
  · exact Or.inr (Or.inr ⟨x,(initial_view_preserved e).1 x hx,eq⟩)
#print axioms initial_view_preserved
#print axioms observation_view_preserved
end Successor.Transition
