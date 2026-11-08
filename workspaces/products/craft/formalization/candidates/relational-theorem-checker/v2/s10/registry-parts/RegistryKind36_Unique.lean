import RegistryKind36_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind36_unique : kind36.pairs.Nodup := by decide
end Registry.Snapshot
