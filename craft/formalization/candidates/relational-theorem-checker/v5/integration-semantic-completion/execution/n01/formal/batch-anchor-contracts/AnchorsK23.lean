import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K23

def plan_0_000 : Plan 23 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.inherits-contract:forbidden:0"
    sourceKind := "capability-instance"
    targetKind := "contract"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "beforeOwner") (.cons (.variable "afterOwner") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "beforeOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact prior owner associated with this artifact and prior captured state", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩)] },
      { name := "afterOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact proposed/final owner associated with this artifact and transition context", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩), ("afterOwner", ⟨.ref, .variable "afterOwner"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 23 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.inherits-contract:forbidden:1"
    sourceKind := "capability-instance"
    targetKind := "contract"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 23 [.ref, .ref, .ref] :=
  { obligationId := "relation.inherits-contract:forbidden:2"
    sourceKind := "capability-instance"
    targetKind := "contract"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "adopter") (.cons (.variable "policy") (.nil)))
    binders := [
      { name := "adopter", sort := .ref, domain := "accountable-participants", selectionRole := "Exact independently governed adopter for this endpoint", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩)] },
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .source⟩), ("adopter", ⟨.ref, .variable "adopter"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_1_000
#print axioms plan_2_000
end CandidateConclusionAnchors.K23
