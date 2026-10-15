import RegistryKind18_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind18_unique : kind18.pairs.Nodup := by decide
end Registry.Snapshot
