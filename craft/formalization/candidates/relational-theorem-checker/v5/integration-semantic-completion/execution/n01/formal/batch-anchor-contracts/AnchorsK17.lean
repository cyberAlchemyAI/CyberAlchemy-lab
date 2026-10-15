import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K17

def plan_0_000 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:0"
    sourceKind := "evaluation"
    targetKind := "capability-realization-binding"
    branchIndex := 0
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:0"
    sourceKind := "evaluation"
    targetKind := "product-capability"
    branchIndex := 1
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:0"
    sourceKind := "evaluation"
    targetKind := "product-thesis"
    branchIndex := 2
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:0"
    sourceKind := "experiment-design"
    targetKind := "capability-realization-binding"
    branchIndex := 3
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:0"
    sourceKind := "experiment-design"
    targetKind := "product"
    branchIndex := 4
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_005 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:0"
    sourceKind := "experiment-design"
    targetKind := "product-capability"
    branchIndex := 5
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_006 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:0"
    sourceKind := "experiment-design"
    targetKind := "product-thesis"
    branchIndex := 6
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_007 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:0"
    sourceKind := "experiment-run"
    targetKind := "capability-realization-binding"
    branchIndex := 7
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_008 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:0"
    sourceKind := "experiment-run"
    targetKind := "product"
    branchIndex := 8
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_009 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:0"
    sourceKind := "experiment-run"
    targetKind := "product-capability"
    branchIndex := 9
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_010 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:0"
    sourceKind := "experiment-run"
    targetKind := "product-thesis"
    branchIndex := 10
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_011 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:0"
    sourceKind := "failure-assessment"
    targetKind := "failure-occurrence"
    branchIndex := 11
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_012 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:0"
    sourceKind := "lesson-outcome-assessment"
    targetKind := "lesson-application"
    branchIndex := 12
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_013 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:0"
    sourceKind := "preference-application-assessment"
    targetKind := "communication-preference"
    branchIndex := 13
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_014 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:0"
    sourceKind := "work-outcome-assessment"
    targetKind := "agent-action"
    branchIndex := 14
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_015 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:0"
    sourceKind := "work-outcome-assessment"
    targetKind := "work"
    branchIndex := 15
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:1"
    sourceKind := "evaluation"
    targetKind := "capability-realization-binding"
    branchIndex := 0
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:1"
    sourceKind := "evaluation"
    targetKind := "product-capability"
    branchIndex := 1
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:1"
    sourceKind := "evaluation"
    targetKind := "product-thesis"
    branchIndex := 2
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:1"
    sourceKind := "experiment-design"
    targetKind := "capability-realization-binding"
    branchIndex := 3
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:1"
    sourceKind := "experiment-design"
    targetKind := "product"
    branchIndex := 4
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_005 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:1"
    sourceKind := "experiment-design"
    targetKind := "product-capability"
    branchIndex := 5
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_006 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:1"
    sourceKind := "experiment-design"
    targetKind := "product-thesis"
    branchIndex := 6
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_007 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:1"
    sourceKind := "experiment-run"
    targetKind := "capability-realization-binding"
    branchIndex := 7
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_008 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:1"
    sourceKind := "experiment-run"
    targetKind := "product"
    branchIndex := 8
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_009 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:1"
    sourceKind := "experiment-run"
    targetKind := "product-capability"
    branchIndex := 9
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_010 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:1"
    sourceKind := "experiment-run"
    targetKind := "product-thesis"
    branchIndex := 10
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_011 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:1"
    sourceKind := "failure-assessment"
    targetKind := "failure-occurrence"
    branchIndex := 11
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_012 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:1"
    sourceKind := "lesson-outcome-assessment"
    targetKind := "lesson-application"
    branchIndex := 12
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_013 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:1"
    sourceKind := "preference-application-assessment"
    targetKind := "communication-preference"
    branchIndex := 13
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_014 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:1"
    sourceKind := "work-outcome-assessment"
    targetKind := "agent-action"
    branchIndex := 14
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_015 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:1"
    sourceKind := "work-outcome-assessment"
    targetKind := "work"
    branchIndex := 15
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:2"
    sourceKind := "evaluation"
    targetKind := "capability-realization-binding"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:2"
    sourceKind := "evaluation"
    targetKind := "product-capability"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:2"
    sourceKind := "evaluation"
    targetKind := "product-thesis"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:2"
    sourceKind := "experiment-design"
    targetKind := "capability-realization-binding"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:2"
    sourceKind := "experiment-design"
    targetKind := "product"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_005 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:2"
    sourceKind := "experiment-design"
    targetKind := "product-capability"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_006 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:2"
    sourceKind := "experiment-design"
    targetKind := "product-thesis"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_007 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:2"
    sourceKind := "experiment-run"
    targetKind := "capability-realization-binding"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_008 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:2"
    sourceKind := "experiment-run"
    targetKind := "product"
    branchIndex := 8
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_009 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:2"
    sourceKind := "experiment-run"
    targetKind := "product-capability"
    branchIndex := 9
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_010 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:2"
    sourceKind := "experiment-run"
    targetKind := "product-thesis"
    branchIndex := 10
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_011 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:2"
    sourceKind := "failure-assessment"
    targetKind := "failure-occurrence"
    branchIndex := 11
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_012 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:2"
    sourceKind := "lesson-outcome-assessment"
    targetKind := "lesson-application"
    branchIndex := 12
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_013 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:2"
    sourceKind := "preference-application-assessment"
    targetKind := "communication-preference"
    branchIndex := 13
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_014 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:2"
    sourceKind := "work-outcome-assessment"
    targetKind := "agent-action"
    branchIndex := 14
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_015 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:2"
    sourceKind := "work-outcome-assessment"
    targetKind := "work"
    branchIndex := 15
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:3"
    sourceKind := "evaluation"
    targetKind := "capability-realization-binding"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:3"
    sourceKind := "evaluation"
    targetKind := "product-capability"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_002 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:3"
    sourceKind := "evaluation"
    targetKind := "product-thesis"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_003 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:3"
    sourceKind := "experiment-design"
    targetKind := "capability-realization-binding"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_004 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:3"
    sourceKind := "experiment-design"
    targetKind := "product"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_005 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:3"
    sourceKind := "experiment-design"
    targetKind := "product-capability"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_006 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:3"
    sourceKind := "experiment-design"
    targetKind := "product-thesis"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_007 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:3"
    sourceKind := "experiment-run"
    targetKind := "capability-realization-binding"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_008 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:3"
    sourceKind := "experiment-run"
    targetKind := "product"
    branchIndex := 8
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_009 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:3"
    sourceKind := "experiment-run"
    targetKind := "product-capability"
    branchIndex := 9
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_010 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:3"
    sourceKind := "experiment-run"
    targetKind := "product-thesis"
    branchIndex := 10
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_011 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:3"
    sourceKind := "failure-assessment"
    targetKind := "failure-occurrence"
    branchIndex := 11
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_012 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:3"
    sourceKind := "lesson-outcome-assessment"
    targetKind := "lesson-application"
    branchIndex := 12
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_013 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:3"
    sourceKind := "preference-application-assessment"
    targetKind := "communication-preference"
    branchIndex := 13
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_014 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:3"
    sourceKind := "work-outcome-assessment"
    targetKind := "agent-action"
    branchIndex := 14
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_015 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:3"
    sourceKind := "work-outcome-assessment"
    targetKind := "work"
    branchIndex := 15
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_4_000 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:4"
    sourceKind := "evaluation"
    targetKind := "capability-realization-binding"
    branchIndex := 0
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_4_001 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:4"
    sourceKind := "evaluation"
    targetKind := "product-capability"
    branchIndex := 1
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_4_002 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:4"
    sourceKind := "evaluation"
    targetKind := "product-thesis"
    branchIndex := 2
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_4_003 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:4"
    sourceKind := "experiment-design"
    targetKind := "capability-realization-binding"
    branchIndex := 3
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_4_004 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:4"
    sourceKind := "experiment-design"
    targetKind := "product"
    branchIndex := 4
    arguments := .cons (.target) (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .target⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .target⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_4_005 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:4"
    sourceKind := "experiment-design"
    targetKind := "product-capability"
    branchIndex := 5
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_4_006 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:4"
    sourceKind := "experiment-design"
    targetKind := "product-thesis"
    branchIndex := 6
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_4_007 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:4"
    sourceKind := "experiment-run"
    targetKind := "capability-realization-binding"
    branchIndex := 7
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_4_008 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:4"
    sourceKind := "experiment-run"
    targetKind := "product"
    branchIndex := 8
    arguments := .cons (.target) (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .target⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .target⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_4_009 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:4"
    sourceKind := "experiment-run"
    targetKind := "product-capability"
    branchIndex := 9
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_4_010 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:4"
    sourceKind := "experiment-run"
    targetKind := "product-thesis"
    branchIndex := 10
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_4_011 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:4"
    sourceKind := "failure-assessment"
    targetKind := "failure-occurrence"
    branchIndex := 11
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_4_012 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:4"
    sourceKind := "lesson-outcome-assessment"
    targetKind := "lesson-application"
    branchIndex := 12
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_4_013 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:4"
    sourceKind := "preference-application-assessment"
    targetKind := "communication-preference"
    branchIndex := 13
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_4_014 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:4"
    sourceKind := "work-outcome-assessment"
    targetKind := "agent-action"
    branchIndex := 14
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_4_015 : Plan 17 [.ref, .ref, .ref] :=
  { obligationId := "relation.evaluates:forbidden:4"
    sourceKind := "work-outcome-assessment"
    targetKind := "work"
    branchIndex := 15
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
#print axioms plan_0_008
#print axioms plan_0_009
#print axioms plan_0_010
#print axioms plan_0_011
#print axioms plan_0_012
#print axioms plan_0_013
#print axioms plan_0_014
#print axioms plan_0_015
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
#print axioms plan_4_000
#print axioms plan_4_001
#print axioms plan_4_002
#print axioms plan_4_003
#print axioms plan_4_004
#print axioms plan_4_005
#print axioms plan_4_006
#print axioms plan_4_007
#print axioms plan_4_008
#print axioms plan_4_009
#print axioms plan_4_010
#print axioms plan_4_011
#print axioms plan_4_012
#print axioms plan_4_013
#print axioms plan_4_014
#print axioms plan_4_015
end CandidateConclusionAnchors.K17
