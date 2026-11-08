import RegistryKind20_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind20_unique : kind20.pairs.Nodup := by decide
end Registry.Snapshot
