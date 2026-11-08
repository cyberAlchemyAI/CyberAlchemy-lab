import RegistryKind13_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind13_unique : kind13.pairs.Nodup := by decide
end Registry.Snapshot
