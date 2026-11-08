import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K09

def plan_0_000 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "agent-assignment"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "agent-capability"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "agent-instance"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "agent-profile"
    branchIndex := 4
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_005 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "agent-reflection"
    branchIndex := 5
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_006 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "agent-session"
    branchIndex := 6
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_007 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "artifact-type"
    branchIndex := 7
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_008 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "artifact-type-request"
    branchIndex := 8
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_009 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "authority-claim"
    branchIndex := 9
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_010 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "bounded-context"
    branchIndex := 10
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_011 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "canonical-package-manifest"
    branchIndex := 11
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_012 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "capability-instance"
    branchIndex := 12
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_013 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "capability-realization-binding"
    branchIndex := 13
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_014 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "challenge-contract"
    branchIndex := 14
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_015 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "challenge-event"
    branchIndex := 15
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_016 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "classification-assignment"
    branchIndex := 16
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_017 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "classification-scheme"
    branchIndex := 17
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_018 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "classification-value"
    branchIndex := 18
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_019 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "communication-preference"
    branchIndex := 19
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_020 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "constitution"
    branchIndex := 20
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_021 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "context"
    branchIndex := 21
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_022 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "context-lineage-record"
    branchIndex := 22
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_023 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "context-map"
    branchIndex := 23
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_024 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "context-migration-manifest"
    branchIndex := 24
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_025 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "context-profile"
    branchIndex := 25
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_026 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "context-request"
    branchIndex := 26
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_027 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "context-view"
    branchIndex := 27
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_028 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "contract"
    branchIndex := 28
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_029 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "decision"
    branchIndex := 29
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_030 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "decision-scope"
    branchIndex := 30
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_031 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "definition"
    branchIndex := 31
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_032 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "delegation"
    branchIndex := 32
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_033 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "drift-assessment"
    branchIndex := 33
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_034 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "effect"
    branchIndex := 34
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_035 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "evaluation"
    branchIndex := 35
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_036 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "evidence-set"
    branchIndex := 36
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_037 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "experiment-design"
    branchIndex := 37
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_038 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "experiment-run"
    branchIndex := 38
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_039 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "failure-assessment"
    branchIndex := 39
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_040 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "failure-control-binding"
    branchIndex := 40
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_041 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "failure-mode"
    branchIndex := 41
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_042 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "failure-occurrence"
    branchIndex := 42
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_043 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "feedback-record"
    branchIndex := 43
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_044 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "finding"
    branchIndex := 44
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_045 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "generated-output"
    branchIndex := 45
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_046 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "goal"
    branchIndex := 46
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_047 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "governance-event-history"
    branchIndex := 47
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_048 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "governed-model"
    branchIndex := 48
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_049 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "hypothesis"
    branchIndex := 49
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_050 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "identity-claim"
    branchIndex := 50
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_051 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "implementation"
    branchIndex := 51
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_052 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "improvement-signal"
    branchIndex := 52
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_053 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "improvement-target"
    branchIndex := 53
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_054 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "incident"
    branchIndex := 54
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_055 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "intent-resolution"
    branchIndex := 55
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_056 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "lesson-application"
    branchIndex := 56
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_057 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 57
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_058 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "measurement-method"
    branchIndex := 58
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_059 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "measurement-result"
    branchIndex := 59
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_060 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "method"
    branchIndex := 60
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_061 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "model-instance-binding"
    branchIndex := 61
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_062 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "observation"
    branchIndex := 62
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_063 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "ontology"
    branchIndex := 63
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_064 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "ontology-cut"
    branchIndex := 64
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_065 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "ontology-edge"
    branchIndex := 65
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_066 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "ontology-manifest"
    branchIndex := 66
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_067 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "ontology-node"
    branchIndex := 67
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_068 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "ontology-package"
    branchIndex := 68
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_069 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "ontology-view"
    branchIndex := 69
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_070 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "operational-lesson"
    branchIndex := 70
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_071 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "operational-observation"
    branchIndex := 71
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_072 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "person"
    branchIndex := 72
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_073 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "person-reference"
    branchIndex := 73
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_074 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "policy"
    branchIndex := 74
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_075 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "preference-application-assessment"
    branchIndex := 75
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_076 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "principal"
    branchIndex := 76
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_077 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "principal-reference"
    branchIndex := 77
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_078 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "product"
    branchIndex := 78
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_079 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "product-capability"
    branchIndex := 79
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_080 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "product-thesis"
    branchIndex := 80
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_081 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "project"
    branchIndex := 81
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_082 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "project-state"
    branchIndex := 82
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_083 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "relation-kind"
    branchIndex := 83
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_084 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "research-inquiry"
    branchIndex := 84
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_085 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "research-run"
    branchIndex := 85
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_086 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "responsibility"
    branchIndex := 86
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_087 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "review"
    branchIndex := 87
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_088 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "role"
    branchIndex := 88
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_089 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "role-assignment"
    branchIndex := 89
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_090 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "schema"
    branchIndex := 90
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_091 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "semantic-event-history"
    branchIndex := 91
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_092 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "source"
    branchIndex := 92
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_093 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "team"
    branchIndex := 93
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_094 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "team-membership"
    branchIndex := 94
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_095 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "tool"
    branchIndex := 95
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_096 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "typed-relation"
    branchIndex := 96
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_097 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "ubiquitous-language"
    branchIndex := 97
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_098 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "work"
    branchIndex := 98
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_099 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:0"
    sourceKind := "challenge-event"
    targetKind := "work-outcome-assessment"
    branchIndex := 99
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "agent-assignment"
    branchIndex := 1
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "agent-capability"
    branchIndex := 2
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "agent-instance"
    branchIndex := 3
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "agent-profile"
    branchIndex := 4
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_005 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "agent-reflection"
    branchIndex := 5
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_006 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "agent-session"
    branchIndex := 6
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_007 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "artifact-type"
    branchIndex := 7
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_008 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "artifact-type-request"
    branchIndex := 8
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_009 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "authority-claim"
    branchIndex := 9
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_010 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "bounded-context"
    branchIndex := 10
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_011 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "canonical-package-manifest"
    branchIndex := 11
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_012 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "capability-instance"
    branchIndex := 12
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_013 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "capability-realization-binding"
    branchIndex := 13
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_014 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "challenge-contract"
    branchIndex := 14
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_015 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "challenge-event"
    branchIndex := 15
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_016 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "classification-assignment"
    branchIndex := 16
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_017 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "classification-scheme"
    branchIndex := 17
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_018 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "classification-value"
    branchIndex := 18
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_019 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "communication-preference"
    branchIndex := 19
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_020 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "constitution"
    branchIndex := 20
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_021 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "context"
    branchIndex := 21
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_022 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "context-lineage-record"
    branchIndex := 22
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_023 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "context-map"
    branchIndex := 23
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_024 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "context-migration-manifest"
    branchIndex := 24
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_025 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "context-profile"
    branchIndex := 25
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_026 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "context-request"
    branchIndex := 26
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_027 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "context-view"
    branchIndex := 27
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_028 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "contract"
    branchIndex := 28
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_029 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "decision"
    branchIndex := 29
    arguments := .cons (.target) (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .target⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .target⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_030 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "decision-scope"
    branchIndex := 30
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_031 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "definition"
    branchIndex := 31
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_032 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "delegation"
    branchIndex := 32
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_033 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "drift-assessment"
    branchIndex := 33
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_034 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "effect"
    branchIndex := 34
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_035 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "evaluation"
    branchIndex := 35
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_036 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "evidence-set"
    branchIndex := 36
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_037 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "experiment-design"
    branchIndex := 37
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_038 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "experiment-run"
    branchIndex := 38
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_039 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "failure-assessment"
    branchIndex := 39
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_040 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "failure-control-binding"
    branchIndex := 40
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_041 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "failure-mode"
    branchIndex := 41
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_042 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "failure-occurrence"
    branchIndex := 42
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_043 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "feedback-record"
    branchIndex := 43
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_044 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "finding"
    branchIndex := 44
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_045 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "generated-output"
    branchIndex := 45
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_046 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "goal"
    branchIndex := 46
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_047 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "governance-event-history"
    branchIndex := 47
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_048 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "governed-model"
    branchIndex := 48
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_049 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "hypothesis"
    branchIndex := 49
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_050 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "identity-claim"
    branchIndex := 50
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_051 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "implementation"
    branchIndex := 51
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_052 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "improvement-signal"
    branchIndex := 52
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_053 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "improvement-target"
    branchIndex := 53
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_054 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "incident"
    branchIndex := 54
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_055 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "intent-resolution"
    branchIndex := 55
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_056 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "lesson-application"
    branchIndex := 56
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_057 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 57
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_058 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "measurement-method"
    branchIndex := 58
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_059 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "measurement-result"
    branchIndex := 59
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_060 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "method"
    branchIndex := 60
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_061 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "model-instance-binding"
    branchIndex := 61
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_062 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "observation"
    branchIndex := 62
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_063 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "ontology"
    branchIndex := 63
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_064 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "ontology-cut"
    branchIndex := 64
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_065 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "ontology-edge"
    branchIndex := 65
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_066 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "ontology-manifest"
    branchIndex := 66
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_067 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "ontology-node"
    branchIndex := 67
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_068 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "ontology-package"
    branchIndex := 68
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_069 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "ontology-view"
    branchIndex := 69
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_070 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "operational-lesson"
    branchIndex := 70
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_071 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "operational-observation"
    branchIndex := 71
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_072 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "person"
    branchIndex := 72
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_073 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "person-reference"
    branchIndex := 73
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_074 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "policy"
    branchIndex := 74
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_075 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "preference-application-assessment"
    branchIndex := 75
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_076 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "principal"
    branchIndex := 76
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_077 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "principal-reference"
    branchIndex := 77
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_078 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "product"
    branchIndex := 78
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_079 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "product-capability"
    branchIndex := 79
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_080 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "product-thesis"
    branchIndex := 80
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_081 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "project"
    branchIndex := 81
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_082 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "project-state"
    branchIndex := 82
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_083 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "relation-kind"
    branchIndex := 83
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_084 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "research-inquiry"
    branchIndex := 84
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_085 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "research-run"
    branchIndex := 85
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_086 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "responsibility"
    branchIndex := 86
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_087 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "review"
    branchIndex := 87
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_088 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "role"
    branchIndex := 88
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_089 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "role-assignment"
    branchIndex := 89
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_090 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "schema"
    branchIndex := 90
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_091 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "semantic-event-history"
    branchIndex := 91
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_092 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "source"
    branchIndex := 92
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_093 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "team"
    branchIndex := 93
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_094 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "team-membership"
    branchIndex := 94
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_095 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "tool"
    branchIndex := 95
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_096 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "typed-relation"
    branchIndex := 96
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_097 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "ubiquitous-language"
    branchIndex := 97
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_098 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "work"
    branchIndex := 98
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_099 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:1"
    sourceKind := "challenge-event"
    targetKind := "work-outcome-assessment"
    branchIndex := 99
    arguments := .cons (.variable "decision") (.cons (.variable "reversal") (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected earlier decision about the challenged target", joins := [("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "reversal", sort := .ref, domain := "reversal-records", selectionRole := "Separate reversal candidate of the exact earlier selected decision", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("reversal", ⟨.ref, .variable "reversal"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "agent-assignment"
    branchIndex := 1
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "agent-capability"
    branchIndex := 2
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "agent-instance"
    branchIndex := 3
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "agent-profile"
    branchIndex := 4
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_005 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "agent-reflection"
    branchIndex := 5
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_006 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "agent-session"
    branchIndex := 6
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_007 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "artifact-type"
    branchIndex := 7
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_008 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "artifact-type-request"
    branchIndex := 8
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_009 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "authority-claim"
    branchIndex := 9
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_010 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "bounded-context"
    branchIndex := 10
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_011 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "canonical-package-manifest"
    branchIndex := 11
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_012 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "capability-instance"
    branchIndex := 12
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_013 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "capability-realization-binding"
    branchIndex := 13
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_014 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "challenge-contract"
    branchIndex := 14
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_015 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "challenge-event"
    branchIndex := 15
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_016 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "classification-assignment"
    branchIndex := 16
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_017 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "classification-scheme"
    branchIndex := 17
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_018 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "classification-value"
    branchIndex := 18
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_019 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "communication-preference"
    branchIndex := 19
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_020 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "constitution"
    branchIndex := 20
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_021 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "context"
    branchIndex := 21
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_022 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "context-lineage-record"
    branchIndex := 22
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_023 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "context-map"
    branchIndex := 23
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_024 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "context-migration-manifest"
    branchIndex := 24
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_025 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "context-profile"
    branchIndex := 25
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_026 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "context-request"
    branchIndex := 26
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_027 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "context-view"
    branchIndex := 27
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_028 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "contract"
    branchIndex := 28
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_029 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "decision"
    branchIndex := 29
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_030 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "decision-scope"
    branchIndex := 30
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_031 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "definition"
    branchIndex := 31
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_032 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "delegation"
    branchIndex := 32
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_033 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "drift-assessment"
    branchIndex := 33
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_034 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "effect"
    branchIndex := 34
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_035 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "evaluation"
    branchIndex := 35
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_036 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "evidence-set"
    branchIndex := 36
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_037 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "experiment-design"
    branchIndex := 37
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_038 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "experiment-run"
    branchIndex := 38
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_039 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "failure-assessment"
    branchIndex := 39
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_040 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "failure-control-binding"
    branchIndex := 40
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_041 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "failure-mode"
    branchIndex := 41
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_042 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "failure-occurrence"
    branchIndex := 42
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_043 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "feedback-record"
    branchIndex := 43
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_044 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "finding"
    branchIndex := 44
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_045 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "generated-output"
    branchIndex := 45
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_046 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "goal"
    branchIndex := 46
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_047 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "governance-event-history"
    branchIndex := 47
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_048 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "governed-model"
    branchIndex := 48
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_049 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "hypothesis"
    branchIndex := 49
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_050 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "identity-claim"
    branchIndex := 50
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_051 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "implementation"
    branchIndex := 51
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_052 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "improvement-signal"
    branchIndex := 52
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_053 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "improvement-target"
    branchIndex := 53
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_054 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "incident"
    branchIndex := 54
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_055 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "intent-resolution"
    branchIndex := 55
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_056 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "lesson-application"
    branchIndex := 56
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_057 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 57
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_058 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "measurement-method"
    branchIndex := 58
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_059 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "measurement-result"
    branchIndex := 59
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_060 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "method"
    branchIndex := 60
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_061 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "model-instance-binding"
    branchIndex := 61
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_062 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "observation"
    branchIndex := 62
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_063 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "ontology"
    branchIndex := 63
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_064 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "ontology-cut"
    branchIndex := 64
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_065 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "ontology-edge"
    branchIndex := 65
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_066 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "ontology-manifest"
    branchIndex := 66
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_067 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "ontology-node"
    branchIndex := 67
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_068 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "ontology-package"
    branchIndex := 68
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_069 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "ontology-view"
    branchIndex := 69
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_070 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "operational-lesson"
    branchIndex := 70
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_071 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "operational-observation"
    branchIndex := 71
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_072 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "person"
    branchIndex := 72
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_073 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "person-reference"
    branchIndex := 73
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_074 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "policy"
    branchIndex := 74
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_075 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "preference-application-assessment"
    branchIndex := 75
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_076 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "principal"
    branchIndex := 76
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_077 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "principal-reference"
    branchIndex := 77
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_078 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "product"
    branchIndex := 78
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_079 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "product-capability"
    branchIndex := 79
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_080 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "product-thesis"
    branchIndex := 80
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_081 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "project"
    branchIndex := 81
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_082 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "project-state"
    branchIndex := 82
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_083 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "relation-kind"
    branchIndex := 83
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_084 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "research-inquiry"
    branchIndex := 84
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_085 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "research-run"
    branchIndex := 85
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_086 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "responsibility"
    branchIndex := 86
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_087 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "review"
    branchIndex := 87
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_088 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "role"
    branchIndex := 88
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_089 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "role-assignment"
    branchIndex := 89
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_090 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "schema"
    branchIndex := 90
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_091 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "semantic-event-history"
    branchIndex := 91
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_092 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "source"
    branchIndex := 92
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_093 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "team"
    branchIndex := 93
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_094 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "team-membership"
    branchIndex := 94
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_095 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "tool"
    branchIndex := 95
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_096 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "typed-relation"
    branchIndex := 96
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_097 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "ubiquitous-language"
    branchIndex := 97
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_098 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "work"
    branchIndex := 98
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_099 : Plan 9 [.ref, .ref, .ref] :=
  { obligationId := "relation.challenges:forbidden:2"
    sourceKind := "challenge-event"
    targetKind := "work-outcome-assessment"
    branchIndex := 99
    arguments := .cons (.frameField "theory" (by decide)) (.cons (.variable "claim") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "proposition-selectors", selectionRole := "Exact owned proposition within the named carrier; an artifact is not itself a unique proposition selector", joins := [("carrier", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("theory", ⟨.ref, .frameField "theory" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "agent-assignment"
    branchIndex := 1
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_002 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "agent-capability"
    branchIndex := 2
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_003 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "agent-instance"
    branchIndex := 3
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_004 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "agent-profile"
    branchIndex := 4
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_005 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "agent-reflection"
    branchIndex := 5
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_006 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "agent-session"
    branchIndex := 6
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_007 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "artifact-type"
    branchIndex := 7
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_008 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "artifact-type-request"
    branchIndex := 8
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_009 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "authority-claim"
    branchIndex := 9
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_010 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "bounded-context"
    branchIndex := 10
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_011 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "canonical-package-manifest"
    branchIndex := 11
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_012 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "capability-instance"
    branchIndex := 12
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_013 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "capability-realization-binding"
    branchIndex := 13
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_014 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "challenge-contract"
    branchIndex := 14
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_015 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "challenge-event"
    branchIndex := 15
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_016 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "classification-assignment"
    branchIndex := 16
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_017 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "classification-scheme"
    branchIndex := 17
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_018 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "classification-value"
    branchIndex := 18
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_019 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "communication-preference"
    branchIndex := 19
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_020 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "constitution"
    branchIndex := 20
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_021 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "context"
    branchIndex := 21
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_022 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "context-lineage-record"
    branchIndex := 22
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_023 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "context-map"
    branchIndex := 23
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_024 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "context-migration-manifest"
    branchIndex := 24
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_025 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "context-profile"
    branchIndex := 25
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_026 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "context-request"
    branchIndex := 26
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_027 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "context-view"
    branchIndex := 27
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_028 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "contract"
    branchIndex := 28
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_029 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "decision"
    branchIndex := 29
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_030 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "decision-scope"
    branchIndex := 30
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_031 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "definition"
    branchIndex := 31
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_032 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "delegation"
    branchIndex := 32
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_033 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "drift-assessment"
    branchIndex := 33
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_034 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "effect"
    branchIndex := 34
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_035 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "evaluation"
    branchIndex := 35
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_036 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "evidence-set"
    branchIndex := 36
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_037 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "experiment-design"
    branchIndex := 37
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_038 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "experiment-run"
    branchIndex := 38
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_039 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "failure-assessment"
    branchIndex := 39
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_040 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "failure-control-binding"
    branchIndex := 40
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_041 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "failure-mode"
    branchIndex := 41
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_042 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "failure-occurrence"
    branchIndex := 42
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_043 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "feedback-record"
    branchIndex := 43
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_044 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "finding"
    branchIndex := 44
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_045 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "generated-output"
    branchIndex := 45
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_046 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "goal"
    branchIndex := 46
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_047 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "governance-event-history"
    branchIndex := 47
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_048 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "governed-model"
    branchIndex := 48
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_049 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "hypothesis"
    branchIndex := 49
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_050 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "identity-claim"
    branchIndex := 50
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_051 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "implementation"
    branchIndex := 51
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_052 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "improvement-signal"
    branchIndex := 52
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_053 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "improvement-target"
    branchIndex := 53
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_054 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "incident"
    branchIndex := 54
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_055 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "intent-resolution"
    branchIndex := 55
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_056 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "lesson-application"
    branchIndex := 56
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_057 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 57
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_058 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "measurement-method"
    branchIndex := 58
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_059 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "measurement-result"
    branchIndex := 59
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_060 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "method"
    branchIndex := 60
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_061 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "model-instance-binding"
    branchIndex := 61
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_062 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "observation"
    branchIndex := 62
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_063 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "ontology"
    branchIndex := 63
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_064 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "ontology-cut"
    branchIndex := 64
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_065 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "ontology-edge"
    branchIndex := 65
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_066 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "ontology-manifest"
    branchIndex := 66
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_067 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "ontology-node"
    branchIndex := 67
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_068 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "ontology-package"
    branchIndex := 68
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_069 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "ontology-view"
    branchIndex := 69
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_070 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "operational-lesson"
    branchIndex := 70
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_071 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "operational-observation"
    branchIndex := 71
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_072 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "person"
    branchIndex := 72
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_073 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "person-reference"
    branchIndex := 73
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_074 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "policy"
    branchIndex := 74
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_075 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "preference-application-assessment"
    branchIndex := 75
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_076 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "principal"
    branchIndex := 76
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_077 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "principal-reference"
    branchIndex := 77
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_078 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "product"
    branchIndex := 78
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_079 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "product-capability"
    branchIndex := 79
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_080 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "product-thesis"
    branchIndex := 80
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_081 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "project"
    branchIndex := 81
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_082 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "project-state"
    branchIndex := 82
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_083 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "relation-kind"
    branchIndex := 83
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_084 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "research-inquiry"
    branchIndex := 84
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_085 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "research-run"
    branchIndex := 85
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_086 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "responsibility"
    branchIndex := 86
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_087 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "review"
    branchIndex := 87
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_088 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "role"
    branchIndex := 88
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_089 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "role-assignment"
    branchIndex := 89
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_090 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "schema"
    branchIndex := 90
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_091 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "semantic-event-history"
    branchIndex := 91
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_092 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "source"
    branchIndex := 92
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_093 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "team"
    branchIndex := 93
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_094 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "team-membership"
    branchIndex := 94
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_095 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "tool"
    branchIndex := 95
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_096 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "typed-relation"
    branchIndex := 96
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_097 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "ubiquitous-language"
    branchIndex := 97
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_098 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "work"
    branchIndex := 98
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_099 : Plan 9 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.challenges:forbidden:3"
    sourceKind := "challenge-event"
    targetKind := "work-outcome-assessment"
    branchIndex := 99
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
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
#print axioms plan_3_072
#print axioms plan_3_073
#print axioms plan_3_074
#print axioms plan_3_075
#print axioms plan_3_076
#print axioms plan_3_077
#print axioms plan_3_078
#print axioms plan_3_079
#print axioms plan_3_080
#print axioms plan_3_081
#print axioms plan_3_082
#print axioms plan_3_083
#print axioms plan_3_084
#print axioms plan_3_085
#print axioms plan_3_086
#print axioms plan_3_087
#print axioms plan_3_088
#print axioms plan_3_089
#print axioms plan_3_090
#print axioms plan_3_091
#print axioms plan_3_092
#print axioms plan_3_093
#print axioms plan_3_094
#print axioms plan_3_095
#print axioms plan_3_096
#print axioms plan_3_097
#print axioms plan_3_098
#print axioms plan_3_099
end CandidateConclusionAnchors.K09
