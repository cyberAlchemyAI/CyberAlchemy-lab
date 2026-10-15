import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K34

def plan_0_000 : Plan 34 [.ref, .ref, .ref] :=
  { obligationId := "relation.responds-to:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "failure-occurrence"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "incident") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "incident", sort := .ref, domain := "incident-occurrence-membership", selectionRole := "Exact Incident independently containing this Failure Occurrence; the occurrence is not relabeled as an Incident", joins := [("occurrence", ⟨.ref, .target⟩), ("action", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("action", ⟨.ref, .source⟩), ("incident", ⟨.ref, .variable "incident"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 34 [.ref, .ref, .ref] :=
  { obligationId := "relation.responds-to:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "incident"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("action", ⟨.ref, .source⟩), ("incident", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 34 [.ref, .ref, .ref] :=
  { obligationId := "relation.responds-to:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "failure-occurrence"
    branchIndex := 0
    arguments := .cons (.variable "cause") (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "cause", sort := .ref, domain := "causal-participants", selectionRole := "Exact independently specified candidate cause of this occurrence/incident; no cause follows from timing or response intention", joins := [("outcome", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .variable "cause"⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 34 [.ref, .ref, .ref] :=
  { obligationId := "relation.responds-to:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "incident"
    branchIndex := 1
    arguments := .cons (.variable "cause") (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "cause", sort := .ref, domain := "causal-participants", selectionRole := "Exact independently specified candidate cause of this occurrence/incident; no cause follows from timing or response intention", joins := [("outcome", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .variable "cause"⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 34 [.ref, .ref, .frame] :=
  { obligationId := "relation.responds-to:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "failure-occurrence"
    branchIndex := 0
    arguments := .cons (.variable "incident") (.cons (.variable "closure") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "incident", sort := .ref, domain := "incident-occurrence-membership", selectionRole := "Exact Incident independently containing this Failure Occurrence; the occurrence is not relabeled as an Incident", joins := [("occurrence", ⟨.ref, .target⟩), ("action", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "closure", sort := .ref, domain := "incident-closure-records", selectionRole := "Separate owned closure candidate for this incident or independently aggregated occurrence envelope", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("incident", ⟨.ref, .variable "incident"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 34 [.ref, .ref, .frame] :=
  { obligationId := "relation.responds-to:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "incident"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.variable "closure") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "closure", sort := .ref, domain := "incident-closure-records", selectionRole := "Separate owned closure candidate for this incident or independently aggregated occurrence envelope", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("incident", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 34 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.responds-to:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "failure-occurrence"
    branchIndex := 0
    arguments := .cons (.variable "holder") (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 34 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.responds-to:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "incident"
    branchIndex := 1
    arguments := .cons (.variable "holder") (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_0_001
#print axioms plan_1_000
#print axioms plan_1_001
#print axioms plan_2_000
#print axioms plan_2_001
#print axioms plan_3_000
#print axioms plan_3_001
end CandidateConclusionAnchors.K34
