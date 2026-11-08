import RegistryKind37_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind37_unique : kind37.pairs.Nodup := by decide
end Registry.Snapshot
