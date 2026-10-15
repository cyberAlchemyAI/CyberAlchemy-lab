import RegistryKind28_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind28_unique : kind28.pairs.Nodup := by decide
end Registry.Snapshot
