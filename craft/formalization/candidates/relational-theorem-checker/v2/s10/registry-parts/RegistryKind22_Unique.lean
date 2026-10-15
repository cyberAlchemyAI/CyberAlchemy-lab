import RegistryKind22_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind22_unique : kind22.pairs.Nodup := by decide
end Registry.Snapshot
