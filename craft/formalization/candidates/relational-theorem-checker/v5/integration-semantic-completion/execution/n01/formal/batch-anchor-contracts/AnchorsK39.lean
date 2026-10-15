import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K39

def plan_0_000 : Plan 39 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-tool:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "implementation"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 39 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-tool:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "tool"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 39 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-tool:forbidden:0"
    sourceKind := "agent-session"
    targetKind := "implementation"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 39 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-tool:forbidden:0"
    sourceKind := "agent-session"
    targetKind := "tool"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 39 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.uses-tool:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "implementation"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 39 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.uses-tool:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "tool"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 39 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.uses-tool:forbidden:1"
    sourceKind := "agent-session"
    targetKind := "implementation"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 39 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.uses-tool:forbidden:1"
    sourceKind := "agent-session"
    targetKind := "tool"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 39 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-tool:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "implementation"
    branchIndex := 0
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 39 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-tool:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "tool"
    branchIndex := 1
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 39 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-tool:forbidden:2"
    sourceKind := "agent-session"
    targetKind := "implementation"
    branchIndex := 2
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 39 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-tool:forbidden:2"
    sourceKind := "agent-session"
    targetKind := "tool"
    branchIndex := 3
    arguments := .cons (.variable "owner") (.cons (.target) (.cons (.variable "record") (.nil)))
    binders := [
      { name := "owner", sort := .ref, domain := "ownership-participants", selectionRole := "Independently identified candidate owner of the affected/used artifact; no transfer or owner equivalence is inferred", joins := [("artifact", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("owner", ⟨.ref, .variable "owner"⟩), ("artifact", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 39 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.uses-tool:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "implementation"
    branchIndex := 0
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 39 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.uses-tool:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "tool"
    branchIndex := 1
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_002 : Plan 39 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.uses-tool:forbidden:3"
    sourceKind := "agent-session"
    targetKind := "implementation"
    branchIndex := 2
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_003 : Plan 39 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.uses-tool:forbidden:3"
    sourceKind := "agent-session"
    targetKind := "tool"
    branchIndex := 3
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
end CandidateConclusionAnchors.K39
