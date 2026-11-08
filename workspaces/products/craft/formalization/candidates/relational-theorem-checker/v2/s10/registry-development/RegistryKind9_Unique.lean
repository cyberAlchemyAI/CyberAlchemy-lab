import RegistryKind9_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind9_unique : kind9.pairs.Nodup := by decide
end Registry.Snapshot
