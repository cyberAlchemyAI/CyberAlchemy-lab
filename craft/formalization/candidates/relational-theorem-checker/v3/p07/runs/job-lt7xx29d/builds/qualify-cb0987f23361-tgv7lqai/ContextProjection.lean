import RequiredStatements

namespace Successor.Projection
open Relational Successor

def edgeTuple (e : Assertion) : Option ConformanceTuple :=
  match e.kind, e.qualifiers with
  | .conformsTo, .conformance scope _ _ => some ⟨e.source,e.target,scope⟩
  | _, _ => none
def projectEdge (g : Relational.Graph) (e : Assertion) : Option ConformanceTuple :=
  if decide (InstanceValid g e) then edgeTuple e else none
def project (g : Relational.Graph) : List ConformanceTuple :=
  if decide (Inv g) then (g.assertions.filterMap (projectEdge g)).eraseDups else []
def projectKinds (g : Relational.Graph) : List (NodeRef × NodeKind) :=
  if decide (Inv g) then (g.nodes.map fun n => (n.ref,n.kind)).eraseDups else []
def projectUnary (g : Relational.Graph) : List NodeRef := (project g).map ConformanceTuple.subject |>.eraseDups
structure Support where
  assertion : Assertion
  version : String
  assessment : String
  deriving DecidableEq, Repr
abbrev SupportValid (g : Relational.Graph) (x : ConformanceTuple) (s : Support) : Prop :=
  s.assertion ∈ g.assertions ∧
  Relational.Logic.ConformsAt g s.assertion x.scope s.version s.assessment ∧
  s.assertion.source = x.subject ∧ s.assertion.target = x.target
-- Support is an exact set-valued relation, preserving multiple witnesses per deduplicated atom.
abbrev Supports (g : Relational.Graph) (x : ConformanceTuple) (s : Support) : Prop :=
  Inv g ∧ SupportValid g x s
end Successor.Projection
