import RegistryKind34_Data
namespace Registry.Snapshot
theorem kind34_basic : kind34.id ≠ "" ∧ kind34.version ≠ "" ∧ kind34.fields.Nodup ∧ (∀ field ∈ kind34.fields, field ≠ "") := by decide
end Registry.Snapshot
