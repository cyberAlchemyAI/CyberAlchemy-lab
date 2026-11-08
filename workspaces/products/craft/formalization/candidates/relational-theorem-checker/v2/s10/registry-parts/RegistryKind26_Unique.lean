import RegistryKind26_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind26_unique : kind26.pairs.Nodup := by decide
end Registry.Snapshot
