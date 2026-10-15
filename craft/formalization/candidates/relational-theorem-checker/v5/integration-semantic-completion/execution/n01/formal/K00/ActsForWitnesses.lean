import ActsForCandidate

set_option autoImplicit false

namespace RelationalSuccessor.CandidateActsFor.Witnesses
open RelationalSuccessor

-- Synthetic immutable records. This is a model instance, not a live grant.
def ref (name : String) : RevisionRef := ⟨⟨"fixture", name, "1"⟩, name⟩
def xScope : Scope := ⟨ref "X", [ref "file-X"]⟩
def interval : Window := ⟨ref "window", .interval "fixture-time" 0 10⟩
def sessionWindow : Window := ⟨ref "session-window", .session (ref "session")⟩
def readRight : Right := ⟨"read", ref "file-X", ref "X"⟩
def writeRight : Right := ⟨"write", ref "file-X", ref "X"⟩
def frame : Frame := ⟨ref "profile", ref "A", ref "P", ref "context",
  ref "X", ref "snapshot", 5, "fixture-time"⟩
def gate : Definition := ⟨ref "gate", .condition (.atom (ref "leaf")), [], ref "owner-review"⟩
def authorityRoot : AuthorityRoot := ⟨ref "root", ref "P", xScope, interval, [readRight]⟩
def parent : Delegation := ⟨ref "parent-delegation", ref "M", ref "P", ref "P",
  none, xScope, interval, [readRight], [ref "gate"], true⟩
def child : Delegation := ⟨ref "child-delegation", ref "A", ref "P", ref "M",
  some parent.ref, xScope, interval, [readRight], [ref "gate"], false⟩
def parentRevocation : Revocation := ⟨ref "parent-status", parent.ref,
  frame.snapshot, frame.epoch, frame.timeDomain, .unrevoked⟩
def childRevocation : Revocation := ⟨ref "child-status", child.ref,
  frame.snapshot, frame.epoch, frame.timeDomain, .unrevoked⟩
def sessionObservation : SessionObservation := ⟨ref "session", frame.snapshot,
  frame.epoch, frame.timeDomain, true⟩
def world : World := ⟨[xScope], [interval, sessionWindow], [parent, child],
  [authorityRoot], [sessionObservation], [parentRevocation, childRevocation],
  [gate], [gate], (fun _ _ => .yes), [readRight, writeRight]⟩
def useWitness : Use := ⟨ref "A", ref "P", frame, child, xScope,
  interval, childRevocation, readRight⟩
def identityState : ProtectedState := ⟨[(ref "A", 1), (ref "P", 2)],
  [(ref "file-X", ref "P")], [authorityRoot], [], []⟩

theorem scope_reflexive (scope : Scope) : ScopeWithin scope scope := by
  intro subject h; exact h

theorem rights_reflexive (rights : List Right) : RightsWithin rights rights := by
  intro right h; exact h

theorem gate_has_owned_positive_meaning :
    PositiveOwned world.conditionRoots world.conditionCatalog (ref "gate") frame
      world.gateEnvironment := by
  exact (owned_positive_exact world.conditionRoots world.conditionCatalog
    (ref "gate") frame world.gateEnvironment).mp (by decide)

theorem parent_locally_valid : LocalValid world frame parent := by
  refine ⟨by decide, by decide, by decide, by simp [WindowActive, parent, interval, frame], ?_,
    ⟨parentRevocation, by unfold LiveRevocation; decide⟩, ?_⟩
  · intro required h
    have same : required = ref "gate" := by simpa [parent] using h
    subst required
    exact gate_has_owned_positive_meaning
  · intro right h
    have same : right = readRight := by simpa [parent] using h
    subst right
    exact ⟨xScope, by decide, rfl, scope_reflexive xScope, by decide⟩

theorem child_locally_valid : LocalValid world frame child := by
  refine ⟨by decide, by decide, by decide, by simp [WindowActive, child, interval, frame], ?_,
    ⟨childRevocation, by unfold LiveRevocation; decide⟩, ?_⟩
  · intro required h
    have same : required = ref "gate" := by simpa [child] using h
    subst required
    exact gate_has_owned_positive_meaning
  · intro right h
    have same : right = readRight := by simpa [child] using h
    subst right
    exact ⟨xScope, by decide, rfl, scope_reflexive xScope, by decide⟩

theorem root_is_valid : RootValid world frame authorityRoot := by
  refine ⟨by decide, by decide, by decide,
    by simp [WindowActive, authorityRoot, interval, frame], ?_⟩
  intro right h
  have same : right = readRight := by simpa [authorityRoot] using h
  subst right
  decide

theorem legitimate_parent_chain : Chain world frame parent authorityRoot :=
  .root parent authorityRoot parent_locally_valid root_is_valid rfl rfl rfl
    (scope_reflexive xScope) (rights_reflexive [readRight])

theorem legitimate_redelegation_chain : Chain world frame child authorityRoot :=
  .child child parent authorityRoot child_locally_valid legitimate_parent_chain
    rfl rfl rfl rfl (scope_reflexive xScope) (rights_reflexive [readRight])

theorem legitimate_representation : Represents world useWitness := by
  exact ⟨rfl, rfl, rfl, rfl, rfl, by decide, scope_reflexive xScope,
    by decide, rfl, rfl, by unfold LiveRevocation; decide, by decide,
    authorityRoot, legitimate_redelegation_chain⟩

theorem session_is_active : WindowActive world frame sessionWindow := by
  exact ⟨sessionObservation, by decide, rfl, rfl, rfl, rfl, rfl⟩

theorem missing_session_observation_is_not_active :
    ¬ WindowActive { world with sessions := [] } frame sessionWindow := by
  simp [WindowActive, sessionWindow]

theorem wrong_session_snapshot_is_not_active :
    ¬ WindowActive { world with sessions :=
      [{ sessionObservation with snapshot := ref "other-snapshot" }] } frame sessionWindow := by
  simp [WindowActive, sessionWindow, sessionObservation, frame, ref]

theorem expiry_cannot_represent :
    ¬ Represents world { useWitness with frame := { frame with epoch := 10 } } := by
  apply inactive_leaf_cannot_represent
  simp [WindowActive, useWitness, child, interval, frame]

theorem wrong_agent_cannot_represent_example :
    ¬ Represents world { useWitness with sourceAgent := ref "B" } := by
  apply wrong_agent_cannot_represent
  decide

theorem unknown_revocation_cannot_represent_example :
    ¬ Represents world { useWitness with revocation :=
      { childRevocation with status := .unknown } } := by
  apply unknown_revocation_cannot_represent
  rfl

theorem revoked_cannot_represent_example :
    ¬ Represents world { useWitness with revocation :=
      { childRevocation with status := .revoked } } := by
  apply revoked_cannot_represent
  rfl

theorem unknown_required_gate_cannot_represent :
    ¬ Represents { world with gateEnvironment := fun _ _ => .unknown } useWitness := by
  apply required_unknown_gate_cannot_represent _ _ (ref "gate")
  · decide
  · decide

theorem rootless_world_cannot_represent :
    ¬ Represents { world with authorityRoots := [] } useWitness :=
  no_root_no_representation _ _ rfl

theorem agent_and_principal_have_distinct_identities :
    ¬ SameIdentity identityState (ref "A") (ref "P") := by
  simp [SameIdentity, identityState, ref]

theorem recording_does_not_transfer_file_ownership :
    ¬ OwnershipChanged identityState
      (record ⟨identityState, []⟩ useWitness).protectedState (ref "file-X") := by
  simp [OwnershipChanged, record, identityState]

theorem write_has_no_delegation_grant :
    ¬ DelegatedRight world frame (ref "A") writeRight := by
  rintro ⟨d, hd, root, _, _, write⟩
  have possibilities : d = parent ∨ d = child := by simpa [world] using hd
  rcases possibilities with hp | hc
  · subst d
    have notGranted : writeRight ∉ parent.rights := by decide
    exact notGranted write
  · subst d
    have notGranted : writeRight ∉ child.rights := by decide
    exact notGranted write

theorem agent_does_not_have_unrestricted_authority :
    ¬ UnrestrictedAuthority world frame (ref "A") := by
  intro h
  exact write_has_no_delegation_grant (h writeRight (by decide))

-- These are countermodels in this explicit candidate fragment, not yet in the
-- complete pinned 41-kind rule theory required for inherited discharge.
theorem identity_equivalence_non_entailment_witness :
    Represents world useWitness ∧ ¬ SameIdentity identityState (ref "A") (ref "P") :=
  ⟨legitimate_representation, agent_and_principal_have_distinct_identities⟩

theorem ownership_transfer_non_entailment_witness :
    Represents world useWitness ∧ ¬ OwnershipChanged identityState
      (record ⟨identityState, []⟩ useWitness).protectedState (ref "file-X") :=
  ⟨legitimate_representation, recording_does_not_transfer_file_ownership⟩

theorem unrestricted_authority_non_entailment_witness :
    Represents world useWitness ∧ ¬ UnrestrictedAuthority world frame (ref "A") :=
  ⟨legitimate_representation, agent_does_not_have_unrestricted_authority⟩

#print axioms scope_reflexive
#print axioms rights_reflexive
#print axioms gate_has_owned_positive_meaning
#print axioms parent_locally_valid
#print axioms child_locally_valid
#print axioms root_is_valid
#print axioms legitimate_parent_chain
#print axioms legitimate_redelegation_chain
#print axioms legitimate_representation
#print axioms session_is_active
#print axioms missing_session_observation_is_not_active
#print axioms wrong_session_snapshot_is_not_active
#print axioms expiry_cannot_represent
#print axioms wrong_agent_cannot_represent_example
#print axioms unknown_revocation_cannot_represent_example
#print axioms revoked_cannot_represent_example
#print axioms unknown_required_gate_cannot_represent
#print axioms rootless_world_cannot_represent
#print axioms agent_and_principal_have_distinct_identities
#print axioms recording_does_not_transfer_file_ownership
#print axioms write_has_no_delegation_grant
#print axioms agent_does_not_have_unrestricted_authority
#print axioms identity_equivalence_non_entailment_witness
#print axioms ownership_transfer_non_entailment_witness
#print axioms unrestricted_authority_non_entailment_witness
end RelationalSuccessor.CandidateActsFor.Witnesses
