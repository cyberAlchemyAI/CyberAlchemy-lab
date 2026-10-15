import RegistryKind38_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind38_unique : kind38.pairs.Nodup := by decide
end Registry.Snapshot
