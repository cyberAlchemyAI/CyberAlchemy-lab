import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K19

def plan_0_000 : Plan 19 [.ref, .ref, .ref] :=
  { obligationId := "relation.frames:forbidden:0"
    sourceKind := "context"
    targetKind := "bounded-context"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "boundary") (.cons (.variable "admissionOrGrant") (.nil)))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact independent governance boundary recognizing the named source/holder", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩)] },
      { name := "admissionOrGrant", sort := .ref, domain := "admission-or-grant-records", selectionRole := "Separate actual admission/grant candidate for that source and authority boundary", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 19 [.ref, .ref, .ref] :=
  { obligationId := "relation.frames:forbidden:0"
    sourceKind := "context"
    targetKind := "goal"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.variable "boundary") (.cons (.variable "admissionOrGrant") (.nil)))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact independent governance boundary recognizing the named source/holder", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩)] },
      { name := "admissionOrGrant", sort := .ref, domain := "admission-or-grant-records", selectionRole := "Separate actual admission/grant candidate for that source and authority boundary", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 19 [.ref, .ref, .ref] :=
  { obligationId := "relation.frames:forbidden:0"
    sourceKind := "context"
    targetKind := "product"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.variable "boundary") (.cons (.variable "admissionOrGrant") (.nil)))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact independent governance boundary recognizing the named source/holder", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩)] },
      { name := "admissionOrGrant", sort := .ref, domain := "admission-or-grant-records", selectionRole := "Separate actual admission/grant candidate for that source and authority boundary", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 19 [.ref, .ref, .ref] :=
  { obligationId := "relation.frames:forbidden:0"
    sourceKind := "context"
    targetKind := "project"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.variable "boundary") (.cons (.variable "admissionOrGrant") (.nil)))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact independent governance boundary recognizing the named source/holder", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩)] },
      { name := "admissionOrGrant", sort := .ref, domain := "admission-or-grant-records", selectionRole := "Separate actual admission/grant candidate for that source and authority boundary", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 19 [.ref, .ref, .ref] :=
  { obligationId := "relation.frames:forbidden:0"
    sourceKind := "context"
    targetKind := "review"
    branchIndex := 4
    arguments := .cons (.target) (.cons (.variable "boundary") (.cons (.variable "admissionOrGrant") (.nil)))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact independent governance boundary recognizing the named source/holder", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩)] },
      { name := "admissionOrGrant", sort := .ref, domain := "admission-or-grant-records", selectionRole := "Separate actual admission/grant candidate for that source and authority boundary", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 19 [.ref, .epoch, .ref, .ref] :=
  { obligationId := "relation.frames:forbidden:1"
    sourceKind := "context"
    targetKind := "bounded-context"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.frameField "epoch" (by decide)) (.cons (.frameField "timeDomain" (by decide)) (.cons (.variable "observedHead") (.nil))))
    binders := [
      { name := "observedHead", sort := .ref, domain := "live-source-observations", selectionRole := "Exact independently observed source-head revision at the requested live epoch and time domain", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("timeDomain", ⟨.ref, .frameField "timeDomain" (by decide)⟩), ("now", ⟨.epoch, .frameField "epoch" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 19 [.ref, .epoch, .ref, .ref] :=
  { obligationId := "relation.frames:forbidden:1"
    sourceKind := "context"
    targetKind := "goal"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.frameField "epoch" (by decide)) (.cons (.frameField "timeDomain" (by decide)) (.cons (.variable "observedHead") (.nil))))
    binders := [
      { name := "observedHead", sort := .ref, domain := "live-source-observations", selectionRole := "Exact independently observed source-head revision at the requested live epoch and time domain", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("timeDomain", ⟨.ref, .frameField "timeDomain" (by decide)⟩), ("now", ⟨.epoch, .frameField "epoch" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 19 [.ref, .epoch, .ref, .ref] :=
  { obligationId := "relation.frames:forbidden:1"
    sourceKind := "context"
    targetKind := "product"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.frameField "epoch" (by decide)) (.cons (.frameField "timeDomain" (by decide)) (.cons (.variable "observedHead") (.nil))))
    binders := [
      { name := "observedHead", sort := .ref, domain := "live-source-observations", selectionRole := "Exact independently observed source-head revision at the requested live epoch and time domain", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("timeDomain", ⟨.ref, .frameField "timeDomain" (by decide)⟩), ("now", ⟨.epoch, .frameField "epoch" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 19 [.ref, .epoch, .ref, .ref] :=
  { obligationId := "relation.frames:forbidden:1"
    sourceKind := "context"
    targetKind := "project"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.frameField "epoch" (by decide)) (.cons (.frameField "timeDomain" (by decide)) (.cons (.variable "observedHead") (.nil))))
    binders := [
      { name := "observedHead", sort := .ref, domain := "live-source-observations", selectionRole := "Exact independently observed source-head revision at the requested live epoch and time domain", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("timeDomain", ⟨.ref, .frameField "timeDomain" (by decide)⟩), ("now", ⟨.epoch, .frameField "epoch" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 19 [.ref, .epoch, .ref, .ref] :=
  { obligationId := "relation.frames:forbidden:1"
    sourceKind := "context"
    targetKind := "review"
    branchIndex := 4
    arguments := .cons (.target) (.cons (.frameField "epoch" (by decide)) (.cons (.frameField "timeDomain" (by decide)) (.cons (.variable "observedHead") (.nil))))
    binders := [
      { name := "observedHead", sort := .ref, domain := "live-source-observations", selectionRole := "Exact independently observed source-head revision at the requested live epoch and time domain", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("timeDomain", ⟨.ref, .frameField "timeDomain" (by decide)⟩), ("now", ⟨.epoch, .frameField "epoch" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 19 [.ref, .ref, .world] :=
  { obligationId := "relation.frames:forbidden:2"
    sourceKind := "context"
    targetKind := "bounded-context"
    branchIndex := 0
    arguments := .cons (.variable "claim") (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 19 [.ref, .ref, .world] :=
  { obligationId := "relation.frames:forbidden:2"
    sourceKind := "context"
    targetKind := "goal"
    branchIndex := 1
    arguments := .cons (.variable "claim") (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 19 [.ref, .ref, .world] :=
  { obligationId := "relation.frames:forbidden:2"
    sourceKind := "context"
    targetKind := "product"
    branchIndex := 2
    arguments := .cons (.variable "claim") (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 19 [.ref, .ref, .world] :=
  { obligationId := "relation.frames:forbidden:2"
    sourceKind := "context"
    targetKind := "project"
    branchIndex := 3
    arguments := .cons (.variable "claim") (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 19 [.ref, .ref, .world] :=
  { obligationId := "relation.frames:forbidden:2"
    sourceKind := "context"
    targetKind := "review"
    branchIndex := 4
    arguments := .cons (.variable "claim") (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
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
end CandidateConclusionAnchors.K19
