import RegistryKind1_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind1_unique : kind1.pairs.Nodup := by decide
end Registry.Snapshot
