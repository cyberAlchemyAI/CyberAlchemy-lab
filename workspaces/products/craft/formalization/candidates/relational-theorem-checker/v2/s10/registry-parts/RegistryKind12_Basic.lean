import RegistryKind12_Data
namespace Registry.Snapshot
theorem kind12_basic : kind12.id ≠ "" ∧ kind12.version ≠ "" ∧ kind12.fields.Nodup ∧ (∀ field ∈ kind12.fields, field ≠ "") := by decide
end Registry.Snapshot
