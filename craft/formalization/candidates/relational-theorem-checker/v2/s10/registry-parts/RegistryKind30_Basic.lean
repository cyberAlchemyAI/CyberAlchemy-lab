import RegistryKind30_Data
namespace Registry.Snapshot
theorem kind30_basic : kind30.id ≠ "" ∧ kind30.version ≠ "" ∧ kind30.fields.Nodup ∧ (∀ field ∈ kind30.fields, field ≠ "") := by decide
end Registry.Snapshot
