import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K13

def plan_0_000 : Plan 13 [.ref, .ref, .ref] :=
  { obligationId := "relation.controls:forbidden:0"
    sourceKind := "failure-control-binding"
    targetKind := "failure-mode"
    branchIndex := 0
    arguments := .cons (.witnessField "control" (by decide)) (.cons (.variable "environment") (.cons (.variable "installationReceipt") (.nil)))
    binders := [
      { name := "environment", sort := .ref, domain := "execution-environments", selectionRole := "Exact independently specified environment of the installation/activation/external operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("control", ⟨.ref, .witnessField "control" (by decide)⟩)] },
      { name := "installationReceipt", sort := .ref, domain := "installation-observations", selectionRole := "Exact independent installation receipt candidate for control and environment", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("control", ⟨.ref, .witnessField "control" (by decide)⟩), ("environment", ⟨.ref, .variable "environment"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 13 [.ref, .ref, .ref] :=
  { obligationId := "relation.controls:forbidden:1"
    sourceKind := "failure-control-binding"
    targetKind := "failure-mode"
    branchIndex := 0
    arguments := .cons (.witnessField "control" (by decide)) (.cons (.variable "occurrence") (.cons (.variable "trace") (.nil)))
    binders := [
      { name := "occurrence", sort := .ref, domain := "failure-occurrences", selectionRole := "Exact independent occurrence targeted by execution of this control", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("control", ⟨.ref, .witnessField "control" (by decide)⟩)] },
      { name := "trace", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual execution candidate trace joining this control and occurrence", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("control", ⟨.ref, .witnessField "control" (by decide)⟩), ("occurrence", ⟨.ref, .variable "occurrence"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 13 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.controls:forbidden:2"
    sourceKind := "failure-control-binding"
    targetKind := "failure-mode"
    branchIndex := 0
    arguments := .cons (.witnessField "control" (by decide)) (.cons (.variable "objective") (.cons (.variable "metric") (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .witnessField "control" (by decide)⟩)] },
      { name := "metric", sort := .ref, domain := "metric-definitions", selectionRole := "Exact independently owned outcome/benefit/improvement metric for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .witnessField "control" (by decide)⟩), ("objective", ⟨.ref, .variable "objective"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 13 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.controls:forbidden:3"
    sourceKind := "failure-control-binding"
    targetKind := "failure-mode"
    branchIndex := 0
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .witnessField "control" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .witnessField "control" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_1_000
#print axioms plan_2_000
#print axioms plan_3_000
end CandidateConclusionAnchors.K13
