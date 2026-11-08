import RegistryKind12_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind12_unique : kind12.pairs.Nodup := by decide
end Registry.Snapshot
