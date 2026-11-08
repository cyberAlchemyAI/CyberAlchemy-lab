import DelegationSemantics
import ObligationSemantics

namespace Stress

theorem revocation_restriction_clear (n b : Option Nat) (t : Nat)
    (h : RevocationRestricts n b) (clear : ClearAt n t) : ClearAt b t := by
  cases b with
  | none => trivial
  | some b =>
    cases n with
    | none => exact False.elim h
    | some n => exact Nat.lt_of_lt_of_le clear h

theorem restriction_preserves_effectiveness (n b : Delegation) (s : Snapshot)
    (en eb : ActsEdge) (action : String) (redelegated : Bool)
    (restricted : Restricts n b) (matched : EdgeMatches eb b)
    (scope : eb.scope = en.scope) (effective : Effective n s en action redelegated) :
    Effective b s eb action redelegated := by
  rcases restricted with ⟨_, _, actions, scopes, start, stop, revoked, policies, gates⟩
  rcases effective with ⟨_, actionMem, scopeMem, started, beforeStop, clear, policyOK, gateOK, direct⟩
  refine ⟨matched, actions action actionMem, ?_, Nat.le_trans start started,
    Nat.lt_of_lt_of_le beforeStop stop, revocation_restriction_clear _ _ _ revoked clear,
    ?_, ?_, direct⟩
  · rw [scope]
    exact scopes en.scope scopeMem
  · intro p hp
    exact policyOK p (policies p hp)
  · intro g hg
    exact gateOK g (gates g hg)

theorem revocation_stable (d : Delegation) (s : Snapshot) (e : ActsEdge)
    (action : String) (redelegated : Bool) (r : Nat)
    (revoked : d.revokedAt = some r) (afterRevocation : r ≤ s.epoch) :
    ¬ Effective d s e action redelegated := by
  intro effective
  have clear := effective.2.2.2.2.2.1
  rw [revoked] at clear
  exact Nat.not_lt_of_ge afterRevocation clear

theorem derivation_preserves_origin (g : Graph) (f : Fact) (h : Derives g f) : Origin g f := by
  induction h with
  | propagate origin => exact origin
  | forward _ ih => exact ih

theorem origin_has_derivation (g : Graph) (f : Fact) (h : Origin g f) : Derives g f :=
  .propagate f h

theorem derives_iff_origin (g : Graph) (f : Fact) : Derives g f ↔ Origin g f :=
  ⟨derivation_preserves_origin g f, origin_has_derivation g f⟩

theorem conformance_does_not_change_origin (g : Graph) (assessments : List Conformance)
    (f : Fact) : Origin { g with conformance := assessments } f ↔ Origin g f := by
  rfl

theorem conformance_does_not_change_derivation (g : Graph) (assessments : List Conformance)
    (f : Fact) : Derives { g with conformance := assessments } f ↔ Derives g f := by
  rw [derives_iff_origin, derives_iff_origin]

end Stress
