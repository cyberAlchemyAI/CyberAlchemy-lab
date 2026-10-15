import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind22 : Kind := { id := "relation.has-capability", version := "sha256:1ce58bfff967a3593a3b9fba9630cc304de5e21b46a1ae56d5aafeb6d98b121b", pairs := [("agent-instance", "agent-capability"), ("agent-profile", "agent-capability")], fields := ["capability_version_ref", "declaration_basis"] }
theorem kind_valid22 : KindValid nodes kind22 := by decide
end Registry.Snapshot
