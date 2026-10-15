import RegistryKind32_Data
namespace Registry.Snapshot
theorem kind32_basic : kind32.id ≠ "" ∧ kind32.version ≠ "" ∧ kind32.fields.Nodup ∧ (∀ field ∈ kind32.fields, field ≠ "") := by decide
end Registry.Snapshot
