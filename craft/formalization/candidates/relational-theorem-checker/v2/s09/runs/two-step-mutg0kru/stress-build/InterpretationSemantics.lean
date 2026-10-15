import ConditionSemantics
import DelegationSemantics

namespace Successor.Interpretation
open Stress
structure Store where
  references : List ((String × String) × Stress.Ref)
  scopes : List (String × String)
  periods : List (String × Stress.Period)
  revocations : List (String × Option Nat)
  deriving DecidableEq, Repr
abbrev StoreFunctional (s : Store) : Prop :=
  (s.references.map Prod.fst).Nodup ∧ (s.scopes.map Prod.fst).Nodup ∧
  (s.periods.map Prod.fst).Nodup ∧ (s.revocations.map Prod.fst).Nodup
structure LegacyActs where
  id : String
  agent : Stress.Ref
  principal : Stress.Ref
  delegationToken : String
  scopeToken : String
  periodToken : String
  revocationToken : String
  deriving DecidableEq, Repr
abbrev MapsActs (s : Store) (raw : LegacyActs) (e : ActsEdge) : Prop :=
  e.id = raw.id ∧ e.agent = raw.agent ∧ e.principal = raw.principal ∧
  (("delegation",raw.delegationToken),e.delegation) ∈ s.references ∧ (raw.scopeToken,e.scope) ∈ s.scopes ∧
  (raw.periodToken,e.period) ∈ s.periods ∧ (raw.revocationToken,e.revokedAt) ∈ s.revocations
-- Independent interpretation of source qualifiers, not defined as adapter/checker success.
abbrev LegacyActsEffective (s : Store) (raw : LegacyActs) (d : Delegation)
    (snapshot : Snapshot) (action : String) (redelegated : Bool) : Prop :=
  (("delegation",raw.delegationToken),d.ref) ∈ s.references ∧ raw.agent = d.agent ∧ raw.principal = d.principal ∧
  (raw.periodToken,d.period) ∈ s.periods ∧ (raw.revocationToken,d.revokedAt) ∈ s.revocations ∧
  (∃ scope, (raw.scopeToken,scope) ∈ s.scopes ∧ scope ∈ d.scopes) ∧
  action ∈ d.actions ∧ d.period.start ≤ snapshot.epoch ∧ snapshot.epoch < d.period.stop ∧
  ClearAt d.revokedAt snapshot.epoch ∧ AllAccepted d.policies snapshot.policies ∧
  AllAccepted d.gates snapshot.gates ∧ redelegated = false
structure LegacyInheritance where
  id : String
  subject : Stress.Ref
  contract : Stress.Ref
  bindingToken : String
  contractVersionToken : String
  deriving DecidableEq, Repr
abbrev MapsInheritance (s : Store) (raw : LegacyInheritance) (e : Inheritance) : Prop :=
  e.id = raw.id ∧ e.subject = raw.subject ∧ e.contract = raw.contract ∧
  (("binding",raw.bindingToken),e.binding) ∈ s.references ∧
  (("contract-version",raw.contractVersionToken),e.contract) ∈ s.references
abbrev LegacyNorm (s : Store) (raw : LegacyInheritance) (g : Stress.Graph) (n : Norm) : Prop :=
  ∃ e ∈ g.inheritances, e.id = raw.id ∧ e.subject = raw.subject ∧ e.contract = raw.contract ∧
    (("binding",raw.bindingToken),e.binding) ∈ s.references ∧ (("contract-version",raw.contractVersionToken),e.contract) ∈ s.references ∧
    ∃ b ∈ g.bindings, ∃ c ∈ g.contracts, Stress.Matches e b c ∧ n ∈ c.norms

-- Shape of StoreFunctional is finite and independently decidable.
instance (s : Store) : Decidable (StoreFunctional s) := by unfold StoreFunctional; infer_instance
instance (s : Store) (raw : LegacyActs) (e : ActsEdge) : Decidable (MapsActs s raw e) := by unfold MapsActs; infer_instance
instance (s : Store) (raw : LegacyInheritance) (e : Inheritance) : Decidable (MapsInheritance s raw e) := by unfold MapsInheritance; infer_instance
end Successor.Interpretation
