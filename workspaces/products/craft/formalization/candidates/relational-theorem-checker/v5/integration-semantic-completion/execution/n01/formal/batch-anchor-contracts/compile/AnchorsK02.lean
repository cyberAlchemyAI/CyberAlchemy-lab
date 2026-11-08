import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K02

def plan_0_000 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:0"
    sourceKind := "agent-assignment"
    targetKind := "intent"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "tests") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "tests", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete satisfaction-test set selected by this Intent Resolution; not a fabricated single test", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("tests", ⟨.ref, .variable "tests"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:0"
    sourceKind := "goal"
    targetKind := "intent"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.variable "tests") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "tests", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete satisfaction-test set selected by this Intent Resolution; not a fabricated single test", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("tests", ⟨.ref, .variable "tests"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:0"
    sourceKind := "product"
    targetKind := "intent"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.variable "tests") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "tests", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete satisfaction-test set selected by this Intent Resolution; not a fabricated single test", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("tests", ⟨.ref, .variable "tests"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:0"
    sourceKind := "product-capability"
    targetKind := "intent"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.variable "tests") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "tests", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete satisfaction-test set selected by this Intent Resolution; not a fabricated single test", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("tests", ⟨.ref, .variable "tests"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:0"
    sourceKind := "project"
    targetKind := "intent"
    branchIndex := 4
    arguments := .cons (.target) (.cons (.variable "tests") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "tests", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete satisfaction-test set selected by this Intent Resolution; not a fabricated single test", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("tests", ⟨.ref, .variable "tests"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_005 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:0"
    sourceKind := "research-inquiry"
    targetKind := "intent"
    branchIndex := 5
    arguments := .cons (.target) (.cons (.variable "tests") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "tests", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete satisfaction-test set selected by this Intent Resolution; not a fabricated single test", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("intent", ⟨.ref, .target⟩), ("tests", ⟨.ref, .variable "tests"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 2 [.ref, .ref, .frame] :=
  { obligationId := "relation.addresses-intent:forbidden:1"
    sourceKind := "agent-assignment"
    targetKind := "intent"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "requirements") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "requirements", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete owned work requirements for this selected work subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("work", ⟨.ref, .source⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 2 [.ref, .ref, .frame] :=
  { obligationId := "relation.addresses-intent:forbidden:1"
    sourceKind := "goal"
    targetKind := "intent"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "requirements") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "requirements", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete owned work requirements for this selected work subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("work", ⟨.ref, .source⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 2 [.ref, .ref, .frame] :=
  { obligationId := "relation.addresses-intent:forbidden:1"
    sourceKind := "product"
    targetKind := "intent"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "requirements") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "requirements", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete owned work requirements for this selected work subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("work", ⟨.ref, .source⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 2 [.ref, .ref, .frame] :=
  { obligationId := "relation.addresses-intent:forbidden:1"
    sourceKind := "product-capability"
    targetKind := "intent"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.variable "requirements") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "requirements", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete owned work requirements for this selected work subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("work", ⟨.ref, .source⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 2 [.ref, .ref, .frame] :=
  { obligationId := "relation.addresses-intent:forbidden:1"
    sourceKind := "project"
    targetKind := "intent"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.variable "requirements") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "requirements", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete owned work requirements for this selected work subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("work", ⟨.ref, .source⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_005 : Plan 2 [.ref, .ref, .frame] :=
  { obligationId := "relation.addresses-intent:forbidden:1"
    sourceKind := "research-inquiry"
    targetKind := "intent"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.variable "requirements") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "requirements", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete owned work requirements for this selected work subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("work", ⟨.ref, .source⟩), ("intentResolution", ⟨.ref, .witnessField "resolution" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 2 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.addresses-intent:forbidden:2"
    sourceKind := "agent-assignment"
    targetKind := "intent"
    branchIndex := 0
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 2 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.addresses-intent:forbidden:2"
    sourceKind := "goal"
    targetKind := "intent"
    branchIndex := 1
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 2 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.addresses-intent:forbidden:2"
    sourceKind := "product"
    targetKind := "intent"
    branchIndex := 2
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 2 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.addresses-intent:forbidden:2"
    sourceKind := "product-capability"
    targetKind := "intent"
    branchIndex := 3
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 2 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.addresses-intent:forbidden:2"
    sourceKind := "project"
    targetKind := "intent"
    branchIndex := 4
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_005 : Plan 2 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.addresses-intent:forbidden:2"
    sourceKind := "research-inquiry"
    targetKind := "intent"
    branchIndex := 5
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:3"
    sourceKind := "agent-assignment"
    targetKind := "intent"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "container") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "container", sort := .ref, domain := "membership-targets", selectionRole := "Exact independently declared container associated with this subject; an Intent or Goal is not silently made a container", joins := [("member", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .variable "container"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:3"
    sourceKind := "goal"
    targetKind := "intent"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "container") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "container", sort := .ref, domain := "membership-targets", selectionRole := "Exact independently declared container associated with this subject; an Intent or Goal is not silently made a container", joins := [("member", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .variable "container"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_002 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:3"
    sourceKind := "product"
    targetKind := "intent"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "container") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "container", sort := .ref, domain := "membership-targets", selectionRole := "Exact independently declared container associated with this subject; an Intent or Goal is not silently made a container", joins := [("member", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .variable "container"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_003 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:3"
    sourceKind := "product-capability"
    targetKind := "intent"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.variable "container") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "container", sort := .ref, domain := "membership-targets", selectionRole := "Exact independently declared container associated with this subject; an Intent or Goal is not silently made a container", joins := [("member", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .variable "container"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_004 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:3"
    sourceKind := "project"
    targetKind := "intent"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.variable "container") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "container", sort := .ref, domain := "membership-targets", selectionRole := "Exact independently declared container associated with this subject; an Intent or Goal is not silently made a container", joins := [("member", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .variable "container"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_005 : Plan 2 [.ref, .ref, .ref] :=
  { obligationId := "relation.addresses-intent:forbidden:3"
    sourceKind := "research-inquiry"
    targetKind := "intent"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.variable "container") (.cons (.variable "record") (.nil)))
    binders := [
      { name := "container", sort := .ref, domain := "membership-targets", selectionRole := "Exact independently declared container associated with this subject; an Intent or Goal is not silently made a container", joins := [("member", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "record", sort := .ref, domain := "relation-records", selectionRole := "Separate independently supplied record for this named conclusion relationship", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("member", ⟨.ref, .source⟩), ("container", ⟨.ref, .variable "container"⟩)] }
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
end CandidateConclusionAnchors.K02
