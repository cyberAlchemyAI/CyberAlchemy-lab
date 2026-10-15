import RegistryKind0_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind0_unique : kind0.pairs.Nodup := by decide
end Registry.Snapshot
