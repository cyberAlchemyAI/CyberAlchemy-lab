import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K33

def plan_0_000 : Plan 33 [.ref, .ref, .ref] :=
  { obligationId := "relation.requests-resolution-of:forbidden:0"
    sourceKind := "context-request"
    targetKind := "context"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "resolution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "resolution", sort := .ref, domain := "resolution-records", selectionRole := "Completed resolution candidate for this exact target under its owned criteria", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("resolution", ⟨.ref, .variable "resolution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 33 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.requests-resolution-of:forbidden:1"
    sourceKind := "context-request"
    targetKind := "context"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "before") (.cons (.variable "after") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "before", sort := .ref, domain := "measurement-snapshots", selectionRole := "Exact baseline observation/state revision for this target under the selected metric policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("context", ⟨.ref, .target⟩)] },
      { name := "after", sort := .ref, domain := "measurement-snapshots", selectionRole := "Exact comparison observation/state revision for this same target under that metric policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("context", ⟨.ref, .target⟩), ("before", ⟨.ref, .variable "before"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("context", ⟨.ref, .target⟩), ("before", ⟨.ref, .variable "before"⟩), ("after", ⟨.ref, .variable "after"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 33 [.ref, .ref, .ref] :=
  { obligationId := "relation.requests-resolution-of:forbidden:2"
    sourceKind := "context-request"
    targetKind := "context"
    branchIndex := 0
    arguments := .cons (.variable "source") (.cons (.variable "boundary") (.cons (.variable "admissionOrGrant") (.nil)))
    binders := [
      { name := "source", sort := .ref, domain := "context-source-boundary", selectionRole := "Exact source revision selected by the requested Context boundary", joins := [("context", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact independent governance boundary recognizing the named source/holder", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .variable "source"⟩)] },
      { name := "admissionOrGrant", sort := .ref, domain := "admission-or-grant-records", selectionRole := "Separate actual admission/grant candidate for that source and authority boundary", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .variable "source"⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_1_000
#print axioms plan_2_000
end CandidateConclusionAnchors.K33
