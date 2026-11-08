import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K14

def plan_0_000 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "agent-capability"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "agent-profile"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "artifact-type"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "capability-realization-binding"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_004 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "challenge-event"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_005 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "classification-assignment"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_006 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "communication-preference"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_007 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "definition"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_008 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "delegation"
    branchIndex := 8
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_009 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "effect"
    branchIndex := 9
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_010 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "failure-assessment"
    branchIndex := 10
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_011 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "failure-control-binding"
    branchIndex := 11
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_012 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "failure-mode"
    branchIndex := 12
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_013 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "failure-occurrence"
    branchIndex := 13
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_014 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "governed-model"
    branchIndex := 14
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_015 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "improvement-target"
    branchIndex := 15
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_016 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "incident"
    branchIndex := 16
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_017 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "intent-resolution"
    branchIndex := 17
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_018 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "operational-lesson"
    branchIndex := 18
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_019 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "product-capability"
    branchIndex := 19
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_020 : Plan 14 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:0"
    sourceKind := "decision"
    targetKind := "relation-kind"
    branchIndex := 20
    arguments := .cons (.source) (.cons (.witnessField "effect" (by decide)) (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "agent-capability"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_001 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "agent-profile"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_002 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "artifact-type"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_003 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "capability-realization-binding"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_004 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "challenge-event"
    branchIndex := 4
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_005 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "classification-assignment"
    branchIndex := 5
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_006 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "communication-preference"
    branchIndex := 6
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_007 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "definition"
    branchIndex := 7
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_008 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "delegation"
    branchIndex := 8
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_009 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "effect"
    branchIndex := 9
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_010 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "failure-assessment"
    branchIndex := 10
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_011 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "failure-control-binding"
    branchIndex := 11
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_012 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "failure-mode"
    branchIndex := 12
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_013 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "failure-occurrence"
    branchIndex := 13
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_014 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "governed-model"
    branchIndex := 14
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_015 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "improvement-target"
    branchIndex := 15
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_016 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "incident"
    branchIndex := 16
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_017 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "intent-resolution"
    branchIndex := 17
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_018 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "operational-lesson"
    branchIndex := 18
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_019 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "product-capability"
    branchIndex := 19
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_1_020 : Plan 14 [.ref, .ref, .effect, .effect] :=
  { obligationId := "relation.declares-effect-on:forbidden:1"
    sourceKind := "decision"
    targetKind := "relation-kind"
    branchIndex := 20
    arguments := .cons (.source) (.cons (.target) (.cons (.witnessField "effect" (by decide)) (.cons (.variable "other") (.nil))))
    binders := [
      { name := "other", sort := .effect, domain := "effect-codes", selectionRole := "A different declared governance effect from the exact selected declared effect", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := [.notEqual (.witnessField "effect" (by decide)) (.variable "other")]
    structurallyValid := by decide }

def plan_2_000 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "agent-capability"
    branchIndex := 0
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "agent-profile"
    branchIndex := 1
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "artifact-type"
    branchIndex := 2
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "capability-realization-binding"
    branchIndex := 3
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_004 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "challenge-event"
    branchIndex := 4
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_005 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "classification-assignment"
    branchIndex := 5
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_006 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "communication-preference"
    branchIndex := 6
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_007 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "definition"
    branchIndex := 7
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_008 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "delegation"
    branchIndex := 8
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_009 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "effect"
    branchIndex := 9
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_010 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "failure-assessment"
    branchIndex := 10
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_011 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "failure-control-binding"
    branchIndex := 11
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_012 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "failure-mode"
    branchIndex := 12
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_013 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "failure-occurrence"
    branchIndex := 13
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_014 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "governed-model"
    branchIndex := 14
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_015 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "improvement-target"
    branchIndex := 15
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_016 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "incident"
    branchIndex := 16
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_017 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "intent-resolution"
    branchIndex := 17
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_018 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "operational-lesson"
    branchIndex := 18
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_019 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "product-capability"
    branchIndex := 19
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_020 : Plan 14 [.ref, .ref, .ref] :=
  { obligationId := "relation.declares-effect-on:forbidden:2"
    sourceKind := "decision"
    targetKind := "relation-kind"
    branchIndex := 20
    arguments := .cons (.variable "operation") (.cons (.variable "execution") (.cons (.variable "criteria") (.nil)))
    binders := [
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Independently specified runtime operation implementing this declaration; declaration is not execution", joins := [("decision", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "execution", sort := .ref, domain := "execution-observations", selectionRole := "Exact actual-execution candidate trace for the named operation/design/subject", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩)] },
      { name := "criteria", sort := .ref, domain := "criterion-sets", selectionRole := "Exact complete independently owned criterion-set revision for these target/operation participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .variable "operation"⟩), ("execution", ⟨.ref, .variable "execution"⟩)] }
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
#print axioms plan_0_019
#print axioms plan_0_020
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
#print axioms plan_1_019
#print axioms plan_1_020
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
#print axioms plan_2_019
#print axioms plan_2_020
end CandidateConclusionAnchors.K14
