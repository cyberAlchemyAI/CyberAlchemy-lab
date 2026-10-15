import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K31

def plan_0_000 : Plan 31 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.profiled-by:forbidden:0"
    sourceKind := "agent-instance"
    targetKind := "agent-profile"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 31 [.ref, .ref, .ref] :=
  { obligationId := "relation.profiled-by:forbidden:1"
    sourceKind := "agent-instance"
    targetKind := "agent-profile"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "capability") (.cons (.variable "basis") (.nil)))
    binders := [
      { name := "capability", sort := .ref, domain := "capability-declarations", selectionRole := "Exact independently declared Agent Capability for this configured instance", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("agent", ⟨.ref, .source⟩)] },
      { name := "basis", sort := .ref, domain := "capability-declaration-bases", selectionRole := "Exact separate owned declaration basis joining agent and capability", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("agent", ⟨.ref, .source⟩), ("capability", ⟨.ref, .variable "capability"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 31 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.profiled-by:forbidden:2"
    sourceKind := "agent-instance"
    targetKind := "agent-profile"
    branchIndex := 0
    arguments := .cons (.variable "holder") (.cons (.variable "action") (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
      { name := "holder", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "action", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 31 [.ref, .ref, .ref] :=
  { obligationId := "relation.profiled-by:forbidden:3"
    sourceKind := "agent-instance"
    targetKind := "agent-profile"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "predecessor") (.cons (.variable "continuityRecord") (.nil)))
    binders := [
      { name := "predecessor", sort := .ref, domain := "identity-continuity-participants", selectionRole := "Exact prior instance identity under an independently governed continuity interpretation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("instance", ⟨.ref, .source⟩)] },
      { name := "continuityRecord", sort := .ref, domain := "identity-continuity-records", selectionRole := "Separate exact identity-continuity record; configuring a profile does not supply it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("instance", ⟨.ref, .source⟩), ("predecessor", ⟨.ref, .variable "predecessor"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_1_000
#print axioms plan_2_000
#print axioms plan_3_000
end CandidateConclusionAnchors.K31
