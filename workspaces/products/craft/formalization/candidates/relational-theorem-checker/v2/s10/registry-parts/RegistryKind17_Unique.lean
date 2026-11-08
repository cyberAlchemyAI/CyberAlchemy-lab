import RegistryKind17_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind17_unique : kind17.pairs.Nodup := by decide
end Registry.Snapshot
