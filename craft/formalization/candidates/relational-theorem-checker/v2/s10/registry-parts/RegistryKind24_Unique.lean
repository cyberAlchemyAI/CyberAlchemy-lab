import RegistryKind24_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind24_unique : kind24.pairs.Nodup := by decide
end Registry.Snapshot
