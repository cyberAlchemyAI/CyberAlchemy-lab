import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K21

def plan_0_000 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "admission-transaction"
    targetKind := "policy"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "policy"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "agent-instance"
    targetKind := "policy"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "agent-profile"
    targetKind := "policy"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "agent-session"
    targetKind := "policy"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_005 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "artifact-type"
    targetKind := "constitution"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_006 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "authority-boundary"
    targetKind := "policy"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_007 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "challenge-contract"
    targetKind := "policy"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_008 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "challenge-contract"
    branchIndex := 8
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_009 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "classification-assignment"
    targetKind := "classification-scheme"
    branchIndex := 9
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_010 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "classification-assignment"
    targetKind := "policy"
    branchIndex := 10
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_011 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "communication-preference"
    targetKind := "policy"
    branchIndex := 11
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_012 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "context"
    targetKind := "policy"
    branchIndex := 12
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_013 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "decision-bundle"
    targetKind := "policy"
    branchIndex := 13
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_014 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "decision-checkpoint"
    targetKind := "policy"
    branchIndex := 14
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_015 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "definition"
    targetKind := "constitution"
    branchIndex := 15
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_016 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "failure-assessment"
    targetKind := "policy"
    branchIndex := 16
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_017 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "failure-control-binding"
    targetKind := "policy"
    branchIndex := 17
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_018 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "failure-mode"
    targetKind := "policy"
    branchIndex := 18
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_019 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "policy"
    branchIndex := 19
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_020 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "feedback-record"
    targetKind := "policy"
    branchIndex := 20
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_021 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "incident"
    targetKind := "policy"
    branchIndex := 21
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_022 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "ontology"
    targetKind := "policy"
    branchIndex := 22
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_023 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "ontology-edge"
    targetKind := "policy"
    branchIndex := 23
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_024 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "ontology-node"
    targetKind := "policy"
    branchIndex := 24
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_025 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "operational-lesson"
    targetKind := "policy"
    branchIndex := 25
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_026 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "relation-kind"
    targetKind := "constitution"
    branchIndex := 26
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_027 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "user-decision-preference"
    targetKind := "policy"
    branchIndex := 27
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_028 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:0"
    sourceKind := "workflow-decision-profile"
    targetKind := "policy"
    branchIndex := 28
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "admission-transaction"
    targetKind := "policy"
    branchIndex := 0
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "policy"
    branchIndex := 1
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "agent-instance"
    targetKind := "policy"
    branchIndex := 2
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "agent-profile"
    targetKind := "policy"
    branchIndex := 3
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "agent-session"
    targetKind := "policy"
    branchIndex := 4
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_005 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "artifact-type"
    targetKind := "constitution"
    branchIndex := 5
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_006 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "authority-boundary"
    targetKind := "policy"
    branchIndex := 6
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_007 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "challenge-contract"
    targetKind := "policy"
    branchIndex := 7
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_008 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "challenge-contract"
    branchIndex := 8
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_009 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "classification-assignment"
    targetKind := "classification-scheme"
    branchIndex := 9
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_010 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "classification-assignment"
    targetKind := "policy"
    branchIndex := 10
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_011 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "communication-preference"
    targetKind := "policy"
    branchIndex := 11
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_012 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "context"
    targetKind := "policy"
    branchIndex := 12
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_013 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "decision-bundle"
    targetKind := "policy"
    branchIndex := 13
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_014 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "decision-checkpoint"
    targetKind := "policy"
    branchIndex := 14
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_015 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "definition"
    targetKind := "constitution"
    branchIndex := 15
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_016 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "failure-assessment"
    targetKind := "policy"
    branchIndex := 16
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_017 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "failure-control-binding"
    targetKind := "policy"
    branchIndex := 17
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_018 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "failure-mode"
    targetKind := "policy"
    branchIndex := 18
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_019 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "policy"
    branchIndex := 19
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_020 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "feedback-record"
    targetKind := "policy"
    branchIndex := 20
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_021 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "incident"
    targetKind := "policy"
    branchIndex := 21
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_022 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "ontology"
    targetKind := "policy"
    branchIndex := 22
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_023 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "ontology-edge"
    targetKind := "policy"
    branchIndex := 23
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_024 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "ontology-node"
    targetKind := "policy"
    branchIndex := 24
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_025 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "operational-lesson"
    targetKind := "policy"
    branchIndex := 25
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_026 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "relation-kind"
    targetKind := "constitution"
    branchIndex := 26
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_027 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "user-decision-preference"
    targetKind := "policy"
    branchIndex := 27
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_028 : Plan 21 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.governed-by:forbidden:1"
    sourceKind := "workflow-decision-profile"
    targetKind := "policy"
    branchIndex := 28
    arguments := .cons (.variable "holder") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "admission-transaction"
    targetKind := "policy"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "policy"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "agent-instance"
    targetKind := "policy"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "agent-profile"
    targetKind := "policy"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "agent-session"
    targetKind := "policy"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_005 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "artifact-type"
    targetKind := "constitution"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_006 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "authority-boundary"
    targetKind := "policy"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_007 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "challenge-contract"
    targetKind := "policy"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_008 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "challenge-contract"
    branchIndex := 8
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_009 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "classification-assignment"
    targetKind := "classification-scheme"
    branchIndex := 9
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_010 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "classification-assignment"
    targetKind := "policy"
    branchIndex := 10
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_011 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "communication-preference"
    targetKind := "policy"
    branchIndex := 11
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_012 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "context"
    targetKind := "policy"
    branchIndex := 12
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_013 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "decision-bundle"
    targetKind := "policy"
    branchIndex := 13
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_014 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "decision-checkpoint"
    targetKind := "policy"
    branchIndex := 14
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_015 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "definition"
    targetKind := "constitution"
    branchIndex := 15
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_016 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "failure-assessment"
    targetKind := "policy"
    branchIndex := 16
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_017 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "failure-control-binding"
    targetKind := "policy"
    branchIndex := 17
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_018 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "failure-mode"
    targetKind := "policy"
    branchIndex := 18
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_019 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "policy"
    branchIndex := 19
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_020 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "feedback-record"
    targetKind := "policy"
    branchIndex := 20
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_021 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "incident"
    targetKind := "policy"
    branchIndex := 21
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_022 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "ontology"
    targetKind := "policy"
    branchIndex := 22
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_023 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "ontology-edge"
    targetKind := "policy"
    branchIndex := 23
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_024 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "ontology-node"
    targetKind := "policy"
    branchIndex := 24
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_025 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "operational-lesson"
    targetKind := "policy"
    branchIndex := 25
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_026 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "relation-kind"
    targetKind := "constitution"
    branchIndex := 26
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_027 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "user-decision-preference"
    targetKind := "policy"
    branchIndex := 27
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_028 : Plan 21 [.ref, .ref, .ref] :=
  { obligationId := "relation.governed-by:forbidden:2"
    sourceKind := "workflow-decision-profile"
    targetKind := "policy"
    branchIndex := 28
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
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
end CandidateConclusionAnchors.K21
