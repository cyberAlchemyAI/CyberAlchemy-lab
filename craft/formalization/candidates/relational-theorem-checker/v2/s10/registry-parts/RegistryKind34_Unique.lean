import RegistryKind34_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind34_unique : kind34.pairs.Nodup := by decide
end Registry.Snapshot
