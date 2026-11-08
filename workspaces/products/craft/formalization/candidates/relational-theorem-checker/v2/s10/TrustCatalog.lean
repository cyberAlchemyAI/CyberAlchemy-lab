import RuntimeCatalog
import StressCheckers
namespace Successor.Qualification.Catalog
open Inference Inference.Extension
def RequiredCountermodel : Prop := RequiredCountermodelSoundness
def RequiredReferenceSaturation : Prop :=
  ∀ T F, ∃ C, saturateFuel (groundInstances T) (groundInstances T).length F
    ((groundInstances T).map GroundInstance.head) = some C ∧
    ∀ a, a ∈ C ↔ Derivable T F a
def RequiredSourceFaithfulPreservation : Prop :=
  ∀ base expanded (e : Recursive.CheckedExtension base expanded) M keys F,
    SourceFaithful keys F M →
    (∀ k ∈ keys, k ∈ base.predicates.map Predicate.key) →
    SourceFaithful keys F (Recursive.Relative e.added M)
def RequiredStressCertificateScope : Prop :=
  ∀ g steps, Stress.checkCertificate g steps = true →
    Stress.ReplayShape steps ∧ ∀ s ∈ steps, Stress.Derives g s.fact
end Successor.Qualification.Catalog
