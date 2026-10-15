import RegistryKind29_Data
namespace Registry.Snapshot
theorem kind29_basic : kind29.id ≠ "" ∧ kind29.version ≠ "" ∧ kind29.fields.Nodup ∧ (∀ field ∈ kind29.fields, field ≠ "") := by decide
end Registry.Snapshot
