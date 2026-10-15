import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K00

def plan_0_000 : Plan 0 [.ref, .ref, .ref] :=
  { obligationId := "relation.acts-for:forbidden:0"
    sourceKind := "agent-instance"
    targetKind := "principal"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "identityModel") (.nil)))
    binders := [
      { name := "identityModel", sort := .ref, domain := "identity-models", selectionRole := "Independent governed identity interpretation for these exact endpoint participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 0 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.acts-for:forbidden:1"
    sourceKind := "agent-instance"
    targetKind := "principal"
    branchIndex := 0
    arguments := .cons (.variable "artifact") (.cons (.variable "beforeOwner") (.cons (.variable "afterOwner") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "artifact", sort := .ref, domain := "owned-artifacts", selectionRole := "An exact governed artifact in the represented Principal envelope", joins := [("principal", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "beforeOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact prior owner associated with this artifact and prior captured state", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .variable "artifact"⟩)] },
      { name := "afterOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact proposed/final owner associated with this artifact and transition context", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .variable "artifact"⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .variable "artifact"⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩), ("afterOwner", ⟨.ref, .variable "afterOwner"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 0 [.ref, .universe, .frame] :=
  { obligationId := "relation.acts-for:forbidden:2"
    sourceKind := "agent-instance"
    targetKind := "principal"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.frameField "ownedUniverse" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_1_000
#print axioms plan_2_000
end CandidateConclusionAnchors.K00
