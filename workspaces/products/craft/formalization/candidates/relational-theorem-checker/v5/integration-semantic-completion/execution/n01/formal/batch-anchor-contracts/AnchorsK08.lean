import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K08

def plan_0_000 : Plan 8 [.ref, .ref, .ref] :=
  { obligationId := "relation.carries-definition:forbidden:0"
    sourceKind := "artifact-type"
    targetKind := "definition"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 8 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.carries-definition:forbidden:1"
    sourceKind := "artifact-type"
    targetKind := "definition"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 8 [.ref, .ref, .ref] :=
  { obligationId := "relation.carries-definition:forbidden:2"
    sourceKind := "artifact-type"
    targetKind := "definition"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_1_000
#print axioms plan_2_000
end CandidateConclusionAnchors.K08
