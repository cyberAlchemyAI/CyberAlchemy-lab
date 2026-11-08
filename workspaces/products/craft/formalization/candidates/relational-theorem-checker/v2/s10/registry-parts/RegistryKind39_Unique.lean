import RegistryKind39_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind39_unique : kind39.pairs.Nodup := by decide
end Registry.Snapshot
