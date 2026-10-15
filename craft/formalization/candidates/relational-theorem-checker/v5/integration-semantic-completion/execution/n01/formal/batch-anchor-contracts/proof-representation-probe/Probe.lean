import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K02

def plan_0_000 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:0"
    sourceKind := "agent-assignment"
    targetKind := "intent"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "tests") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "tests", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete satisfaction-test set selected by this Intent Resolution; not a fabricated single test", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("tests", ⟨.ref, .variable "tests"⟩)] }
    ]
    constraints := []
    structurallyValid := by rfl }

def plan_0_001 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:0"
    sourceKind := "goal"
    targetKind := "intent"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.variable "tests") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "tests", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete satisfaction-test set selected by this Intent Resolution; not a fabricated single test", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("tests", ⟨.ref, .variable "tests"⟩)] }
    ]
    constraints := []
    structurallyValid := by rfl }

def plan_0_002 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:0"
    sourceKind := "product"
    targetKind := "intent"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.variable "tests") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "tests", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete satisfaction-test set selected by this Intent Resolution; not a fabricated single test", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("tests", ⟨.ref, .variable "tests"⟩)] }
    ]
    constraints := []
    structurallyValid := by rfl }

def plan_0_003 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:0"
    sourceKind := "product-capability"
    targetKind := "intent"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.variable "tests") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "tests", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete satisfaction-test set selected by this Intent Resolution; not a fabricated single test", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("tests", ⟨.ref, .variable "tests"⟩)] }
    ]
    constraints := []
    structurallyValid := by rfl }

def plan_0_004 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:0"
    sourceKind := "project"
    targetKind := "intent"
    branchIndex := 4
    arguments := .cons (.target) (.cons (.variable "tests") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "tests", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete satisfaction-test set selected by this Intent Resolution; not a fabricated single test", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("tests", ⟨.ref, .variable "tests"⟩)] }
    ]
    constraints := []
    structurallyValid := by rfl }

def plan_0_005 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:0"
    sourceKind := "research-inquiry"
    targetKind := "intent"
    branchIndex := 5
    arguments := .cons (.target) (.cons (.variable "tests") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "tests", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete satisfaction-test set selected by this Intent Resolution; not a fabricated single test", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("tests", ⟨.ref, .variable "tests"⟩)] }
    ]
    constraints := []
    structurallyValid := by rfl }


end CandidateConclusionAnchors.K02
