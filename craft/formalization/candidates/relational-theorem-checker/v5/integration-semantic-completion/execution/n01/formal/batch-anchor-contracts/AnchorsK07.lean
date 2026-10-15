import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K07

def plan_0_000 : Plan 7 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.binds-implementation:forbidden:0"
    sourceKind := "implementation"
    targetKind := "ontology"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 7 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.binds-implementation:forbidden:0"
    sourceKind := "implementation"
    targetKind := "schema"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 7 [.ref, .ref, .ref] :=
  { obligationId := "relation.binds-implementation:forbidden:1"
    sourceKind := "implementation"
    targetKind := "ontology"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("implementation", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("implementation", ⟨.ref, .source⟩), ("objective", ⟨.ref, .variable "objective"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 7 [.ref, .ref, .ref] :=
  { obligationId := "relation.binds-implementation:forbidden:1"
    sourceKind := "implementation"
    targetKind := "schema"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("implementation", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("implementation", ⟨.ref, .source⟩), ("objective", ⟨.ref, .variable "objective"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 7 [.ref, .ref, .ref] :=
  { obligationId := "relation.binds-implementation:forbidden:2"
    sourceKind := "implementation"
    targetKind := "ontology"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 7 [.ref, .ref, .ref] :=
  { obligationId := "relation.binds-implementation:forbidden:2"
    sourceKind := "implementation"
    targetKind := "schema"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_0_001
#print axioms plan_1_000
#print axioms plan_1_001
#print axioms plan_2_000
#print axioms plan_2_001
end CandidateConclusionAnchors.K07
