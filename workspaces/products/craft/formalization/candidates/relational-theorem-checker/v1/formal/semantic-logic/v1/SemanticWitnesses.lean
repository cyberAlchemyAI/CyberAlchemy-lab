import SemanticLogic
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000

namespace Relational.Logic.Witnesses
open Relational Relational.Logic

-- Independent semantic models: this module imports no checker or checker proof.
def cap : Node := ⟨⟨"cap", "v1"⟩, .capabilityInstance, "cap-content"⟩
def contract : Node := ⟨⟨"contract", "v1"⟩, .contract, "contract-content"⟩
def decision : Node := ⟨⟨"decision", "v1"⟩, .decision, "decision-content"⟩
def transaction : Node := ⟨⟨"transaction", "v1"⟩, .admissionTransaction, "transaction-content"⟩
def output : Node := ⟨⟨"output", "v1"⟩, .generatedOutput, "output-content"⟩
def assessment : Assessment :=
  ⟨"evidence", .conformance, cap.ref, contract.ref, "static", "", "", true⟩
def receipt : Assessment :=
  ⟨"receipt", .applicationReceipt, transaction.ref, output.ref, "", "artifact", "output-content", true⟩
def conforms : Assertion :=
  ⟨"conforms", .conformsTo, cap.ref, contract.ref, .conformance "static" "v1" "evidence"⟩
def runtimeConforms : Assertion :=
  { conforms with id := "runtime-conforms", qualifiers := .conformance "runtime" "v1" "evidence" }
def materializes : Assertion :=
  ⟨"materializes", .materializesConsequence, transaction.ref, output.ref,
    .materialization "receipt" "artifact" "output-content"⟩
def graph : Graph :=
  ⟨[cap, contract, decision, transaction, output], [assessment, receipt],
    [conforms, materializes], []⟩
def root : AdmissionRoot := ⟨cap.ref, decision.ref, "separate-authority-evidence"⟩
def rootedGraph : Graph := withAdmissionRoots graph [root]
def ambiguousGraph : Graph :=
  { graph with
    assessments := [assessment, { assessment with scope := "runtime" }]
    assertions := [conforms, runtimeConforms] }

theorem inhabited_semantic_model :
    Inv graph ∧ ConformsAt graph conforms "static" "v1" "evidence" ∧
    MaterializesAs graph materializes "receipt" "artifact" "output-content" := by decide

theorem conformance_without_root :
    Inv graph ∧ conforms ∈ graph.assertions ∧
    ConformsAt graph conforms "static" "v1" "evidence" ∧
    ¬ HasAdmissionRoot graph conforms.source := by decide

theorem conformance_does_not_entail_admission_root :
    ¬ (∀ (g : Graph) (e : Assertion) (scope version evidence : String),
      Inv g → e ∈ g.assertions → ConformsAt g e scope version evidence →
      HasAdmissionRoot g e.source) := by
  intro h
  rcases conformance_without_root with ⟨hinv, hmem, hconforms, hnotroot⟩
  exact hnotroot (h graph conforms "static" "v1" "evidence" hinv hmem hconforms)

theorem admission_independence_models :
    graph.nodes = rootedGraph.nodes ∧ graph.assessments = rootedGraph.assessments ∧
    graph.assertions = rootedGraph.assertions ∧ Inv graph ∧ Inv rootedGraph ∧
    ConformsAt graph conforms "static" "v1" "evidence" ∧
    ConformsAt rootedGraph conforms "static" "v1" "evidence" ∧
    ¬ HasAdmissionRoot graph cap.ref ∧ HasAdmissionRoot rootedGraph cap.ref := by decide

theorem no_automatic_scope_upgrade :
    Inv graph ∧ ConformsAt graph conforms "static" "v1" "evidence" ∧
    ¬ ConformsAt graph runtimeConforms "runtime" "v1" "evidence" := by decide

theorem same_bound_evidence_reuse_is_allowed :
    Inv { graph with assertions := [conforms, { conforms with id := "second-conforms" }, materializes] } := by decide

def separateAssessment : Assessment :=
  { assessment with ref := "runtime-evidence", scope := "runtime" }
def separatelyAssessedConforms : Assertion :=
  { runtimeConforms with qualifiers := .conformance "runtime" "v1" "runtime-evidence" }
def separatelyAssessedGraph : Graph :=
  { graph with
    assessments := [assessment, separateAssessment, receipt]
    assertions := [conforms, separatelyAssessedConforms, materializes] }

theorem separate_scope_assessment_is_allowed :
    Inv separatelyAssessedGraph ∧
    ConformsAt separatelyAssessedGraph conforms "static" "v1" "evidence" ∧
    ConformsAt separatelyAssessedGraph separatelyAssessedConforms
      "runtime" "v1" "runtime-evidence" := by
  exact ⟨by decide, by decide, by decide⟩

-- Removing unique assessment identities destroys the evidence-functionality law.
theorem unique_identity_premise_is_needed :
    ConformsAt ambiguousGraph conforms "static" "v1" "evidence" ∧
    ConformsAt ambiguousGraph runtimeConforms "runtime" "v1" "evidence" ∧
    ("static" : String) ≠ "runtime" ∧ ¬ Inv ambiguousGraph := by decide

theorem functionality_without_invariant_is_false :
    ¬ (∀ (g : Graph) (e₁ e₂ : Assertion) (scope₁ scope₂ ver₁ ver₂ evidence : String),
      ConformsAt g e₁ scope₁ ver₁ evidence → ConformsAt g e₂ scope₂ ver₂ evidence →
      scope₁ = scope₂) := by
  intro h
  rcases unique_identity_premise_is_needed with ⟨h₁, h₂, hne, _⟩
  exact hne (h ambiguousGraph conforms runtimeConforms "static" "runtime" "v1" "v1" "evidence" h₁ h₂)

end Relational.Logic.Witnesses
