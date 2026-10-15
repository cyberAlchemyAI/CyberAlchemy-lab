import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K18

def plan_0_000 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "authority-claim"
    branchIndex := 0
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "challenge-event"
    branchIndex := 1
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "classification-assignment"
    branchIndex := 2
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "drift-assessment"
    branchIndex := 3
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "failure-assessment"
    branchIndex := 4
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_005 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "failure-occurrence"
    branchIndex := 5
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_006 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "finding"
    branchIndex := 6
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_007 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "hypothesis"
    branchIndex := 7
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_008 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "identity-claim"
    branchIndex := 8
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_009 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "improvement-signal"
    branchIndex := 9
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_010 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 10
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_011 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "operational-lesson"
    branchIndex := 11
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_012 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "preference-application-assessment"
    branchIndex := 12
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_013 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "work-outcome-assessment"
    branchIndex := 13
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_014 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "feedback-record"
    targetKind := "challenge-event"
    branchIndex := 14
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_015 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "feedback-record"
    targetKind := "classification-assignment"
    branchIndex := 15
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_016 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "feedback-record"
    targetKind := "drift-assessment"
    branchIndex := 16
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_017 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "feedback-record"
    targetKind := "failure-assessment"
    branchIndex := 17
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_018 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "feedback-record"
    targetKind := "failure-occurrence"
    branchIndex := 18
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_019 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "feedback-record"
    targetKind := "improvement-signal"
    branchIndex := 19
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_020 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "feedback-record"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 20
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_021 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "feedback-record"
    targetKind := "operational-lesson"
    branchIndex := 21
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_022 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "feedback-record"
    targetKind := "preference-application-assessment"
    branchIndex := 22
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_023 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "feedback-record"
    targetKind := "work-outcome-assessment"
    branchIndex := 23
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_024 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "finding"
    targetKind := "challenge-event"
    branchIndex := 24
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_025 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "finding"
    targetKind := "classification-assignment"
    branchIndex := 25
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_026 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "finding"
    targetKind := "drift-assessment"
    branchIndex := 26
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_027 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "finding"
    targetKind := "failure-assessment"
    branchIndex := 27
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_028 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "finding"
    targetKind := "failure-occurrence"
    branchIndex := 28
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_029 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "finding"
    targetKind := "improvement-signal"
    branchIndex := 29
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_030 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "finding"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 30
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_031 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "finding"
    targetKind := "operational-lesson"
    branchIndex := 31
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_032 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "finding"
    targetKind := "preference-application-assessment"
    branchIndex := 32
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_033 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "finding"
    targetKind := "work-outcome-assessment"
    branchIndex := 33
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_034 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "authority-claim"
    branchIndex := 34
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_035 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "challenge-event"
    branchIndex := 35
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_036 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "classification-assignment"
    branchIndex := 36
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_037 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "drift-assessment"
    branchIndex := 37
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_038 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "failure-assessment"
    branchIndex := 38
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_039 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "failure-occurrence"
    branchIndex := 39
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_040 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "finding"
    branchIndex := 40
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_041 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "hypothesis"
    branchIndex := 41
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_042 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "identity-claim"
    branchIndex := 42
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_043 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "improvement-signal"
    branchIndex := 43
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_044 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 44
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_045 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "operational-lesson"
    branchIndex := 45
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_046 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "preference-application-assessment"
    branchIndex := 46
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_047 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "work-outcome-assessment"
    branchIndex := 47
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_048 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "observation"
    targetKind := "authority-claim"
    branchIndex := 48
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_049 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "observation"
    targetKind := "challenge-event"
    branchIndex := 49
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_050 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "observation"
    targetKind := "classification-assignment"
    branchIndex := 50
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_051 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "observation"
    targetKind := "drift-assessment"
    branchIndex := 51
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_052 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "observation"
    targetKind := "failure-assessment"
    branchIndex := 52
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_053 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "observation"
    targetKind := "failure-occurrence"
    branchIndex := 53
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_054 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "observation"
    targetKind := "finding"
    branchIndex := 54
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_055 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "observation"
    targetKind := "hypothesis"
    branchIndex := 55
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_056 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "observation"
    targetKind := "identity-claim"
    branchIndex := 56
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_057 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "observation"
    targetKind := "improvement-signal"
    branchIndex := 57
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_058 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "observation"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 58
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_059 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "observation"
    targetKind := "operational-lesson"
    branchIndex := 59
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_060 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "observation"
    targetKind := "preference-application-assessment"
    branchIndex := 60
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_061 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "observation"
    targetKind := "work-outcome-assessment"
    branchIndex := 61
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_062 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "operational-observation"
    targetKind := "challenge-event"
    branchIndex := 62
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_063 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "operational-observation"
    targetKind := "classification-assignment"
    branchIndex := 63
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_064 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "operational-observation"
    targetKind := "drift-assessment"
    branchIndex := 64
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_065 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "operational-observation"
    targetKind := "failure-assessment"
    branchIndex := 65
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_066 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "operational-observation"
    targetKind := "failure-occurrence"
    branchIndex := 66
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_067 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "operational-observation"
    targetKind := "improvement-signal"
    branchIndex := 67
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_068 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "operational-observation"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 68
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_069 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "operational-observation"
    targetKind := "operational-lesson"
    branchIndex := 69
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_070 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "operational-observation"
    targetKind := "preference-application-assessment"
    branchIndex := 70
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_071 : Plan 18 [.ref, .ref, .frame] :=
  { obligationId := "relation.evidence-bears-on:forbidden:0"
    sourceKind := "operational-observation"
    targetKind := "work-outcome-assessment"
    branchIndex := 71
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "decision") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "authority-claim"
    branchIndex := 0
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "challenge-event"
    branchIndex := 1
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "classification-assignment"
    branchIndex := 2
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "drift-assessment"
    branchIndex := 3
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "failure-assessment"
    branchIndex := 4
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_005 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "failure-occurrence"
    branchIndex := 5
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_006 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "finding"
    branchIndex := 6
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_007 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "hypothesis"
    branchIndex := 7
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_008 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "identity-claim"
    branchIndex := 8
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_009 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "improvement-signal"
    branchIndex := 9
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_010 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 10
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_011 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "operational-lesson"
    branchIndex := 11
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_012 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "preference-application-assessment"
    branchIndex := 12
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_013 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "work-outcome-assessment"
    branchIndex := 13
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_014 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "feedback-record"
    targetKind := "challenge-event"
    branchIndex := 14
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_015 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "feedback-record"
    targetKind := "classification-assignment"
    branchIndex := 15
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_016 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "feedback-record"
    targetKind := "drift-assessment"
    branchIndex := 16
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_017 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "feedback-record"
    targetKind := "failure-assessment"
    branchIndex := 17
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_018 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "feedback-record"
    targetKind := "failure-occurrence"
    branchIndex := 18
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_019 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "feedback-record"
    targetKind := "improvement-signal"
    branchIndex := 19
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_020 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "feedback-record"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 20
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_021 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "feedback-record"
    targetKind := "operational-lesson"
    branchIndex := 21
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_022 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "feedback-record"
    targetKind := "preference-application-assessment"
    branchIndex := 22
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_023 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "feedback-record"
    targetKind := "work-outcome-assessment"
    branchIndex := 23
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_024 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "finding"
    targetKind := "challenge-event"
    branchIndex := 24
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_025 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "finding"
    targetKind := "classification-assignment"
    branchIndex := 25
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_026 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "finding"
    targetKind := "drift-assessment"
    branchIndex := 26
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_027 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "finding"
    targetKind := "failure-assessment"
    branchIndex := 27
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_028 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "finding"
    targetKind := "failure-occurrence"
    branchIndex := 28
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_029 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "finding"
    targetKind := "improvement-signal"
    branchIndex := 29
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_030 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "finding"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 30
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_031 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "finding"
    targetKind := "operational-lesson"
    branchIndex := 31
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_032 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "finding"
    targetKind := "preference-application-assessment"
    branchIndex := 32
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_033 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "finding"
    targetKind := "work-outcome-assessment"
    branchIndex := 33
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_034 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "authority-claim"
    branchIndex := 34
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_035 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "challenge-event"
    branchIndex := 35
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_036 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "classification-assignment"
    branchIndex := 36
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_037 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "drift-assessment"
    branchIndex := 37
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_038 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "failure-assessment"
    branchIndex := 38
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_039 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "failure-occurrence"
    branchIndex := 39
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_040 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "finding"
    branchIndex := 40
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_041 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "hypothesis"
    branchIndex := 41
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_042 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "identity-claim"
    branchIndex := 42
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_043 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "improvement-signal"
    branchIndex := 43
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_044 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 44
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_045 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "operational-lesson"
    branchIndex := 45
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_046 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "preference-application-assessment"
    branchIndex := 46
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_047 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "work-outcome-assessment"
    branchIndex := 47
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_048 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "observation"
    targetKind := "authority-claim"
    branchIndex := 48
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_049 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "observation"
    targetKind := "challenge-event"
    branchIndex := 49
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_050 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "observation"
    targetKind := "classification-assignment"
    branchIndex := 50
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_051 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "observation"
    targetKind := "drift-assessment"
    branchIndex := 51
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_052 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "observation"
    targetKind := "failure-assessment"
    branchIndex := 52
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_053 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "observation"
    targetKind := "failure-occurrence"
    branchIndex := 53
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_054 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "observation"
    targetKind := "finding"
    branchIndex := 54
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_055 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "observation"
    targetKind := "hypothesis"
    branchIndex := 55
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_056 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "observation"
    targetKind := "identity-claim"
    branchIndex := 56
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_057 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "observation"
    targetKind := "improvement-signal"
    branchIndex := 57
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_058 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "observation"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 58
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_059 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "observation"
    targetKind := "operational-lesson"
    branchIndex := 59
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_060 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "observation"
    targetKind := "preference-application-assessment"
    branchIndex := 60
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_061 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "observation"
    targetKind := "work-outcome-assessment"
    branchIndex := 61
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_062 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "operational-observation"
    targetKind := "challenge-event"
    branchIndex := 62
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_063 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "operational-observation"
    targetKind := "classification-assignment"
    branchIndex := 63
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_064 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "operational-observation"
    targetKind := "drift-assessment"
    branchIndex := 64
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_065 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "operational-observation"
    targetKind := "failure-assessment"
    branchIndex := 65
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_066 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "operational-observation"
    targetKind := "failure-occurrence"
    branchIndex := 66
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_067 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "operational-observation"
    targetKind := "improvement-signal"
    branchIndex := 67
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_068 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "operational-observation"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 68
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_069 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "operational-observation"
    targetKind := "operational-lesson"
    branchIndex := 69
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_070 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "operational-observation"
    targetKind := "preference-application-assessment"
    branchIndex := 70
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_071 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:1"
    sourceKind := "operational-observation"
    targetKind := "work-outcome-assessment"
    branchIndex := 71
    arguments := .cons (.variable "decision") (.cons (.variable "outcome") (.cons (.variable "review") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independent decision concerning this target proposition", joins := [("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "outcome", sort := .ref, domain := "decision-outcomes", selectionRole := "Exact independently selected outcome for this decision about the named proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "review", sort := .ref, domain := "actual-review-records", selectionRole := "Exact actual review candidate concerning this decision and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("outcome", ⟨.ref, .variable "outcome"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "authority-claim"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "challenge-event"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "classification-assignment"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "drift-assessment"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "failure-assessment"
    branchIndex := 4
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_005 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "failure-occurrence"
    branchIndex := 5
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_006 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "finding"
    branchIndex := 6
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_007 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "hypothesis"
    branchIndex := 7
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_008 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "identity-claim"
    branchIndex := 8
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_009 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "improvement-signal"
    branchIndex := 9
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_010 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 10
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_011 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "operational-lesson"
    branchIndex := 11
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_012 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "preference-application-assessment"
    branchIndex := 12
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_013 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "work-outcome-assessment"
    branchIndex := 13
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_014 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "feedback-record"
    targetKind := "challenge-event"
    branchIndex := 14
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_015 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "feedback-record"
    targetKind := "classification-assignment"
    branchIndex := 15
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_016 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "feedback-record"
    targetKind := "drift-assessment"
    branchIndex := 16
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_017 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "feedback-record"
    targetKind := "failure-assessment"
    branchIndex := 17
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_018 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "feedback-record"
    targetKind := "failure-occurrence"
    branchIndex := 18
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_019 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "feedback-record"
    targetKind := "improvement-signal"
    branchIndex := 19
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_020 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "feedback-record"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 20
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_021 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "feedback-record"
    targetKind := "operational-lesson"
    branchIndex := 21
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_022 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "feedback-record"
    targetKind := "preference-application-assessment"
    branchIndex := 22
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_023 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "feedback-record"
    targetKind := "work-outcome-assessment"
    branchIndex := 23
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_024 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "finding"
    targetKind := "challenge-event"
    branchIndex := 24
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_025 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "finding"
    targetKind := "classification-assignment"
    branchIndex := 25
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_026 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "finding"
    targetKind := "drift-assessment"
    branchIndex := 26
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_027 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "finding"
    targetKind := "failure-assessment"
    branchIndex := 27
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_028 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "finding"
    targetKind := "failure-occurrence"
    branchIndex := 28
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_029 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "finding"
    targetKind := "improvement-signal"
    branchIndex := 29
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_030 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "finding"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 30
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_031 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "finding"
    targetKind := "operational-lesson"
    branchIndex := 31
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_032 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "finding"
    targetKind := "preference-application-assessment"
    branchIndex := 32
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_033 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "finding"
    targetKind := "work-outcome-assessment"
    branchIndex := 33
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_034 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "authority-claim"
    branchIndex := 34
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_035 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "challenge-event"
    branchIndex := 35
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_036 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "classification-assignment"
    branchIndex := 36
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_037 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "drift-assessment"
    branchIndex := 37
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_038 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "failure-assessment"
    branchIndex := 38
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_039 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "failure-occurrence"
    branchIndex := 39
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_040 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "finding"
    branchIndex := 40
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_041 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "hypothesis"
    branchIndex := 41
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_042 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "identity-claim"
    branchIndex := 42
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_043 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "improvement-signal"
    branchIndex := 43
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_044 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 44
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_045 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "operational-lesson"
    branchIndex := 45
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_046 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "preference-application-assessment"
    branchIndex := 46
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_047 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "work-outcome-assessment"
    branchIndex := 47
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_048 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "observation"
    targetKind := "authority-claim"
    branchIndex := 48
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_049 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "observation"
    targetKind := "challenge-event"
    branchIndex := 49
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_050 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "observation"
    targetKind := "classification-assignment"
    branchIndex := 50
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_051 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "observation"
    targetKind := "drift-assessment"
    branchIndex := 51
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_052 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "observation"
    targetKind := "failure-assessment"
    branchIndex := 52
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_053 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "observation"
    targetKind := "failure-occurrence"
    branchIndex := 53
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_054 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "observation"
    targetKind := "finding"
    branchIndex := 54
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_055 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "observation"
    targetKind := "hypothesis"
    branchIndex := 55
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_056 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "observation"
    targetKind := "identity-claim"
    branchIndex := 56
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_057 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "observation"
    targetKind := "improvement-signal"
    branchIndex := 57
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_058 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "observation"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 58
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_059 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "observation"
    targetKind := "operational-lesson"
    branchIndex := 59
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_060 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "observation"
    targetKind := "preference-application-assessment"
    branchIndex := 60
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_061 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "observation"
    targetKind := "work-outcome-assessment"
    branchIndex := 61
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_062 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "operational-observation"
    targetKind := "challenge-event"
    branchIndex := 62
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_063 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "operational-observation"
    targetKind := "classification-assignment"
    branchIndex := 63
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_064 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "operational-observation"
    targetKind := "drift-assessment"
    branchIndex := 64
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_065 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "operational-observation"
    targetKind := "failure-assessment"
    branchIndex := 65
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_066 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "operational-observation"
    targetKind := "failure-occurrence"
    branchIndex := 66
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_067 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "operational-observation"
    targetKind := "improvement-signal"
    branchIndex := 67
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_068 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "operational-observation"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 68
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_069 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "operational-observation"
    targetKind := "operational-lesson"
    branchIndex := 69
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_070 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "operational-observation"
    targetKind := "preference-application-assessment"
    branchIndex := 70
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_071 : Plan 18 [.ref, .ref, .ref] :=
  { obligationId := "relation.evidence-bears-on:forbidden:2"
    sourceKind := "operational-observation"
    targetKind := "work-outcome-assessment"
    branchIndex := 71
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "evidence-set"
    targetKind := "authority-claim"
    branchIndex := 0
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "evidence-set"
    targetKind := "challenge-event"
    branchIndex := 1
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_002 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "evidence-set"
    targetKind := "classification-assignment"
    branchIndex := 2
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_003 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "evidence-set"
    targetKind := "drift-assessment"
    branchIndex := 3
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_004 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "evidence-set"
    targetKind := "failure-assessment"
    branchIndex := 4
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_005 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "evidence-set"
    targetKind := "failure-occurrence"
    branchIndex := 5
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_006 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "evidence-set"
    targetKind := "finding"
    branchIndex := 6
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_007 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "evidence-set"
    targetKind := "hypothesis"
    branchIndex := 7
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_008 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "evidence-set"
    targetKind := "identity-claim"
    branchIndex := 8
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_009 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "evidence-set"
    targetKind := "improvement-signal"
    branchIndex := 9
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_010 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "evidence-set"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 10
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_011 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "evidence-set"
    targetKind := "operational-lesson"
    branchIndex := 11
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_012 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "evidence-set"
    targetKind := "preference-application-assessment"
    branchIndex := 12
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_013 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "evidence-set"
    targetKind := "work-outcome-assessment"
    branchIndex := 13
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_014 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "feedback-record"
    targetKind := "challenge-event"
    branchIndex := 14
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_015 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "feedback-record"
    targetKind := "classification-assignment"
    branchIndex := 15
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_016 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "feedback-record"
    targetKind := "drift-assessment"
    branchIndex := 16
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_017 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "feedback-record"
    targetKind := "failure-assessment"
    branchIndex := 17
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_018 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "feedback-record"
    targetKind := "failure-occurrence"
    branchIndex := 18
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_019 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "feedback-record"
    targetKind := "improvement-signal"
    branchIndex := 19
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_020 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "feedback-record"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 20
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_021 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "feedback-record"
    targetKind := "operational-lesson"
    branchIndex := 21
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_022 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "feedback-record"
    targetKind := "preference-application-assessment"
    branchIndex := 22
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_023 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "feedback-record"
    targetKind := "work-outcome-assessment"
    branchIndex := 23
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_024 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "finding"
    targetKind := "challenge-event"
    branchIndex := 24
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_025 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "finding"
    targetKind := "classification-assignment"
    branchIndex := 25
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_026 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "finding"
    targetKind := "drift-assessment"
    branchIndex := 26
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_027 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "finding"
    targetKind := "failure-assessment"
    branchIndex := 27
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_028 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "finding"
    targetKind := "failure-occurrence"
    branchIndex := 28
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_029 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "finding"
    targetKind := "improvement-signal"
    branchIndex := 29
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_030 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "finding"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 30
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_031 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "finding"
    targetKind := "operational-lesson"
    branchIndex := 31
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_032 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "finding"
    targetKind := "preference-application-assessment"
    branchIndex := 32
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_033 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "finding"
    targetKind := "work-outcome-assessment"
    branchIndex := 33
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_034 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "measurement-result"
    targetKind := "authority-claim"
    branchIndex := 34
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_035 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "measurement-result"
    targetKind := "challenge-event"
    branchIndex := 35
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_036 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "measurement-result"
    targetKind := "classification-assignment"
    branchIndex := 36
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_037 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "measurement-result"
    targetKind := "drift-assessment"
    branchIndex := 37
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_038 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "measurement-result"
    targetKind := "failure-assessment"
    branchIndex := 38
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_039 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "measurement-result"
    targetKind := "failure-occurrence"
    branchIndex := 39
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_040 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "measurement-result"
    targetKind := "finding"
    branchIndex := 40
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_041 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "measurement-result"
    targetKind := "hypothesis"
    branchIndex := 41
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_042 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "measurement-result"
    targetKind := "identity-claim"
    branchIndex := 42
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_043 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "measurement-result"
    targetKind := "improvement-signal"
    branchIndex := 43
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_044 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "measurement-result"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 44
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_045 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "measurement-result"
    targetKind := "operational-lesson"
    branchIndex := 45
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_046 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "measurement-result"
    targetKind := "preference-application-assessment"
    branchIndex := 46
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_047 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "measurement-result"
    targetKind := "work-outcome-assessment"
    branchIndex := 47
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_048 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "observation"
    targetKind := "authority-claim"
    branchIndex := 48
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_049 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "observation"
    targetKind := "challenge-event"
    branchIndex := 49
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_050 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "observation"
    targetKind := "classification-assignment"
    branchIndex := 50
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_051 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "observation"
    targetKind := "drift-assessment"
    branchIndex := 51
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_052 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "observation"
    targetKind := "failure-assessment"
    branchIndex := 52
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_053 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "observation"
    targetKind := "failure-occurrence"
    branchIndex := 53
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_054 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "observation"
    targetKind := "finding"
    branchIndex := 54
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_055 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "observation"
    targetKind := "hypothesis"
    branchIndex := 55
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_056 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "observation"
    targetKind := "identity-claim"
    branchIndex := 56
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_057 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "observation"
    targetKind := "improvement-signal"
    branchIndex := 57
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_058 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "observation"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 58
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_059 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "observation"
    targetKind := "operational-lesson"
    branchIndex := 59
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_060 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "observation"
    targetKind := "preference-application-assessment"
    branchIndex := 60
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_061 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "observation"
    targetKind := "work-outcome-assessment"
    branchIndex := 61
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_062 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "operational-observation"
    targetKind := "challenge-event"
    branchIndex := 62
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_063 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "operational-observation"
    targetKind := "classification-assignment"
    branchIndex := 63
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_064 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "operational-observation"
    targetKind := "drift-assessment"
    branchIndex := 64
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_065 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "operational-observation"
    targetKind := "failure-assessment"
    branchIndex := 65
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_066 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "operational-observation"
    targetKind := "failure-occurrence"
    branchIndex := 66
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_067 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "operational-observation"
    targetKind := "improvement-signal"
    branchIndex := 67
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_068 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "operational-observation"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 68
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_069 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "operational-observation"
    targetKind := "operational-lesson"
    branchIndex := 69
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_070 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "operational-observation"
    targetKind := "preference-application-assessment"
    branchIndex := 70
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_071 : Plan 18 [.ref, .ref, .world] :=
  { obligationId := "relation.evidence-bears-on:forbidden:3"
    sourceKind := "operational-observation"
    targetKind := "work-outcome-assessment"
    branchIndex := 71
    arguments := .cons (.witnessField "proposition" (by decide)) (.cons (.variable "interpretation") (.cons (.variable "world") (.nil)))
    binders := [
      { name := "interpretation", sort := .ref, domain := "proposition-interpretations", selectionRole := "Exact independent interpretation of this selected claim/proposition", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩)] },
      { name := "world", sort := .world, domain := "truth-interpretations", selectionRole := "Independent semantic world/valuation for this interpreted claim; evidential polarity is not truth", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .witnessField "proposition" (by decide)⟩), ("interpretation", ⟨.ref, .variable "interpretation"⟩)] }
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
#print axioms plan_3_024
#print axioms plan_3_025
#print axioms plan_3_026
#print axioms plan_3_027
#print axioms plan_3_028
#print axioms plan_3_029
#print axioms plan_3_030
#print axioms plan_3_031
#print axioms plan_3_032
#print axioms plan_3_033
#print axioms plan_3_034
#print axioms plan_3_035
#print axioms plan_3_036
#print axioms plan_3_037
#print axioms plan_3_038
#print axioms plan_3_039
#print axioms plan_3_040
#print axioms plan_3_041
#print axioms plan_3_042
#print axioms plan_3_043
#print axioms plan_3_044
#print axioms plan_3_045
#print axioms plan_3_046
#print axioms plan_3_047
#print axioms plan_3_048
#print axioms plan_3_049
#print axioms plan_3_050
#print axioms plan_3_051
#print axioms plan_3_052
#print axioms plan_3_053
#print axioms plan_3_054
#print axioms plan_3_055
#print axioms plan_3_056
#print axioms plan_3_057
#print axioms plan_3_058
#print axioms plan_3_059
#print axioms plan_3_060
#print axioms plan_3_061
#print axioms plan_3_062
#print axioms plan_3_063
#print axioms plan_3_064
#print axioms plan_3_065
#print axioms plan_3_066
#print axioms plan_3_067
#print axioms plan_3_068
#print axioms plan_3_069
#print axioms plan_3_070
#print axioms plan_3_071
end CandidateConclusionAnchors.K18
