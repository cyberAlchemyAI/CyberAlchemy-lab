import RegistryKind16_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind16_unique : kind16.pairs.Nodup := by decide
end Registry.Snapshot
