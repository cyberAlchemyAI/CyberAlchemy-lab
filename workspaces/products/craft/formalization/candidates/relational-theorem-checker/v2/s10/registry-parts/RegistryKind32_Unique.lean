import RegistryKind32_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind32_unique : kind32.pairs.Nodup := by decide
end Registry.Snapshot
