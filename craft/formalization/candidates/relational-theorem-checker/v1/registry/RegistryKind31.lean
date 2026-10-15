import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind31 : Kind := { id := "relation.profiled-by", version := "sha256:ba59dbd901e25e3a80270ba3569afeea18fddbaef646f1780919c21e6f2c2f0a", pairs := [("agent-instance", "agent-profile")], fields := ["profile_version_ref", "binding_ref"] }
theorem kind_valid31 : KindValid nodes kind31 := by decide
end Registry.Snapshot
