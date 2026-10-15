import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K24

def plan_0_000 : Plan 24 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.instance-of:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "classification-value"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 24 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.instance-of:forbidden:0"
    sourceKind := "agent-instance"
    targetKind := "classification-value"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 24 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.instance-of:forbidden:0"
    sourceKind := "capability-instance"
    targetKind := "governed-model"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 24 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.instance-of:forbidden:0"
    sourceKind := "capability-instance"
    targetKind := "product-capability"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 24 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.instance-of:forbidden:0"
    sourceKind := "failure-mode"
    targetKind := "classification-value"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_005 : Plan 24 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.instance-of:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "classification-value"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_006 : Plan 24 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.instance-of:forbidden:0"
    sourceKind := "failure-occurrence"
    targetKind := "failure-mode"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_007 : Plan 24 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.instance-of:forbidden:0"
    sourceKind := "implementation"
    targetKind := "governed-model"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_008 : Plan 24 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.instance-of:forbidden:0"
    sourceKind := "implementation"
    targetKind := "product-capability"
    branchIndex := 8
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_009 : Plan 24 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.instance-of:forbidden:0"
    sourceKind := "improvement-target"
    targetKind := "classification-value"
    branchIndex := 9
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_010 : Plan 24 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.instance-of:forbidden:0"
    sourceKind := "operational-lesson"
    targetKind := "classification-value"
    branchIndex := 10
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_011 : Plan 24 [.ref, .ref, .ref, .frame] :=
  { obligationId := "relation.instance-of:forbidden:0"
    sourceKind := "product-capability"
    targetKind := "product"
    branchIndex := 11
    arguments := .cons (.source) (.cons (.target) (.cons (.frameField "scope" (by decide)) (.cons (.frameField "frame" (by decide)) (.nil))))
    binders := [
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 24 [.ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "classification-value"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 24 [.ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:1"
    sourceKind := "agent-instance"
    targetKind := "classification-value"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 24 [.ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:1"
    sourceKind := "capability-instance"
    targetKind := "governed-model"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 24 [.ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:1"
    sourceKind := "capability-instance"
    targetKind := "product-capability"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 24 [.ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:1"
    sourceKind := "failure-mode"
    targetKind := "classification-value"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_005 : Plan 24 [.ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "classification-value"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_006 : Plan 24 [.ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:1"
    sourceKind := "failure-occurrence"
    targetKind := "failure-mode"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_007 : Plan 24 [.ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:1"
    sourceKind := "implementation"
    targetKind := "governed-model"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_008 : Plan 24 [.ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:1"
    sourceKind := "implementation"
    targetKind := "product-capability"
    branchIndex := 8
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_009 : Plan 24 [.ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:1"
    sourceKind := "improvement-target"
    targetKind := "classification-value"
    branchIndex := 9
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_010 : Plan 24 [.ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:1"
    sourceKind := "operational-lesson"
    targetKind := "classification-value"
    branchIndex := 10
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_011 : Plan 24 [.ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:1"
    sourceKind := "product-capability"
    targetKind := "product"
    branchIndex := 11
    arguments := .cons (.source) (.cons (.target) (.cons (.variable "witness") (.nil)))
    binders := [
      { name := "witness", sort := .ref, domain := "realization-witnesses", selectionRole := "Independent exact instantiation/execution witness for these realization participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 24 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "classification-value"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "beforeOwner") (.cons (.variable "afterOwner") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "beforeOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact prior owner associated with this artifact and prior captured state", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩)] },
      { name := "afterOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact proposed/final owner associated with this artifact and transition context", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩), ("afterOwner", ⟨.ref, .variable "afterOwner"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 24 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:2"
    sourceKind := "agent-instance"
    targetKind := "classification-value"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "beforeOwner") (.cons (.variable "afterOwner") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "beforeOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact prior owner associated with this artifact and prior captured state", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩)] },
      { name := "afterOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact proposed/final owner associated with this artifact and transition context", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩), ("afterOwner", ⟨.ref, .variable "afterOwner"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 24 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:2"
    sourceKind := "capability-instance"
    targetKind := "governed-model"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "beforeOwner") (.cons (.variable "afterOwner") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "beforeOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact prior owner associated with this artifact and prior captured state", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩)] },
      { name := "afterOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact proposed/final owner associated with this artifact and transition context", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩), ("afterOwner", ⟨.ref, .variable "afterOwner"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 24 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:2"
    sourceKind := "capability-instance"
    targetKind := "product-capability"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.variable "beforeOwner") (.cons (.variable "afterOwner") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "beforeOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact prior owner associated with this artifact and prior captured state", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩)] },
      { name := "afterOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact proposed/final owner associated with this artifact and transition context", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩), ("afterOwner", ⟨.ref, .variable "afterOwner"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 24 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:2"
    sourceKind := "failure-mode"
    targetKind := "classification-value"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.variable "beforeOwner") (.cons (.variable "afterOwner") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "beforeOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact prior owner associated with this artifact and prior captured state", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩)] },
      { name := "afterOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact proposed/final owner associated with this artifact and transition context", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩), ("afterOwner", ⟨.ref, .variable "afterOwner"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_005 : Plan 24 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "classification-value"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.variable "beforeOwner") (.cons (.variable "afterOwner") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "beforeOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact prior owner associated with this artifact and prior captured state", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩)] },
      { name := "afterOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact proposed/final owner associated with this artifact and transition context", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩), ("afterOwner", ⟨.ref, .variable "afterOwner"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_006 : Plan 24 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:2"
    sourceKind := "failure-occurrence"
    targetKind := "failure-mode"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.variable "beforeOwner") (.cons (.variable "afterOwner") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "beforeOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact prior owner associated with this artifact and prior captured state", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩)] },
      { name := "afterOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact proposed/final owner associated with this artifact and transition context", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩), ("afterOwner", ⟨.ref, .variable "afterOwner"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_007 : Plan 24 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:2"
    sourceKind := "implementation"
    targetKind := "governed-model"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.variable "beforeOwner") (.cons (.variable "afterOwner") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "beforeOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact prior owner associated with this artifact and prior captured state", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩)] },
      { name := "afterOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact proposed/final owner associated with this artifact and transition context", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩), ("afterOwner", ⟨.ref, .variable "afterOwner"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_008 : Plan 24 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:2"
    sourceKind := "implementation"
    targetKind := "product-capability"
    branchIndex := 8
    arguments := .cons (.source) (.cons (.variable "beforeOwner") (.cons (.variable "afterOwner") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "beforeOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact prior owner associated with this artifact and prior captured state", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩)] },
      { name := "afterOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact proposed/final owner associated with this artifact and transition context", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩), ("afterOwner", ⟨.ref, .variable "afterOwner"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_009 : Plan 24 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:2"
    sourceKind := "improvement-target"
    targetKind := "classification-value"
    branchIndex := 9
    arguments := .cons (.source) (.cons (.variable "beforeOwner") (.cons (.variable "afterOwner") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "beforeOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact prior owner associated with this artifact and prior captured state", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩)] },
      { name := "afterOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact proposed/final owner associated with this artifact and transition context", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩), ("afterOwner", ⟨.ref, .variable "afterOwner"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_010 : Plan 24 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:2"
    sourceKind := "operational-lesson"
    targetKind := "classification-value"
    branchIndex := 10
    arguments := .cons (.source) (.cons (.variable "beforeOwner") (.cons (.variable "afterOwner") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "beforeOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact prior owner associated with this artifact and prior captured state", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩)] },
      { name := "afterOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact proposed/final owner associated with this artifact and transition context", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩), ("afterOwner", ⟨.ref, .variable "afterOwner"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_011 : Plan 24 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.instance-of:forbidden:2"
    sourceKind := "product-capability"
    targetKind := "product"
    branchIndex := 11
    arguments := .cons (.source) (.cons (.variable "beforeOwner") (.cons (.variable "afterOwner") (.cons (.variable "transition") (.nil))))
    binders := [
      { name := "beforeOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact prior owner associated with this artifact and prior captured state", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩)] },
      { name := "afterOwner", sort := .ref, domain := "ownership-participants", selectionRole := "Exact proposed/final owner associated with this artifact and transition context", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩)] },
      { name := "transition", sort := .ref, domain := "state-transitions", selectionRole := "Separate qualified transition candidate for these named participants; selecting it does not establish authorization/application", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("artifact", ⟨.ref, .source⟩), ("beforeOwner", ⟨.ref, .variable "beforeOwner"⟩), ("afterOwner", ⟨.ref, .variable "afterOwner"⟩)] }
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
#print axioms plan_0_007
#print axioms plan_0_008
#print axioms plan_0_009
#print axioms plan_0_010
#print axioms plan_0_011
#print axioms plan_1_000
#print axioms plan_1_001
#print axioms plan_1_002
#print axioms plan_1_003
#print axioms plan_1_004
#print axioms plan_1_005
#print axioms plan_1_006
#print axioms plan_1_007
#print axioms plan_1_008
#print axioms plan_1_009
#print axioms plan_1_010
#print axioms plan_1_011
#print axioms plan_2_000
#print axioms plan_2_001
#print axioms plan_2_002
#print axioms plan_2_003
#print axioms plan_2_004
#print axioms plan_2_005
#print axioms plan_2_006
#print axioms plan_2_007
#print axioms plan_2_008
#print axioms plan_2_009
#print axioms plan_2_010
#print axioms plan_2_011
end CandidateConclusionAnchors.K24
