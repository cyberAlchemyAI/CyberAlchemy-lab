import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K03

def plan_0_000 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "agent-capability"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "agent-session"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "artifact-type"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "generated-output"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "implementation"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_005 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "ontology"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_006 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "person-reference"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_007 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "product"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_008 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "product-capability"
    branchIndex := 8
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_009 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "project"
    branchIndex := 9
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_010 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "work"
    branchIndex := 10
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_011 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "incident"
    targetKind := "agent-capability"
    branchIndex := 11
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_012 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "incident"
    targetKind := "agent-session"
    branchIndex := 12
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_013 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "incident"
    targetKind := "artifact-type"
    branchIndex := 13
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_014 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "incident"
    targetKind := "generated-output"
    branchIndex := 14
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_015 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "incident"
    targetKind := "implementation"
    branchIndex := 15
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_016 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "incident"
    targetKind := "ontology"
    branchIndex := 16
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_017 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "incident"
    targetKind := "person-reference"
    branchIndex := 17
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_018 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "incident"
    targetKind := "product"
    branchIndex := 18
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_019 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "incident"
    targetKind := "product-capability"
    branchIndex := 19
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_020 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "incident"
    targetKind := "project"
    branchIndex := 20
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_021 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:0"
    sourceKind := "incident"
    targetKind := "work"
    branchIndex := 21
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .source⟩), ("outcome", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "agent-capability"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
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

def plan_1_002 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "artifact-type"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "generated-output"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "implementation"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_005 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "ontology"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_006 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "person-reference"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_007 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "product"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_008 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "product-capability"
    branchIndex := 8
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_009 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "project"
    branchIndex := 9
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_010 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "work"
    branchIndex := 10
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_011 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "incident"
    targetKind := "agent-capability"
    branchIndex := 11
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_012 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "incident"
    targetKind := "agent-session"
    branchIndex := 12
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_013 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "incident"
    targetKind := "artifact-type"
    branchIndex := 13
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_014 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "incident"
    targetKind := "generated-output"
    branchIndex := 14
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_015 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "incident"
    targetKind := "implementation"
    branchIndex := 15
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_016 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "incident"
    targetKind := "ontology"
    branchIndex := 16
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_017 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "incident"
    targetKind := "person-reference"
    branchIndex := 17
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_018 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "incident"
    targetKind := "product"
    branchIndex := 18
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_019 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "incident"
    targetKind := "product-capability"
    branchIndex := 19
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_020 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "incident"
    targetKind := "project"
    branchIndex := 20
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_021 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:1"
    sourceKind := "incident"
    targetKind := "work"
    branchIndex := 21
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "agent-capability"
    branchIndex := 0
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
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

def plan_2_002 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "artifact-type"
    branchIndex := 2
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "generated-output"
    branchIndex := 3
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "implementation"
    branchIndex := 4
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_005 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "ontology"
    branchIndex := 5
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_006 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "person-reference"
    branchIndex := 6
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_007 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "product"
    branchIndex := 7
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_008 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "product-capability"
    branchIndex := 8
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_009 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "project"
    branchIndex := 9
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_010 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "work"
    branchIndex := 10
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_011 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "incident"
    targetKind := "agent-capability"
    branchIndex := 11
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_012 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "incident"
    targetKind := "agent-session"
    branchIndex := 12
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_013 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "incident"
    targetKind := "artifact-type"
    branchIndex := 13
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_014 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "incident"
    targetKind := "generated-output"
    branchIndex := 14
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_015 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "incident"
    targetKind := "implementation"
    branchIndex := 15
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_016 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "incident"
    targetKind := "ontology"
    branchIndex := 16
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_017 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "incident"
    targetKind := "person-reference"
    branchIndex := 17
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_018 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "incident"
    targetKind := "product"
    branchIndex := 18
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_019 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "incident"
    targetKind := "product-capability"
    branchIndex := 19
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_020 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "incident"
    targetKind := "project"
    branchIndex := 20
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_021 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:2"
    sourceKind := "incident"
    targetKind := "work"
    branchIndex := 21
    arguments := .cons (.variable "actor") (.cons (.source) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently assessed actor associated with this occurrence; timing does not identify blame", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("actor", ⟨.ref, .variable "actor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "agent-capability"
    branchIndex := 0
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "agent-session"
    branchIndex := 1
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_002 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "artifact-type"
    branchIndex := 2
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_003 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "generated-output"
    branchIndex := 3
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_004 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "implementation"
    branchIndex := 4
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_005 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "ontology"
    branchIndex := 5
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_006 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "person-reference"
    branchIndex := 6
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_007 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "product"
    branchIndex := 7
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_008 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "product-capability"
    branchIndex := 8
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_009 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "project"
    branchIndex := 9
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_010 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "work"
    branchIndex := 10
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_011 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "incident"
    targetKind := "agent-capability"
    branchIndex := 11
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_012 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "incident"
    targetKind := "agent-session"
    branchIndex := 12
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_013 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "incident"
    targetKind := "artifact-type"
    branchIndex := 13
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_014 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "incident"
    targetKind := "generated-output"
    branchIndex := 14
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_015 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "incident"
    targetKind := "implementation"
    branchIndex := 15
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_016 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "incident"
    targetKind := "ontology"
    branchIndex := 16
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_017 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "incident"
    targetKind := "person-reference"
    branchIndex := 17
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_018 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "incident"
    targetKind := "product"
    branchIndex := 18
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_019 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "incident"
    targetKind := "product-capability"
    branchIndex := 19
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_020 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "incident"
    targetKind := "project"
    branchIndex := 20
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_021 : Plan 3 [.ref, .ref, .ref] :=
  { obligationId := "relation.affects:forbidden:3"
    sourceKind := "incident"
    targetKind := "work"
    branchIndex := 21
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_0_001
#print axioms plan_0_002
#print axioms plan_0_003
#print axioms plan_0_004
#print axioms plan_0_005
#print axioms plan_0_006
#print axioms plan_0_007
#print axioms plan_0_008
#print axioms plan_0_009
#print axioms plan_0_010
#print axioms plan_0_011
#print axioms plan_0_012
#print axioms plan_0_013
#print axioms plan_0_014
#print axioms plan_0_015
#print axioms plan_0_016
#print axioms plan_0_017
#print axioms plan_0_018
#print axioms plan_0_019
#print axioms plan_0_020
#print axioms plan_0_021
#print axioms plan_1_000
#print axioms plan_1_001
#print axioms plan_1_002
#print axioms plan_1_003
#print axioms plan_1_004
#print axioms plan_1_005
#print axioms plan_1_006
#print axioms plan_1_007
#print axioms plan_1_008
#print axioms plan_1_009
#print axioms plan_1_010
#print axioms plan_1_011
#print axioms plan_1_012
#print axioms plan_1_013
#print axioms plan_1_014
#print axioms plan_1_015
#print axioms plan_1_016
#print axioms plan_1_017
#print axioms plan_1_018
#print axioms plan_1_019
#print axioms plan_1_020
#print axioms plan_1_021
#print axioms plan_2_000
#print axioms plan_2_001
#print axioms plan_2_002
#print axioms plan_2_003
#print axioms plan_2_004
#print axioms plan_2_005
#print axioms plan_2_006
#print axioms plan_2_007
#print axioms plan_2_008
#print axioms plan_2_009
#print axioms plan_2_010
#print axioms plan_2_011
#print axioms plan_2_012
#print axioms plan_2_013
#print axioms plan_2_014
#print axioms plan_2_015
#print axioms plan_2_016
#print axioms plan_2_017
#print axioms plan_2_018
#print axioms plan_2_019
#print axioms plan_2_020
#print axioms plan_2_021
#print axioms plan_3_000
#print axioms plan_3_001
#print axioms plan_3_002
#print axioms plan_3_003
#print axioms plan_3_004
#print axioms plan_3_005
#print axioms plan_3_006
#print axioms plan_3_007
#print axioms plan_3_008
#print axioms plan_3_009
#print axioms plan_3_010
#print axioms plan_3_011
#print axioms plan_3_012
#print axioms plan_3_013
#print axioms plan_3_014
#print axioms plan_3_015
#print axioms plan_3_016
#print axioms plan_3_017
#print axioms plan_3_018
#print axioms plan_3_019
#print axioms plan_3_020
#print axioms plan_3_021
end CandidateConclusionAnchors.K03
