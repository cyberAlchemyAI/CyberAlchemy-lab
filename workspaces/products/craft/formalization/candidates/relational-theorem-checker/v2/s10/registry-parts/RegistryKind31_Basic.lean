import RegistryKind31_Data
namespace Registry.Snapshot
theorem kind31_basic : kind31.id ≠ "" ∧ kind31.version ≠ "" ∧ kind31.fields.Nodup ∧ (∀ field ∈ kind31.fields, field ≠ "") := by decide
end Registry.Snapshot
