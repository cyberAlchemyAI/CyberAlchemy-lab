import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K05

def plan_0_000 : Plan 5 [.ref, .ref, .ref] :=
  { obligationId := "relation.asserts-identity-of:forbidden:0"
    sourceKind := "identity-claim"
    targetKind := "person-reference"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 5 [.ref, .ref, .ref] :=
  { obligationId := "relation.asserts-identity-of:forbidden:0"
    sourceKind := "person-reference"
    targetKind := "person"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 5 [.ref, .ref, .ref] :=
  { obligationId := "relation.asserts-identity-of:forbidden:0"
    sourceKind := "person-reference"
    targetKind := "person-reference"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 5 [.ref, .ref, .ref] :=
  { obligationId := "relation.asserts-identity-of:forbidden:0"
    sourceKind := "principal-reference"
    targetKind := "principal"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "transition") (.nil)))
    binders := [
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("source", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 5 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.asserts-identity-of:forbidden:1"
    sourceKind := "identity-claim"
    targetKind := "person-reference"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 5 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.asserts-identity-of:forbidden:1"
    sourceKind := "person-reference"
    targetKind := "person"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 5 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.asserts-identity-of:forbidden:1"
    sourceKind := "person-reference"
    targetKind := "person-reference"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 5 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.asserts-identity-of:forbidden:1"
    sourceKind := "principal-reference"
    targetKind := "principal"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 5 [.ref, .ref, .value, .ref] :=
  { obligationId := "relation.asserts-identity-of:forbidden:2"
    sourceKind := "identity-claim"
    targetKind := "person-reference"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "attribute") (.cons (.variable "value") (.cons (.variable "provenance") (.nil))))
    binders := [
      { name := "attribute", sort := .ref, domain := "private-attribute-definitions", selectionRole := "Exact private attribute definition concerning this correspondence target", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "value", sort := .value, domain := "typed-attribute-values", selectionRole := "Independently supplied typed value for that subject and attribute; assertion content alone does not establish it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("attribute", ⟨.ref, .variable "attribute"⟩)] },
      { name := "provenance", sort := .ref, domain := "provenance-records", selectionRole := "Exact independent provenance candidate for the selected subject/attribute/value", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("attribute", ⟨.ref, .variable "attribute"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 5 [.ref, .ref, .value, .ref] :=
  { obligationId := "relation.asserts-identity-of:forbidden:2"
    sourceKind := "person-reference"
    targetKind := "person"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.variable "attribute") (.cons (.variable "value") (.cons (.variable "provenance") (.nil))))
    binders := [
      { name := "attribute", sort := .ref, domain := "private-attribute-definitions", selectionRole := "Exact private attribute definition concerning this correspondence target", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "value", sort := .value, domain := "typed-attribute-values", selectionRole := "Independently supplied typed value for that subject and attribute; assertion content alone does not establish it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("attribute", ⟨.ref, .variable "attribute"⟩)] },
      { name := "provenance", sort := .ref, domain := "provenance-records", selectionRole := "Exact independent provenance candidate for the selected subject/attribute/value", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("attribute", ⟨.ref, .variable "attribute"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 5 [.ref, .ref, .value, .ref] :=
  { obligationId := "relation.asserts-identity-of:forbidden:2"
    sourceKind := "person-reference"
    targetKind := "person-reference"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.variable "attribute") (.cons (.variable "value") (.cons (.variable "provenance") (.nil))))
    binders := [
      { name := "attribute", sort := .ref, domain := "private-attribute-definitions", selectionRole := "Exact private attribute definition concerning this correspondence target", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "value", sort := .value, domain := "typed-attribute-values", selectionRole := "Independently supplied typed value for that subject and attribute; assertion content alone does not establish it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("attribute", ⟨.ref, .variable "attribute"⟩)] },
      { name := "provenance", sort := .ref, domain := "provenance-records", selectionRole := "Exact independent provenance candidate for the selected subject/attribute/value", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("attribute", ⟨.ref, .variable "attribute"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 5 [.ref, .ref, .value, .ref] :=
  { obligationId := "relation.asserts-identity-of:forbidden:2"
    sourceKind := "principal-reference"
    targetKind := "principal"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.variable "attribute") (.cons (.variable "value") (.cons (.variable "provenance") (.nil))))
    binders := [
      { name := "attribute", sort := .ref, domain := "private-attribute-definitions", selectionRole := "Exact private attribute definition concerning this correspondence target", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] },
      { name := "value", sort := .value, domain := "typed-attribute-values", selectionRole := "Independently supplied typed value for that subject and attribute; assertion content alone does not establish it", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("attribute", ⟨.ref, .variable "attribute"⟩)] },
      { name := "provenance", sort := .ref, domain := "provenance-records", selectionRole := "Exact independent provenance candidate for the selected subject/attribute/value", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩), ("attribute", ⟨.ref, .variable "attribute"⟩)] }
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
end CandidateConclusionAnchors.K05
