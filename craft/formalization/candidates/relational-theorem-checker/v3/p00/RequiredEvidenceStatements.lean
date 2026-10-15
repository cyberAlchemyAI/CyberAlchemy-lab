import EvidenceSemantics

namespace RelationalV3.Required
open RelationalV3

abbrev ExactRequiredInventory : Prop :=
  ∀ r m, EvidenceComplete r m →
    m.obligations = requiredObligations r.changeClass ∧
    m.modules.map ModuleEvidence.role = requiredModules r.layout

abbrev FreshRequiresCurrent : Prop :=
  ∀ r m current invocation accepted,
    FreshQualified r m current invocation accepted → RecordedCurrent r m current

abbrev SavedCannotSupplyFreshReplay : Prop :=
  ∀ r m current session accepted,
    ¬ FreshQualified r m current ⟨session, []⟩ accepted

abbrev ResourceRefusalBlocksClaims : Prop :=
  ∀ claim, ¬ ClaimPermitted .unknownResource claim ∧
    ¬ ClaimPermitted .cancelled claim ∧ ¬ ClaimPermitted .unsupportedPolicy claim

abbrev PublicationNeedsFreshReviewedHead : Prop :=
  ∀ r m current invocation accepted p,
    PublicationQualified r m current invocation accepted p →
    p.mediatedWriters = true ∧ p.reviewedGeneration = p.observedGeneration ∧
    p.successor = r.identity ∧ FreshQualified r m current invocation accepted

theorem exact_required_inventory : ExactRequiredInventory := by
  intro r m h
  exact ⟨h.2.2.2.2.1, h.2.2.2.2.2.1⟩

theorem fresh_requires_current : FreshRequiresCurrent := by
  intro r m current invocation accepted h
  exact h.1

theorem saved_cannot_supply_fresh_replay : SavedCannotSupplyFreshReplay := by
  intro r m current session accepted h
  rcases h.2.2 with ⟨e, membership, _⟩
  cases membership

theorem resource_refusal_blocks_claims : ResourceRefusalBlocksClaims := by
  intro claim
  exact ⟨by simp [ClaimPermitted], by simp [ClaimPermitted], by simp [ClaimPermitted]⟩

theorem publication_needs_fresh_reviewed_head : PublicationNeedsFreshReviewedHead := by
  intro r m current invocation accepted p h
  exact ⟨h.2.1, h.2.2.1, h.2.2.2.1, h.2.2.2.2⟩

theorem retained_every_old_model_expands : Successor.Recursive.RequiredConservativity :=
  Successor.Recursive.every_old_model_expands

theorem retained_active_needs_holds : Successor.Required.ActivationNeedsHolds :=
  Successor.Conditions.activation_needs_holds

theorem retained_potential_has_origin : Successor.Required.ActivationHasOrigin :=
  Successor.Conditions.activation_has_origin

#print axioms exact_required_inventory
#print axioms fresh_requires_current
#print axioms saved_cannot_supply_fresh_replay
#print axioms resource_refusal_blocks_claims
#print axioms publication_needs_fresh_reviewed_head
#print axioms retained_every_old_model_expands
#print axioms retained_active_needs_holds

end RelationalV3.Required
