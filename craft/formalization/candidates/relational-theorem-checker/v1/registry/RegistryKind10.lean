import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind10 : Kind := { id := "relation.conforms-to", version := "sha256:f8da5ba839d1e262817d1b1bcdde5a1ee1463a52d15ce14c426c1ec707970608", pairs := [("capability-instance", "contract"), ("capability-instance", "governed-model"), ("context", "context-profile")], fields := ["conformance_scope", "exact_version_ref", "conformance_evidence_refs"] }
theorem kind_valid10 : KindValid nodes kind10 := by decide
end Registry.Snapshot
