import RegistryKind29_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind29_unique : kind29.pairs.Nodup := by decide
end Registry.Snapshot
