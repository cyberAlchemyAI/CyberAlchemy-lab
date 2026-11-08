import RegistryKind5_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind5_unique : kind5.pairs.Nodup := by decide
end Registry.Snapshot
