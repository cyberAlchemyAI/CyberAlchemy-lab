import RegistryKind23_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind23_unique : kind23.pairs.Nodup := by decide
end Registry.Snapshot
