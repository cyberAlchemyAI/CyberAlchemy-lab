import RegistryKind39_Data
namespace Registry.Snapshot
theorem kind39_basic : kind39.id ≠ "" ∧ kind39.version ≠ "" ∧ kind39.fields.Nodup ∧ (∀ field ∈ kind39.fields, field ≠ "") := by decide
end Registry.Snapshot
