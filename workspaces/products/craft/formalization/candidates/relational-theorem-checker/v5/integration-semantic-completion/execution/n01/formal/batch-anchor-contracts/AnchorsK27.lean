import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K27

def plan_0_000 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.variable "cause") (.cons (.source) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "cause", sort := .ref, domain := "causal-participants", selectionRole := "Exact independently specified candidate cause of this occurrence/incident; no cause follows from timing or response intention", joins := [("outcome", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .variable "cause"⟩), ("outcome", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "agent-session"
    branchIndex := 1
    arguments := .cons (.variable "cause") (.cons (.source) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "cause", sort := .ref, domain := "causal-participants", selectionRole := "Exact independently specified candidate cause of this occurrence/incident; no cause follows from timing or response intention", joins := [("outcome", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .variable "cause"⟩), ("outcome", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "experiment-run"
    branchIndex := 2
    arguments := .cons (.variable "cause") (.cons (.source) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "cause", sort := .ref, domain := "causal-participants", selectionRole := "Exact independently specified candidate cause of this occurrence/incident; no cause follows from timing or response intention", joins := [("outcome", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .variable "cause"⟩), ("outcome", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "research-run"
    branchIndex := 3
    arguments := .cons (.variable "cause") (.cons (.source) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "cause", sort := .ref, domain := "causal-participants", selectionRole := "Exact independently specified candidate cause of this occurrence/incident; no cause follows from timing or response intention", joins := [("outcome", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .variable "cause"⟩), ("outcome", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "work"
    branchIndex := 4
    arguments := .cons (.variable "cause") (.cons (.source) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "cause", sort := .ref, domain := "causal-participants", selectionRole := "Exact independently specified candidate cause of this occurrence/incident; no cause follows from timing or response intention", joins := [("outcome", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .variable "cause"⟩), ("outcome", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "agent-session"
    branchIndex := 1
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "experiment-run"
    branchIndex := 2
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "research-run"
    branchIndex := 3
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "work"
    branchIndex := 4
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "agent-session"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "experiment-run"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "research-run"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "work"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("envelope", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "agent-session"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("envelope", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_002 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "experiment-run"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("envelope", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_003 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "research-run"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("envelope", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_004 : Plan 27 [.ref, .ref, .ref] :=
  { obligationId := "relation.occurs-during:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "work"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("envelope", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_0_001
#print axioms plan_0_002
#print axioms plan_0_003
#print axioms plan_0_004
#print axioms plan_1_000
#print axioms plan_1_001
#print axioms plan_1_002
#print axioms plan_1_003
#print axioms plan_1_004
#print axioms plan_2_000
#print axioms plan_2_001
#print axioms plan_2_002
#print axioms plan_2_003
#print axioms plan_2_004
#print axioms plan_3_000
#print axioms plan_3_001
#print axioms plan_3_002
#print axioms plan_3_003
#print axioms plan_3_004
end CandidateConclusionAnchors.K27
