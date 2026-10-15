import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K36

def plan_0_000 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "agent-assignment"
    targetKind := "agent-assignment"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "agent-capability"
    targetKind := "agent-capability"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "agent-instance"
    targetKind := "agent-instance"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "agent-profile"
    targetKind := "agent-profile"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_005 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "agent-reflection"
    targetKind := "agent-reflection"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_006 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "agent-session"
    targetKind := "agent-session"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_007 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "artifact-type"
    targetKind := "artifact-type"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_008 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "artifact-type-request"
    targetKind := "artifact-type-request"
    branchIndex := 8
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_009 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "authority-claim"
    targetKind := "authority-claim"
    branchIndex := 9
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_010 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "bounded-context"
    targetKind := "bounded-context"
    branchIndex := 10
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_011 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "canonical-package-manifest"
    targetKind := "canonical-package-manifest"
    branchIndex := 11
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_012 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "capability-instance"
    targetKind := "capability-instance"
    branchIndex := 12
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_013 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "capability-realization-binding"
    targetKind := "capability-realization-binding"
    branchIndex := 13
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_014 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "challenge-contract"
    targetKind := "challenge-contract"
    branchIndex := 14
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_015 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "challenge-event"
    branchIndex := 15
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_016 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "classification-assignment"
    targetKind := "classification-assignment"
    branchIndex := 16
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_017 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "classification-scheme"
    targetKind := "classification-scheme"
    branchIndex := 17
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_018 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "classification-value"
    targetKind := "classification-value"
    branchIndex := 18
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_019 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "communication-preference"
    targetKind := "communication-preference"
    branchIndex := 19
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_020 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "constitution"
    targetKind := "constitution"
    branchIndex := 20
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_021 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "context"
    targetKind := "context"
    branchIndex := 21
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_022 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "context-lineage-record"
    targetKind := "context-lineage-record"
    branchIndex := 22
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_023 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "context-map"
    targetKind := "context-map"
    branchIndex := 23
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_024 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "context-migration-manifest"
    targetKind := "context-migration-manifest"
    branchIndex := 24
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_025 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "context-profile"
    targetKind := "context-profile"
    branchIndex := 25
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_026 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "context-request"
    targetKind := "context-request"
    branchIndex := 26
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_027 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "context-view"
    targetKind := "context-view"
    branchIndex := 27
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_028 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "contract"
    targetKind := "contract"
    branchIndex := 28
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_029 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "decision"
    targetKind := "decision"
    branchIndex := 29
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_030 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "decision-scope"
    targetKind := "decision-scope"
    branchIndex := 30
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_031 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "definition"
    targetKind := "definition"
    branchIndex := 31
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_032 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "delegation"
    targetKind := "delegation"
    branchIndex := 32
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_033 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "drift-assessment"
    targetKind := "drift-assessment"
    branchIndex := 33
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_034 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "effect"
    targetKind := "effect"
    branchIndex := 34
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_035 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "evaluation"
    targetKind := "evaluation"
    branchIndex := 35
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_036 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "evidence-set"
    branchIndex := 36
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_037 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "experiment-design"
    targetKind := "experiment-design"
    branchIndex := 37
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_038 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "experiment-run"
    targetKind := "experiment-run"
    branchIndex := 38
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_039 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "failure-assessment"
    targetKind := "failure-assessment"
    branchIndex := 39
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_040 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "failure-control-binding"
    targetKind := "failure-control-binding"
    branchIndex := 40
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_041 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "failure-mode"
    targetKind := "failure-mode"
    branchIndex := 41
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_042 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "failure-occurrence"
    branchIndex := 42
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_043 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "feedback-record"
    targetKind := "feedback-record"
    branchIndex := 43
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_044 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "finding"
    targetKind := "finding"
    branchIndex := 44
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_045 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "generated-output"
    targetKind := "generated-output"
    branchIndex := 45
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_046 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "goal"
    targetKind := "goal"
    branchIndex := 46
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_047 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "governance-event-history"
    targetKind := "governance-event-history"
    branchIndex := 47
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_048 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "governed-model"
    targetKind := "governed-model"
    branchIndex := 48
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_049 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "hypothesis"
    targetKind := "hypothesis"
    branchIndex := 49
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_050 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "identity-claim"
    targetKind := "identity-claim"
    branchIndex := 50
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_051 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "implementation"
    targetKind := "implementation"
    branchIndex := 51
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_052 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "improvement-signal"
    targetKind := "improvement-signal"
    branchIndex := 52
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_053 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "improvement-target"
    targetKind := "improvement-target"
    branchIndex := 53
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_054 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "incident"
    targetKind := "incident"
    branchIndex := 54
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_055 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "intent-resolution"
    targetKind := "intent-resolution"
    branchIndex := 55
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_056 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "lesson-application"
    targetKind := "lesson-application"
    branchIndex := 56
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_057 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "lesson-outcome-assessment"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 57
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_058 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "measurement-method"
    targetKind := "measurement-method"
    branchIndex := 58
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_059 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "measurement-result"
    branchIndex := 59
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_060 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "method"
    targetKind := "method"
    branchIndex := 60
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_061 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "model-instance-binding"
    targetKind := "model-instance-binding"
    branchIndex := 61
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_062 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "observation"
    targetKind := "observation"
    branchIndex := 62
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_063 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "ontology"
    targetKind := "ontology"
    branchIndex := 63
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_064 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "ontology-cut"
    targetKind := "ontology-cut"
    branchIndex := 64
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_065 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "ontology-edge"
    targetKind := "ontology-edge"
    branchIndex := 65
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_066 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "ontology-manifest"
    targetKind := "ontology-manifest"
    branchIndex := 66
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_067 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "ontology-node"
    targetKind := "ontology-node"
    branchIndex := 67
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_068 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "ontology-package"
    targetKind := "ontology-package"
    branchIndex := 68
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_069 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "ontology-view"
    targetKind := "ontology-view"
    branchIndex := 69
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_070 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "operational-lesson"
    targetKind := "operational-lesson"
    branchIndex := 70
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_071 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "operational-observation"
    targetKind := "operational-observation"
    branchIndex := 71
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_072 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "person"
    targetKind := "person"
    branchIndex := 72
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_073 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "person-reference"
    targetKind := "person-reference"
    branchIndex := 73
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_074 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "policy"
    targetKind := "policy"
    branchIndex := 74
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_075 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "preference-application-assessment"
    targetKind := "preference-application-assessment"
    branchIndex := 75
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_076 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "principal"
    targetKind := "principal"
    branchIndex := 76
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_077 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "principal-reference"
    targetKind := "principal-reference"
    branchIndex := 77
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_078 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "product"
    targetKind := "product"
    branchIndex := 78
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_079 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "product-capability"
    targetKind := "product-capability"
    branchIndex := 79
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_080 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "product-thesis"
    targetKind := "product-thesis"
    branchIndex := 80
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_081 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "project"
    targetKind := "project"
    branchIndex := 81
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_082 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "project-state"
    targetKind := "project-state"
    branchIndex := 82
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_083 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "relation-kind"
    targetKind := "relation-kind"
    branchIndex := 83
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_084 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "research-inquiry"
    targetKind := "research-inquiry"
    branchIndex := 84
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_085 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "research-run"
    targetKind := "research-run"
    branchIndex := 85
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_086 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "responsibility"
    targetKind := "responsibility"
    branchIndex := 86
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_087 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "review"
    targetKind := "review"
    branchIndex := 87
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_088 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "role"
    targetKind := "role"
    branchIndex := 88
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_089 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "role-assignment"
    targetKind := "role-assignment"
    branchIndex := 89
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_090 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "schema"
    targetKind := "schema"
    branchIndex := 90
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_091 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "semantic-event-history"
    targetKind := "semantic-event-history"
    branchIndex := 91
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_092 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "source"
    targetKind := "source"
    branchIndex := 92
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_093 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "team"
    targetKind := "team"
    branchIndex := 93
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_094 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "team-membership"
    targetKind := "team-membership"
    branchIndex := 94
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_095 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "tool"
    targetKind := "tool"
    branchIndex := 95
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_096 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "typed-relation"
    targetKind := "typed-relation"
    branchIndex := 96
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_097 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "ubiquitous-language"
    targetKind := "ubiquitous-language"
    branchIndex := 97
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_098 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "work"
    targetKind := "work"
    branchIndex := 98
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_099 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:0"
    sourceKind := "work-outcome-assessment"
    targetKind := "work-outcome-assessment"
    branchIndex := 99
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "agent-assignment"
    targetKind := "agent-assignment"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "agent-capability"
    targetKind := "agent-capability"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "agent-instance"
    targetKind := "agent-instance"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "agent-profile"
    targetKind := "agent-profile"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_005 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "agent-reflection"
    targetKind := "agent-reflection"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_006 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "agent-session"
    targetKind := "agent-session"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_007 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "artifact-type"
    targetKind := "artifact-type"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_008 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "artifact-type-request"
    targetKind := "artifact-type-request"
    branchIndex := 8
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_009 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "authority-claim"
    targetKind := "authority-claim"
    branchIndex := 9
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_010 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "bounded-context"
    targetKind := "bounded-context"
    branchIndex := 10
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_011 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "canonical-package-manifest"
    targetKind := "canonical-package-manifest"
    branchIndex := 11
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_012 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "capability-instance"
    targetKind := "capability-instance"
    branchIndex := 12
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_013 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "capability-realization-binding"
    targetKind := "capability-realization-binding"
    branchIndex := 13
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_014 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "challenge-contract"
    targetKind := "challenge-contract"
    branchIndex := 14
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_015 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "challenge-event"
    branchIndex := 15
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_016 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "classification-assignment"
    targetKind := "classification-assignment"
    branchIndex := 16
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_017 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "classification-scheme"
    targetKind := "classification-scheme"
    branchIndex := 17
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_018 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "classification-value"
    targetKind := "classification-value"
    branchIndex := 18
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_019 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "communication-preference"
    targetKind := "communication-preference"
    branchIndex := 19
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_020 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "constitution"
    targetKind := "constitution"
    branchIndex := 20
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_021 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "context"
    targetKind := "context"
    branchIndex := 21
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_022 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "context-lineage-record"
    targetKind := "context-lineage-record"
    branchIndex := 22
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_023 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "context-map"
    targetKind := "context-map"
    branchIndex := 23
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_024 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "context-migration-manifest"
    targetKind := "context-migration-manifest"
    branchIndex := 24
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_025 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "context-profile"
    targetKind := "context-profile"
    branchIndex := 25
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_026 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "context-request"
    targetKind := "context-request"
    branchIndex := 26
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_027 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "context-view"
    targetKind := "context-view"
    branchIndex := 27
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_028 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "contract"
    targetKind := "contract"
    branchIndex := 28
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_029 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "decision"
    targetKind := "decision"
    branchIndex := 29
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_030 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "decision-scope"
    targetKind := "decision-scope"
    branchIndex := 30
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_031 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "definition"
    targetKind := "definition"
    branchIndex := 31
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_032 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "delegation"
    targetKind := "delegation"
    branchIndex := 32
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_033 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "drift-assessment"
    targetKind := "drift-assessment"
    branchIndex := 33
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_034 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "effect"
    targetKind := "effect"
    branchIndex := 34
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_035 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "evaluation"
    targetKind := "evaluation"
    branchIndex := 35
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_036 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "evidence-set"
    branchIndex := 36
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_037 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "experiment-design"
    targetKind := "experiment-design"
    branchIndex := 37
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_038 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "experiment-run"
    targetKind := "experiment-run"
    branchIndex := 38
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_039 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "failure-assessment"
    targetKind := "failure-assessment"
    branchIndex := 39
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_040 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "failure-control-binding"
    targetKind := "failure-control-binding"
    branchIndex := 40
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_041 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "failure-mode"
    targetKind := "failure-mode"
    branchIndex := 41
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_042 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "failure-occurrence"
    branchIndex := 42
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_043 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "feedback-record"
    targetKind := "feedback-record"
    branchIndex := 43
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_044 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "finding"
    targetKind := "finding"
    branchIndex := 44
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_045 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "generated-output"
    targetKind := "generated-output"
    branchIndex := 45
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_046 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "goal"
    targetKind := "goal"
    branchIndex := 46
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_047 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "governance-event-history"
    targetKind := "governance-event-history"
    branchIndex := 47
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_048 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "governed-model"
    targetKind := "governed-model"
    branchIndex := 48
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_049 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "hypothesis"
    targetKind := "hypothesis"
    branchIndex := 49
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_050 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "identity-claim"
    targetKind := "identity-claim"
    branchIndex := 50
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_051 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "implementation"
    targetKind := "implementation"
    branchIndex := 51
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_052 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "improvement-signal"
    targetKind := "improvement-signal"
    branchIndex := 52
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_053 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "improvement-target"
    targetKind := "improvement-target"
    branchIndex := 53
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_054 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "incident"
    targetKind := "incident"
    branchIndex := 54
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_055 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "intent-resolution"
    targetKind := "intent-resolution"
    branchIndex := 55
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_056 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "lesson-application"
    targetKind := "lesson-application"
    branchIndex := 56
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_057 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "lesson-outcome-assessment"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 57
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_058 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "measurement-method"
    targetKind := "measurement-method"
    branchIndex := 58
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_059 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "measurement-result"
    branchIndex := 59
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_060 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "method"
    targetKind := "method"
    branchIndex := 60
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_061 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "model-instance-binding"
    targetKind := "model-instance-binding"
    branchIndex := 61
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_062 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "observation"
    targetKind := "observation"
    branchIndex := 62
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_063 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "ontology"
    targetKind := "ontology"
    branchIndex := 63
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_064 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "ontology-cut"
    targetKind := "ontology-cut"
    branchIndex := 64
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_065 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "ontology-edge"
    targetKind := "ontology-edge"
    branchIndex := 65
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_066 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "ontology-manifest"
    targetKind := "ontology-manifest"
    branchIndex := 66
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_067 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "ontology-node"
    targetKind := "ontology-node"
    branchIndex := 67
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_068 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "ontology-package"
    targetKind := "ontology-package"
    branchIndex := 68
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_069 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "ontology-view"
    targetKind := "ontology-view"
    branchIndex := 69
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_070 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "operational-lesson"
    targetKind := "operational-lesson"
    branchIndex := 70
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_071 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "operational-observation"
    targetKind := "operational-observation"
    branchIndex := 71
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_072 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "person"
    targetKind := "person"
    branchIndex := 72
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_073 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "person-reference"
    targetKind := "person-reference"
    branchIndex := 73
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_074 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "policy"
    targetKind := "policy"
    branchIndex := 74
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_075 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "preference-application-assessment"
    targetKind := "preference-application-assessment"
    branchIndex := 75
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_076 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "principal"
    targetKind := "principal"
    branchIndex := 76
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_077 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "principal-reference"
    targetKind := "principal-reference"
    branchIndex := 77
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_078 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "product"
    targetKind := "product"
    branchIndex := 78
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_079 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "product-capability"
    targetKind := "product-capability"
    branchIndex := 79
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_080 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "product-thesis"
    targetKind := "product-thesis"
    branchIndex := 80
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_081 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "project"
    targetKind := "project"
    branchIndex := 81
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_082 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "project-state"
    targetKind := "project-state"
    branchIndex := 82
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_083 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "relation-kind"
    targetKind := "relation-kind"
    branchIndex := 83
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_084 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "research-inquiry"
    targetKind := "research-inquiry"
    branchIndex := 84
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_085 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "research-run"
    targetKind := "research-run"
    branchIndex := 85
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_086 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "responsibility"
    targetKind := "responsibility"
    branchIndex := 86
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_087 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "review"
    targetKind := "review"
    branchIndex := 87
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_088 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "role"
    targetKind := "role"
    branchIndex := 88
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_089 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "role-assignment"
    targetKind := "role-assignment"
    branchIndex := 89
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_090 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "schema"
    targetKind := "schema"
    branchIndex := 90
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_091 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "semantic-event-history"
    targetKind := "semantic-event-history"
    branchIndex := 91
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_092 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "source"
    targetKind := "source"
    branchIndex := 92
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_093 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "team"
    targetKind := "team"
    branchIndex := 93
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_094 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "team-membership"
    targetKind := "team-membership"
    branchIndex := 94
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_095 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "tool"
    targetKind := "tool"
    branchIndex := 95
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_096 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "typed-relation"
    targetKind := "typed-relation"
    branchIndex := 96
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_097 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "ubiquitous-language"
    targetKind := "ubiquitous-language"
    branchIndex := 97
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_098 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "work"
    targetKind := "work"
    branchIndex := 98
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_099 : Plan 36 [.ref, .ref, .ref] :=
  { obligationId := "relation.successor-of:forbidden:1"
    sourceKind := "work-outcome-assessment"
    targetKind := "work-outcome-assessment"
    branchIndex := 99
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "agent-assignment"
    targetKind := "agent-assignment"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "agent-capability"
    targetKind := "agent-capability"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "agent-instance"
    targetKind := "agent-instance"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "agent-profile"
    targetKind := "agent-profile"
    branchIndex := 4
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_005 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "agent-reflection"
    targetKind := "agent-reflection"
    branchIndex := 5
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_006 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "agent-session"
    targetKind := "agent-session"
    branchIndex := 6
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_007 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "artifact-type"
    targetKind := "artifact-type"
    branchIndex := 7
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_008 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "artifact-type-request"
    targetKind := "artifact-type-request"
    branchIndex := 8
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_009 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "authority-claim"
    targetKind := "authority-claim"
    branchIndex := 9
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_010 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "bounded-context"
    targetKind := "bounded-context"
    branchIndex := 10
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_011 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "canonical-package-manifest"
    targetKind := "canonical-package-manifest"
    branchIndex := 11
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_012 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "capability-instance"
    targetKind := "capability-instance"
    branchIndex := 12
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_013 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "capability-realization-binding"
    targetKind := "capability-realization-binding"
    branchIndex := 13
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_014 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "challenge-contract"
    targetKind := "challenge-contract"
    branchIndex := 14
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_015 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "challenge-event"
    branchIndex := 15
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_016 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "classification-assignment"
    targetKind := "classification-assignment"
    branchIndex := 16
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_017 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "classification-scheme"
    targetKind := "classification-scheme"
    branchIndex := 17
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_018 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "classification-value"
    targetKind := "classification-value"
    branchIndex := 18
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_019 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "communication-preference"
    targetKind := "communication-preference"
    branchIndex := 19
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_020 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "constitution"
    targetKind := "constitution"
    branchIndex := 20
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_021 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "context"
    targetKind := "context"
    branchIndex := 21
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_022 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "context-lineage-record"
    targetKind := "context-lineage-record"
    branchIndex := 22
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_023 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "context-map"
    targetKind := "context-map"
    branchIndex := 23
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_024 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "context-migration-manifest"
    targetKind := "context-migration-manifest"
    branchIndex := 24
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_025 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "context-profile"
    targetKind := "context-profile"
    branchIndex := 25
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_026 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "context-request"
    targetKind := "context-request"
    branchIndex := 26
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_027 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "context-view"
    targetKind := "context-view"
    branchIndex := 27
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_028 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "contract"
    targetKind := "contract"
    branchIndex := 28
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_029 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "decision"
    targetKind := "decision"
    branchIndex := 29
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_030 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "decision-scope"
    targetKind := "decision-scope"
    branchIndex := 30
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_031 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "definition"
    targetKind := "definition"
    branchIndex := 31
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_032 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "delegation"
    targetKind := "delegation"
    branchIndex := 32
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_033 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "drift-assessment"
    targetKind := "drift-assessment"
    branchIndex := 33
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_034 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "effect"
    targetKind := "effect"
    branchIndex := 34
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_035 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "evaluation"
    targetKind := "evaluation"
    branchIndex := 35
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_036 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "evidence-set"
    branchIndex := 36
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_037 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "experiment-design"
    targetKind := "experiment-design"
    branchIndex := 37
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_038 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "experiment-run"
    targetKind := "experiment-run"
    branchIndex := 38
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_039 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "failure-assessment"
    targetKind := "failure-assessment"
    branchIndex := 39
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_040 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "failure-control-binding"
    targetKind := "failure-control-binding"
    branchIndex := 40
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_041 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "failure-mode"
    targetKind := "failure-mode"
    branchIndex := 41
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_042 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "failure-occurrence"
    branchIndex := 42
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_043 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "feedback-record"
    targetKind := "feedback-record"
    branchIndex := 43
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_044 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "finding"
    targetKind := "finding"
    branchIndex := 44
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_045 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "generated-output"
    targetKind := "generated-output"
    branchIndex := 45
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_046 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "goal"
    targetKind := "goal"
    branchIndex := 46
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_047 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "governance-event-history"
    targetKind := "governance-event-history"
    branchIndex := 47
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_048 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "governed-model"
    targetKind := "governed-model"
    branchIndex := 48
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_049 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "hypothesis"
    targetKind := "hypothesis"
    branchIndex := 49
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_050 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "identity-claim"
    targetKind := "identity-claim"
    branchIndex := 50
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_051 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "implementation"
    targetKind := "implementation"
    branchIndex := 51
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_052 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "improvement-signal"
    targetKind := "improvement-signal"
    branchIndex := 52
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_053 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "improvement-target"
    targetKind := "improvement-target"
    branchIndex := 53
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_054 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "incident"
    targetKind := "incident"
    branchIndex := 54
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_055 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "intent-resolution"
    targetKind := "intent-resolution"
    branchIndex := 55
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_056 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "lesson-application"
    targetKind := "lesson-application"
    branchIndex := 56
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_057 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "lesson-outcome-assessment"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 57
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_058 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "measurement-method"
    targetKind := "measurement-method"
    branchIndex := 58
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_059 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "measurement-result"
    branchIndex := 59
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_060 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "method"
    targetKind := "method"
    branchIndex := 60
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_061 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "model-instance-binding"
    targetKind := "model-instance-binding"
    branchIndex := 61
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_062 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "observation"
    targetKind := "observation"
    branchIndex := 62
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_063 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "ontology"
    targetKind := "ontology"
    branchIndex := 63
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_064 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "ontology-cut"
    targetKind := "ontology-cut"
    branchIndex := 64
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_065 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "ontology-edge"
    targetKind := "ontology-edge"
    branchIndex := 65
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_066 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "ontology-manifest"
    targetKind := "ontology-manifest"
    branchIndex := 66
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_067 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "ontology-node"
    targetKind := "ontology-node"
    branchIndex := 67
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_068 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "ontology-package"
    targetKind := "ontology-package"
    branchIndex := 68
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_069 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "ontology-view"
    targetKind := "ontology-view"
    branchIndex := 69
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_070 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "operational-lesson"
    targetKind := "operational-lesson"
    branchIndex := 70
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_071 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "operational-observation"
    targetKind := "operational-observation"
    branchIndex := 71
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_072 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "person"
    targetKind := "person"
    branchIndex := 72
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_073 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "person-reference"
    targetKind := "person-reference"
    branchIndex := 73
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_074 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "policy"
    targetKind := "policy"
    branchIndex := 74
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_075 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "preference-application-assessment"
    targetKind := "preference-application-assessment"
    branchIndex := 75
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_076 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "principal"
    targetKind := "principal"
    branchIndex := 76
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_077 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "principal-reference"
    targetKind := "principal-reference"
    branchIndex := 77
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_078 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "product"
    targetKind := "product"
    branchIndex := 78
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_079 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "product-capability"
    targetKind := "product-capability"
    branchIndex := 79
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_080 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "product-thesis"
    targetKind := "product-thesis"
    branchIndex := 80
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_081 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "project"
    targetKind := "project"
    branchIndex := 81
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_082 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "project-state"
    targetKind := "project-state"
    branchIndex := 82
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_083 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "relation-kind"
    targetKind := "relation-kind"
    branchIndex := 83
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_084 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "research-inquiry"
    targetKind := "research-inquiry"
    branchIndex := 84
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_085 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "research-run"
    targetKind := "research-run"
    branchIndex := 85
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_086 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "responsibility"
    targetKind := "responsibility"
    branchIndex := 86
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_087 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "review"
    targetKind := "review"
    branchIndex := 87
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_088 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "role"
    targetKind := "role"
    branchIndex := 88
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_089 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "role-assignment"
    targetKind := "role-assignment"
    branchIndex := 89
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_090 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "schema"
    targetKind := "schema"
    branchIndex := 90
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_091 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "semantic-event-history"
    targetKind := "semantic-event-history"
    branchIndex := 91
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_092 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "source"
    targetKind := "source"
    branchIndex := 92
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_093 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "team"
    targetKind := "team"
    branchIndex := 93
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_094 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "team-membership"
    targetKind := "team-membership"
    branchIndex := 94
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_095 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "tool"
    targetKind := "tool"
    branchIndex := 95
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_096 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "typed-relation"
    targetKind := "typed-relation"
    branchIndex := 96
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_097 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "ubiquitous-language"
    targetKind := "ubiquitous-language"
    branchIndex := 97
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_098 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "work"
    targetKind := "work"
    branchIndex := 98
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_099 : Plan 36 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.successor-of:forbidden:2"
    sourceKind := "work-outcome-assessment"
    targetKind := "work-outcome-assessment"
    branchIndex := 99
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_0_001
#print axioms plan_0_002
#print axioms plan_0_003
#print axioms plan_0_004
#print axioms plan_0_005
#print axioms plan_0_006
#print axioms plan_0_007
#print axioms plan_0_008
#print axioms plan_0_009
#print axioms plan_0_010
#print axioms plan_0_011
#print axioms plan_0_012
#print axioms plan_0_013
#print axioms plan_0_014
#print axioms plan_0_015
#print axioms plan_0_016
#print axioms plan_0_017
#print axioms plan_0_018
#print axioms plan_0_019
#print axioms plan_0_020
#print axioms plan_0_021
#print axioms plan_0_022
#print axioms plan_0_023
#print axioms plan_0_024
#print axioms plan_0_025
#print axioms plan_0_026
#print axioms plan_0_027
#print axioms plan_0_028
#print axioms plan_0_029
#print axioms plan_0_030
#print axioms plan_0_031
#print axioms plan_0_032
#print axioms plan_0_033
#print axioms plan_0_034
#print axioms plan_0_035
#print axioms plan_0_036
#print axioms plan_0_037
#print axioms plan_0_038
#print axioms plan_0_039
#print axioms plan_0_040
#print axioms plan_0_041
#print axioms plan_0_042
#print axioms plan_0_043
#print axioms plan_0_044
#print axioms plan_0_045
#print axioms plan_0_046
#print axioms plan_0_047
#print axioms plan_0_048
#print axioms plan_0_049
#print axioms plan_0_050
#print axioms plan_0_051
#print axioms plan_0_052
#print axioms plan_0_053
#print axioms plan_0_054
#print axioms plan_0_055
#print axioms plan_0_056
#print axioms plan_0_057
#print axioms plan_0_058
#print axioms plan_0_059
#print axioms plan_0_060
#print axioms plan_0_061
#print axioms plan_0_062
#print axioms plan_0_063
#print axioms plan_0_064
#print axioms plan_0_065
#print axioms plan_0_066
#print axioms plan_0_067
#print axioms plan_0_068
#print axioms plan_0_069
#print axioms plan_0_070
#print axioms plan_0_071
#print axioms plan_0_072
#print axioms plan_0_073
#print axioms plan_0_074
#print axioms plan_0_075
#print axioms plan_0_076
#print axioms plan_0_077
#print axioms plan_0_078
#print axioms plan_0_079
#print axioms plan_0_080
#print axioms plan_0_081
#print axioms plan_0_082
#print axioms plan_0_083
#print axioms plan_0_084
#print axioms plan_0_085
#print axioms plan_0_086
#print axioms plan_0_087
#print axioms plan_0_088
#print axioms plan_0_089
#print axioms plan_0_090
#print axioms plan_0_091
#print axioms plan_0_092
#print axioms plan_0_093
#print axioms plan_0_094
#print axioms plan_0_095
#print axioms plan_0_096
#print axioms plan_0_097
#print axioms plan_0_098
#print axioms plan_0_099
#print axioms plan_1_000
#print axioms plan_1_001
#print axioms plan_1_002
#print axioms plan_1_003
#print axioms plan_1_004
#print axioms plan_1_005
#print axioms plan_1_006
#print axioms plan_1_007
#print axioms plan_1_008
#print axioms plan_1_009
#print axioms plan_1_010
#print axioms plan_1_011
#print axioms plan_1_012
#print axioms plan_1_013
#print axioms plan_1_014
#print axioms plan_1_015
#print axioms plan_1_016
#print axioms plan_1_017
#print axioms plan_1_018
#print axioms plan_1_019
#print axioms plan_1_020
#print axioms plan_1_021
#print axioms plan_1_022
#print axioms plan_1_023
#print axioms plan_1_024
#print axioms plan_1_025
#print axioms plan_1_026
#print axioms plan_1_027
#print axioms plan_1_028
#print axioms plan_1_029
#print axioms plan_1_030
#print axioms plan_1_031
#print axioms plan_1_032
#print axioms plan_1_033
#print axioms plan_1_034
#print axioms plan_1_035
#print axioms plan_1_036
#print axioms plan_1_037
#print axioms plan_1_038
#print axioms plan_1_039
#print axioms plan_1_040
#print axioms plan_1_041
#print axioms plan_1_042
#print axioms plan_1_043
#print axioms plan_1_044
#print axioms plan_1_045
#print axioms plan_1_046
#print axioms plan_1_047
#print axioms plan_1_048
#print axioms plan_1_049
#print axioms plan_1_050
#print axioms plan_1_051
#print axioms plan_1_052
#print axioms plan_1_053
#print axioms plan_1_054
#print axioms plan_1_055
#print axioms plan_1_056
#print axioms plan_1_057
#print axioms plan_1_058
#print axioms plan_1_059
#print axioms plan_1_060
#print axioms plan_1_061
#print axioms plan_1_062
#print axioms plan_1_063
#print axioms plan_1_064
#print axioms plan_1_065
#print axioms plan_1_066
#print axioms plan_1_067
#print axioms plan_1_068
#print axioms plan_1_069
#print axioms plan_1_070
#print axioms plan_1_071
#print axioms plan_1_072
#print axioms plan_1_073
#print axioms plan_1_074
#print axioms plan_1_075
#print axioms plan_1_076
#print axioms plan_1_077
#print axioms plan_1_078
#print axioms plan_1_079
#print axioms plan_1_080
#print axioms plan_1_081
#print axioms plan_1_082
#print axioms plan_1_083
#print axioms plan_1_084
#print axioms plan_1_085
#print axioms plan_1_086
#print axioms plan_1_087
#print axioms plan_1_088
#print axioms plan_1_089
#print axioms plan_1_090
#print axioms plan_1_091
#print axioms plan_1_092
#print axioms plan_1_093
#print axioms plan_1_094
#print axioms plan_1_095
#print axioms plan_1_096
#print axioms plan_1_097
#print axioms plan_1_098
#print axioms plan_1_099
#print axioms plan_2_000
#print axioms plan_2_001
#print axioms plan_2_002
#print axioms plan_2_003
#print axioms plan_2_004
#print axioms plan_2_005
#print axioms plan_2_006
#print axioms plan_2_007
#print axioms plan_2_008
#print axioms plan_2_009
#print axioms plan_2_010
#print axioms plan_2_011
#print axioms plan_2_012
#print axioms plan_2_013
#print axioms plan_2_014
#print axioms plan_2_015
#print axioms plan_2_016
#print axioms plan_2_017
#print axioms plan_2_018
#print axioms plan_2_019
#print axioms plan_2_020
#print axioms plan_2_021
#print axioms plan_2_022
#print axioms plan_2_023
#print axioms plan_2_024
#print axioms plan_2_025
#print axioms plan_2_026
#print axioms plan_2_027
#print axioms plan_2_028
#print axioms plan_2_029
#print axioms plan_2_030
#print axioms plan_2_031
#print axioms plan_2_032
#print axioms plan_2_033
#print axioms plan_2_034
#print axioms plan_2_035
#print axioms plan_2_036
#print axioms plan_2_037
#print axioms plan_2_038
#print axioms plan_2_039
#print axioms plan_2_040
#print axioms plan_2_041
#print axioms plan_2_042
#print axioms plan_2_043
#print axioms plan_2_044
#print axioms plan_2_045
#print axioms plan_2_046
#print axioms plan_2_047
#print axioms plan_2_048
#print axioms plan_2_049
#print axioms plan_2_050
#print axioms plan_2_051
#print axioms plan_2_052
#print axioms plan_2_053
#print axioms plan_2_054
#print axioms plan_2_055
#print axioms plan_2_056
#print axioms plan_2_057
#print axioms plan_2_058
#print axioms plan_2_059
#print axioms plan_2_060
#print axioms plan_2_061
#print axioms plan_2_062
#print axioms plan_2_063
#print axioms plan_2_064
#print axioms plan_2_065
#print axioms plan_2_066
#print axioms plan_2_067
#print axioms plan_2_068
#print axioms plan_2_069
#print axioms plan_2_070
#print axioms plan_2_071
#print axioms plan_2_072
#print axioms plan_2_073
#print axioms plan_2_074
#print axioms plan_2_075
#print axioms plan_2_076
#print axioms plan_2_077
#print axioms plan_2_078
#print axioms plan_2_079
#print axioms plan_2_080
#print axioms plan_2_081
#print axioms plan_2_082
#print axioms plan_2_083
#print axioms plan_2_084
#print axioms plan_2_085
#print axioms plan_2_086
#print axioms plan_2_087
#print axioms plan_2_088
#print axioms plan_2_089
#print axioms plan_2_090
#print axioms plan_2_091
#print axioms plan_2_092
#print axioms plan_2_093
#print axioms plan_2_094
#print axioms plan_2_095
#print axioms plan_2_096
#print axioms plan_2_097
#print axioms plan_2_098
#print axioms plan_2_099
end CandidateConclusionAnchors.K36
