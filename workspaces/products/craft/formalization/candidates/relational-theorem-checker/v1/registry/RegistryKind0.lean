import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind0 : Kind := { id := "relation.acts-for", version := "sha256:da08d8570d32664fe5045782b76c602ec5162afaeea4eb1cafcf1a09e66e46f3", pairs := [("agent-instance", "principal")], fields := ["delegation_ref", "scope_ref", "effective_period", "revocation_state"] }
theorem kind_valid0 : KindValid nodes kind0 := by decide
end Registry.Snapshot
