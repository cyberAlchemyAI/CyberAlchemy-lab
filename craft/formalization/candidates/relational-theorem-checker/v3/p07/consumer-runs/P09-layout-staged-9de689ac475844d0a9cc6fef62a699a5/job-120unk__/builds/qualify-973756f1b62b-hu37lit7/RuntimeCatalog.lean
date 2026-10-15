import RecursiveExtension
import MappingStatements
import BaselineTransition
import SourceInterpretation
namespace Successor.Runtime.Catalog
open Inference
-- Closed independently specified conjunction. Removing a conjunct changes the
-- required type; the submission verifier compares the exact trusted definition.
def RequiredGeneralBundle : Prop :=
  Required.ProjectionExact Projection.project ∧
  Required.KindProjectionExact Projection.projectKinds ∧
  Required.ExistentialViewExact Projection.project Projection.projectUnary ∧
  Required.KindEncodingInjective ∧
  Required.ObservationDerivationExact ∧
  (∀ v g a, a ∈ Observation.observed v g ↔ Observation.SourceMeaning v g a) ∧
  (∀ g x, x ∈ Projection.project g ↔ ∃ w, Projection.Supports g x w) ∧
  Required.FiniteUniverse Recursive.atomUniverse ∧
  Required.NoUnseededFacts ∧
  Recursive.RequiredConservativity ∧
  RequiredDerivationSoundness ∧ RequiredClosureAdequacy ∧ RequiredProtectedLineage ∧
  Required.ConflictBlocksHolds ∧ Required.ActivationHasOrigin ∧ Required.ActivationNeedsHolds ∧
  Required.PotentialIndependentOfConformance ∧
  Interpretation.RequiredActsMapping ∧ Interpretation.RequiredInheritanceMapping ∧
  Source.RequiredTokenBinding ∧
  (∀ before after, Transition.AppendGraph before after → Transition.InitialViewRelation before after)
end Successor.Runtime.Catalog
