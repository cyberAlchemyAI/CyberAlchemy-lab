import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K29

def plan_0_000 : Plan 29 [.ref, .ref, .ref] :=
  { obligationId := "relation.performs:forbidden:0"
    sourceKind := "agent-instance"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .source⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 29 [.ref, .ref, .ref] :=
  { obligationId := "relation.performs:forbidden:0"
    sourceKind := "agent-instance"
    targetKind := "experiment-run"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .source⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 29 [.ref, .ref, .ref] :=
  { obligationId := "relation.performs:forbidden:0"
    sourceKind := "agent-instance"
    targetKind := "research-run"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .source⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 29 [.ref, .ref, .ref] :=
  { obligationId := "relation.performs:forbidden:0"
    sourceKind := "agent-instance"
    targetKind := "review"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .source⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 29 [.ref, .ref, .ref] :=
  { obligationId := "relation.performs:forbidden:0"
    sourceKind := "agent-instance"
    targetKind := "work"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .source⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 29 [.ref, .ref, .frame] :=
  { obligationId := "relation.performs:forbidden:1"
    sourceKind := "agent-instance"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "owner") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "review-owners", selectionRole := "Exact independently assigned accountable owner for this operation and approval scope; the performing agent is not assumed to be its own approving owner", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 29 [.ref, .ref, .frame] :=
  { obligationId := "relation.performs:forbidden:1"
    sourceKind := "agent-instance"
    targetKind := "experiment-run"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.variable "owner") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "review-owners", selectionRole := "Exact independently assigned accountable owner for this operation and approval scope; the performing agent is not assumed to be its own approving owner", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 29 [.ref, .ref, .frame] :=
  { obligationId := "relation.performs:forbidden:1"
    sourceKind := "agent-instance"
    targetKind := "research-run"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.variable "owner") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "review-owners", selectionRole := "Exact independently assigned accountable owner for this operation and approval scope; the performing agent is not assumed to be its own approving owner", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 29 [.ref, .ref, .frame] :=
  { obligationId := "relation.performs:forbidden:1"
    sourceKind := "agent-instance"
    targetKind := "review"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.variable "owner") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "review-owners", selectionRole := "Exact independently assigned accountable owner for this operation and approval scope; the performing agent is not assumed to be its own approving owner", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 29 [.ref, .ref, .frame] :=
  { obligationId := "relation.performs:forbidden:1"
    sourceKind := "agent-instance"
    targetKind := "work"
    branchIndex := 4
    arguments := .cons (.target) (.cons (.variable "owner") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "review-owners", selectionRole := "Exact independently assigned accountable owner for this operation and approval scope; the performing agent is not assumed to be its own approving owner", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 29 [.ref, .ref, .ref] :=
  { obligationId := "relation.performs:forbidden:2"
    sourceKind := "agent-instance"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 29 [.ref, .ref, .ref] :=
  { obligationId := "relation.performs:forbidden:2"
    sourceKind := "agent-instance"
    targetKind := "experiment-run"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 29 [.ref, .ref, .ref] :=
  { obligationId := "relation.performs:forbidden:2"
    sourceKind := "agent-instance"
    targetKind := "research-run"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 29 [.ref, .ref, .ref] :=
  { obligationId := "relation.performs:forbidden:2"
    sourceKind := "agent-instance"
    targetKind := "review"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 29 [.ref, .ref, .ref] :=
  { obligationId := "relation.performs:forbidden:2"
    sourceKind := "agent-instance"
    targetKind := "work"
    branchIndex := 4
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 29 [.ref, .ref, .ref] :=
  { obligationId := "relation.performs:forbidden:3"
    sourceKind := "agent-instance"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "objective") (.cons (.variable "observation") (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("action", ⟨.ref, .target⟩)] },
      { name := "observation", sort := .ref, domain := "outcome-observations", selectionRole := "Exact independent outcome/external observation for this operation and its environment/objective", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("action", ⟨.ref, .target⟩), ("objective", ⟨.ref, .variable "objective"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 29 [.ref, .ref, .ref] :=
  { obligationId := "relation.performs:forbidden:3"
    sourceKind := "agent-instance"
    targetKind := "experiment-run"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.variable "objective") (.cons (.variable "observation") (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("action", ⟨.ref, .target⟩)] },
      { name := "observation", sort := .ref, domain := "outcome-observations", selectionRole := "Exact independent outcome/external observation for this operation and its environment/objective", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("action", ⟨.ref, .target⟩), ("objective", ⟨.ref, .variable "objective"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_002 : Plan 29 [.ref, .ref, .ref] :=
  { obligationId := "relation.performs:forbidden:3"
    sourceKind := "agent-instance"
    targetKind := "research-run"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.variable "objective") (.cons (.variable "observation") (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("action", ⟨.ref, .target⟩)] },
      { name := "observation", sort := .ref, domain := "outcome-observations", selectionRole := "Exact independent outcome/external observation for this operation and its environment/objective", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("action", ⟨.ref, .target⟩), ("objective", ⟨.ref, .variable "objective"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_003 : Plan 29 [.ref, .ref, .ref] :=
  { obligationId := "relation.performs:forbidden:3"
    sourceKind := "agent-instance"
    targetKind := "review"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.variable "objective") (.cons (.variable "observation") (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("action", ⟨.ref, .target⟩)] },
      { name := "observation", sort := .ref, domain := "outcome-observations", selectionRole := "Exact independent outcome/external observation for this operation and its environment/objective", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("action", ⟨.ref, .target⟩), ("objective", ⟨.ref, .variable "objective"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_004 : Plan 29 [.ref, .ref, .ref] :=
  { obligationId := "relation.performs:forbidden:3"
    sourceKind := "agent-instance"
    targetKind := "work"
    branchIndex := 4
    arguments := .cons (.target) (.cons (.variable "objective") (.cons (.variable "observation") (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("action", ⟨.ref, .target⟩)] },
      { name := "observation", sort := .ref, domain := "outcome-observations", selectionRole := "Exact independent outcome/external observation for this operation and its environment/objective", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("action", ⟨.ref, .target⟩), ("objective", ⟨.ref, .variable "objective"⟩)] }
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
#print axioms plan_3_000
#print axioms plan_3_001
#print axioms plan_3_002
#print axioms plan_3_003
#print axioms plan_3_004
end CandidateConclusionAnchors.K29
