import StressTypes

namespace Stress

abbrev Matches (e : Inheritance) (b : Binding) (c : Contract) : Prop :=
  e.binding = b.ref ∧ e.subject = b.subject ∧ e.contract = c.ref ∧
  c.ref ∈ b.contracts ∧ e.scope = b.scope ∧ e.scope = c.scope ∧
  e.condition = c.condition ∧ b.active = true ∧ b.overrides = [] ∧ c.interpreted = true

abbrev Origin (g : Graph) (f : Fact) : Prop :=
  f.edge ∈ g.inheritances ∧ ∃ b ∈ g.bindings, ∃ c ∈ g.contracts,
    Matches f.edge b c ∧ f.norm ∈ c.norms

inductive Derives (g : Graph) : Fact → Prop where
  | propagate (f : Fact) (origin : Origin g f) : Derives g f
  | forward (f : Fact) (premise : Derives g f) : Derives g f

abbrev Conforms (g : Graph) (e : Inheritance) : Prop :=
  ∃ a ∈ g.conformance, a.subject = e.subject ∧ a.contract = e.contract ∧
    a.scope = e.scope ∧ a.accepted = true

abbrev BindingValid (b : Binding) : Prop :=
  RefValid b.ref ∧ RefValid b.subject ∧ b.scope ≠ "" ∧
  (∀ c ∈ b.contracts, RefValid c) ∧ b.contracts.Nodup ∧
  (∀ o ∈ b.overrides, RefValid o) ∧ b.overrides.Nodup

abbrev ContractValid (c : Contract) : Prop :=
  RefValid c.ref ∧ c.scope ≠ "" ∧ c.condition ≠ "" ∧
  (∀ n ∈ c.norms, n.action ≠ "") ∧ c.norms.Nodup

abbrev InheritanceValid (e : Inheritance) : Prop :=
  e.id ≠ "" ∧ RefValid e.subject ∧ RefValid e.contract ∧ RefValid e.binding ∧
  e.scope ≠ "" ∧ e.condition ≠ ""

abbrev GraphValid (g : Graph) : Prop :=
  (∀ b ∈ g.bindings, BindingValid b) ∧ (g.bindings.map Binding.ref).Nodup ∧
  (∀ c ∈ g.contracts, ContractValid c) ∧ (g.contracts.map Contract.ref).Nodup ∧
  (∀ e ∈ g.inheritances, InheritanceValid e) ∧ (g.inheritances.map Inheritance.id).Nodup ∧
  (∀ a ∈ g.conformance, RefValid a.subject ∧ RefValid a.contract ∧ a.scope ≠ "")

abbrev InheritanceKnown (g : Graph) : Prop :=
  ∀ e ∈ g.inheritances, (∃ b ∈ g.bindings, b.ref = e.binding ∧ b.overrides = []) ∧
    ∃ c ∈ g.contracts, c.ref = e.contract ∧ c.interpreted = true

abbrev InheritanceMatches (g : Graph) : Prop :=
  ∀ e ∈ g.inheritances, ∃ b ∈ g.bindings, ∃ c ∈ g.contracts, Matches e b c

abbrev ConflictPair (f h : Fact) : Prop :=
  f.norm.mode = .require ∧ h.norm.mode = .forbid ∧ f.norm.action = h.norm.action ∧
  f.edge.subject = h.edge.subject ∧ f.edge.scope = h.edge.scope ∧
  f.edge.condition = h.edge.condition

instance (g : Graph) (f : Fact) : Decidable (Origin g f) := by
  unfold Origin
  infer_instance
instance (g : Graph) (e : Inheritance) : Decidable (Conforms g e) := by
  unfold Conforms
  infer_instance
instance (b : Binding) : Decidable (BindingValid b) := by
  unfold BindingValid
  infer_instance
instance (c : Contract) : Decidable (ContractValid c) := by
  unfold ContractValid
  infer_instance
instance (g : Graph) : Decidable (GraphValid g) := by
  unfold GraphValid
  infer_instance
instance (g : Graph) : Decidable (InheritanceKnown g) := by
  unfold InheritanceKnown
  infer_instance
instance (g : Graph) : Decidable (InheritanceMatches g) := by
  unfold InheritanceMatches
  infer_instance

end Stress
