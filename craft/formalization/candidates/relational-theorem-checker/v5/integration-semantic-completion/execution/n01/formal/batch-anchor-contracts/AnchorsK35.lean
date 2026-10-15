import AnchorContracts

set_option maxRecDepth 8192
set_option maxHeartbeats 20000000

namespace CandidateConclusionAnchors.K35

def plan_0_000 : Plan 35 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.scopes-authority-over:forbidden:0"
    sourceKind := "authority-boundary"
    targetKind := "decision-scope"
    branchIndex := 0
    arguments := .cons (.variable "actor") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.variable "grant") (.nil))))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "grant", sort := .ref, domain := "permission-grants", selectionRole := "Separate authorized grant candidate for this actor, operation and scope", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("actor", ⟨.ref, .variable "actor"⟩), ("operation", ⟨.ref, .variable "operation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_001 : Plan 35 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.scopes-authority-over:forbidden:0"
    sourceKind := "authority-claim"
    targetKind := "decision-scope"
    branchIndex := 1
    arguments := .cons (.variable "actor") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.variable "grant") (.nil))))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "grant", sort := .ref, domain := "permission-grants", selectionRole := "Separate authorized grant candidate for this actor, operation and scope", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("actor", ⟨.ref, .variable "actor"⟩), ("operation", ⟨.ref, .variable "operation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_0_002 : Plan 35 [.ref, .ref, .ref, .ref] :=
  { obligationId := "relation.scopes-authority-over:forbidden:0"
    sourceKind := "authority-claim"
    targetKind := "role-assignment"
    branchIndex := 2
    arguments := .cons (.variable "actor") (.cons (.variable "operation") (.cons (.frameField "scope" (by decide)) (.cons (.variable "grant") (.nil))))
    binders := [
      { name := "actor", sort := .ref, domain := "accountable-participants", selectionRole := "Independently declared accountable actor for this subject/envelope; not an inferred grant", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "operation", sort := .ref, domain := "operation-targets", selectionRole := "Exact independently specified operation/use associated with the primary subject; selecting it does not establish execution", joins := [("subject", ⟨.ref, .source⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "grant", sort := .ref, domain := "permission-grants", selectionRole := "Separate authorized grant candidate for this actor, operation and scope", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("actor", ⟨.ref, .variable "actor"⟩), ("operation", ⟨.ref, .variable "operation"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_000 : Plan 35 [.ref, .ref, .ref] :=
  { obligationId := "relation.scopes-authority-over:forbidden:1"
    sourceKind := "authority-boundary"
    targetKind := "decision-scope"
    branchIndex := 0
    arguments := .cons (.variable "claim") (.cons (.variable "issuer") (.cons (.variable "verification") (.nil)))
    binders := [
      { name := "claim", sort := .ref, domain := "boundary-claims", selectionRole := "Exact Authority Claim independently associated with this Authority Boundary", joins := [("boundary", ⟨.ref, .source⟩), ("subject", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "issuer", sort := .ref, domain := "claim-issuers", selectionRole := "Exact issuer independently associated with this authority claim", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩)] },
      { name := "verification", sort := .ref, domain := "authentication-records", selectionRole := "Exact issuer/content authentication candidate for the claim", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .variable "claim"⟩), ("issuer", ⟨.ref, .variable "issuer"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_001 : Plan 35 [.ref, .ref, .ref] :=
  { obligationId := "relation.scopes-authority-over:forbidden:1"
    sourceKind := "authority-claim"
    targetKind := "decision-scope"
    branchIndex := 1
    arguments := .cons (.source) (.cons (.variable "issuer") (.cons (.variable "verification") (.nil)))
    binders := [
      { name := "issuer", sort := .ref, domain := "claim-issuers", selectionRole := "Exact issuer independently associated with this authority claim", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .source⟩)] },
      { name := "verification", sort := .ref, domain := "authentication-records", selectionRole := "Exact issuer/content authentication candidate for the claim", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .source⟩), ("issuer", ⟨.ref, .variable "issuer"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_1_002 : Plan 35 [.ref, .ref, .ref] :=
  { obligationId := "relation.scopes-authority-over:forbidden:1"
    sourceKind := "authority-claim"
    targetKind := "role-assignment"
    branchIndex := 2
    arguments := .cons (.source) (.cons (.variable "issuer") (.cons (.variable "verification") (.nil)))
    binders := [
      { name := "issuer", sort := .ref, domain := "claim-issuers", selectionRole := "Exact issuer independently associated with this authority claim", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .source⟩)] },
      { name := "verification", sort := .ref, domain := "authentication-records", selectionRole := "Exact issuer/content authentication candidate for the claim", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("claim", ⟨.ref, .source⟩), ("issuer", ⟨.ref, .variable "issuer"⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_000 : Plan 35 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.scopes-authority-over:forbidden:2"
    sourceKind := "authority-boundary"
    targetKind := "decision-scope"
    branchIndex := 0
    arguments := .cons (.variable "decision") (.cons (.variable "effect") (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected effect decision about this declared authority subject", joins := [("declarer", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_001 : Plan 35 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.scopes-authority-over:forbidden:2"
    sourceKind := "authority-claim"
    targetKind := "decision-scope"
    branchIndex := 1
    arguments := .cons (.variable "decision") (.cons (.variable "effect") (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected effect decision about this declared authority subject", joins := [("declarer", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

def plan_2_002 : Plan 35 [.ref, .effect, .ref, .ref] :=
  { obligationId := "relation.scopes-authority-over:forbidden:2"
    sourceKind := "authority-claim"
    targetKind := "role-assignment"
    branchIndex := 2
    arguments := .cons (.variable "decision") (.cons (.variable "effect") (.cons (.target) (.cons (.variable "receipt") (.nil))))
    binders := [
      { name := "decision", sort := .ref, domain := "selected-decisions", selectionRole := "Exact independently selected effect decision about this declared authority subject", joins := [("declarer", ⟨.ref, .source⟩), ("target", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩)] },
      { name := "effect", sort := .effect, domain := "effect-codes", selectionRole := "Exact independently declared effect of this decision, separate from the primary relation declaration", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("target", ⟨.ref, .target⟩)] },
      { name := "receipt", sort := .ref, domain := "execution-receipts", selectionRole := "Exact independently captured applied/executed/validated receipt candidate for these participants", joins := [("primarySource", ⟨.ref, .source⟩), ("primaryTarget", ⟨.ref, .target⟩), ("scope", ⟨.ref, .frameField "scope" (by decide)⟩), ("decision", ⟨.ref, .variable "decision"⟩), ("target", ⟨.ref, .target⟩)] }
    ]
    constraints := []
    structurallyValid := by decide }

#print axioms plan_0_000
#print axioms plan_0_001
#print axioms plan_0_002
#print axioms plan_1_000
#print axioms plan_1_001
#print axioms plan_1_002
#print axioms plan_2_000
#print axioms plan_2_001
#print axioms plan_2_002
end CandidateConclusionAnchors.K35
