import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind6 : Kind := { id := "relation.assigned-to", version := "sha256:b772abbe7ed9af4649b8ed39cac281045f36610ba347b15fbd1596c41fb5f610", pairs := [("agent-instance", "responsibility"), ("agent-instance", "role"), ("person-reference", "responsibility"), ("person-reference", "role"), ("team", "responsibility"), ("team", "role")], fields := ["assignment_kind", "relation_record_ref"] }
theorem kind_valid6 : KindValid nodes kind6 := by decide
end Registry.Snapshot
