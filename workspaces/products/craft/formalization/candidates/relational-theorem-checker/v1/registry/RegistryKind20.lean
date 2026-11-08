import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind20 : Kind := { id := "relation.fulfills-request", version := "sha256:9ec53ca0ef109e7e199e53e352e21d64aceb5d4c1ef736779eea09571cbbc4dc", pairs := [("context-view", "context-request")], fields := ["fulfillment_role"] }
theorem kind_valid20 : KindValid nodes kind20 := by decide
end Registry.Snapshot
