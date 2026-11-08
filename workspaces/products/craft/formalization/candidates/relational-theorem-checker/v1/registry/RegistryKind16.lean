import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind16 : Kind := { id := "relation.engages-inquiry", version := "sha256:080978c35ebdd242b3398d038db802d1031f10c1dedf3097161de7dc3910583a", pairs := [("experiment-design", "research-inquiry"), ("experiment-run", "research-inquiry"), ("finding", "research-inquiry"), ("research-run", "research-inquiry")], fields := ["inquiry_role"] }
theorem kind_valid16 : KindValid nodes kind16 := by decide
end Registry.Snapshot
