import RegistryKind6_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind6_unique : kind6.pairs.Nodup := by decide
end Registry.Snapshot
