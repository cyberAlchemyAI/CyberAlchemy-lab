import TrustCatalog
import RuntimeProofs
import StressProofs
namespace Successor.Qualification.Proofs
theorem countermodel : Catalog.RequiredCountermodel := Inference.audited_countermodel_soundness
theorem reference_saturation : Catalog.RequiredReferenceSaturation := Recursive.reference_saturation_exact
theorem source_faithful_preservation : Catalog.RequiredSourceFaithfulPreservation := by
  intro base expanded e M keys F source old
  exact Recursive.source_faithfulness_preserved e source old
theorem stress_certificate_scope : Catalog.RequiredStressCertificateScope := Stress.certificate_checker_sound
#print axioms countermodel
#print axioms reference_saturation
#print axioms source_faithful_preservation
#print axioms stress_certificate_scope
end Successor.Qualification.Proofs
