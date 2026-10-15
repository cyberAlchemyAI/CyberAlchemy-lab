import RegistryKind40_Data
namespace Registry.Snapshot
theorem kind40_basic : kind40.id ≠ "" ∧ kind40.version ≠ "" ∧ kind40.fields.Nodup ∧ (∀ field ∈ kind40.fields, field ≠ "") := by decide
end Registry.Snapshot
