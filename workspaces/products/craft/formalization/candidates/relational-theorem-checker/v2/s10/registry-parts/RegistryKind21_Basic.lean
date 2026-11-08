import RegistryKind21_Data
namespace Registry.Snapshot
theorem kind21_basic : kind21.id ≠ "" ∧ kind21.version ≠ "" ∧ kind21.fields.Nodup ∧ (∀ field ∈ kind21.fields, field ≠ "") := by decide
end Registry.Snapshot
