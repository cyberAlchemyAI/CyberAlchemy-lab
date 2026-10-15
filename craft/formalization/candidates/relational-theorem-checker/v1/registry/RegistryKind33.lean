import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind33 : Kind := { id := "relation.requests-resolution-of", version := "sha256:e59b4da66971a08fa757f1a0022e8b5ed9a1972b9b2bdabf9b70843ea0c34772", pairs := [("context-request", "context")], fields := ["context_version_ref"] }
theorem kind_valid33 : KindValid nodes kind33 := by decide
end Registry.Snapshot
