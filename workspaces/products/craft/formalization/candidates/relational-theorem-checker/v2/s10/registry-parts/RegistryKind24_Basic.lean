import RegistryKind24_Data
namespace Registry.Snapshot
theorem kind24_basic : kind24.id ≠ "" ∧ kind24.version ≠ "" ∧ kind24.fields.Nodup ∧ (∀ field ∈ kind24.fields, field ≠ "") := by decide
end Registry.Snapshot
