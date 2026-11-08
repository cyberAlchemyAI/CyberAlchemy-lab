import RegistryKind20_Data
namespace Registry.Snapshot
theorem kind20_basic : kind20.id ≠ "" ∧ kind20.version ≠ "" ∧ kind20.fields.Nodup ∧ (∀ field ∈ kind20.fields, field ≠ "") := by decide
end Registry.Snapshot
