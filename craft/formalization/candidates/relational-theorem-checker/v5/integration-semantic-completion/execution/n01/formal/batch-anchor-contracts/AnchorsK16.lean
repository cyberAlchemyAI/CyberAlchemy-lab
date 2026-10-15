import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K16

def plan_0_000 : Plan 16 [.ref, .ref, .frame] :=
  { obligationId := "relation.engages-inquiry:forbidden:0"
    sourceKind := "experiment-design"
    targetKind := "research-inquiry"
    branchIndex := 0
    arguments := .cons (.variable "finding") (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "finding", sort := .ref, domain := "research-outputs", selectionRole := "Exact Finding independently recorded as an output of this inquiry activity", joins := [("activity", ⟨.ref, .source⟩), ("inquiry", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("finding", ⟨.ref, .variable "finding"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 16 [.ref, .ref, .frame] :=
  { obligationId := "relation.engages-inquiry:forbidden:0"
    sourceKind := "experiment-run"
    targetKind := "research-inquiry"
    branchIndex := 1
    arguments := .cons (.variable "finding") (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "finding", sort := .ref, domain := "research-outputs", selectionRole := "Exact Finding independently recorded as an output of this inquiry activity", joins := [("activity", ⟨.ref, .source⟩), ("inquiry", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("finding", ⟨.ref, .variable "finding"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 16 [.ref, .ref, .frame] :=
  { obligationId := "relation.engages-inquiry:forbidden:0"
    sourceKind := "finding"
    targetKind := "research-inquiry"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("finding", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 16 [.ref, .ref, .frame] :=
  { obligationId := "relation.engages-inquiry:forbidden:0"
    sourceKind := "research-run"
    targetKind := "research-inquiry"
    branchIndex := 3
    arguments := .cons (.variable "finding") (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "finding", sort := .ref, domain := "research-outputs", selectionRole := "Exact Finding independently recorded as an output of this inquiry activity", joins := [("activity", ⟨.ref, .source⟩), ("inquiry", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("finding", ⟨.ref, .variable "finding"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 16 [.ref, .ref, .ref] :=
  { obligationId := "relation.engages-inquiry:forbidden:1"
    sourceKind := "experiment-design"
    targetKind := "research-inquiry"
    branchIndex := 0
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 16 [.ref, .ref, .ref] :=
  { obligationId := "relation.engages-inquiry:forbidden:1"
    sourceKind := "experiment-run"
    targetKind := "research-inquiry"
    branchIndex := 1
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 16 [.ref, .ref, .ref] :=
  { obligationId := "relation.engages-inquiry:forbidden:1"
    sourceKind := "finding"
    targetKind := "research-inquiry"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact proposed-answer statement carried by this Finding for this Inquiry", joins := [("carrier", ⟨.ref, .source⟩), ("inquiry", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 16 [.ref, .ref, .ref] :=
  { obligationId := "relation.engages-inquiry:forbidden:1"
    sourceKind := "research-run"
    targetKind := "research-inquiry"
    branchIndex := 3
    arguments := .cons (.variable "evidence") (.cons (.variable "claim") (.cons (.frameField "evidencePolicy" (by decide)) (.nil)))
    binders := [
      { name := "evidence", sort := .ref, domain := "evidence-carriers", selectionRole := "Exact evidence independently associated with this evaluated/tested/realized/answer subject", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 16 [.ref, .ref, .frame] :=
  { obligationId := "relation.engages-inquiry:forbidden:2"
    sourceKind := "experiment-design"
    targetKind := "research-inquiry"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "criteria") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("inquiry", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 16 [.ref, .ref, .frame] :=
  { obligationId := "relation.engages-inquiry:forbidden:2"
    sourceKind := "experiment-run"
    targetKind := "research-inquiry"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.variable "criteria") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("inquiry", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 16 [.ref, .ref, .frame] :=
  { obligationId := "relation.engages-inquiry:forbidden:2"
    sourceKind := "finding"
    targetKind := "research-inquiry"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.variable "criteria") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("inquiry", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 16 [.ref, .ref, .frame] :=
  { obligationId := "relation.engages-inquiry:forbidden:2"
    sourceKind := "research-run"
    targetKind := "research-inquiry"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.variable "criteria") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("inquiry", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_0_001
#print axioms plan_0_002
#print axioms plan_0_003
#print axioms plan_1_000
#print axioms plan_1_001
#print axioms plan_1_002
#print axioms plan_1_003
#print axioms plan_2_000
#print axioms plan_2_001
#print axioms plan_2_002
#print axioms plan_2_003
end CandidateConclusionAnchors.K16
