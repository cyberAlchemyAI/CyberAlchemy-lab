import RegistryKind3_Data
namespace Registry.Snapshot
theorem kind3_basic : kind3.id ≠ "" ∧ kind3.version ≠ "" ∧ kind3.fields.Nodup ∧ (∀ field ∈ kind3.fields, field ≠ "") := by decide
end Registry.Snapshot
