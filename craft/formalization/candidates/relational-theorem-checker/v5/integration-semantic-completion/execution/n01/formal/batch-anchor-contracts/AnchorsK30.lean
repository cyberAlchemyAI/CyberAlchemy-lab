import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K30

def plan_0_000 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "agent-reflection"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "challenge-event"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "classification-assignment"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "definition"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "drift-assessment"
    branchIndex := 4
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_005 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "evidence-set"
    branchIndex := 5
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_006 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "failure-assessment"
    branchIndex := 6
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_007 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "failure-occurrence"
    branchIndex := 7
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_008 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "feedback-record"
    branchIndex := 8
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_009 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "finding"
    branchIndex := 9
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_010 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "generated-output"
    branchIndex := 10
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_011 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "improvement-signal"
    branchIndex := 11
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_012 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "lesson-application"
    branchIndex := 12
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_013 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "measurement-result"
    branchIndex := 13
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_014 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "observation"
    branchIndex := 14
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_015 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "operational-lesson"
    branchIndex := 15
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_016 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "operational-observation"
    branchIndex := 16
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_017 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "typed-relation"
    branchIndex := 17
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_018 : Plan 30 [.ref, .ref, .frame] :=
  { obligationId := "relation.produces:forbidden:0"
    sourceKind := "agent-action"
    targetKind := "work-outcome-assessment"
    branchIndex := 18
    arguments := .cons (.target) (.cons (.variable "policy") (.cons (.frameField "frame" (by decide)) (.nil)))
    binders := [
      { name := "policy", sort := .ref, domain := "assessment-policies", selectionRole := "Exact owned policy for acceptance/adoption or evidential interpretation of this subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("subject", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "agent-reflection"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "challenge-event"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "classification-assignment"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "definition"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_004 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "drift-assessment"
    branchIndex := 4
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_005 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "evidence-set"
    branchIndex := 5
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_006 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "failure-assessment"
    branchIndex := 6
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_007 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "failure-occurrence"
    branchIndex := 7
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_008 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "feedback-record"
    branchIndex := 8
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_009 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "finding"
    branchIndex := 9
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_010 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "generated-output"
    branchIndex := 10
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_011 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "improvement-signal"
    branchIndex := 11
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_012 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "lesson-application"
    branchIndex := 12
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_013 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "measurement-result"
    branchIndex := 13
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_014 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "observation"
    branchIndex := 14
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_015 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "operational-lesson"
    branchIndex := 15
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_016 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "operational-observation"
    branchIndex := 16
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_017 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "typed-relation"
    branchIndex := 17
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_018 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:1"
    sourceKind := "agent-action"
    targetKind := "work-outcome-assessment"
    branchIndex := 18
    arguments := .cons (.target) (.cons (.variable "specification") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "specification", sort := .ref, domain := "correctness-specifications", selectionRole := "Exact independent correctness specification of this output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("specification", ⟨.ref, .variable "specification"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "agent-reflection"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "challenge-event"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "classification-assignment"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "definition"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "drift-assessment"
    branchIndex := 4
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_005 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "evidence-set"
    branchIndex := 5
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_006 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "failure-assessment"
    branchIndex := 6
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_007 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "failure-occurrence"
    branchIndex := 7
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_008 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "feedback-record"
    branchIndex := 8
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_009 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "finding"
    branchIndex := 9
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_010 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "generated-output"
    branchIndex := 10
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_011 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "improvement-signal"
    branchIndex := 11
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_012 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "lesson-application"
    branchIndex := 12
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_013 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "measurement-result"
    branchIndex := 13
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_014 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "observation"
    branchIndex := 14
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_015 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "operational-lesson"
    branchIndex := 15
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_016 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "operational-observation"
    branchIndex := 16
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_017 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "typed-relation"
    branchIndex := 17
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_018 : Plan 30 [.ref, .ref, .ref] :=
  { obligationId := "relation.produces:forbidden:2"
    sourceKind := "agent-action"
    targetKind := "work-outcome-assessment"
    branchIndex := 18
    arguments := .cons (.target) (.cons (.variable "decision") (.cons (.variable "state") (.nil)))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩)] },
      { name := "state", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact state revision relevant to this admission candidate", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("endpoint", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "agent-reflection"
    branchIndex := 0
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "challenge-event"
    branchIndex := 1
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_002 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "classification-assignment"
    branchIndex := 2
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_003 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "definition"
    branchIndex := 3
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_004 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "drift-assessment"
    branchIndex := 4
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_005 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "evidence-set"
    branchIndex := 5
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_006 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "failure-assessment"
    branchIndex := 6
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_007 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "failure-occurrence"
    branchIndex := 7
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_008 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "feedback-record"
    branchIndex := 8
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_009 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "finding"
    branchIndex := 9
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_010 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "generated-output"
    branchIndex := 10
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_011 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "improvement-signal"
    branchIndex := 11
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_012 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "lesson-application"
    branchIndex := 12
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_013 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "measurement-result"
    branchIndex := 13
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_014 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "observation"
    branchIndex := 14
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_015 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "operational-lesson"
    branchIndex := 15
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_016 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "operational-observation"
    branchIndex := 16
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_017 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "typed-relation"
    branchIndex := 17
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_018 : Plan 30 [.ref, .ref, .effect, .ref] :=
  { obligationId := "relation.produces:forbidden:3"
    sourceKind := "agent-action"
    targetKind := "work-outcome-assessment"
    branchIndex := 18
    arguments := .cons (.variable "decision") (.cons (.target) (.cons (.variable "effect") (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "decision-candidates", selectionRole := "Separate independently captured decision candidate about the named governed subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("target", ⟨.ref, .target⟩), ("decision", ⟨.ref, .variable "decision"⟩)] }
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
#print axioms plan_0_012
#print axioms plan_0_013
#print axioms plan_0_014
#print axioms plan_0_015
#print axioms plan_0_016
#print axioms plan_0_017
#print axioms plan_0_018
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
#print axioms plan_1_012
#print axioms plan_1_013
#print axioms plan_1_014
#print axioms plan_1_015
#print axioms plan_1_016
#print axioms plan_1_017
#print axioms plan_1_018
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
#print axioms plan_2_012
#print axioms plan_2_013
#print axioms plan_2_014
#print axioms plan_2_015
#print axioms plan_2_016
#print axioms plan_2_017
#print axioms plan_2_018
#print axioms plan_3_000
#print axioms plan_3_001
#print axioms plan_3_002
#print axioms plan_3_003
#print axioms plan_3_004
#print axioms plan_3_005
#print axioms plan_3_006
#print axioms plan_3_007
#print axioms plan_3_008
#print axioms plan_3_009
#print axioms plan_3_010
#print axioms plan_3_011
#print axioms plan_3_012
#print axioms plan_3_013
#print axioms plan_3_014
#print axioms plan_3_015
#print axioms plan_3_016
#print axioms plan_3_017
#print axioms plan_3_018
end CandidateConclusionAnchors.K30
