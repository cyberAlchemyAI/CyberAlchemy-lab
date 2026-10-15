import RegistryKind7_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind7_unique : kind7.pairs.Nodup := by decide
end Registry.Snapshot
