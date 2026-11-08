import SupportLineage
import MappingStatements
namespace Successor.Source
open Relational
-- The plural legacy field is one exact opaque token in this selected profile.
-- A future evidence-list profile needs a new decoder, source meaning and proofs.
abbrev BoundConformanceToken (g : Graph) (e : Assertion) (scope ver token : String) : Prop :=
  e ∈ g.assertions ∧ Logic.ConformsAt g e scope ver token
abbrev RequiredTokenBinding : Prop :=
  ∀ g e scope ver token, BoundConformanceToken g e scope ver token →
    ver = e.target.version ∧ ∃ a ∈ g.assessments,
      a.ref = token ∧ a.mode = .conformance ∧ a.accepted = true ∧
      a.subject = e.source ∧ a.target = e.target ∧ a.scope = scope
theorem token_binding : RequiredTokenBinding := by
  intro g e scope ver token h
  exact Logic.conformance_has_bound_assessment g e scope ver token h.2
-- Exact fragment references (id,revision) are retained; token interpretation
-- and external authenticity remain supplied inputs, never inferred truth.
#print axioms token_binding
end Successor.Source
