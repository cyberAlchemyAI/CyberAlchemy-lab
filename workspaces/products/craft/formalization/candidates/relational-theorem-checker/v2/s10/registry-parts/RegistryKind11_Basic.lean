import RegistryKind11_Data
namespace Registry.Snapshot
theorem kind11_basic : kind11.id ≠ "" ∧ kind11.version ≠ "" ∧ kind11.fields.Nodup ∧ (∀ field ∈ kind11.fields, field ≠ "") := by decide
end Registry.Snapshot
