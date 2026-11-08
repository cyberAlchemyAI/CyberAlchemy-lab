import RegistryKind0_Data
namespace Registry.Snapshot
theorem kind0_basic : kind0.id ≠ "" ∧ kind0.version ≠ "" ∧ kind0.fields.Nodup ∧ (∀ field ∈ kind0.fields, field ≠ "") := by decide
end Registry.Snapshot
