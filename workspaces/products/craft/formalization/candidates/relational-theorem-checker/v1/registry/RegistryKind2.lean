import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind2 : Kind := { id := "relation.addresses-intent", version := "sha256:387bc793dd5199d280e5002916b2721af238d0e6f9991d426d8fa7233017ae85", pairs := [("agent-assignment", "intent"), ("goal", "intent"), ("product", "intent"), ("product-capability", "intent"), ("project", "intent"), ("research-inquiry", "intent")], fields := ["intent_resolution_ref", "addressing_role"] }
theorem kind_valid2 : KindValid nodes kind2 := by decide
end Registry.Snapshot
