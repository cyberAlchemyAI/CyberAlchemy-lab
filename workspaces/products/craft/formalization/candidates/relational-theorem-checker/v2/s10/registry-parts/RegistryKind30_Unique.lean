import RegistryKind30_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind30_unique : kind30.pairs.Nodup := by decide
end Registry.Snapshot
