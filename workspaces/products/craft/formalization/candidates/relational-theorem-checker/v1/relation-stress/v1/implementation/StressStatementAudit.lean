import StressWitnesses

namespace Stress.Audit

def RequiredRestriction : Prop :=
  ∀ (n b : Delegation) (s : Snapshot) (en eb : ActsEdge) (a : String) (r : Bool),
    Restricts n b → EdgeMatches eb b → eb.scope = en.scope → Effective n s en a r → Effective b s eb a r
def RequiredRevocation : Prop :=
  ∀ (d : Delegation) (s : Snapshot) (e : ActsEdge) (a : String) (via : Bool) (r : Nat),
    d.revokedAt = some r → r ≤ s.epoch → ¬ Effective d s e a via
def RequiredOrigin : Prop := ∀ (g : Graph) (f : Fact), Derives g f → Origin g f
def RequiredClosure : Prop := ∀ (g : Graph) (f : Fact), f ∈ closure g ↔ Origin g f
def RequiredCertificate : Prop := ∀ (g : Graph) (steps : List Step),
  checkCertificate g steps = true → ReplayShape steps ∧ ∀ s ∈ steps, Derives g s.fact
def RequiredActsChecker : Prop := ∀ (ds : List Delegation) (s : Snapshot) (e : ActsEdge) (a : String) (r : Bool),
  checkActs ds s e a r = .yes → ActsHolds ds s e a r

theorem audited_restriction : RequiredRestriction := restriction_preserves_effectiveness
theorem audited_revocation : RequiredRevocation := revocation_stable
theorem audited_origin : RequiredOrigin := derivation_preserves_origin
theorem audited_closure : RequiredClosure := closure_exact
theorem audited_certificate : RequiredCertificate := certificate_checker_sound
theorem audited_acts_checker : RequiredActsChecker := acts_checker_sound

#print axioms revocation_restriction_clear
#print axioms restriction_preserves_effectiveness
#print axioms revocation_stable
#print axioms derivation_preserves_origin
#print axioms origin_has_derivation
#print axioms derives_iff_origin
#print axioms conformance_does_not_change_origin
#print axioms conformance_does_not_change_derivation
#print axioms acts_checker_sound
#print axioms acts_checker_iff_when_known
#print axioms origin_in_candidates
#print axioms closure_exact
#print axioms closure_equals_derivability
#print axioms inheritance_checker_sound
#print axioms certificate_check_iff
#print axioms certificate_checker_sound
#print axioms Witnesses.inhabited_temporal_profile
#print axioms Witnesses.historical_edge_survives_expiration
#print axioms Witnesses.recorded_does_not_entail_effective
#print axioms Witnesses.revocation_boundary_rejected
#print axioms Witnesses.narrower_delegation_is_inhabited
#print axioms Witnesses.inhabited_obligation_profile
#print axioms Witnesses.inheritance_without_conformance
#print axioms Witnesses.inheritance_does_not_entail_conformance
#print axioms Witnesses.separate_conformance_can_coexist
#print axioms Witnesses.conflict_has_no_explosion
#print axioms Witnesses.replay_valid_certificate
#print axioms Witnesses.replay_cycle_rejected
#print axioms Witnesses.empty_budget_is_unknown
#print axioms audited_restriction
#print axioms audited_revocation
#print axioms audited_origin
#print axioms audited_closure
#print axioms audited_certificate
#print axioms audited_acts_checker

end Stress.Audit
