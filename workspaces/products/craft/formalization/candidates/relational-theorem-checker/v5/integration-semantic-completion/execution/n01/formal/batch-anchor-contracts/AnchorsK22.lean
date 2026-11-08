import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K22

def plan_0_000 : Plan 22 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.has-capability:forbidden:0"
    sourceKind := "agent-instance"
    targetKind := "agent-capability"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 22 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.has-capability:forbidden:0"
    sourceKind := "agent-profile"
    targetKind := "agent-capability"
    branchIndex := 1
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 22 [.ref, .ref, .ref] :=
  { obligationId := "relation.has-capability:forbidden:1"
    sourceKind := "agent-instance"
    targetKind := "agent-capability"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("agent", ⟨.ref, .source⟩), ("capability", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 22 [.ref, .ref, .ref] :=
  { obligationId := "relation.has-capability:forbidden:1"
    sourceKind := "agent-profile"
    targetKind := "agent-capability"
    branchIndex := 1
    arguments := .cons (.variable "agent") (.cons (.target) (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "agent", sort := .ref, domain := "profile-instances", selectionRole := "Exact Agent Instance independently configured by this Agent Profile; a profile is not relabeled as its performing instance", joins := [("profile", ⟨.ref, .source⟩), ("capability", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("agent", ⟨.ref, .variable "agent"⟩), ("capability", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 22 [.ref, .ref, .ref] :=
  { obligationId := "relation.has-capability:forbidden:2"
    sourceKind := "agent-instance"
    targetKind := "agent-capability"
    branchIndex := 0
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 22 [.ref, .ref, .ref] :=
  { obligationId := "relation.has-capability:forbidden:2"
    sourceKind := "agent-profile"
    targetKind := "agent-capability"
    branchIndex := 1
    arguments := .cons (.variable "product") (.cons (.variable "valuationPolicy") (.cons (.variable "assessment") (.nil)))
    binders := [
      { name := "product", sort := .ref, domain := "product-associations", selectionRole := "Exact independently associated Product; capability, thesis and goal are not relabeled as a Product", joins := [("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "valuationPolicy", sort := .ref, domain := "valuation-policies", selectionRole := "Exact owned Product valuation metric/baseline policy", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩)] },
      { name := "assessment", sort := .ref, domain := "assessment-candidates", selectionRole := "Exact independently captured assessment candidate concerning these participants; outcome/admissibility remain separate predicates", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("product", ⟨.ref, .variable "product"⟩), ("valuationPolicy", ⟨.ref, .variable "valuationPolicy"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_0_001
#print axioms plan_1_000
#print axioms plan_1_001
#print axioms plan_2_000
#print axioms plan_2_001
end CandidateConclusionAnchors.K22
