import RegistryKind36_Data
namespace Registry.Snapshot
theorem kind36_basic : kind36.id ≠ "" ∧ kind36.version ≠ "" ∧ kind36.fields.Nodup ∧ (∀ field ∈ kind36.fields, field ≠ "") := by decide
end Registry.Snapshot
