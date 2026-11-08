import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K32

def plan_0_000 : Plan 32 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.realizes:forbidden:0"
    sourceKind := "experiment-run"
    targetKind := "experiment-design"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 32 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.realizes:forbidden:0"
    sourceKind := "implementation"
    targetKind := "product-capability"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 32 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.realizes:forbidden:1"
    sourceKind := "experiment-run"
    targetKind := "experiment-design"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.variable "metric") (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩)] },
      { name := "metric", sort := .ref, domain := "metric-definitions", selectionRole := "Exact independently owned outcome/benefit/improvement metric for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("objective", ⟨.ref, .variable "objective"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 32 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.realizes:forbidden:1"
    sourceKind := "implementation"
    targetKind := "product-capability"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.variable "metric") (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩)] },
      { name := "metric", sort := .ref, domain := "metric-definitions", selectionRole := "Exact independently owned outcome/benefit/improvement metric for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("objective", ⟨.ref, .variable "objective"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 32 [.ref, .ref, .ref] :=
  { obligationId := "relation.realizes:forbidden:2"
    sourceKind := "experiment-run"
    targetKind := "experiment-design"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 32 [.ref, .ref, .ref] :=
  { obligationId := "relation.realizes:forbidden:2"
    sourceKind := "implementation"
    targetKind := "product-capability"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 32 [.ref, .ref, .ref] :=
  { obligationId := "relation.realizes:forbidden:3"
    sourceKind := "experiment-run"
    targetKind := "experiment-design"
    branchIndex := 0
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 32 [.ref, .ref, .ref] :=
  { obligationId := "relation.realizes:forbidden:3"
    sourceKind := "implementation"
    targetKind := "product-capability"
    branchIndex := 1
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
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
end CandidateConclusionAnchors.K32
