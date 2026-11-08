import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K25

def plan_0_000 : Plan 25 [.ref, .ref, .ref] :=
  { obligationId := "relation.materializes-consequence:forbidden:0"
    sourceKind := "admission-transaction"
    targetKind := "generated-output"
    branchIndex := 0
    arguments := .cons (.variable "before") (.cons (.variable "after") (.cons (.variable "root") (.nil)))
    binders := [
      { name := "before", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact captured prior state of this authorized transaction", joins := [("transaction", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "after", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact captured final applied state of this same transaction", joins := [("transaction", ⟨.ref, .source⟩), ("output", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "root", sort := .ref, domain := "authorization-roots", selectionRole := "An exact root in the final state absent from the prior approved envelope; its existence must be independently established", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("before", ⟨.ref, .variable "before"⟩), ("after", ⟨.ref, .variable "after"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 25 [.ref, .ref, .ref] :=
  { obligationId := "relation.materializes-consequence:forbidden:0"
    sourceKind := "admission-transaction"
    targetKind := "project-governance-event-history"
    branchIndex := 1
    arguments := .cons (.variable "before") (.cons (.variable "after") (.cons (.variable "root") (.nil)))
    binders := [
      { name := "before", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact captured prior state of this authorized transaction", joins := [("transaction", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "after", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact captured final applied state of this same transaction", joins := [("transaction", ⟨.ref, .source⟩), ("output", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "root", sort := .ref, domain := "authorization-roots", selectionRole := "An exact root in the final state absent from the prior approved envelope; its existence must be independently established", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("before", ⟨.ref, .variable "before"⟩), ("after", ⟨.ref, .variable "after"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 25 [.ref, .ref, .ref] :=
  { obligationId := "relation.materializes-consequence:forbidden:0"
    sourceKind := "admission-transaction"
    targetKind := "project-semantic-event-history"
    branchIndex := 2
    arguments := .cons (.variable "before") (.cons (.variable "after") (.cons (.variable "root") (.nil)))
    binders := [
      { name := "before", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact captured prior state of this authorized transaction", joins := [("transaction", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "after", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact captured final applied state of this same transaction", joins := [("transaction", ⟨.ref, .source⟩), ("output", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "root", sort := .ref, domain := "authorization-roots", selectionRole := "An exact root in the final state absent from the prior approved envelope; its existence must be independently established", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("before", ⟨.ref, .variable "before"⟩), ("after", ⟨.ref, .variable "after"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_003 : Plan 25 [.ref, .ref, .ref] :=
  { obligationId := "relation.materializes-consequence:forbidden:0"
    sourceKind := "admission-transaction"
    targetKind := "project-state"
    branchIndex := 3
    arguments := .cons (.variable "before") (.cons (.variable "after") (.cons (.variable "root") (.nil)))
    binders := [
      { name := "before", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact captured prior state of this authorized transaction", joins := [("transaction", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "after", sort := .ref, domain := "captured-state-snapshots", selectionRole := "Exact captured final applied state of this same transaction", joins := [("transaction", ⟨.ref, .source⟩), ("output", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "root", sort := .ref, domain := "authorization-roots", selectionRole := "An exact root in the final state absent from the prior approved envelope; its existence must be independently established", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("before", ⟨.ref, .variable "before"⟩), ("after", ⟨.ref, .variable "after"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 25 [.ref, .ref, .ref] :=
  { obligationId := "relation.materializes-consequence:forbidden:1"
    sourceKind := "admission-transaction"
    targetKind := "generated-output"
    branchIndex := 0
    arguments := .cons (.target) (.cons (.variable "meaning") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "meaning", sort := .ref, domain := "semantic-specifications", selectionRole := "Exact independent intended semantic specification for the generated output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("meaning", ⟨.ref, .variable "meaning"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 25 [.ref, .ref, .ref] :=
  { obligationId := "relation.materializes-consequence:forbidden:1"
    sourceKind := "admission-transaction"
    targetKind := "project-governance-event-history"
    branchIndex := 1
    arguments := .cons (.target) (.cons (.variable "meaning") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "meaning", sort := .ref, domain := "semantic-specifications", selectionRole := "Exact independent intended semantic specification for the generated output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("meaning", ⟨.ref, .variable "meaning"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 25 [.ref, .ref, .ref] :=
  { obligationId := "relation.materializes-consequence:forbidden:1"
    sourceKind := "admission-transaction"
    targetKind := "project-semantic-event-history"
    branchIndex := 2
    arguments := .cons (.target) (.cons (.variable "meaning") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "meaning", sort := .ref, domain := "semantic-specifications", selectionRole := "Exact independent intended semantic specification for the generated output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("meaning", ⟨.ref, .variable "meaning"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_003 : Plan 25 [.ref, .ref, .ref] :=
  { obligationId := "relation.materializes-consequence:forbidden:1"
    sourceKind := "admission-transaction"
    targetKind := "project-state"
    branchIndex := 3
    arguments := .cons (.target) (.cons (.variable "meaning") (.cons (.variable "proof") (.nil)))
    binders := [
      { name := "meaning", sort := .ref, domain := "semantic-specifications", selectionRole := "Exact independent intended semantic specification for the generated output", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩)] },
      { name := "proof", sort := .ref, domain := "proof-artifacts", selectionRole := "Exact proof artifact of the independently specified statement; selection does not establish validity", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("output", ⟨.ref, .target⟩), ("meaning", ⟨.ref, .variable "meaning"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 25 [.ref, .ref, .ref] :=
  { obligationId := "relation.materializes-consequence:forbidden:2"
    sourceKind := "admission-transaction"
    targetKind := "generated-output"
    branchIndex := 0
    arguments := .cons (.variable "implementation") (.cons (.variable "environment") (.cons (.variable "activationReceipt") (.nil)))
    binders := [
      { name := "implementation", sort := .ref, domain := "runtime-targets", selectionRole := "Exact runtime implementation independently associated with this applied bundle; a generated output/state/history is not itself an Implementation", joins := [("transaction", ⟨.ref, .source⟩), ("output", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "environment", sort := .ref, domain := "execution-environments", selectionRole := "Exact independently specified environment of the installation/activation/external operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("implementation", ⟨.ref, .variable "implementation"⟩)] },
      { name := "activationReceipt", sort := .ref, domain := "runtime-activation-observations", selectionRole := "Exact actual permitted activation candidate joining implementation and environment", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("implementation", ⟨.ref, .variable "implementation"⟩), ("environment", ⟨.ref, .variable "environment"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 25 [.ref, .ref, .ref] :=
  { obligationId := "relation.materializes-consequence:forbidden:2"
    sourceKind := "admission-transaction"
    targetKind := "project-governance-event-history"
    branchIndex := 1
    arguments := .cons (.variable "implementation") (.cons (.variable "environment") (.cons (.variable "activationReceipt") (.nil)))
    binders := [
      { name := "implementation", sort := .ref, domain := "runtime-targets", selectionRole := "Exact runtime implementation independently associated with this applied bundle; a generated output/state/history is not itself an Implementation", joins := [("transaction", ⟨.ref, .source⟩), ("output", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "environment", sort := .ref, domain := "execution-environments", selectionRole := "Exact independently specified environment of the installation/activation/external operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("implementation", ⟨.ref, .variable "implementation"⟩)] },
      { name := "activationReceipt", sort := .ref, domain := "runtime-activation-observations", selectionRole := "Exact actual permitted activation candidate joining implementation and environment", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("implementation", ⟨.ref, .variable "implementation"⟩), ("environment", ⟨.ref, .variable "environment"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 25 [.ref, .ref, .ref] :=
  { obligationId := "relation.materializes-consequence:forbidden:2"
    sourceKind := "admission-transaction"
    targetKind := "project-semantic-event-history"
    branchIndex := 2
    arguments := .cons (.variable "implementation") (.cons (.variable "environment") (.cons (.variable "activationReceipt") (.nil)))
    binders := [
      { name := "implementation", sort := .ref, domain := "runtime-targets", selectionRole := "Exact runtime implementation independently associated with this applied bundle; a generated output/state/history is not itself an Implementation", joins := [("transaction", ⟨.ref, .source⟩), ("output", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "environment", sort := .ref, domain := "execution-environments", selectionRole := "Exact independently specified environment of the installation/activation/external operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("implementation", ⟨.ref, .variable "implementation"⟩)] },
      { name := "activationReceipt", sort := .ref, domain := "runtime-activation-observations", selectionRole := "Exact actual permitted activation candidate joining implementation and environment", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("implementation", ⟨.ref, .variable "implementation"⟩), ("environment", ⟨.ref, .variable "environment"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_003 : Plan 25 [.ref, .ref, .ref] :=
  { obligationId := "relation.materializes-consequence:forbidden:2"
    sourceKind := "admission-transaction"
    targetKind := "project-state"
    branchIndex := 3
    arguments := .cons (.variable "implementation") (.cons (.variable "environment") (.cons (.variable "activationReceipt") (.nil)))
    binders := [
      { name := "implementation", sort := .ref, domain := "runtime-targets", selectionRole := "Exact runtime implementation independently associated with this applied bundle; a generated output/state/history is not itself an Implementation", joins := [("transaction", ⟨.ref, .source⟩), ("output", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "environment", sort := .ref, domain := "execution-environments", selectionRole := "Exact independently specified environment of the installation/activation/external operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("implementation", ⟨.ref, .variable "implementation"⟩)] },
      { name := "activationReceipt", sort := .ref, domain := "runtime-activation-observations", selectionRole := "Exact actual permitted activation candidate joining implementation and environment", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("implementation", ⟨.ref, .variable "implementation"⟩), ("environment", ⟨.ref, .variable "environment"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_000 : Plan 25 [.ref, .ref, .ref] :=
  { obligationId := "relation.materializes-consequence:forbidden:3"
    sourceKind := "admission-transaction"
    targetKind := "generated-output"
    branchIndex := 0
    arguments := .cons (.source) (.cons (.variable "environment") (.cons (.variable "observation") (.nil)))
    binders := [
      { name := "environment", sort := .ref, domain := "execution-environments", selectionRole := "Exact independently specified environment of the installation/activation/external operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .source⟩)] },
      { name := "observation", sort := .ref, domain := "outcome-observations", selectionRole := "Exact independent outcome/external observation for this operation and its environment/objective", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .source⟩), ("environment", ⟨.ref, .variable "environment"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_001 : Plan 25 [.ref, .ref, .ref] :=
  { obligationId := "relation.materializes-consequence:forbidden:3"
    sourceKind := "admission-transaction"
    targetKind := "project-governance-event-history"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "environment") (.cons (.variable "observation") (.nil)))
    binders := [
      { name := "environment", sort := .ref, domain := "execution-environments", selectionRole := "Exact independently specified environment of the installation/activation/external operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .source⟩)] },
      { name := "observation", sort := .ref, domain := "outcome-observations", selectionRole := "Exact independent outcome/external observation for this operation and its environment/objective", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .source⟩), ("environment", ⟨.ref, .variable "environment"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_002 : Plan 25 [.ref, .ref, .ref] :=
  { obligationId := "relation.materializes-consequence:forbidden:3"
    sourceKind := "admission-transaction"
    targetKind := "project-semantic-event-history"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "environment") (.cons (.variable "observation") (.nil)))
    binders := [
      { name := "environment", sort := .ref, domain := "execution-environments", selectionRole := "Exact independently specified environment of the installation/activation/external operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .source⟩)] },
      { name := "observation", sort := .ref, domain := "outcome-observations", selectionRole := "Exact independent outcome/external observation for this operation and its environment/objective", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .source⟩), ("environment", ⟨.ref, .variable "environment"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_3_003 : Plan 25 [.ref, .ref, .ref] :=
  { obligationId := "relation.materializes-consequence:forbidden:3"
    sourceKind := "admission-transaction"
    targetKind := "project-state"
    branchIndex := 3
    arguments := .cons (.source) (.cons (.variable "environment") (.cons (.variable "observation") (.nil)))
    binders := [
      { name := "environment", sort := .ref, domain := "execution-environments", selectionRole := "Exact independently specified environment of the installation/activation/external operation", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .source⟩)] },
      { name := "observation", sort := .ref, domain := "outcome-observations", selectionRole := "Exact independent outcome/external observation for this operation and its environment/objective", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("operation", ⟨.ref, .source⟩), ("environment", ⟨.ref, .variable "environment"⟩)] }
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
#print axioms plan_3_000
#print axioms plan_3_001
#print axioms plan_3_002
#print axioms plan_3_003
end CandidateConclusionAnchors.K25
