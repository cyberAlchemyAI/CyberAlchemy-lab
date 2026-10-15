import ReferenceChecker
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000
namespace Relational.Fixtures
open Relational

def cap : Node := ⟨⟨"cap", "v1"⟩, .capabilityInstance, "cap-content"⟩
def contract : Node := ⟨⟨"contract", "v1"⟩, .contract, "contract-content"⟩
def decision : Node := ⟨⟨"decision", "v1"⟩, .decision, "decision-content"⟩
def effect : Node := ⟨⟨"effect", "v1"⟩, .effect, "effect-content"⟩
def transaction : Node := ⟨⟨"transaction", "v1"⟩, .admissionTransaction, "transaction-content"⟩
def output : Node := ⟨⟨"output", "v1"⟩, .generatedOutput, "output-content"⟩

def conformanceAssessment : Assessment :=
  ⟨"assessment", .conformance, cap.ref, contract.ref, "static", "", "", true⟩
def receiptAssessment : Assessment :=
  ⟨"receipt", .applicationReceipt, transaction.ref, output.ref, "", "artifact", "output-content", true⟩
def conforms : Assertion :=
  ⟨"conforms", .conformsTo, cap.ref, contract.ref, .conformance "static" "v1" "assessment"⟩
def declares : Assertion :=
  ⟨"declares", .declaresEffectOn, decision.ref, effect.ref, .effect "authorization" "v1"⟩
def materializes : Assertion :=
  ⟨"materializes", .materializesConsequence, transaction.ref, output.ref,
    .materialization "receipt" "artifact" "output-content"⟩
def validGraph : Graph :=
  ⟨[cap, contract, decision, effect, transaction, output],
    [conformanceAssessment, receiptAssessment], [conforms, declares, materializes], []⟩
def baseGraph : Graph := { validGraph with assertions := [conforms, declares] }
def independentRoot : AdmissionRoot := ⟨cap.ref, decision.ref, "independent-authority-receipt"⟩
def graphWithAdmission : Graph := { validGraph with admissionRoots := [independentRoot] }

-- Pair controls synthesize fresh finite fixture ledgers for all 28 declarations.
def pairGraph (k : RelationKind) (s t : NodeKind) : Graph :=
  let sn : Node := ⟨⟨"source", "v1"⟩, s, "source-content"⟩
  let tn : Node := ⟨⟨"target", "v1"⟩, t, "target-content"⟩
  let q := match k with
    | .conformsTo => Qualifiers.conformance "scope" "v1" "assessment"
    | .declaresEffectOn => Qualifiers.effect "opaque-effect-value" "v1"
    | .materializesConsequence => Qualifiers.materialization "receipt" "role" "target-content"
  let assessments := match k with
    | .conformsTo => [Assessment.mk "assessment" .conformance sn.ref tn.ref "scope" "" "" true]
    | .declaresEffectOn => []
    | .materializesConsequence => [Assessment.mk "receipt" .applicationReceipt sn.ref tn.ref "" "role" "target-content" true]
  ⟨[sn, tn], assessments, [Assertion.mk "assertion" k sn.ref tn.ref q], []⟩

end Relational.Fixtures
