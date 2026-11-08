import RegistryKind21_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind21_unique : kind21.pairs.Nodup := by decide
end Registry.Snapshot
