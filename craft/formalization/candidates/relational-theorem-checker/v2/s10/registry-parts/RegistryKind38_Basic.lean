import RegistryKind38_Data
namespace Registry.Snapshot
theorem kind38_basic : kind38.id ≠ "" ∧ kind38.version ≠ "" ∧ kind38.fields.Nodup ∧ (∀ field ∈ kind38.fields, field ≠ "") := by decide
end Registry.Snapshot
