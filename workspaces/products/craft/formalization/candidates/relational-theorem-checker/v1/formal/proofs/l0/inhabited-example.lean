import CheckerSoundness
import FixtureGraphs
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000
namespace Relational.Witnesses
open Relational Relational.Fixtures

theorem inhabited_valid_graph : ∃ g : Graph,
    Inv g ∧ g.assertions.length = 3 ∧ g.admissionRoots = [] := by
  exact ⟨validGraph, graph_check_sound validGraph (by decide), rfl, rfl⟩

theorem inhabited_valid_addition :
    Inv baseGraph ∧ checkAddition baseGraph materializes = true ∧
    Inv (applyAddition baseGraph materializes) := by
  exact ⟨graph_check_sound baseGraph (by decide), by decide,
    addition_preserves baseGraph materializes (by decide)⟩

theorem conformance_without_admission :
    Inv validGraph ∧ conforms ∈ validGraph.assertions ∧ validGraph.admissionRoots = [] := by
  exact ⟨graph_check_sound validGraph (by decide), by decide, rfl⟩

theorem independent_admission_coexistence :
    Inv graphWithAdmission ∧ conforms ∈ graphWithAdmission.assertions ∧
    independentRoot ∈ graphWithAdmission.admissionRoots := by
  exact ⟨graph_check_sound graphWithAdmission (by decide), by decide, by decide⟩

end Relational.Witnesses
