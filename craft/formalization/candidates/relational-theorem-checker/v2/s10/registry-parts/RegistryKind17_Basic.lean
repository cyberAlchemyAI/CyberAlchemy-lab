import RegistryKind17_Data
namespace Registry.Snapshot
theorem kind17_basic : kind17.id ≠ "" ∧ kind17.version ≠ "" ∧ kind17.fields.Nodup ∧ (∀ field ∈ kind17.fields, field ≠ "") := by decide
end Registry.Snapshot
