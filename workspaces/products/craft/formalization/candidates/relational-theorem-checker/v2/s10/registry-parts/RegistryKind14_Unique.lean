import RegistryKind14_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind14_unique : kind14.pairs.Nodup := by decide
end Registry.Snapshot
