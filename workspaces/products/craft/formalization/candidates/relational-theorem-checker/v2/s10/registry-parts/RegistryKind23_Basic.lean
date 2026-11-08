import RegistryKind23_Data
namespace Registry.Snapshot
theorem kind23_basic : kind23.id ≠ "" ∧ kind23.version ≠ "" ∧ kind23.fields.Nodup ∧ (∀ field ∈ kind23.fields, field ≠ "") := by decide
end Registry.Snapshot
