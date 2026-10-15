import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K01

def plan_0_000 : Plan 1 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-improvement-target:forbidden:0"
    sourceKind := "research-inquiry"
    targetKind := "improvement-target"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "resolution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "resolution", sort := .ref, domain := "resolution-records", selectionRole := "Completed resolution candidate for this exact target under its owned criteria", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("resolution", ⟨.ref, .variable "resolution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 1 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.addresses-improvement-target:forbidden:1"
    sourceKind := "research-inquiry"
    targetKind := "improvement-target"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "before") (.cons (.variable "after") (.cons (.variable "metric") (.nil))))
    binders := [
      { name := "before", sort := .ref, domain := "measurement-snapshots", selectionRole := "Exact baseline observation/state revision for this target under the selected metric policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "after", sort := .ref, domain := "measurement-snapshots", selectionRole := "Exact comparison observation/state revision for this same target under that metric policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("before", ⟨.ref, .variable "before"⟩)] },
      { name := "metric", sort := .ref, domain := "metric-definitions", selectionRole := "Exact independently owned outcome/benefit/improvement metric for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("before", ⟨.ref, .variable "before"⟩), ("after", ⟨.ref, .variable "after"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 1 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-improvement-target:forbidden:2"
    sourceKind := "research-inquiry"
    targetKind := "improvement-target"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "queue") (.cons (.variable "orderingPolicy") (.nil)))
    binders := [
      { name := "queue", sort := .ref, domain := "work-queues", selectionRole := "Exact owned work queue containing this target", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "orderingPolicy", sort := .ref, domain := "ordering-policies", selectionRole := "Exact owned ordering policy for the selected queue/target", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("queue", ⟨.ref, .variable "queue"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 1 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.addresses-improvement-target:forbidden:3"
    sourceKind := "research-inquiry"
    targetKind := "improvement-target"
    branchIndex := 0
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_1_000
#print axioms plan_2_000
#print axioms plan_3_000
end CandidateConclusionAnchors.K01
