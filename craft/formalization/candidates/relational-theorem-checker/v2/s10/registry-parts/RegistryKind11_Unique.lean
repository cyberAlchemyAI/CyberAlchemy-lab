import RegistryKind11_Data
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind11_unique : kind11.pairs.Nodup := by decide
end Registry.Snapshot
