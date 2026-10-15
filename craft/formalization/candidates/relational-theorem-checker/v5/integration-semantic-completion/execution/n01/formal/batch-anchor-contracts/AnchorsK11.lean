import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K11

def plan_0_000 : Plan 11 [.ref, .epoch, .ref, .ref] :=
  { obligationId := "relation.consumes-view:forbidden:0"
    sourceKind := "agent-session"
    targetKind := "context-view"
    branchIndex := 0
    arguments := .cons (.variable "source") (.cons (.frameField "epoch" (by decide)) (.cons (.frameField "timeDomain" (by decide)) (.cons (.variable "observedHead") (.nil))))
    binders := [
      { name := "source", sort := .ref, domain := "view-lineage", selectionRole := "Exact included source revision of this immutable view, excluding omitted material", joins := [("view", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "observedHead", sort := .ref, domain := "live-source-observations", selectionRole := "Exact independently observed source-head revision at the requested live epoch and time domain", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .variable "source"⟩), ("timeDomain", ⟨.ref, .frameField "timeDomain" (by decide)⟩), ("now", ⟨.epoch, .frameField "epoch" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 11 [.ref, .epoch, .ref, .ref] :=
  { obligationId := "relation.consumes-view:forbidden:0"
    sourceKind := "agent-session"
    targetKind := "ontology-view"
    branchIndex := 1
    arguments := .cons (.variable "source") (.cons (.frameField "epoch" (by decide)) (.cons (.frameField "timeDomain" (by decide)) (.cons (.variable "observedHead") (.nil))))
    binders := [
      { name := "source", sort := .ref, domain := "view-lineage", selectionRole := "Exact included source revision of this immutable view, excluding omitted material", joins := [("view", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "observedHead", sort := .ref, domain := "live-source-observations", selectionRole := "Exact independently observed source-head revision at the requested live epoch and time domain", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .variable "source"⟩), ("timeDomain", ⟨.ref, .frameField "timeDomain" (by decide)⟩), ("now", ⟨.epoch, .frameField "epoch" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 11 [.ref, .ref, .ref] :=
  { obligationId := "relation.consumes-view:forbidden:1"
    sourceKind := "agent-session"
    targetKind := "context-view"
    branchIndex := 0
    arguments := .cons (.variable "source") (.cons (.variable "boundary") (.cons (.variable "admissionOrGrant") (.nil)))
    binders := [
      { name := "source", sort := .ref, domain := "view-lineage", selectionRole := "Exact included source revision of this immutable view, excluding omitted material", joins := [("view", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact independent governance boundary recognizing the named source/holder", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .variable "source"⟩)] },
      { name := "admissionOrGrant", sort := .ref, domain := "admission-or-grant-records", selectionRole := "Separate actual admission/grant candidate for that source and authority boundary", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .variable "source"⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 11 [.ref, .ref, .ref] :=
  { obligationId := "relation.consumes-view:forbidden:1"
    sourceKind := "agent-session"
    targetKind := "ontology-view"
    branchIndex := 1
    arguments := .cons (.variable "source") (.cons (.variable "boundary") (.cons (.variable "admissionOrGrant") (.nil)))
    binders := [
      { name := "source", sort := .ref, domain := "view-lineage", selectionRole := "Exact included source revision of this immutable view, excluding omitted material", joins := [("view", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact independent governance boundary recognizing the named source/holder", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .variable "source"⟩)] },
      { name := "admissionOrGrant", sort := .ref, domain := "admission-or-grant-records", selectionRole := "Separate actual admission/grant candidate for that source and authority boundary", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .variable "source"⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 11 [.ref, .ref, .ref] :=
  { obligationId := "relation.consumes-view:forbidden:2"
    sourceKind := "agent-session"
    targetKind := "context-view"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "ownershipRecord") (.nil)))
    binders := [
      { name := "ownershipRecord", sort := .ref, domain := "ownership-records", selectionRole := "Separate exact ownership record joining holder and memory/artifact", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("holder", ⟨.ref, .source⟩), ("memory", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 11 [.ref, .ref, .ref] :=
  { obligationId := "relation.consumes-view:forbidden:2"
    sourceKind := "agent-session"
    targetKind := "ontology-view"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "ownershipRecord") (.nil)))
    binders := [
      { name := "ownershipRecord", sort := .ref, domain := "ownership-records", selectionRole := "Separate exact ownership record joining holder and memory/artifact", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("holder", ⟨.ref, .source⟩), ("memory", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 11 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.consumes-view:forbidden:3"
    sourceKind := "agent-session"
    targetKind := "context-view"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "request") (.cons (.variable "criteria") (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "request", sort := .ref, domain := "view-requests", selectionRole := "Exact Context Request independently referenced by this view; consumption alone does not fulfill it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("view", ⟨.ref, .target⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("view", ⟨.ref, .target⟩), ("request", ⟨.ref, .variable "request"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 11 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.consumes-view:forbidden:3"
    sourceKind := "agent-session"
    targetKind := "ontology-view"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.variable "request") (.cons (.variable "criteria") (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "request", sort := .ref, domain := "view-requests", selectionRole := "Exact Context Request independently referenced by this view; consumption alone does not fulfill it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("view", ⟨.ref, .target⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("view", ⟨.ref, .target⟩), ("request", ⟨.ref, .variable "request"⟩)] }
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
end CandidateConclusionAnchors.K11
