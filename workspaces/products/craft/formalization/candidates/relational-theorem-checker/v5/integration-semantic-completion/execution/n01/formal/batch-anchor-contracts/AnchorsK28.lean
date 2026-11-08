import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K28

def plan_0_000 : Plan 28 [.ref, .ref, .ref] :=
  { obligationId := "relation.originates-from:forbidden:0"
    sourceKind := "artifact-type"
    targetKind := "source"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transform") (.nil)))
    binders := [
      { name := "transform", sort := .ref, domain := "transformation-records", selectionRole := "Separate exact transformation/compilation/projection record joining this derived artifact to this source", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("derived", ⟨.ref, .source⟩), ("source", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 28 [.ref, .ref, .ref] :=
  { obligationId := "relation.originates-from:forbidden:0"
    sourceKind := "definition"
    targetKind := "source"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transform") (.nil)))
    binders := [
      { name := "transform", sort := .ref, domain := "transformation-records", selectionRole := "Separate exact transformation/compilation/projection record joining this derived artifact to this source", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("derived", ⟨.ref, .source⟩), ("source", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 28 [.ref, .ref, .ref] :=
  { obligationId := "relation.originates-from:forbidden:0"
    sourceKind := "drift-assessment"
    targetKind := "source"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transform") (.nil)))
    binders := [
      { name := "transform", sort := .ref, domain := "transformation-records", selectionRole := "Separate exact transformation/compilation/projection record joining this derived artifact to this source", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("derived", ⟨.ref, .source⟩), ("source", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 28 [.ref, .ref, .ref] :=
  { obligationId := "relation.originates-from:forbidden:0"
    sourceKind := "feedback-record"
    targetKind := "source"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transform") (.nil)))
    binders := [
      { name := "transform", sort := .ref, domain := "transformation-records", selectionRole := "Separate exact transformation/compilation/projection record joining this derived artifact to this source", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("derived", ⟨.ref, .source⟩), ("source", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 28 [.ref, .ref, .ref] :=
  { obligationId := "relation.originates-from:forbidden:0"
    sourceKind := "finding"
    targetKind := "source"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transform") (.nil)))
    binders := [
      { name := "transform", sort := .ref, domain := "transformation-records", selectionRole := "Separate exact transformation/compilation/projection record joining this derived artifact to this source", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("derived", ⟨.ref, .source⟩), ("source", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_005 : Plan 28 [.ref, .ref, .ref] :=
  { obligationId := "relation.originates-from:forbidden:0"
    sourceKind := "operational-observation"
    targetKind := "source"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transform") (.nil)))
    binders := [
      { name := "transform", sort := .ref, domain := "transformation-records", selectionRole := "Separate exact transformation/compilation/projection record joining this derived artifact to this source", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("derived", ⟨.ref, .source⟩), ("source", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_006 : Plan 28 [.ref, .ref, .ref] :=
  { obligationId := "relation.originates-from:forbidden:0"
    sourceKind := "relation-kind"
    targetKind := "source"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transform") (.nil)))
    binders := [
      { name := "transform", sort := .ref, domain := "transformation-records", selectionRole := "Separate exact transformation/compilation/projection record joining this derived artifact to this source", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("derived", ⟨.ref, .source⟩), ("source", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 28 [.ref, .ref, .ref] :=
  { obligationId := "relation.originates-from:forbidden:1"
    sourceKind := "artifact-type"
    targetKind := "source"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "succession") (.nil)))
    binders := [
      { name := "succession", sort := .ref, domain := "succession-records", selectionRole := "Separate exact directional succession record; origin does not supply it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 28 [.ref, .ref, .ref] :=
  { obligationId := "relation.originates-from:forbidden:1"
    sourceKind := "definition"
    targetKind := "source"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "succession") (.nil)))
    binders := [
      { name := "succession", sort := .ref, domain := "succession-records", selectionRole := "Separate exact directional succession record; origin does not supply it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 28 [.ref, .ref, .ref] :=
  { obligationId := "relation.originates-from:forbidden:1"
    sourceKind := "drift-assessment"
    targetKind := "source"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "succession") (.nil)))
    binders := [
      { name := "succession", sort := .ref, domain := "succession-records", selectionRole := "Separate exact directional succession record; origin does not supply it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 28 [.ref, .ref, .ref] :=
  { obligationId := "relation.originates-from:forbidden:1"
    sourceKind := "feedback-record"
    targetKind := "source"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "succession") (.nil)))
    binders := [
      { name := "succession", sort := .ref, domain := "succession-records", selectionRole := "Separate exact directional succession record; origin does not supply it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 28 [.ref, .ref, .ref] :=
  { obligationId := "relation.originates-from:forbidden:1"
    sourceKind := "finding"
    targetKind := "source"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "succession") (.nil)))
    binders := [
      { name := "succession", sort := .ref, domain := "succession-records", selectionRole := "Separate exact directional succession record; origin does not supply it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_005 : Plan 28 [.ref, .ref, .ref] :=
  { obligationId := "relation.originates-from:forbidden:1"
    sourceKind := "operational-observation"
    targetKind := "source"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "succession") (.nil)))
    binders := [
      { name := "succession", sort := .ref, domain := "succession-records", selectionRole := "Separate exact directional succession record; origin does not supply it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_006 : Plan 28 [.ref, .ref, .ref] :=
  { obligationId := "relation.originates-from:forbidden:1"
    sourceKind := "relation-kind"
    targetKind := "source"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "succession") (.nil)))
    binders := [
      { name := "succession", sort := .ref, domain := "succession-records", selectionRole := "Separate exact directional succession record; origin does not supply it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("successor", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 28 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.originates-from:forbidden:2"
    sourceKind := "artifact-type"
    targetKind := "source"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 28 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.originates-from:forbidden:2"
    sourceKind := "definition"
    targetKind := "source"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 28 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.originates-from:forbidden:2"
    sourceKind := "drift-assessment"
    targetKind := "source"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 28 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.originates-from:forbidden:2"
    sourceKind := "feedback-record"
    targetKind := "source"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 28 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.originates-from:forbidden:2"
    sourceKind := "finding"
    targetKind := "source"
    branchIndex := 4
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_005 : Plan 28 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.originates-from:forbidden:2"
    sourceKind := "operational-observation"
    targetKind := "source"
    branchIndex := 5
    arguments := .cons (.target) (.cons (.source) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_006 : Plan 28 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.originates-from:forbidden:2"
    sourceKind := "relation-kind"
    targetKind := "source"
    branchIndex := 6
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
#print axioms plan_1_000
#print axioms plan_1_001
#print axioms plan_1_002
#print axioms plan_1_003
#print axioms plan_1_004
#print axioms plan_1_005
#print axioms plan_1_006
#print axioms plan_2_000
#print axioms plan_2_001
#print axioms plan_2_002
#print axioms plan_2_003
#print axioms plan_2_004
#print axioms plan_2_005
#print axioms plan_2_006
end CandidateConclusionAnchors.K28
