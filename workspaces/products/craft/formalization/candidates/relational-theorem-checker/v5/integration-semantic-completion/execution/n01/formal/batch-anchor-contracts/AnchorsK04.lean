import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K04

def plan_0_000 : Plan 4 [.ref, .ref, .frame] :=
  { obligationId := "relation.applies-lesson:forbidden:0"
    sourceKind := "lesson-application"
    targetKind := "operational-lesson"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "instruction") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "instruction", sort := .ref, domain := "instruction-origins", selectionRole := "Exact applicable instruction origin for this lesson application, retaining precedence and conflicts", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("application", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 4 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.applies-lesson:forbidden:1"
    sourceKind := "lesson-application"
    targetKind := "operational-lesson"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "metric") (.cons (.variable "baseline") (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "metric", sort := .ref, domain := "metric-definitions", selectionRole := "Exact independently owned outcome/benefit/improvement metric for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("application", ⟨.ref, .source⟩)] },
      { name := "baseline", sort := .ref, domain := "measurement-snapshots", selectionRole := "Exact independently owned comparison baseline for this lesson application and metric", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("application", ⟨.ref, .source⟩), ("metric", ⟨.ref, .variable "metric"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 4 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.applies-lesson:forbidden:2"
    sourceKind := "lesson-application"
    targetKind := "operational-lesson"
    branchIndex := 0
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .witnessField "sessionOrAction" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .witnessField "sessionOrAction" (by decide)⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 4 [.ref, .ref, .ref] :=
  { obligationId := "relation.applies-lesson:forbidden:3"
    sourceKind := "lesson-application"
    targetKind := "operational-lesson"
    branchIndex := 0
    arguments := .cons (.witnessField "sessionOrAction" (by decide)) (.cons (.variable "method") (.cons (.variable "useRecord") (.nil)))
    binders := [
      { name := "method", sort := .ref, domain := "method-targets", selectionRole := "Exact Method specification independently employed by this session/action; the lesson is not substituted for it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .witnessField "sessionOrAction" (by decide)⟩)] },
      { name := "useRecord", sort := .ref, domain := "method-use-records", selectionRole := "Separate exact method-employment record joining subject and method", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .witnessField "sessionOrAction" (by decide)⟩), ("method", ⟨.ref, .variable "method"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_1_000
#print axioms plan_2_000
#print axioms plan_3_000
end CandidateConclusionAnchors.K04
