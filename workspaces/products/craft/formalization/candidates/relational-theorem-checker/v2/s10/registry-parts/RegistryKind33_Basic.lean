import RegistryKind33_Data
namespace Registry.Snapshot
theorem kind33_basic : kind33.id ≠ "" ∧ kind33.version ≠ "" ∧ kind33.fields.Nodup ∧ (∀ field ∈ kind33.fields, field ≠ "") := by decide
end Registry.Snapshot
