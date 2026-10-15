import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind8 : Kind := { id := "relation.carries-definition", version := "sha256:8dff2439e99a86deed5ef3284d787082aa53f5bba51c8bd7c289b8a3bdd0cbd5", pairs := [("artifact-type", "definition")], fields := ["definition_version_ref", "definition_sha256"] }
theorem kind_valid8 : KindValid nodes kind8 := by decide
end Registry.Snapshot
