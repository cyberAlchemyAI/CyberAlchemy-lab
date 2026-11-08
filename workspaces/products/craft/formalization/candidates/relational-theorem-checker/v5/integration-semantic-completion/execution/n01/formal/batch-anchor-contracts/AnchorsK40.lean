import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K40

def plan_0_000 : Plan 40 [.ref, .ref, .ref] :=
  { obligationId := "relation.violates:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "challenge-contract"
    branchIndex := 0
    arguments := .cons (.variable "cause") (.cons (.source) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "cause", sort := .ref, domain := "causal-participants", selectionRole := "Exact independently specified candidate cause of this occurrence/incident; no cause follows from timing or response intention", joins := [("outcome", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .variable "cause"⟩), ("outcome", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 40 [.ref, .ref, .ref] :=
  { obligationId := "relation.violates:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "contract"
    branchIndex := 1
    arguments := .cons (.variable "cause") (.cons (.source) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "cause", sort := .ref, domain := "causal-participants", selectionRole := "Exact independently specified candidate cause of this occurrence/incident; no cause follows from timing or response intention", joins := [("outcome", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .variable "cause"⟩), ("outcome", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 40 [.ref, .ref, .ref] :=
  { obligationId := "relation.violates:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "policy"
    branchIndex := 2
    arguments := .cons (.variable "cause") (.cons (.source) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "cause", sort := .ref, domain := "causal-participants", selectionRole := "Exact independently specified candidate cause of this occurrence/incident; no cause follows from timing or response intention", joins := [("outcome", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .variable "cause"⟩), ("outcome", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 40 [.ref, .ref, .ref] :=
  { obligationId := "relation.violates:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "schema"
    branchIndex := 3
    arguments := .cons (.variable "cause") (.cons (.source) (.cons (.variable "causalModel") (.nil)))
    binders := [
      { name := "cause", sort := .ref, domain := "causal-participants", selectionRole := "Exact independently specified candidate cause of this occurrence/incident; no cause follows from timing or response intention", joins := [("outcome", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "causalModel", sort := .ref, domain := "causal-models", selectionRole := "Exact independently owned causal interpretation joining the candidate cause and outcome", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("cause", ⟨.ref, .variable "cause"⟩), ("outcome", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 40 [.ref, .ref, .ref] :=
  { obligationId := "relation.violates:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "challenge-contract"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 40 [.ref, .ref, .ref] :=
  { obligationId := "relation.violates:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "contract"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 40 [.ref, .ref, .ref] :=
  { obligationId := "relation.violates:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "policy"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 40 [.ref, .ref, .ref] :=
  { obligationId := "relation.violates:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "schema"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.variable "severityPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "severityPolicy", sort := .ref, domain := "severity-policies", selectionRole := "Exact independently owned severity grading policy for this occurrence/incident", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("severityPolicy", ⟨.ref, .variable "severityPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 40 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.violates:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "challenge-contract"
    branchIndex := 0
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 40 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.violates:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "contract"
    branchIndex := 1
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 40 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.violates:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "policy"
    branchIndex := 2
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 40 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.violates:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "schema"
    branchIndex := 3
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 40 [.ref, .ref, .ref] :=
  { obligationId := "relation.violates:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "challenge-contract"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "mode") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "mode", sort := .ref, domain := "failure-mode-targets", selectionRole := "Exact independently assessed Failure Mode of this occurrence; boundary failure does not confirm it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("mode", ⟨.ref, .variable "mode"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 40 [.ref, .ref, .ref] :=
  { obligationId := "relation.violates:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "contract"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "mode") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "mode", sort := .ref, domain := "failure-mode-targets", selectionRole := "Exact independently assessed Failure Mode of this occurrence; boundary failure does not confirm it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("mode", ⟨.ref, .variable "mode"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_002 : Plan 40 [.ref, .ref, .ref] :=
  { obligationId := "relation.violates:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "policy"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "mode") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "mode", sort := .ref, domain := "failure-mode-targets", selectionRole := "Exact independently assessed Failure Mode of this occurrence; boundary failure does not confirm it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("mode", ⟨.ref, .variable "mode"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_003 : Plan 40 [.ref, .ref, .ref] :=
  { obligationId := "relation.violates:forbidden:3"
    sourceKind := "failure-occurrence"
    targetKind := "schema"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.variable "mode") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "mode", sort := .ref, domain := "failure-mode-targets", selectionRole := "Exact independently assessed Failure Mode of this occurrence; boundary failure does not confirm it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("occurrence", ⟨.ref, .source⟩), ("mode", ⟨.ref, .variable "mode"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_0_001
#print axioms plan_0_002
#print axioms plan_0_003
#print axioms plan_1_000
#print axioms plan_1_001
#print axioms plan_1_002
#print axioms plan_1_003
#print axioms plan_2_000
#print axioms plan_2_001
#print axioms plan_2_002
#print axioms plan_2_003
#print axioms plan_3_000
#print axioms plan_3_001
#print axioms plan_3_002
#print axioms plan_3_003
end CandidateConclusionAnchors.K40
