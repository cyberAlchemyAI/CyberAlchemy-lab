import RegistryKind25_Data
namespace Registry.Snapshot
theorem kind25_basic : kind25.id ≠ "" ∧ kind25.version ≠ "" ∧ kind25.fields.Nodup ∧ (∀ field ∈ kind25.fields, field ≠ "") := by decide
end Registry.Snapshot
