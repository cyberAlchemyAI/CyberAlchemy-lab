import RegistryKind28_Data
namespace Registry.Snapshot
theorem kind28_basic : kind28.id ≠ "" ∧ kind28.version ≠ "" ∧ kind28.fields.Nodup ∧ (∀ field ∈ kind28.fields, field ≠ "") := by decide
end Registry.Snapshot
