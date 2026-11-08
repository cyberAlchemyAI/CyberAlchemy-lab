import RegistryKind8_Data
namespace Registry.Snapshot
theorem kind8_basic : kind8.id ≠ "" ∧ kind8.version ≠ "" ∧ kind8.fields.Nodup ∧ (∀ field ∈ kind8.fields, field ≠ "") := by decide
end Registry.Snapshot
