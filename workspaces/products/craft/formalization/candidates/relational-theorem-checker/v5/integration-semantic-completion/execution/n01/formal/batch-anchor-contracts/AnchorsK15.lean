import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K15

def plan_0_000 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "agent-reflection"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "agent-reflection"
    targetKind := "agent-session"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "agent-reflection"
    targetKind := "evidence-set"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "agent-reflection"
    targetKind := "failure-assessment"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "agent-reflection"
    targetKind := "feedback-record"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_005 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "agent-reflection"
    targetKind := "finding"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_006 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "agent-reflection"
    targetKind := "observation"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_007 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "agent-reflection"
    targetKind := "operational-observation"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_008 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "agent-reflection"
    targetKind := "work-outcome-assessment"
    branchIndex := 8
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_009 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "classification-assignment"
    targetKind := "evidence-set"
    branchIndex := 9
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_010 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "classification-assignment"
    targetKind := "feedback-record"
    branchIndex := 10
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_011 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "classification-assignment"
    targetKind := "finding"
    branchIndex := 11
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_012 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "classification-assignment"
    targetKind := "measurement-result"
    branchIndex := 12
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_013 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "classification-assignment"
    targetKind := "observation"
    branchIndex := 13
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_014 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "classification-assignment"
    targetKind := "operational-observation"
    branchIndex := 14
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_015 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "classification-assignment"
    targetKind := "source"
    branchIndex := 15
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_016 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "context-view"
    targetKind := "context"
    branchIndex := 16
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_017 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "experiment-run"
    branchIndex := 17
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_018 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "evidence-set"
    targetKind := "research-run"
    branchIndex := 18
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_019 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "finding"
    targetKind := "evidence-set"
    branchIndex := 19
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_020 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "finding"
    targetKind := "research-run"
    branchIndex := 20
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_021 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "generated-output"
    targetKind := "source"
    branchIndex := 21
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_022 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "improvement-signal"
    targetKind := "drift-assessment"
    branchIndex := 22
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_023 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "improvement-signal"
    targetKind := "failure-assessment"
    branchIndex := 23
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_024 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "improvement-signal"
    targetKind := "operational-observation"
    branchIndex := 24
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_025 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "improvement-signal"
    targetKind := "work-outcome-assessment"
    branchIndex := 25
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_026 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "improvement-target"
    targetKind := "improvement-signal"
    branchIndex := 26
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_027 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "improvement-target"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 27
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_028 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "improvement-target"
    targetKind := "operational-lesson"
    branchIndex := 28
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_029 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "experiment-run"
    branchIndex := 29
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_030 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "research-run"
    branchIndex := 30
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_031 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "observation"
    targetKind := "experiment-run"
    branchIndex := 31
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_032 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "observation"
    targetKind := "research-run"
    branchIndex := 32
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_033 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "operational-lesson"
    targetKind := "agent-reflection"
    branchIndex := 33
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_034 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "operational-lesson"
    targetKind := "evidence-set"
    branchIndex := 34
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_035 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "operational-lesson"
    targetKind := "failure-assessment"
    branchIndex := 35
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_036 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "operational-lesson"
    targetKind := "feedback-record"
    branchIndex := 36
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_037 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "operational-lesson"
    targetKind := "finding"
    branchIndex := 37
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_038 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "operational-lesson"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 38
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_039 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:0"
    sourceKind := "product-capability"
    targetKind := "product-thesis"
    branchIndex := 39
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "agent-reflection"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "agent-reflection"
    targetKind := "agent-session"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "agent-reflection"
    targetKind := "evidence-set"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "agent-reflection"
    targetKind := "failure-assessment"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "agent-reflection"
    targetKind := "feedback-record"
    branchIndex := 4
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_005 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "agent-reflection"
    targetKind := "finding"
    branchIndex := 5
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_006 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "agent-reflection"
    targetKind := "observation"
    branchIndex := 6
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_007 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "agent-reflection"
    targetKind := "operational-observation"
    branchIndex := 7
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_008 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "agent-reflection"
    targetKind := "work-outcome-assessment"
    branchIndex := 8
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_009 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "classification-assignment"
    targetKind := "evidence-set"
    branchIndex := 9
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_010 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "classification-assignment"
    targetKind := "feedback-record"
    branchIndex := 10
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_011 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "classification-assignment"
    targetKind := "finding"
    branchIndex := 11
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_012 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "classification-assignment"
    targetKind := "measurement-result"
    branchIndex := 12
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_013 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "classification-assignment"
    targetKind := "observation"
    branchIndex := 13
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_014 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "classification-assignment"
    targetKind := "operational-observation"
    branchIndex := 14
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_015 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "classification-assignment"
    targetKind := "source"
    branchIndex := 15
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_016 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "context-view"
    targetKind := "context"
    branchIndex := 16
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_017 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "experiment-run"
    branchIndex := 17
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_018 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "evidence-set"
    targetKind := "research-run"
    branchIndex := 18
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_019 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "finding"
    targetKind := "evidence-set"
    branchIndex := 19
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_020 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "finding"
    targetKind := "research-run"
    branchIndex := 20
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_021 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "generated-output"
    targetKind := "source"
    branchIndex := 21
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_022 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "improvement-signal"
    targetKind := "drift-assessment"
    branchIndex := 22
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_023 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "improvement-signal"
    targetKind := "failure-assessment"
    branchIndex := 23
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_024 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "improvement-signal"
    targetKind := "operational-observation"
    branchIndex := 24
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_025 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "improvement-signal"
    targetKind := "work-outcome-assessment"
    branchIndex := 25
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_026 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "improvement-target"
    targetKind := "improvement-signal"
    branchIndex := 26
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_027 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "improvement-target"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 27
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_028 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "improvement-target"
    targetKind := "operational-lesson"
    branchIndex := 28
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_029 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "experiment-run"
    branchIndex := 29
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_030 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "research-run"
    branchIndex := 30
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_031 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "observation"
    targetKind := "experiment-run"
    branchIndex := 31
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_032 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "observation"
    targetKind := "research-run"
    branchIndex := 32
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_033 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "operational-lesson"
    targetKind := "agent-reflection"
    branchIndex := 33
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_034 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "operational-lesson"
    targetKind := "evidence-set"
    branchIndex := 34
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_035 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "operational-lesson"
    targetKind := "failure-assessment"
    branchIndex := 35
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_036 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "operational-lesson"
    targetKind := "feedback-record"
    branchIndex := 36
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_037 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "operational-lesson"
    targetKind := "finding"
    branchIndex := 37
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_038 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "operational-lesson"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 38
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_039 : Plan 15 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:1"
    sourceKind := "product-capability"
    targetKind := "product-thesis"
    branchIndex := 39
    arguments := .cons (.target) (.cons (.source) (.cons (.variable "boundary") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "boundary", sort := .ref, domain := "authority-boundaries", selectionRole := "Exact boundary relevant to the source/derived authority transfer", joins := [("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .target⟩), ("derived", ⟨.ref, .source⟩), ("boundary", ⟨.ref, .variable "boundary"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "agent-reflection"
    targetKind := "agent-action"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "agent-reflection"
    targetKind := "agent-session"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "agent-reflection"
    targetKind := "evidence-set"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "agent-reflection"
    targetKind := "failure-assessment"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "agent-reflection"
    targetKind := "feedback-record"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_005 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "agent-reflection"
    targetKind := "finding"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_006 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "agent-reflection"
    targetKind := "observation"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_007 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "agent-reflection"
    targetKind := "operational-observation"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_008 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "agent-reflection"
    targetKind := "work-outcome-assessment"
    branchIndex := 8
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_009 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "classification-assignment"
    targetKind := "evidence-set"
    branchIndex := 9
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_010 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "classification-assignment"
    targetKind := "feedback-record"
    branchIndex := 10
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_011 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "classification-assignment"
    targetKind := "finding"
    branchIndex := 11
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_012 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "classification-assignment"
    targetKind := "measurement-result"
    branchIndex := 12
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_013 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "classification-assignment"
    targetKind := "observation"
    branchIndex := 13
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_014 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "classification-assignment"
    targetKind := "operational-observation"
    branchIndex := 14
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_015 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "classification-assignment"
    targetKind := "source"
    branchIndex := 15
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_016 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "context-view"
    targetKind := "context"
    branchIndex := 16
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_017 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "experiment-run"
    branchIndex := 17
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_018 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "evidence-set"
    targetKind := "research-run"
    branchIndex := 18
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_019 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "finding"
    targetKind := "evidence-set"
    branchIndex := 19
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_020 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "finding"
    targetKind := "research-run"
    branchIndex := 20
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_021 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "generated-output"
    targetKind := "source"
    branchIndex := 21
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_022 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "improvement-signal"
    targetKind := "drift-assessment"
    branchIndex := 22
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_023 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "improvement-signal"
    targetKind := "failure-assessment"
    branchIndex := 23
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_024 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "improvement-signal"
    targetKind := "operational-observation"
    branchIndex := 24
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_025 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "improvement-signal"
    targetKind := "work-outcome-assessment"
    branchIndex := 25
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_026 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "improvement-target"
    targetKind := "improvement-signal"
    branchIndex := 26
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_027 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "improvement-target"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 27
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_028 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "improvement-target"
    targetKind := "operational-lesson"
    branchIndex := 28
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_029 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "experiment-run"
    branchIndex := 29
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_030 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "research-run"
    branchIndex := 30
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_031 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "observation"
    targetKind := "experiment-run"
    branchIndex := 31
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_032 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "observation"
    targetKind := "research-run"
    branchIndex := 32
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_033 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "operational-lesson"
    targetKind := "agent-reflection"
    branchIndex := 33
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_034 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "operational-lesson"
    targetKind := "evidence-set"
    branchIndex := 34
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_035 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "operational-lesson"
    targetKind := "failure-assessment"
    branchIndex := 35
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_036 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "operational-lesson"
    targetKind := "feedback-record"
    branchIndex := 36
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_037 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "operational-lesson"
    targetKind := "finding"
    branchIndex := 37
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_038 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "operational-lesson"
    targetKind := "lesson-outcome-assessment"
    branchIndex := 38
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_039 : Plan 15 [.ref, .ref, .ref] :=
  { obligationId := "relation.derives-from:forbidden:2"
    sourceKind := "product-capability"
    targetKind := "product-thesis"
    branchIndex := 39
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
end CandidateConclusionAnchors.K15
