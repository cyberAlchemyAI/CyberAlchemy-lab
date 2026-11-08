import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind23 : Kind := { id := "relation.inherits-contract", version := "sha256:bfa1c4ca9dbf8ebaea6cd1f9859a454268915b47b20bee067faed7c88e5312ee", pairs := [("capability-instance", "contract")], fields := ["binding_ref", "contract_version_ref"] }
theorem kind_valid23 : KindValid nodes kind23 := by decide
end Registry.Snapshot
