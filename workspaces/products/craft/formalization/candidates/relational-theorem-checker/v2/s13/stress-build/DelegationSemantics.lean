import StressTypes

namespace Stress

abbrev ClearAt (r : Option Nat) (epoch : Nat) : Prop :=
  match r with
  | none => True
  | some revoked => epoch < revoked

abbrev EdgeMatches (e : ActsEdge) (d : Delegation) : Prop :=
  e.delegation = d.ref ∧ e.agent = d.agent ∧ e.principal = d.principal ∧
  e.period = d.period ∧ e.revokedAt = d.revokedAt

abbrev AllAccepted (required : List Ref) (assessments : List Assessment) : Prop :=
  ∀ r ∈ required, ∃ a ∈ assessments, a.ref = r ∧ a.accepted = true

abbrev AllResolved (required : List Ref) (assessments : List Assessment) : Prop :=
  ∀ r ∈ required, ∃ a ∈ assessments, a.ref = r

abbrev Effective (d : Delegation) (s : Snapshot) (e : ActsEdge)
    (action : String) (redelegated : Bool) : Prop :=
  EdgeMatches e d ∧ action ∈ d.actions ∧ e.scope ∈ d.scopes ∧
  d.period.start ≤ s.epoch ∧ s.epoch < d.period.stop ∧ ClearAt d.revokedAt s.epoch ∧
  AllAccepted d.policies s.policies ∧ AllAccepted d.gates s.gates ∧ redelegated = false

abbrev Recorded (edges : List ActsEdge) (e : ActsEdge) : Prop := e ∈ edges

abbrev RevocationRestricts (narrow broad : Option Nat) : Prop :=
  match narrow, broad with
  | _, none => True
  | some n, some b => n ≤ b
  | none, some _ => False

abbrev Restricts (narrow broad : Delegation) : Prop :=
  narrow.agent = broad.agent ∧ narrow.principal = broad.principal ∧
  (∀ a ∈ narrow.actions, a ∈ broad.actions) ∧
  (∀ scope ∈ narrow.scopes, scope ∈ broad.scopes) ∧
  broad.period.start ≤ narrow.period.start ∧ narrow.period.stop ≤ broad.period.stop ∧
  RevocationRestricts narrow.revokedAt broad.revokedAt ∧
  (∀ p ∈ broad.policies, p ∈ narrow.policies) ∧
  (∀ gate ∈ broad.gates, gate ∈ narrow.gates)

abbrev DelegationValid (d : Delegation) : Prop :=
  RefValid d.ref ∧ RefValid d.agent ∧ RefValid d.principal ∧ PeriodValid d.period ∧
  (∀ s ∈ d.scopes, s ≠ "") ∧ d.scopes.Nodup ∧
  (∀ a ∈ d.actions, a ≠ "") ∧ d.actions.Nodup ∧
  (∀ p ∈ d.policies, RefValid p) ∧ d.policies.Nodup ∧
  (∀ g ∈ d.gates, RefValid g) ∧ d.gates.Nodup

abbrev ActsInventoryValid (ds : List Delegation) (s : Snapshot) (e : ActsEdge)
    (action : String) : Prop :=
  (∀ d ∈ ds, DelegationValid d) ∧ (ds.map Delegation.ref).Nodup ∧
  RefValid s.ref ∧ (∀ a ∈ s.policies, RefValid a.ref) ∧
  (s.policies.map Assessment.ref).Nodup ∧ (∀ a ∈ s.gates, RefValid a.ref) ∧
  (s.gates.map Assessment.ref).Nodup ∧ e.id ≠ "" ∧ RefValid e.agent ∧
  RefValid e.principal ∧ RefValid e.delegation ∧ e.scope ≠ "" ∧ PeriodValid e.period ∧ action ≠ ""

abbrev DelegationResolved (ds : List Delegation) (e : ActsEdge) : Prop :=
  ∃ d ∈ ds, d.ref = e.delegation

abbrev InterpretationKnown (ds : List Delegation) (s : Snapshot) (e : ActsEdge) : Prop :=
  ∀ d ∈ ds, d.ref = e.delegation →
    AllResolved d.policies s.policies ∧ AllResolved d.gates s.gates

abbrev PermitsRedelegation (ds : List Delegation) (e : ActsEdge) : Prop :=
  ∃ d ∈ ds, d.ref = e.delegation ∧ d.redelegationAllowed = true

abbrev ActsHolds (ds : List Delegation) (s : Snapshot) (e : ActsEdge)
    (action : String) (redelegated : Bool) : Prop :=
  ∃ d ∈ ds, Effective d s e action redelegated

instance (r : Option Nat) (t : Nat) : Decidable (ClearAt r t) := by
  cases r <;> infer_instance
instance (n b : Option Nat) : Decidable (RevocationRestricts n b) := by
  cases n <;> cases b <;> infer_instance
instance (rs : List Ref) (as_ : List Assessment) : Decidable (AllAccepted rs as_) := by
  unfold AllAccepted
  infer_instance
instance (rs : List Ref) (as_ : List Assessment) : Decidable (AllResolved rs as_) := by
  unfold AllResolved
  infer_instance
instance (d : Delegation) : Decidable (DelegationValid d) := by
  unfold DelegationValid
  infer_instance
instance (ds : List Delegation) (s : Snapshot) (e : ActsEdge) (a : String) :
    Decidable (ActsInventoryValid ds s e a) := by
  unfold ActsInventoryValid
  infer_instance
instance (ds : List Delegation) (e : ActsEdge) : Decidable (DelegationResolved ds e) := by
  unfold DelegationResolved
  infer_instance
instance (ds : List Delegation) (s : Snapshot) (e : ActsEdge) :
    Decidable (InterpretationKnown ds s e) := by
  unfold InterpretationKnown
  infer_instance
instance (ds : List Delegation) (e : ActsEdge) : Decidable (PermitsRedelegation ds e) := by
  unfold PermitsRedelegation
  infer_instance
instance (d : Delegation) (s : Snapshot) (e : ActsEdge) (a : String) (r : Bool) :
    Decidable (Effective d s e a r) := by
  unfold Effective
  infer_instance
instance (ds : List Delegation) (s : Snapshot) (e : ActsEdge) (a : String) (r : Bool) :
    Decidable (ActsHolds ds s e a r) := by
  unfold ActsHolds
  infer_instance

end Stress
