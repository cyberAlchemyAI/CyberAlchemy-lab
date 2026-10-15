import RelationalInput

namespace Registry
abbrev Ref := Relational.NodeRef

structure Kind where
  id : String
  version : String
  pairs : List (String × String)
  fields : List String
  deriving DecidableEq, Repr
structure Theory where
  nodeKinds : List String
  kinds : List Kind
  deriving DecidableEq, Repr
structure Node where
  ref : Ref
  kind : String
  contentIdentity : String
  deriving DecidableEq, Repr
structure Assertion where
  id : String
  kindId : String
  kindVersion : String
  source : Ref
  target : Ref
  qualifiers : List (String × String)
  deriving DecidableEq, Repr
structure Graph where
  nodes : List Node
  assertions : List Assertion
  deriving DecidableEq, Repr

-- The selected profile preserves the source's closed, required nonempty strings.
abbrev QualifierValid (d : Kind) (q : List (String × String)) : Prop :=
  (q.map Prod.fst).Nodup ∧ (∀ field ∈ d.fields, field ∈ q.map Prod.fst) ∧
  ∀ entry ∈ q, entry.1 ∈ d.fields ∧ entry.2 ≠ ""

abbrev KindValid (nodeKinds : List String) (d : Kind) : Prop :=
    d.id ≠ "" ∧ d.version ≠ "" ∧ d.pairs.Nodup ∧
    (∀ pair ∈ d.pairs, pair.1 ∈ nodeKinds ∧ pair.2 ∈ nodeKinds) ∧
    d.fields.Nodup ∧ ∀ field ∈ d.fields, field ≠ ""

abbrev TheoryValid (r : Theory) : Prop :=
  r.nodeKinds.Nodup ∧ (∀ k ∈ r.nodeKinds, k ≠ "" ∧ k ≠ "*") ∧
  (r.kinds.map Kind.id).Nodup ∧ ∀ d ∈ r.kinds, KindValid r.nodeKinds d

abbrev InstanceValid (r : Theory) (g : Graph) (e : Assertion) : Prop :=
  e.id ≠ "" ∧ ∃ source ∈ g.nodes, ∃ target ∈ g.nodes,
    source.ref = e.source ∧ target.ref = e.target ∧ ∃ d ∈ r.kinds,
      d.id = e.kindId ∧ d.version = e.kindVersion ∧
      (source.kind,target.kind) ∈ d.pairs ∧ QualifierValid d e.qualifiers

abbrev Inv (r : Theory) (g : Graph) : Prop :=
  TheoryValid r ∧ (g.nodes.map Node.ref).Nodup ∧
  (∀ n ∈ g.nodes, n.ref.id ≠ "" ∧ n.ref.version ≠ "" ∧ n.contentIdentity ≠ "" ∧ n.kind ∈ r.nodeKinds) ∧
  (g.assertions.map Assertion.id).Nodup ∧ ∀ e ∈ g.assertions, InstanceValid r g e

instance (d : Kind) (q : List (String × String)) : Decidable (QualifierValid d q) := by
  unfold QualifierValid
  infer_instance
instance (r : Theory) : Decidable (TheoryValid r) := by
  unfold TheoryValid
  infer_instance
instance (r : Theory) (g : Graph) (e : Assertion) : Decidable (InstanceValid r g e) := by
  unfold InstanceValid
  infer_instance
instance (r : Theory) (g : Graph) : Decidable (Inv r g) := by
  unfold Inv
  infer_instance

def checkInstance (r : Theory) (g : Graph) (e : Assertion) : Bool := decide (InstanceValid r g e)
def checkGraph (r : Theory) (g : Graph) : Bool := decide (Inv r g)

theorem instance_checker_iff (r : Theory) (g : Graph) (e : Assertion) :
    checkInstance r g e = true ↔ InstanceValid r g e := by simp [checkInstance]
theorem graph_checker_iff (r : Theory) (g : Graph) :
    checkGraph r g = true ↔ Inv r g := by simp [checkGraph]

-- This conclusion exposes the exact source pair; no Cartesian-product rule exists.
theorem accepted_pair_has_origin (r : Theory) (g : Graph) (e : Assertion)
    (accepted : checkInstance r g e = true) :
    ∃ source ∈ g.nodes, ∃ target ∈ g.nodes, ∃ d ∈ r.kinds,
      source.ref = e.source ∧ target.ref = e.target ∧ d.id = e.kindId ∧
      d.version = e.kindVersion ∧ (source.kind,target.kind) ∈ d.pairs := by
  rcases (instance_checker_iff r g e).mp accepted with
    ⟨_, source, hs, target, ht, sourceRef, targetRef, d, hd, id, version, pair, _⟩
  exact ⟨source,hs,target,ht,d,hd,sourceRef,targetRef,id,version,pair⟩

end Registry
