import ScopedImpactCheck
import ScopedImpactWitnesses

set_option autoImplicit false
set_option maxHeartbeats 2000000

namespace RelationalSuccessor.CandidateScopedImpact.Checker.Examples
open RelationalSuccessor
open Witnesses

def withObservation (s : SourceKind) (t : TargetKind) (replacement : Observation) : World × Claim :=
  ({ world s t with observations := [replacement] },
   { claim s t with observation := replacement })
def withMeasurement (s : SourceKind) (t : TargetKind) (replacement : Measurement) : World × Claim :=
  ({ world s t with measurements := [replacement] },
   { claim s t with measurement := replacement })
def withScope (s : SourceKind) (t : TargetKind) (replacement : Scope) : World × Claim :=
  ({ world s t with scopes := [replacement] }, { claim s t with scope := replacement })
def withSnapshot (s : SourceKind) (t : TargetKind) : World × Claim :=
  let replacedFrame := { frame s t with snapshot := ref "stale" }
  let replacedObservation := { observation s t with frame := replacedFrame }
  let replacedProvenance := { provenance s t with frame := replacedFrame }
  ({ world s t with observations := [replacedObservation], provenanceRoots := [replacedProvenance] },
   { claim s t with observation := replacedObservation, provenance := replacedProvenance })

def isolatedCases (s : SourceKind) (t : TargetKind) : List ((World × Claim) × List Diagnostic) :=
  [(withObservation s t { observation s t with posture := .predicted }, [.observed]),
   (({ world s t with measurements := [] }, claim s t), [.measurementOwned]),
   (withScope s t { scope s t with participants := [(source s).ref] }, [.scopedTarget]),
   (({ world s t with provenanceRoots := [] }, claim s t), [.provenanceOwned]),
   ((world s t, { claim s t with postureQualifier := "definitely-observed" }), [.postureQualifier]),
   (withMeasurement s t { measurement t with observed := 0 }, [.impact]),
   (withMeasurement s t { measurement t with observedAt := 1 }, [.fresh]),
   (withMeasurement s t { measurement t with observedAt := 6 }, [.notFuture]),
   (({ world s t with evidenceRoots := [] }, claim s t), [.evidenceRoot]),
   (withMeasurement s t { measurement t with unit := ref "unregistered-unit" }, [.unit]),
   (withMeasurement s t { measurement t with method := ref "unregistered-method" }, [.method]),
   (withSnapshot s t, [.frameSnapshot]),
   ((world s t, { claim s t with scopeQualifier := ref "different-scope" }), [.scopeQualifier]),
   (withScope s t { scope s t with start := 5 }, [.measurementInScope])]

def isolatedChecksPass (s : SourceKind) (t : TargetKind) : Bool :=
  (isolatedCases s t).all (fun specimen =>
    decide (diagnostics specimen.1.1 specimen.1.2 = specimen.2))

theorem isolated_refusals_all_22 :
    allowedSources.all (fun s => allowedTargets.all (fun t => isolatedChecksPass s t)) = true := by
  decide

theorem positive_diagnostics_empty (s : SourceKind) (t : TargetKind)
    (hs : s ∈ allowedSources) (ht : t ∈ allowedTargets) :
    diagnostics (world s t) (claim s t) = [] :=
  (diagnostics_empty_exact _ _).mpr (legitimate_impact s t hs ht)

theorem positive_checker_accepts (s : SourceKind) (t : TargetKind)
    (hs : s ∈ allowedSources) (ht : t ∈ allowedTargets) :
    check (world s t) (claim s t) = true :=
  (check_exact _ _).mpr (legitimate_impact s t hs ht)

#print axioms isolated_refusals_all_22
#print axioms positive_diagnostics_empty
#print axioms positive_checker_accepts
end RelationalSuccessor.CandidateScopedImpact.Checker.Examples
