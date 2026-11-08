import RequirementSemantics

namespace Successor.Required
open Successor
abbrev ProjectionExact (project : Relational.Graph → List ConformanceTuple) : Prop :=
  ∀ g x, x ∈ project g ↔ MemberConformance g x
abbrev KindProjectionExact (project : Relational.Graph → List (Relational.NodeRef × Relational.NodeKind)) : Prop :=
  ∀ g r k, (r,k) ∈ project g ↔ MemberKind g r k
abbrev ExistentialViewExact (project : Relational.Graph → List ConformanceTuple)
    (unary : Relational.Graph → List Relational.NodeRef) : Prop :=
  ∀ g r, r ∈ unary g ↔ ∃ x ∈ project g, x.subject = r
abbrev ObservationDerivationExact : Prop :=
  ∀ T F keys a, NoSealedHeads T keys → Sealed keys a →
    (Inference.Derivable T F a ↔ a ∈ F)
abbrev ConflictBlocksHolds : Prop :=
  ∀ es k a b, a ∈ es → b ∈ es → a.key = k → b.key = k →
    a.status ≠ b.status → ¬ CheckedHolds es k
abbrev ActivationHasOrigin : Prop :=
  ∀ g f es k, ActiveNorm g f es k → Stress.Origin g f
abbrev ActivationNeedsHolds : Prop :=
  ∀ g f es k, ActiveNorm g f es k → CheckedHolds es k
abbrev PotentialIndependentOfConformance : Prop :=
  ∀ g rows f, PotentialNorm {g with conformance := rows} f ↔ PotentialNorm g f
abbrev KindEncodingInjective : Prop :=
  ∀ a b, kindName a = kindName b → a = b
-- Recursive-extension and transition hypotheses are independently specified by their later
-- task contracts; no catalog can substitute a sampled closure for every-old-model expansion.
abbrev FiniteUniverse (enumerate : Inference.Theory → List Inference.Atom) : Prop :=
  ∀ T a, Inference.AtomValid T a → a ∈ enumerate T
abbrev NoUnseededFacts : Prop :=
  ∀ T, (∀ i, Inference.ValidInstance T i → i.body ≠ []) →
    ∀ a, ¬ Inference.Derivable T [] a
end Successor.Required
