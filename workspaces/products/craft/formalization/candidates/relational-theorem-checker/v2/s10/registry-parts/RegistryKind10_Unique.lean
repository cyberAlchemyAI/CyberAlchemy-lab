import RegistryKind10_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind10_unique : kind10.pairs.Nodup := by decide
end Registry.Snapshot
