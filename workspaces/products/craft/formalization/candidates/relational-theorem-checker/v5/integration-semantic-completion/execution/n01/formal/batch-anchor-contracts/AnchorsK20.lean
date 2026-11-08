import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K20

def plan_0_000 : Plan 20 [.ref, .epoch, .ref, .ref] :=
  { obligationId := "relation.fulfills-request:forbidden:0"
    sourceKind := "context-view"
    targetKind := "context-request"
    branchIndex := 0
    arguments := .cons (.variable "source") (.cons (.frameField "epoch" (by decide)) (.cons (.frameField "timeDomain" (by decide)) (.cons (.variable "observedHead") (.nil))))
    binders := [
      { name := "source", sort := .ref, domain := "view-lineage", selectionRole := "Exact included source revision of this immutable view, excluding omitted material", joins := [("view", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "observedHead", sort := .ref, domain := "live-source-observations", selectionRole := "Exact independently observed source-head revision at the requested live epoch and time domain", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .variable "source"⟩), ("timeDomain", ⟨.ref, .frameField "timeDomain" (by decide)⟩), ("now", ⟨.epoch, .frameField "epoch" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 20 [.ref, .ref, .ref] :=
  { obligationId := "relation.fulfills-request:forbidden:1"
    sourceKind := "context-view"
    targetKind := "context-request"
    branchIndex := 0
    arguments := .cons (.variable "source") (.cons (.variable "boundary") (.cons (.variable "admissionOrGrant") (.nil)))
    binders := [
      { name := "source", sort := .ref, domain := "view-lineage", selectionRole := "Exact included source revision of this immutable view, excluding omitted material", joins := [("view", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact independent governance boundary recognizing the named source/holder", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .variable "source"⟩)] },
      { name := "admissionOrGrant", sort := .ref, domain := "admission-or-grant-records", selectionRole := "Separate actual admission/grant candidate for that source and authority boundary", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .variable "source"⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 20 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.fulfills-request:forbidden:2"
    sourceKind := "context-view"
    targetKind := "context-request"
    branchIndex := 0
    arguments := .cons (.variable "context") (.cons (.variable "before") (.cons (.variable "after") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "context", sort := .ref, domain := "view-contexts", selectionRole := "Exact Context revision referenced by this fulfilled Context View and Request", joins := [("view", ⟨.ref, .source⟩), ("request", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "before", sort := .ref, domain := "measurement-snapshots", selectionRole := "Exact baseline observation/state revision for this target under the selected metric policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("context", ⟨.ref, .variable "context"⟩)] },
      { name := "after", sort := .ref, domain := "measurement-snapshots", selectionRole := "Exact comparison observation/state revision for this same target under that metric policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("context", ⟨.ref, .variable "context"⟩), ("before", ⟨.ref, .variable "before"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("context", ⟨.ref, .variable "context"⟩), ("before", ⟨.ref, .variable "before"⟩), ("after", ⟨.ref, .variable "after"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_1_000
#print axioms plan_2_000
end CandidateConclusionAnchors.K20
