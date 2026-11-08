import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind34 : Kind := { id := "relation.responds-to", version := "sha256:56f28bbcbc3b490064d486b213ee30baaa00c8fdba566d7bb6051eccb638ba25", pairs := [("agent-action", "failure-occurrence"), ("agent-action", "incident")], fields := ["response_role", "intended_outcome"] }
theorem kind_valid34 : KindValid nodes kind34 := by decide
end Registry.Snapshot
