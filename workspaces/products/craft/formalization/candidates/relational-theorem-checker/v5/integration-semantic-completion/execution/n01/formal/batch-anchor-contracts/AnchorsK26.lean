import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K26

def plan_0_000 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "agent-session"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "agent-assignment"
    targetKind := "project"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "agent-instance"
    targetKind := "agent-session"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "capability-realization-binding"
    targetKind := "project"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "classification-value"
    targetKind := "classification-scheme"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_005 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "context"
    targetKind := "product"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_006 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "context"
    targetKind := "project"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_007 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "decision"
    targetKind := "decision-bundle"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_008 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "project"
    branchIndex := 8
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_009 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "experiment-design"
    targetKind := "project"
    branchIndex := 9
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_010 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "experiment-run"
    targetKind := "project"
    branchIndex := 10
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_011 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "incident"
    branchIndex := 11
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_012 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "goal"
    targetKind := "project"
    branchIndex := 12
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_013 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "ontology-node"
    targetKind := "ontology"
    branchIndex := 13
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_014 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "person-reference"
    targetKind := "team"
    branchIndex := 14
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_015 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "product"
    targetKind := "product"
    branchIndex := 15
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_016 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "product-capability"
    targetKind := "product"
    branchIndex := 16
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_017 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "product-thesis"
    targetKind := "product"
    branchIndex := 17
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_018 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "project-state"
    targetKind := "project"
    branchIndex := 18
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_019 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "research-inquiry"
    targetKind := "project"
    branchIndex := 19
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_020 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "research-run"
    targetKind := "project"
    branchIndex := 20
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_021 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "responsibility"
    targetKind := "role"
    branchIndex := 21
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_022 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "typed-relation"
    targetKind := "ontology"
    branchIndex := 22
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_023 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:0"
    sourceKind := "work"
    targetKind := "project"
    branchIndex := 23
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "scope" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "contribution-targets", selectionRole := "Exact Product or Goal independently associated with this membership record", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "agent-session"
    branchIndex := 0
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "agent-assignment"
    targetKind := "project"
    branchIndex := 1
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "agent-instance"
    targetKind := "agent-session"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .source⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "capability-realization-binding"
    targetKind := "project"
    branchIndex := 3
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "classification-value"
    targetKind := "classification-scheme"
    branchIndex := 4
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_005 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "context"
    targetKind := "product"
    branchIndex := 5
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_006 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "context"
    targetKind := "project"
    branchIndex := 6
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_007 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "decision"
    targetKind := "decision-bundle"
    branchIndex := 7
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_008 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "project"
    branchIndex := 8
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_009 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "experiment-design"
    targetKind := "project"
    branchIndex := 9
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_010 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "experiment-run"
    targetKind := "project"
    branchIndex := 10
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_011 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "incident"
    branchIndex := 11
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_012 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "goal"
    targetKind := "project"
    branchIndex := 12
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_013 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "ontology-node"
    targetKind := "ontology"
    branchIndex := 13
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_014 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "person-reference"
    targetKind := "team"
    branchIndex := 14
    arguments := .cons (.source) (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .source⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_015 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "product"
    targetKind := "product"
    branchIndex := 15
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_016 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "product-capability"
    targetKind := "product"
    branchIndex := 16
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_017 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "product-thesis"
    targetKind := "product"
    branchIndex := 17
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_018 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "project-state"
    targetKind := "project"
    branchIndex := 18
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_019 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "research-inquiry"
    targetKind := "project"
    branchIndex := 19
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_020 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "research-run"
    targetKind := "project"
    branchIndex := 20
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_021 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "responsibility"
    targetKind := "role"
    branchIndex := 21
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "role-responsibilities", selectionRole := "Exact Responsibility within this Role; a Role is not substituted for a Responsibility", joins := [("role", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_022 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "typed-relation"
    targetKind := "ontology"
    branchIndex := 22
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_023 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:1"
    sourceKind := "work"
    targetKind := "project"
    branchIndex := 23
    arguments := .cons (.variable "assignee") (.cons (.variable "responsibility") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "responsibility", sort := .ref, domain := "assignment-targets", selectionRole := "Exact Responsibility independently associated with this member/container", joins := [("assignee", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assignee", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently identified assignee associated with this member; an action/work/artifact is not relabeled as an assignable actor", joins := [("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .variable "assignee"⟩), ("responsibility", ⟨.ref, .variable "responsibility"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "agent-session"
    branchIndex := 0
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "agent-assignment"
    targetKind := "project"
    branchIndex := 1
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "agent-instance"
    targetKind := "agent-session"
    branchIndex := 2
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "capability-realization-binding"
    targetKind := "project"
    branchIndex := 3
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "classification-value"
    targetKind := "classification-scheme"
    branchIndex := 4
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_005 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "context"
    targetKind := "product"
    branchIndex := 5
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_006 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "context"
    targetKind := "project"
    branchIndex := 6
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_007 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "decision"
    targetKind := "decision-bundle"
    branchIndex := 7
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_008 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "project"
    branchIndex := 8
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_009 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "experiment-design"
    targetKind := "project"
    branchIndex := 9
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_010 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "experiment-run"
    targetKind := "project"
    branchIndex := 10
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_011 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "incident"
    branchIndex := 11
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_012 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "goal"
    targetKind := "project"
    branchIndex := 12
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_013 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "ontology-node"
    targetKind := "ontology"
    branchIndex := 13
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_014 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "person-reference"
    targetKind := "team"
    branchIndex := 14
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_015 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "product"
    targetKind := "product"
    branchIndex := 15
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_016 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "product-capability"
    targetKind := "product"
    branchIndex := 16
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_017 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "product-thesis"
    targetKind := "product"
    branchIndex := 17
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_018 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "project-state"
    targetKind := "project"
    branchIndex := 18
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_019 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "research-inquiry"
    targetKind := "project"
    branchIndex := 19
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_020 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "research-run"
    targetKind := "project"
    branchIndex := 20
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_021 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "responsibility"
    targetKind := "role"
    branchIndex := 21
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_022 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "typed-relation"
    targetKind := "ontology"
    branchIndex := 22
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_023 : Plan 26 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.member-of:forbidden:2"
    sourceKind := "work"
    targetKind := "project"
    branchIndex := 23
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "agent-session"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "agent-assignment"
    targetKind := "project"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_002 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "agent-instance"
    targetKind := "agent-session"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_003 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "capability-realization-binding"
    targetKind := "project"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_004 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "classification-value"
    targetKind := "classification-scheme"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_005 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "context"
    targetKind := "product"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_006 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "context"
    targetKind := "project"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_007 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "decision"
    targetKind := "decision-bundle"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_008 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "evidence-set"
    targetKind := "project"
    branchIndex := 8
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_009 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "experiment-design"
    targetKind := "project"
    branchIndex := 9
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_010 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "experiment-run"
    targetKind := "project"
    branchIndex := 10
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_011 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "incident"
    branchIndex := 11
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_012 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "goal"
    targetKind := "project"
    branchIndex := 12
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_013 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "ontology-node"
    targetKind := "ontology"
    branchIndex := 13
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_014 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "person-reference"
    targetKind := "team"
    branchIndex := 14
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_015 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "product"
    targetKind := "product"
    branchIndex := 15
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_016 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "product-capability"
    targetKind := "product"
    branchIndex := 16
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_017 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "product-thesis"
    targetKind := "product"
    branchIndex := 17
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_018 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "project-state"
    targetKind := "project"
    branchIndex := 18
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_019 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "research-inquiry"
    targetKind := "project"
    branchIndex := 19
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_020 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "research-run"
    targetKind := "project"
    branchIndex := 20
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_021 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "responsibility"
    targetKind := "role"
    branchIndex := 21
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_022 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "typed-relation"
    targetKind := "ontology"
    branchIndex := 22
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_023 : Plan 26 [.ref, .ref, .ref] :=
  { obligationId := "relation.member-of:forbidden:3"
    sourceKind := "work"
    targetKind := "project"
    branchIndex := 23
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
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
#print axioms plan_3_000
#print axioms plan_3_001
#print axioms plan_3_002
#print axioms plan_3_003
#print axioms plan_3_004
#print axioms plan_3_005
#print axioms plan_3_006
#print axioms plan_3_007
#print axioms plan_3_008
#print axioms plan_3_009
#print axioms plan_3_010
#print axioms plan_3_011
#print axioms plan_3_012
#print axioms plan_3_013
#print axioms plan_3_014
#print axioms plan_3_015
#print axioms plan_3_016
#print axioms plan_3_017
#print axioms plan_3_018
#print axioms plan_3_019
#print axioms plan_3_020
#print axioms plan_3_021
#print axioms plan_3_022
#print axioms plan_3_023
end CandidateConclusionAnchors.K26
