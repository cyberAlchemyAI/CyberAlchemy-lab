import Init

namespace Stress

structure Ref where
  id : String
  version : String
  deriving DecidableEq, Repr

structure Period where
  start : Nat
  stop : Nat
  deriving DecidableEq, Repr

structure Assessment where
  ref : Ref
  accepted : Bool
  deriving DecidableEq, Repr

structure Snapshot where
  ref : Ref
  epoch : Nat
  policies : List Assessment
  gates : List Assessment
  deriving DecidableEq, Repr

structure Delegation where
  ref : Ref
  agent : Ref
  principal : Ref
  scopes : List String
  actions : List String
  period : Period
  revokedAt : Option Nat
  policies : List Ref
  gates : List Ref
  redelegationAllowed : Bool
  deriving DecidableEq, Repr

structure ActsEdge where
  id : String
  agent : Ref
  principal : Ref
  delegation : Ref
  scope : String
  period : Period
  revokedAt : Option Nat
  deriving DecidableEq, Repr

inductive Verdict where
  | yes | no | unknown | invalid
  deriving DecidableEq, Repr

inductive NormMode where
  | require | forbid | permit
  deriving DecidableEq, Repr

structure Norm where
  mode : NormMode
  action : String
  deriving DecidableEq, Repr

structure Contract where
  ref : Ref
  scope : String
  condition : String
  interpreted : Bool
  norms : List Norm
  deriving DecidableEq, Repr

structure Binding where
  ref : Ref
  subject : Ref
  contracts : List Ref
  scope : String
  active : Bool
  overrides : List Ref
  deriving DecidableEq, Repr

structure Inheritance where
  id : String
  subject : Ref
  contract : Ref
  binding : Ref
  scope : String
  condition : String
  deriving DecidableEq, Repr

structure Conformance where
  subject : Ref
  contract : Ref
  scope : String
  accepted : Bool
  deriving DecidableEq, Repr

structure Graph where
  inheritances : List Inheritance
  bindings : List Binding
  contracts : List Contract
  conformance : List Conformance
  deriving DecidableEq, Repr

structure Fact where
  edge : Inheritance
  norm : Norm
  deriving DecidableEq, Repr

inductive Rule where
  | propagate | forward
  deriving DecidableEq, Repr

structure Step where
  rule : Rule
  fact : Fact
  parent : Option Nat
  deriving DecidableEq, Repr

abbrev RefValid (r : Ref) : Prop := r.id ≠ "" ∧ r.version ≠ ""
abbrev PeriodValid (p : Period) : Prop := p.start < p.stop

end Stress
