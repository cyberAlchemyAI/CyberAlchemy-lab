import RegistryKind35_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind35_unique : kind35.pairs.Nodup := by decide
end Registry.Snapshot
