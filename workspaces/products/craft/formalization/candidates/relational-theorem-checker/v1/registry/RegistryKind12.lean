import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind12 : Kind := { id := "relation.contributes-to", version := "sha256:a162c2943fe792186572b280c04b8f4b9fc919cba6ced30decc3da17c006fd52", pairs := [("agent-action", "goal"), ("agent-action", "product"), ("experiment-design", "goal"), ("experiment-run", "goal"), ("project", "goal"), ("project", "product"), ("research-inquiry", "goal"), ("research-run", "goal")], fields := ["contribution_role", "contribution_scope"] }
theorem kind_valid12 : KindValid nodes kind12 := by decide
end Registry.Snapshot
