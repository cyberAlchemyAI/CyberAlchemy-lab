import RegistrySnapshot
import Preservation
import ConservativeExpansion
namespace Registry.RuleIdentity
def actual : Evolution.FreshExtension Snapshot.captured Snapshot.captured :=
  { added := [], nodes_equal := rfl, kinds_append := by simp, fresh_ids := by simp,
    base_valid := Snapshot.valid_snapshot, expanded_valid := Snapshot.valid_snapshot }
theorem actual_registry_preservation : ∀ g, Evolution.OldLanguage Snapshot.captured g →
    (Inv Snapshot.captured g ↔ Inv Snapshot.captured g) := Evolution.preserves_old_language actual
theorem actual_registry_conservativity : ∀ model, Inv Snapshot.captured model →
    ∃ expansion, Inv Snapshot.captured expansion ∧ Models.oldReduct Snapshot.captured expansion = model :=
  Models.expands_every_base_model Snapshot.captured [] (by simpa [Models.expandedTheory] using Snapshot.valid_snapshot)
theorem required_preservation : Evolution.RequiredPreservation := Evolution.audited_preservation
theorem required_conservativity : Models.RequiredConservativity := Models.audited_conservativity
#print axioms actual_registry_preservation
#print axioms actual_registry_conservativity
#print axioms required_preservation
#print axioms required_conservativity
end Registry.RuleIdentity
