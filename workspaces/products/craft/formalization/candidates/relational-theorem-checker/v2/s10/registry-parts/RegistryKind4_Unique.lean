import RegistryKind4_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind4_unique : kind4.pairs.Nodup := by decide
end Registry.Snapshot
