import RegistryKind33_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind33_unique : kind33.pairs.Nodup := by decide
end Registry.Snapshot
