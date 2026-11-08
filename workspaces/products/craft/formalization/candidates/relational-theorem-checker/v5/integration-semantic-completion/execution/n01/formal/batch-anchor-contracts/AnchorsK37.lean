import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K37

def plan_0_000 : Plan 37 [.ref, .ref, .ref] :=
  { obligationId := "relation.tests-hypothesis:forbidden:0"
    sourceKind := "experiment-design"
    targetKind := "hypothesis"
    branchIndex := 0
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact interpreted proposition carried by the targeted Hypothesis revision", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 37 [.ref, .ref, .ref] :=
  { obligationId := "relation.tests-hypothesis:forbidden:1"
    sourceKind := "experiment-design"
    targetKind := "hypothesis"
    branchIndex := 0
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact interpreted proposition carried by the targeted Hypothesis revision", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 37 [.ref, .ref, .world] :=
  { obligationId := "relation.tests-hypothesis:forbidden:2"
    sourceKind := "experiment-design"
    targetKind := "hypothesis"
    branchIndex := 0
    arguments := .cons (.variable "claim") (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact interpreted proposition carried by the targeted Hypothesis revision", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 37 [.ref, .ref, .ref] :=
  { obligationId := "relation.tests-hypothesis:forbidden:3"
    sourceKind := "experiment-design"
    targetKind := "hypothesis"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("design", ⟨.ref, .source⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("design", ⟨.ref, .source⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_1_000
#print axioms plan_2_000
#print axioms plan_3_000
end CandidateConclusionAnchors.K37
