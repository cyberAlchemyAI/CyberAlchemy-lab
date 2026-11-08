import RegistryKind27_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind27_unique : kind27.pairs.Nodup := by decide
end Registry.Snapshot
