import RegistryKind27_Data
namespace Registry.Snapshot
theorem kind27_basic : kind27.id ≠ "" ∧ kind27.version ≠ "" ∧ kind27.fields.Nodup ∧ (∀ field ∈ kind27.fields, field ≠ "") := by decide
end Registry.Snapshot
