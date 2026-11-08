import RequirementSemantics

namespace Successor.Baseline
open Inference
structure Snapshot where
  graph : Relational.Graph
  theory : Theory
  facts : List Atom
  producer : List (Key × ProducerClass)
  sourceIdentity : String
  interpretationIdentity : String
  contextIdentity : String
  catalogIdentity : String
  toolchainIdentity : String
  policyIdentity : String
  epoch : Nat
abbrev ProducerCoverage (s : Snapshot) : Prop :=
  (s.producer.map Prod.fst).Nodup ∧
  ∀ p ∈ s.theory.predicates, ∃ c, (p.key,c) ∈ s.producer
abbrev WellFormed (s : Snapshot) : Prop :=
  Relational.Inv s.graph ∧ TheoryValid s.theory ∧ InitialValid s.theory s.facts ∧
  ProducerCoverage s ∧ s.theory.epoch = s.epoch ∧
  s.sourceIdentity ≠ "" ∧ s.interpretationIdentity ≠ "" ∧
  s.contextIdentity ≠ "" ∧ s.catalogIdentity ≠ "" ∧
  s.toolchainIdentity ≠ "" ∧ s.policyIdentity ≠ ""
-- Structural validation is distinct from independently replayed registration.
abbrev Registered (s : Snapshot) (expectedCatalog expectedToolchain expectedPolicy : String)
    (qualified : Snapshot → Prop) : Prop :=
  WellFormed s ∧ s.catalogIdentity = expectedCatalog ∧
  s.toolchainIdentity = expectedToolchain ∧ s.policyIdentity = expectedPolicy ∧ qualified s
abbrev StableReferences (before after : Relational.Graph) : Prop :=
  ∀ a ∈ before.nodes, ∀ b ∈ after.nodes, a.ref = b.ref →
    a.kind = b.kind ∧ a.contentIdentity = b.contentIdentity
abbrev RuleOnlyFrame (before after : Snapshot) : Prop :=
  before.graph = after.graph ∧ before.theory.domain = after.theory.domain ∧
  before.theory.roots = after.theory.roots ∧ before.facts = after.facts ∧
  before.sourceIdentity = after.sourceIdentity ∧
  before.interpretationIdentity = after.interpretationIdentity ∧
  before.contextIdentity = after.contextIdentity ∧ before.epoch = after.epoch
abbrev RequiredRegistrationBinding : Prop :=
  ∀ s c t p q, Registered s c t p q →
    WellFormed s ∧ s.catalogIdentity = c ∧ s.toolchainIdentity = t ∧ s.policyIdentity = p ∧ q s
abbrev RequiredReferenceImmutability : Prop :=
  ∀ before after a b, StableReferences before after →
    a ∈ before.nodes → b ∈ after.nodes → a.ref = b.ref →
    a.kind = b.kind ∧ a.contentIdentity = b.contentIdentity
theorem registration_binding : RequiredRegistrationBinding := by
  intro s c t p q h
  exact h
theorem reference_immutability : RequiredReferenceImmutability := by
  intro before after a b h ha hb eq
  exact h a ha b hb eq
-- No rule emptiness assumption is part of WellFormed or Registered.
#print axioms registration_binding
#print axioms reference_immutability
end Successor.Baseline
