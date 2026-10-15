import RegistryKind3_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind3_unique : kind3.pairs.Nodup := by decide
end Registry.Snapshot
