import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K10

def plan_0_000 : Plan 10 [.ref, .ref, .ref] :=
  { obligationId := "relation.conforms-to:forbidden:0"
    sourceKind := "capability-instance"
    targetKind := "contract"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 10 [.ref, .ref, .ref] :=
  { obligationId := "relation.conforms-to:forbidden:0"
    sourceKind := "capability-instance"
    targetKind := "governed-model"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 10 [.ref, .ref, .ref] :=
  { obligationId := "relation.conforms-to:forbidden:0"
    sourceKind := "context"
    targetKind := "context-profile"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 10 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.conforms-to:forbidden:1"
    sourceKind := "capability-instance"
    targetKind := "contract"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "execution") (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("contract", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 10 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.conforms-to:forbidden:1"
    sourceKind := "capability-instance"
    targetKind := "governed-model"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "contract") (.cons (.variable "execution") (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "contract", sort := .ref, domain := "runtime-contracts", selectionRole := "Exact independently owned live-runtime contract associated with the conformance subject/target", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("contract", ⟨.ref, .variable "contract"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 10 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.conforms-to:forbidden:1"
    sourceKind := "context"
    targetKind := "context-profile"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "contract") (.cons (.variable "execution") (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "contract", sort := .ref, domain := "runtime-contracts", selectionRole := "Exact independently owned live-runtime contract associated with the conformance subject/target", joins := [("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("contract", ⟨.ref, .variable "contract"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 10 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.conforms-to:forbidden:2"
    sourceKind := "capability-instance"
    targetKind := "contract"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.variable "metric") (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩)] },
      { name := "metric", sort := .ref, domain := "metric-definitions", selectionRole := "Exact independently owned outcome/benefit/improvement metric for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("objective", ⟨.ref, .variable "objective"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 10 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.conforms-to:forbidden:2"
    sourceKind := "capability-instance"
    targetKind := "governed-model"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.variable "metric") (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩)] },
      { name := "metric", sort := .ref, domain := "metric-definitions", selectionRole := "Exact independently owned outcome/benefit/improvement metric for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("objective", ⟨.ref, .variable "objective"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 10 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.conforms-to:forbidden:2"
    sourceKind := "context"
    targetKind := "context-profile"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.variable "metric") (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩)] },
      { name := "metric", sort := .ref, domain := "metric-definitions", selectionRole := "Exact independently owned outcome/benefit/improvement metric for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("objective", ⟨.ref, .variable "objective"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 10 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.conforms-to:forbidden:3"
    sourceKind := "capability-instance"
    targetKind := "contract"
    branchIndex := 0
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 10 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.conforms-to:forbidden:3"
    sourceKind := "capability-instance"
    targetKind := "governed-model"
    branchIndex := 1
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_002 : Plan 10 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.conforms-to:forbidden:3"
    sourceKind := "context"
    targetKind := "context-profile"
    branchIndex := 2
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
#print axioms plan_1_000
#print axioms plan_1_001
#print axioms plan_1_002
#print axioms plan_2_000
#print axioms plan_2_001
#print axioms plan_2_002
#print axioms plan_3_000
#print axioms plan_3_001
#print axioms plan_3_002
end CandidateConclusionAnchors.K10
