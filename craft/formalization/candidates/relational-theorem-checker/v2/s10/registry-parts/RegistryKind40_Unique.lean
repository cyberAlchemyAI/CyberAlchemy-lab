import RegistryKind40_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind40_unique : kind40.pairs.Nodup := by decide
end Registry.Snapshot
