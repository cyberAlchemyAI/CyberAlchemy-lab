import SharedSemantics

-- N01 candidate-model preparation only. No accepted K00 meaning, raw source
-- decoder, runtime permission, authenticity, or inherited discharge is claimed.
namespace RelationalSuccessor.CandidateActsFor
open RelationalSuccessor

structure Scope where
  ref : RevisionRef
  subjects : List RevisionRef
  deriving DecidableEq, Repr

structure Right where
  action : String
  subject : RevisionRef
  scope : RevisionRef
  deriving DecidableEq, Repr

inductive WindowBody where
  | interval (timeDomain : String) (start stop : Nat)
  | session (session : RevisionRef)
  deriving DecidableEq, Repr

structure Window where
  ref : RevisionRef
  body : WindowBody
  deriving DecidableEq, Repr

structure SessionObservation where
  session : RevisionRef
  snapshot : RevisionRef
  epoch : Nat
  timeDomain : String
  active : Bool
  deriving DecidableEq, Repr

inductive RevocationStatus where
  | unrevoked | revoked | unknown
  deriving DecidableEq, Repr

structure Revocation where
  ref : RevisionRef
  delegation : RevisionRef
  snapshot : RevisionRef
  epoch : Nat
  timeDomain : String
  status : RevocationStatus
  deriving DecidableEq, Repr

structure Delegation where
  ref : RevisionRef
  agent : RevisionRef
  principal : RevisionRef
  issuer : RevisionRef
  parent : Option RevisionRef
  scope : Scope
  window : Window
  rights : List Right
  gates : List RevisionRef
  mayRedelegate : Bool
  deriving DecidableEq, Repr

structure AuthorityRoot where
  ref : RevisionRef
  issuer : RevisionRef
  scope : Scope
  window : Window
  rights : List Right
  deriving DecidableEq, Repr

-- Each list is independently owned/observed context, not a request-provided
-- "approved" flag. Authentic capture of these lists remains an explicit premise.
structure World where
  scopes : List Scope
  windows : List Window
  delegations : List Delegation
  authorityRoots : List AuthorityRoot
  sessions : List SessionObservation
  revocations : List Revocation
  conditionRoots : List Definition
  conditionCatalog : Catalog
  gateEnvironment : Frame → RevisionRef → Truth
  universe : List Right

def ScopeWithin (inner outer : Scope) : Prop :=
  ∀ subject ∈ inner.subjects, subject ∈ outer.subjects

def RightsWithin (inner outer : List Right) : Prop :=
  ∀ right ∈ inner, right ∈ outer

def WindowActive (w : World) (f : Frame) (window : Window) : Prop :=
  match window.body with
  | .interval domain start stop =>
      domain = f.timeDomain ∧ start ≤ f.epoch ∧ f.epoch < stop
  | .session session =>
      ∃ observation ∈ w.sessions,
        observation.session = session ∧ observation.snapshot = f.snapshot ∧
        observation.epoch = f.epoch ∧ observation.timeDomain = f.timeDomain ∧
        observation.active = true

def LiveRevocation (w : World) (f : Frame) (d : Delegation) (r : Revocation) : Prop :=
  r ∈ w.revocations ∧ r.delegation = d.ref ∧ r.snapshot = f.snapshot ∧
  r.epoch = f.epoch ∧ r.timeDomain = f.timeDomain ∧ r.status = .unrevoked

structure LocalValid (w : World) (f : Frame) (d : Delegation) : Prop where
  member : d ∈ w.delegations
  scope : d.scope ∈ w.scopes
  window : d.window ∈ w.windows
  active : WindowActive w f d.window
  gates : ∀ gate ∈ d.gates,
    PositiveOwned w.conditionRoots w.conditionCatalog gate f w.gateEnvironment
  revocation : ∃ revocation, LiveRevocation w f d revocation
  scopedRights : ∀ right ∈ d.rights, ∃ scope ∈ w.scopes,
    scope.ref = right.scope ∧ ScopeWithin scope d.scope ∧ right.subject ∈ scope.subjects

def RootValid (w : World) (f : Frame) (root : AuthorityRoot) : Prop :=
  root ∈ w.authorityRoots ∧ root.scope ∈ w.scopes ∧ root.window ∈ w.windows ∧
  WindowActive w f root.window ∧ RightsWithin root.rights w.universe

-- The semantic chain is inductive, independent of a traversal algorithm. Every
-- finite derivation needs an independently supplied authority root. Each child
-- inherits all ancestor bounds, rather than checking only its immediate label.
inductive Chain (w : World) (f : Frame) : Delegation → AuthorityRoot → Prop where
  | root (d : Delegation) (root : AuthorityRoot)
      (local : LocalValid w f d) (trusted : RootValid w f root)
      (noParent : d.parent = none) (issuer : d.issuer = root.issuer)
      (principal : d.principal = root.issuer)
      (scope : ScopeWithin d.scope root.scope)
      (rights : RightsWithin d.rights root.rights) : Chain w f d root
  | child (d parent : Delegation) (root : AuthorityRoot)
      (local : LocalValid w f d) (ancestor : Chain w f parent root)
      (parentRef : d.parent = some parent.ref) (issuer : d.issuer = parent.agent)
      (principal : d.principal = parent.principal)
      (redelegation : parent.mayRedelegate = true)
      (scope : ScopeWithin d.scope parent.scope)
      (rights : RightsWithin d.rights parent.rights) : Chain w f d root

structure Use where
  sourceAgent : RevisionRef
  targetPrincipal : RevisionRef
  frame : Frame
  delegation : Delegation
  scope : Scope
  window : Window
  revocation : Revocation
  proposed : Right
  deriving DecidableEq, Repr

-- This is a resolved witness, not a decoding of the four raw string qualifiers.
-- The proposed action/subject is explicit primary-witness context; source mapping
-- and owner assessment must decide its exact binding, not invent it from an edge.
structure Represents (w : World) (u : Use) : Prop where
  agent : u.delegation.agent = u.sourceAgent
  principal : u.delegation.principal = u.targetPrincipal
  frameSubject : u.frame.subject = u.sourceAgent
  frameTarget : u.frame.target = u.targetPrincipal
  frameScope : u.frame.scope = u.scope.ref
  ownedScope : u.scope ∈ w.scopes
  scopeWithin : ScopeWithin u.scope u.delegation.scope
  rightSubject : u.proposed.subject ∈ u.scope.subjects
  rightScope : u.proposed.scope = u.scope.ref
  exactWindow : u.window = u.delegation.window
  revocation : LiveRevocation w u.frame u.delegation u.revocation
  right : u.proposed ∈ u.delegation.rights
  chain : ∃ root, Chain w u.frame u.delegation root

theorem chain_has_root (w : World) (f : Frame) (d : Delegation) (root : AuthorityRoot)
    (h : Chain w f d root) : root ∈ w.authorityRoots := by
  induction h with
  | root _ _ _ trusted _ _ _ _ _ => exact trusted.1
  | child _ _ _ _ _ _ _ _ _ _ _ ih => exact ih

theorem chain_root_rights (w : World) (f : Frame) (d : Delegation) (root : AuthorityRoot)
    (h : Chain w f d root) : RightsWithin d.rights root.rights := by
  induction h with
  | root _ _ _ _ _ _ _ _ rights => exact rights
  | child _ _ _ _ _ _ _ _ _ _ rights ih =>
      intro right hd; exact ih right (rights right hd)

theorem chain_root_scope (w : World) (f : Frame) (d : Delegation) (root : AuthorityRoot)
    (h : Chain w f d root) : ScopeWithin d.scope root.scope := by
  induction h with
  | root _ _ _ _ _ _ _ scope _ => exact scope
  | child _ _ _ _ _ _ _ _ _ scope _ ih =>
      intro subject hd; exact ih subject (scope subject hd)

theorem chain_local_valid (w : World) (f : Frame) (d : Delegation) (root : AuthorityRoot)
    (h : Chain w f d root) : LocalValid w f d := by
  cases h with
  | root _ _ local _ _ _ _ _ _ => exact local
  | child _ _ _ local _ _ _ _ _ _ _ => exact local

theorem no_root_no_representation (w : World) (u : Use)
    (empty : w.authorityRoots = []) : ¬ Represents w u := by
  intro representation
  rcases representation.chain with ⟨root, chain⟩
  have h := chain_has_root w u.frame u.delegation root chain
  simp [empty] at h

theorem representation_stays_in_root_envelope (w : World) (u : Use)
    (h : Represents w u) :
    ∃ root ∈ w.authorityRoots, u.proposed ∈ root.rights ∧
      ScopeWithin u.scope root.scope := by
  rcases h.chain with ⟨root, chain⟩
  refine ⟨root, chain_has_root w u.frame u.delegation root chain,
    chain_root_rights w u.frame u.delegation root chain u.proposed h.right, ?_⟩
  intro subject hs
  exact chain_root_scope w u.frame u.delegation root chain subject (h.scopeWithin subject hs)

theorem wrong_agent_cannot_represent (w : World) (u : Use)
    (wrong : u.delegation.agent ≠ u.sourceAgent) : ¬ Represents w u := by
  intro h; exact wrong h.agent

theorem revoked_cannot_represent (w : World) (u : Use)
    (revoked : u.revocation.status = .revoked) : ¬ Represents w u := by
  intro h
  have active := h.revocation.2.2.2.2.2
  simp [revoked] at active

theorem unknown_revocation_cannot_represent (w : World) (u : Use)
    (unknown : u.revocation.status = .unknown) : ¬ Represents w u := by
  intro h
  have active := h.revocation.2.2.2.2.2
  simp [unknown] at active

theorem inactive_leaf_cannot_represent (w : World) (u : Use)
    (inactive : ¬ WindowActive w u.frame u.delegation.window) : ¬ Represents w u := by
  intro h
  rcases h.chain with ⟨root, chain⟩
  exact inactive (chain_local_valid w u.frame u.delegation root chain).active

theorem required_unknown_gate_cannot_represent (w : World) (u : Use) (gate : RevisionRef)
    (required : gate ∈ u.delegation.gates)
    (unknown : ownedValue w.conditionRoots w.conditionCatalog gate u.frame
      w.gateEnvironment = .unknown) : ¬ Represents w u := by
  intro h
  rcases h.chain with ⟨root, chain⟩
  have positive := (chain_local_valid w u.frame u.delegation root chain).gates gate required
  have yes := (owned_positive_exact w.conditionRoots w.conditionCatalog gate u.frame
    w.gateEnvironment).mpr positive
  simp [unknown] at yes

-- A relation-record append changes only the record list in this candidate model.
-- Identical-revision idempotence, conflicting-content rejection, source provenance
-- and crash-safe public execution are separate N02/N09 implementation obligations.
structure ProtectedState where
  identities : List (RevisionRef × Nat)
  owners : List (RevisionRef × RevisionRef)
  authorityRoots : List AuthorityRoot
  admissions : List RevisionRef
  externalState : List UInt8
  deriving DecidableEq, Repr

structure State where
  protected : ProtectedState
  records : List Use
  deriving DecidableEq, Repr

def record (state : State) (u : Use) : State :=
  { state with records := state.records ++ [u] }

theorem recording_preserves_protected_state (state : State) (u : Use) :
    (record state u).protected = state.protected := rfl

def SameIdentity (state : ProtectedState) (a b : RevisionRef) : Prop :=
  ∃ identity, (a, identity) ∈ state.identities ∧ (b, identity) ∈ state.identities

def OwnershipChanged (before after : ProtectedState) (artifact : RevisionRef) : Prop :=
  ∃ oldOwner newOwner, oldOwner ≠ newOwner ∧
    (artifact, oldOwner) ∈ before.owners ∧ (artifact, newOwner) ∈ after.owners

-- This searches every independently supplied delegation, including independent
-- grants. It does not define authority as merely the rights of u.delegation.
def DelegatedRight (w : World) (f : Frame) (actor : RevisionRef) (right : Right) : Prop :=
  ∃ d ∈ w.delegations, ∃ root, Chain w f d root ∧
    d.agent = actor ∧ right ∈ d.rights

def UnrestrictedAuthority (w : World) (f : Frame) (actor : RevisionRef) : Prop :=
  ∀ right ∈ w.universe, DelegatedRight w f actor right

#print axioms chain_has_root
#print axioms chain_root_rights
#print axioms chain_root_scope
#print axioms chain_local_valid
#print axioms no_root_no_representation
#print axioms representation_stays_in_root_envelope
#print axioms wrong_agent_cannot_represent
#print axioms revoked_cannot_represent
#print axioms unknown_revocation_cannot_represent
#print axioms inactive_leaf_cannot_represent
#print axioms required_unknown_gate_cannot_represent
#print axioms recording_preserves_protected_state
end RelationalSuccessor.CandidateActsFor
