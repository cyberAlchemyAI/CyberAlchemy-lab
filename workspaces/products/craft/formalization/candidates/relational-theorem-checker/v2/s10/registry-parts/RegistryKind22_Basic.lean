import RegistryKind22_Data
namespace Registry.Snapshot
theorem kind22_basic : kind22.id ≠ "" ∧ kind22.version ≠ "" ∧ kind22.fields.Nodup ∧ (∀ field ∈ kind22.fields, field ≠ "") := by decide
end Registry.Snapshot
