import MappingStatements

namespace Successor.ActsMappingControls
open Stress Successor.Interpretation

def delegation : Delegation := {
  ref := ⟨"delegation","v1"⟩, agent := ⟨"agent","v1"⟩, principal := ⟨"principal","v1"⟩,
  scopes := ["repo"], actions := ["read"], period := ⟨0,10⟩, revokedAt := none,
  policies := [], gates := [], redelegationAllowed := false }
def edge : ActsEdge := ⟨"acts",delegation.agent,delegation.principal,delegation.ref,"repo",delegation.period,none⟩
def raw : LegacyActs := ⟨"acts",delegation.agent,delegation.principal,"delegation-token","scope-token","period-token","revocation-token"⟩
def store : Store := ⟨[(("delegation","delegation-token"),delegation.ref)],[("scope-token","repo")],[("period-token",delegation.period)],[("revocation-token",none)]⟩
def snapshot : Snapshot := ⟨⟨"snapshot","v1"⟩,5,[],[]⟩
def expired : Snapshot := {snapshot with epoch := 10}

theorem mapped_direct_is_inhabited : MapsActs store raw edge ∧ LegacyActsEffective store raw delegation snapshot "read" false := by
  exact ⟨by decide,(acts_mapping_exact store raw edge delegation snapshot "read" false (by decide) (by decide)).mp (by decide)⟩
theorem expired_legacy_not_effective : ¬ LegacyActsEffective store raw delegation expired "read" false := by
  intro h
  have effective := (acts_mapping_exact store raw edge delegation expired "read" false (by decide) (by decide)).mpr h
  have no : ¬ Effective delegation expired edge "read" false := by decide
  exact no effective
theorem wrong_scope_token_rejected : ¬ MapsActs store {raw with scopeToken := "uninterpreted"} edge := by decide
theorem wrong_period_token_rejected : ¬ MapsActs store {raw with periodToken := "uninterpreted"} edge := by decide
theorem wrong_revocation_token_rejected : ¬ MapsActs store {raw with revocationToken := "uninterpreted"} edge := by decide
theorem wrong_delegation_revision_rejected : ¬ MapsActs store raw {edge with delegation := ⟨"delegation","v2"⟩} := by decide
theorem wrong_principal_rejected : ¬ MapsActs store raw {edge with principal := ⟨"other","v1"⟩} := by decide
theorem ambiguous_token_store_rejected : ¬ StoreFunctional {store with scopes := [("scope-token","repo"),("scope-token","other")]} := by decide

#print axioms mapped_direct_is_inhabited
#print axioms expired_legacy_not_effective
#print axioms ambiguous_token_store_rejected
end Successor.ActsMappingControls
