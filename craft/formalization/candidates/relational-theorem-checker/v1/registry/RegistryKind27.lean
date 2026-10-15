import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind27 : Kind := { id := "relation.occurs-during", version := "sha256:9cd76083a271f0ae9a3eb02115df8c9d1e52b7014689a899e561379383296b3a", pairs := [("failure-occurrence", "agent-action"), ("failure-occurrence", "agent-session"), ("failure-occurrence", "experiment-run"), ("failure-occurrence", "research-run"), ("failure-occurrence", "work")], fields := ["envelope_version_ref", "temporal_scope"] }
theorem kind_valid27 : KindValid nodes kind27 := by decide
end Registry.Snapshot
