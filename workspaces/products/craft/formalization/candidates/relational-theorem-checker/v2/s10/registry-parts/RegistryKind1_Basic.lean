import RegistryKind1_Data
namespace Registry.Snapshot
theorem kind1_basic : kind1.id ≠ "" ∧ kind1.version ≠ "" ∧ kind1.fields.Nodup ∧ (∀ field ∈ kind1.fields, field ≠ "") := by decide
end Registry.Snapshot
