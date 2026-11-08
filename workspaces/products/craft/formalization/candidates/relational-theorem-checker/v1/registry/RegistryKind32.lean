import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind32 : Kind := { id := "relation.realizes", version := "sha256:affd03d8d00c136c70fa379e5aaf389b11cc8fd5856336790ce228277fcc16e3", pairs := [("experiment-run", "experiment-design"), ("implementation", "product-capability")], fields := ["realization_role", "exact_target_version_ref"] }
theorem kind_valid32 : KindValid nodes kind32 := by decide
end Registry.Snapshot
