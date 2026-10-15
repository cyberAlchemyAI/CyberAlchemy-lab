import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K06

def plan_0_000 : Plan 6 [.ref, .ref, .ref] :=
  { obligationId := "relation.assigned-to:forbidden:0"
    sourceKind := "agent-instance"
    targetKind := "responsibility"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "team") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "team", sort := .ref, domain := "team-membership-targets", selectionRole := "Exact Team independently associated with this assignee; assignment does not add membership", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .source⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .source⟩), ("team", ⟨.ref, .variable "team"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 6 [.ref, .ref, .ref] :=
  { obligationId := "relation.assigned-to:forbidden:0"
    sourceKind := "agent-instance"
    targetKind := "role"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "team") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "team", sort := .ref, domain := "team-membership-targets", selectionRole := "Exact Team independently associated with this assignee; assignment does not add membership", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .source⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .source⟩), ("team", ⟨.ref, .variable "team"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 6 [.ref, .ref, .ref] :=
  { obligationId := "relation.assigned-to:forbidden:0"
    sourceKind := "person-reference"
    targetKind := "responsibility"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "team") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "team", sort := .ref, domain := "team-membership-targets", selectionRole := "Exact Team independently associated with this assignee; assignment does not add membership", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .source⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .source⟩), ("team", ⟨.ref, .variable "team"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 6 [.ref, .ref, .ref] :=
  { obligationId := "relation.assigned-to:forbidden:0"
    sourceKind := "person-reference"
    targetKind := "role"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.variable "team") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "team", sort := .ref, domain := "team-membership-targets", selectionRole := "Exact Team independently associated with this assignee; assignment does not add membership", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .source⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .source⟩), ("team", ⟨.ref, .variable "team"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 6 [.ref, .ref, .ref] :=
  { obligationId := "relation.assigned-to:forbidden:0"
    sourceKind := "team"
    targetKind := "responsibility"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.variable "team") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "team", sort := .ref, domain := "team-membership-targets", selectionRole := "Exact Team independently associated with this assignee; assignment does not add membership", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .source⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .source⟩), ("team", ⟨.ref, .variable "team"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_005 : Plan 6 [.ref, .ref, .ref] :=
  { obligationId := "relation.assigned-to:forbidden:0"
    sourceKind := "team"
    targetKind := "role"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.variable "team") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "team", sort := .ref, domain := "team-membership-targets", selectionRole := "Exact Team independently associated with this assignee; assignment does not add membership", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .source⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("assignee", ⟨.ref, .source⟩), ("team", ⟨.ref, .variable "team"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 6 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.assigned-to:forbidden:1"
    sourceKind := "agent-instance"
    targetKind := "responsibility"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 6 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.assigned-to:forbidden:1"
    sourceKind := "agent-instance"
    targetKind := "role"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 6 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.assigned-to:forbidden:1"
    sourceKind := "person-reference"
    targetKind := "responsibility"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 6 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.assigned-to:forbidden:1"
    sourceKind := "person-reference"
    targetKind := "role"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 6 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.assigned-to:forbidden:1"
    sourceKind := "team"
    targetKind := "responsibility"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_005 : Plan 6 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.assigned-to:forbidden:1"
    sourceKind := "team"
    targetKind := "role"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 6 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.assigned-to:forbidden:2"
    sourceKind := "agent-instance"
    targetKind := "responsibility"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 6 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.assigned-to:forbidden:2"
    sourceKind := "agent-instance"
    targetKind := "role"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 6 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.assigned-to:forbidden:2"
    sourceKind := "person-reference"
    targetKind := "responsibility"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 6 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.assigned-to:forbidden:2"
    sourceKind := "person-reference"
    targetKind := "role"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 6 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.assigned-to:forbidden:2"
    sourceKind := "team"
    targetKind := "responsibility"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_005 : Plan 6 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.assigned-to:forbidden:2"
    sourceKind := "team"
    targetKind := "role"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 6 [.ref, .ref, .ref] :=
  { obligationId := "relation.assigned-to:forbidden:3"
    sourceKind := "agent-instance"
    targetKind := "responsibility"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 6 [.ref, .ref, .ref] :=
  { obligationId := "relation.assigned-to:forbidden:3"
    sourceKind := "agent-instance"
    targetKind := "role"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_002 : Plan 6 [.ref, .ref, .ref] :=
  { obligationId := "relation.assigned-to:forbidden:3"
    sourceKind := "person-reference"
    targetKind := "responsibility"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_003 : Plan 6 [.ref, .ref, .ref] :=
  { obligationId := "relation.assigned-to:forbidden:3"
    sourceKind := "person-reference"
    targetKind := "role"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_004 : Plan 6 [.ref, .ref, .ref] :=
  { obligationId := "relation.assigned-to:forbidden:3"
    sourceKind := "team"
    targetKind := "responsibility"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_005 : Plan 6 [.ref, .ref, .ref] :=
  { obligationId := "relation.assigned-to:forbidden:3"
    sourceKind := "team"
    targetKind := "role"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_0_001
#print axioms plan_0_002
#print axioms plan_0_003
#print axioms plan_0_004
#print axioms plan_0_005
#print axioms plan_1_000
#print axioms plan_1_001
#print axioms plan_1_002
#print axioms plan_1_003
#print axioms plan_1_004
#print axioms plan_1_005
#print axioms plan_2_000
#print axioms plan_2_001
#print axioms plan_2_002
#print axioms plan_2_003
#print axioms plan_2_004
#print axioms plan_2_005
#print axioms plan_3_000
#print axioms plan_3_001
#print axioms plan_3_002
#print axioms plan_3_003
#print axioms plan_3_004
#print axioms plan_3_005
end CandidateConclusionAnchors.K06
