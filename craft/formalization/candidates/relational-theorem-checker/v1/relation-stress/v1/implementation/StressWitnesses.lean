import StressProofs

namespace Stress.Witnesses

def agent : Ref := ⟨"agent", "v1"⟩
def principal : Ref := ⟨"principal", "v1"⟩
def delegation : Delegation := {
  ref := ⟨"delegation", "v1"⟩
  agent := agent
  principal := principal
  scopes := ["repo"]
  actions := ["read"]
  period := ⟨0,10⟩
  revokedAt := none
  policies := []
  gates := []
  redelegationAllowed := false }
def edge : ActsEdge := {
  id := "acts-1"
  agent := agent
  principal := principal
  delegation := delegation.ref
  scope := "repo"
  period := delegation.period
  revokedAt := none }
def snapshot : Snapshot := { ref := ⟨"snapshot", "v1"⟩, epoch := 5, policies := [], gates := [] }
def expired : Snapshot := { snapshot with epoch := 10 }
def revoked : Delegation := { delegation with revokedAt := some 5 }
def revokedEdge : ActsEdge := { edge with revokedAt := some 5 }
def narrowed : Delegation := { delegation with ref := ⟨"delegation", "v2"⟩, period := ⟨2,8⟩ }
def narrowEdge : ActsEdge := { edge with delegation := narrowed.ref, period := narrowed.period }

theorem inhabited_temporal_profile :
    ActsInventoryValid [delegation] snapshot edge "read" ∧
    Effective delegation snapshot edge "read" false ∧
    checkActs [delegation] snapshot edge "read" false = .yes := by
  exact ⟨by decide, by decide, by decide⟩

theorem historical_edge_survives_expiration :
    Recorded [edge] edge ∧ ¬ Effective delegation expired edge "read" false ∧
    checkActs [delegation] expired edge "read" false = .no := by
  exact ⟨by decide, by decide, by decide⟩

theorem recorded_does_not_entail_effective :
    ¬ (∀ (ds : List Delegation) (s : Snapshot) (edges : List ActsEdge) (e : ActsEdge),
      Recorded edges e → ActsHolds ds s e "read" false) := by
  intro claim
  have h := claim [delegation] expired [edge] edge (by decide)
  have no : ¬ ActsHolds [delegation] expired edge "read" false := by decide
  exact no h

theorem revocation_boundary_rejected : checkActs [revoked] snapshot revokedEdge "read" false = .no := by decide
theorem narrower_delegation_is_inhabited :
    Restricts narrowed delegation ∧ Effective narrowed snapshot narrowEdge "read" false := by
  exact ⟨by decide, by decide⟩

def contract : Contract := {
  ref := ⟨"contract", "v1"⟩
  scope := "repo"
  condition := "always"
  interpreted := true
  norms := [⟨.require, "receipt"⟩] }
def binding : Binding := {
  ref := ⟨"binding", "v1"⟩
  subject := agent
  contracts := [contract.ref]
  scope := "repo"
  active := true
  overrides := [] }
def inheritance : Inheritance := {
  id := "inherits-1"
  subject := agent
  contract := contract.ref
  binding := binding.ref
  scope := "repo"
  condition := "always" }
def graph : Graph := {
  inheritances := [inheritance]
  bindings := [binding]
  contracts := [contract]
  conformance := [] }
def fact : Fact := ⟨inheritance, ⟨.require, "receipt"⟩⟩
def certificate : List Step := [⟨.propagate, fact, none⟩, ⟨.forward, fact, some 0⟩]
def cycle : List Step := [⟨.forward, fact, some 0⟩]
def unsupportedFact : Fact := ⟨inheritance, ⟨.require, "publish"⟩⟩
def conflictContract : Contract := { contract with norms := [⟨.require,"receipt"⟩,⟨.forbid,"receipt"⟩] }
def conflictGraph : Graph := { graph with contracts := [conflictContract] }
def forbiddenFact : Fact := ⟨inheritance, ⟨.forbid, "receipt"⟩⟩

theorem inhabited_obligation_profile : GraphValid graph ∧ Origin graph fact ∧ checkInheritance graph 100 = .yes := by
  exact ⟨by decide, by decide, by decide⟩

theorem inheritance_without_conformance :
    inheritance ∈ graph.inheritances ∧ Derives graph fact ∧ ¬ Conforms graph inheritance := by
  exact ⟨by decide, origin_has_derivation _ _ (by decide), by decide⟩

theorem inheritance_does_not_entail_conformance :
    ¬ (∀ (g : Graph) (f : Fact), Derives g f → Conforms g f.edge) := by
  intro claim
  exact inheritance_without_conformance.2.2 (claim graph fact inheritance_without_conformance.2.1)

theorem separate_conformance_can_coexist :
    let g := { graph with conformance := [⟨agent,contract.ref,"repo",true⟩] }
    Origin g fact ∧ Conforms g inheritance := by
  exact ⟨by decide, by decide⟩

theorem conflict_has_no_explosion :
    GraphValid conflictGraph ∧ Origin conflictGraph fact ∧ Origin conflictGraph forbiddenFact ∧
    ConflictPair fact forbiddenFact ∧ ¬ Derives conflictGraph unsupportedFact := by
  refine ⟨by decide, by decide, by decide, by decide, ?_⟩
  intro derived
  have no : ¬ Origin conflictGraph unsupportedFact := by decide
  exact no (derivation_preserves_origin _ _ derived)

theorem replay_valid_certificate : checkCertificate graph certificate = true := by decide
theorem replay_cycle_rejected : checkCertificate graph cycle = false := by decide
theorem empty_budget_is_unknown : checkInheritance graph 0 = .unknown := by decide

end Stress.Witnesses
