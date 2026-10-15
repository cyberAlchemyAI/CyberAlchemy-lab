import RegistryKind31_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind31_unique : kind31.pairs.Nodup := by decide
end Registry.Snapshot
