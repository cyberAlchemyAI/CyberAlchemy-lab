import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K12

def plan_0_000 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "goal"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "container") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "container", sort := .ref, domain := "membership-targets", selectionRole := "Exact independently declared container associated with this subject; an Intent or Goal is not silently made a container", joins := [("member", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .variable "container"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "product"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:0"
    sourceKind := "experiment-design"
    targetKind := "goal"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "container") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "container", sort := .ref, domain := "membership-targets", selectionRole := "Exact independently declared container associated with this subject; an Intent or Goal is not silently made a container", joins := [("member", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .variable "container"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:0"
    sourceKind := "experiment-run"
    targetKind := "goal"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.variable "container") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "container", sort := .ref, domain := "membership-targets", selectionRole := "Exact independently declared container associated with this subject; an Intent or Goal is not silently made a container", joins := [("member", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .variable "container"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:0"
    sourceKind := "project"
    targetKind := "goal"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.variable "container") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "container", sort := .ref, domain := "membership-targets", selectionRole := "Exact independently declared container associated with this subject; an Intent or Goal is not silently made a container", joins := [("member", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .variable "container"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_005 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:0"
    sourceKind := "project"
    targetKind := "product"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_006 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:0"
    sourceKind := "research-inquiry"
    targetKind := "goal"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.variable "container") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "container", sort := .ref, domain := "membership-targets", selectionRole := "Exact independently declared container associated with this subject; an Intent or Goal is not silently made a container", joins := [("member", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .variable "container"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_007 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:0"
    sourceKind := "research-run"
    targetKind := "goal"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.variable "container") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "container", sort := .ref, domain := "membership-targets", selectionRole := "Exact independently declared container associated with this subject; an Intent or Goal is not silently made a container", joins := [("member", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .variable "container"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "goal"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "product"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:1"
    sourceKind := "experiment-design"
    targetKind := "goal"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:1"
    sourceKind := "experiment-run"
    targetKind := "goal"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:1"
    sourceKind := "project"
    targetKind := "goal"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_005 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:1"
    sourceKind := "project"
    targetKind := "product"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_006 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:1"
    sourceKind := "research-inquiry"
    targetKind := "goal"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_007 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:1"
    sourceKind := "research-run"
    targetKind := "goal"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 12 [.ref, .result, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "goal"
    branchIndex := 0
    arguments := .cons (.variable "evaluation") (.cons (.variable "result") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "evaluation", sort := .ref, domain := "evaluation-targets", selectionRole := "Independent evaluation associated with this intended contribution", joins := [("activity", ⟨.ref, .source⟩), ("objective", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "result", sort := .result, domain := "evaluation-results", selectionRole := "Independent typed result associated with this exact evaluation; targeting alone supplies no result", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("evaluation", ⟨.ref, .variable "evaluation"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("evaluation", ⟨.ref, .variable "evaluation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 12 [.ref, .result, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "product"
    branchIndex := 1
    arguments := .cons (.variable "evaluation") (.cons (.variable "result") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "evaluation", sort := .ref, domain := "evaluation-targets", selectionRole := "Independent evaluation associated with this intended contribution", joins := [("activity", ⟨.ref, .source⟩), ("objective", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "result", sort := .result, domain := "evaluation-results", selectionRole := "Independent typed result associated with this exact evaluation; targeting alone supplies no result", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("evaluation", ⟨.ref, .variable "evaluation"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("evaluation", ⟨.ref, .variable "evaluation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 12 [.ref, .result, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:2"
    sourceKind := "experiment-design"
    targetKind := "goal"
    branchIndex := 2
    arguments := .cons (.variable "evaluation") (.cons (.variable "result") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "evaluation", sort := .ref, domain := "evaluation-targets", selectionRole := "Independent evaluation associated with this intended contribution", joins := [("activity", ⟨.ref, .source⟩), ("objective", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "result", sort := .result, domain := "evaluation-results", selectionRole := "Independent typed result associated with this exact evaluation; targeting alone supplies no result", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("evaluation", ⟨.ref, .variable "evaluation"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("evaluation", ⟨.ref, .variable "evaluation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 12 [.ref, .result, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:2"
    sourceKind := "experiment-run"
    targetKind := "goal"
    branchIndex := 3
    arguments := .cons (.variable "evaluation") (.cons (.variable "result") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "evaluation", sort := .ref, domain := "evaluation-targets", selectionRole := "Independent evaluation associated with this intended contribution", joins := [("activity", ⟨.ref, .source⟩), ("objective", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "result", sort := .result, domain := "evaluation-results", selectionRole := "Independent typed result associated with this exact evaluation; targeting alone supplies no result", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("evaluation", ⟨.ref, .variable "evaluation"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("evaluation", ⟨.ref, .variable "evaluation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 12 [.ref, .result, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:2"
    sourceKind := "project"
    targetKind := "goal"
    branchIndex := 4
    arguments := .cons (.variable "evaluation") (.cons (.variable "result") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "evaluation", sort := .ref, domain := "evaluation-targets", selectionRole := "Independent evaluation associated with this intended contribution", joins := [("activity", ⟨.ref, .source⟩), ("objective", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "result", sort := .result, domain := "evaluation-results", selectionRole := "Independent typed result associated with this exact evaluation; targeting alone supplies no result", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("evaluation", ⟨.ref, .variable "evaluation"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("evaluation", ⟨.ref, .variable "evaluation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_005 : Plan 12 [.ref, .result, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:2"
    sourceKind := "project"
    targetKind := "product"
    branchIndex := 5
    arguments := .cons (.variable "evaluation") (.cons (.variable "result") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "evaluation", sort := .ref, domain := "evaluation-targets", selectionRole := "Independent evaluation associated with this intended contribution", joins := [("activity", ⟨.ref, .source⟩), ("objective", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "result", sort := .result, domain := "evaluation-results", selectionRole := "Independent typed result associated with this exact evaluation; targeting alone supplies no result", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("evaluation", ⟨.ref, .variable "evaluation"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("evaluation", ⟨.ref, .variable "evaluation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_006 : Plan 12 [.ref, .result, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:2"
    sourceKind := "research-inquiry"
    targetKind := "goal"
    branchIndex := 6
    arguments := .cons (.variable "evaluation") (.cons (.variable "result") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "evaluation", sort := .ref, domain := "evaluation-targets", selectionRole := "Independent evaluation associated with this intended contribution", joins := [("activity", ⟨.ref, .source⟩), ("objective", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "result", sort := .result, domain := "evaluation-results", selectionRole := "Independent typed result associated with this exact evaluation; targeting alone supplies no result", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("evaluation", ⟨.ref, .variable "evaluation"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("evaluation", ⟨.ref, .variable "evaluation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_007 : Plan 12 [.ref, .result, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:2"
    sourceKind := "research-run"
    targetKind := "goal"
    branchIndex := 7
    arguments := .cons (.variable "evaluation") (.cons (.variable "result") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "evaluation", sort := .ref, domain := "evaluation-targets", selectionRole := "Independent evaluation associated with this intended contribution", joins := [("activity", ⟨.ref, .source⟩), ("objective", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "result", sort := .result, domain := "evaluation-results", selectionRole := "Independent typed result associated with this exact evaluation; targeting alone supplies no result", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("evaluation", ⟨.ref, .variable "evaluation"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("evaluation", ⟨.ref, .variable "evaluation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "goal"
    branchIndex := 0
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "product"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .target⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .target⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_002 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:3"
    sourceKind := "experiment-design"
    targetKind := "goal"
    branchIndex := 2
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_003 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:3"
    sourceKind := "experiment-run"
    targetKind := "goal"
    branchIndex := 3
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_004 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:3"
    sourceKind := "project"
    targetKind := "goal"
    branchIndex := 4
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_005 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:3"
    sourceKind := "project"
    targetKind := "product"
    branchIndex := 5
    arguments := .cons (.target) (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .target⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .target⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_006 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:3"
    sourceKind := "research-inquiry"
    targetKind := "goal"
    branchIndex := 6
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_007 : Plan 12 [.ref, .ref, .ref] :=
  { obligationId := "relation.contributes-to:forbidden:3"
    sourceKind := "research-run"
    targetKind := "goal"
    branchIndex := 7
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
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
#print axioms plan_1_000
#print axioms plan_1_001
#print axioms plan_1_002
#print axioms plan_1_003
#print axioms plan_1_004
#print axioms plan_1_005
#print axioms plan_1_006
#print axioms plan_1_007
#print axioms plan_2_000
#print axioms plan_2_001
#print axioms plan_2_002
#print axioms plan_2_003
#print axioms plan_2_004
#print axioms plan_2_005
#print axioms plan_2_006
#print axioms plan_2_007
#print axioms plan_3_000
#print axioms plan_3_001
#print axioms plan_3_002
#print axioms plan_3_003
#print axioms plan_3_004
#print axioms plan_3_005
#print axioms plan_3_006
#print axioms plan_3_007
end CandidateConclusionAnchors.K12
