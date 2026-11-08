import RegistryKind19_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind19_unique : kind19.pairs.Nodup := by decide
end Registry.Snapshot
