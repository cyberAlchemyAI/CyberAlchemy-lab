import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K38

def plan_0_000 : Plan 38 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.uses-method:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "method"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 38 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.uses-method:forbidden:0"
    sourceKind := "experiment-run"
    targetKind := "method"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 38 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.uses-method:forbidden:0"
    sourceKind := "measurement-result"
    targetKind := "method"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 38 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.uses-method:forbidden:0"
    sourceKind := "observation"
    targetKind := "method"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 38 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.uses-method:forbidden:0"
    sourceKind := "product"
    targetKind := "method"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_005 : Plan 38 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.uses-method:forbidden:0"
    sourceKind := "project"
    targetKind := "method"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_006 : Plan 38 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.uses-method:forbidden:0"
    sourceKind := "research-run"
    targetKind := "method"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 38 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-method:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "method"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 38 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-method:forbidden:1"
    sourceKind := "experiment-run"
    targetKind := "method"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 38 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-method:forbidden:1"
    sourceKind := "measurement-result"
    targetKind := "method"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 38 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-method:forbidden:1"
    sourceKind := "observation"
    targetKind := "method"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 38 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-method:forbidden:1"
    sourceKind := "product"
    targetKind := "method"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_005 : Plan 38 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-method:forbidden:1"
    sourceKind := "project"
    targetKind := "method"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_006 : Plan 38 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-method:forbidden:1"
    sourceKind := "research-run"
    targetKind := "method"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 38 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-method:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "method"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "receipt") (.nil)))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("specification", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 38 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-method:forbidden:2"
    sourceKind := "experiment-run"
    targetKind := "method"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "receipt") (.nil)))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("specification", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 38 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-method:forbidden:2"
    sourceKind := "measurement-result"
    targetKind := "method"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "receipt") (.nil)))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("specification", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 38 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-method:forbidden:2"
    sourceKind := "observation"
    targetKind := "method"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "receipt") (.nil)))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("specification", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 38 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-method:forbidden:2"
    sourceKind := "product"
    targetKind := "method"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "receipt") (.nil)))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("specification", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_005 : Plan 38 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-method:forbidden:2"
    sourceKind := "project"
    targetKind := "method"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "receipt") (.nil)))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("specification", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_006 : Plan 38 [.ref, .ref, .ref] :=
  { obligationId := "relation.uses-method:forbidden:2"
    sourceKind := "research-run"
    targetKind := "method"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "receipt") (.nil)))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("specification", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 38 [.ref, .ref, .frame] :=
  { obligationId := "relation.uses-method:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "method"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 38 [.ref, .ref, .frame] :=
  { obligationId := "relation.uses-method:forbidden:3"
    sourceKind := "experiment-run"
    targetKind := "method"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_002 : Plan 38 [.ref, .ref, .frame] :=
  { obligationId := "relation.uses-method:forbidden:3"
    sourceKind := "measurement-result"
    targetKind := "method"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_003 : Plan 38 [.ref, .ref, .frame] :=
  { obligationId := "relation.uses-method:forbidden:3"
    sourceKind := "observation"
    targetKind := "method"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_004 : Plan 38 [.ref, .ref, .frame] :=
  { obligationId := "relation.uses-method:forbidden:3"
    sourceKind := "product"
    targetKind := "method"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_005 : Plan 38 [.ref, .ref, .frame] :=
  { obligationId := "relation.uses-method:forbidden:3"
    sourceKind := "project"
    targetKind := "method"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_006 : Plan 38 [.ref, .ref, .frame] :=
  { obligationId := "relation.uses-method:forbidden:3"
    sourceKind := "research-run"
    targetKind := "method"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.variable "objective") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "objective", sort := .ref, domain := "objective-definitions", selectionRole := "Exact independently owned outcome/objective of the named subject/operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_0_001
#print axioms plan_0_002
#print axioms plan_0_003
#print axioms plan_0_004
#print axioms plan_0_005
#print axioms plan_0_006
#print axioms plan_1_000
#print axioms plan_1_001
#print axioms plan_1_002
#print axioms plan_1_003
#print axioms plan_1_004
#print axioms plan_1_005
#print axioms plan_1_006
#print axioms plan_2_000
#print axioms plan_2_001
#print axioms plan_2_002
#print axioms plan_2_003
#print axioms plan_2_004
#print axioms plan_2_005
#print axioms plan_2_006
#print axioms plan_3_000
#print axioms plan_3_001
#print axioms plan_3_002
#print axioms plan_3_003
#print axioms plan_3_004
#print axioms plan_3_005
#print axioms plan_3_006
end CandidateConclusionAnchors.K38
