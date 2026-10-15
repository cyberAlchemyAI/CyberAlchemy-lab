import RegistryKind26_Data
namespace Registry.Snapshot
theorem kind26_basic : kind26.id ≠ "" ∧ kind26.version ≠ "" ∧ kind26.fields.Nodup ∧ (∀ field ∈ kind26.fields, field ≠ "") := by decide
end Registry.Snapshot
