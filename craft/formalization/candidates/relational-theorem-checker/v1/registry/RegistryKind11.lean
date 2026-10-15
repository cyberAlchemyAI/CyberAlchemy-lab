import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind11 : Kind := { id := "relation.consumes-view", version := "sha256:db94a3c2f5903a27f2ec33277ab753cd0443d3ef630e8cd6fab1a52cdb83ec72", pairs := [("agent-session", "context-view"), ("agent-session", "ontology-view")], fields := ["view_digest", "cursor", "consumption_purpose"] }
theorem kind_valid11 : KindValid nodes kind11 := by decide
end Registry.Snapshot
