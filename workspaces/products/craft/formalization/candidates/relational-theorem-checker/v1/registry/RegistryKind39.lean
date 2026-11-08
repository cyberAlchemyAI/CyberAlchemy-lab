import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind39 : Kind := { id := "relation.uses-tool", version := "sha256:634d394ad29f581eef1044debed00e0a3f7d652f672dd67ed698256fdf61772b", pairs := [("agent-action", "implementation"), ("agent-action", "tool"), ("agent-session", "implementation"), ("agent-session", "tool")], fields := ["tool_version_ref", "invocation_contract_ref", "use_role"] }
theorem kind_valid39 : KindValid nodes kind39 := by decide
end Registry.Snapshot
