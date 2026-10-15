import Lean

namespace CandidateConclusionAnchors

inductive Sort where
  | ref | frame | epoch | effect | universe | value | result | world
  deriving DecidableEq, Repr

def witnessSlots : Nat → List (String × Sort)
  | 0 => []
  | 1 => []
  | 2 => [("resolution", .ref)]
  | 3 => []
  | 4 => [("sessionOrAction", .ref)]
  | 5 => []
  | 6 => []
  | 7 => []
  | 8 => []
  | 9 => []
  | 10 => []
  | 11 => []
  | 12 => []
  | 13 => [("control", .ref)]
  | 14 => [("effect", .effect)]
  | 15 => []
  | 16 => []
  | 17 => []
  | 18 => [("proposition", .ref)]
  | 19 => []
  | 20 => []
  | 21 => []
  | 22 => []
  | 23 => []
  | 24 => []
  | 25 => []
  | 26 => []
  | 27 => []
  | 28 => []
  | 29 => []
  | 30 => []
  | 31 => []
  | 32 => []
  | 33 => []
  | 34 => []
  | 35 => []
  | 36 => []
  | 37 => []
  | 38 => []
  | 39 => []
  | 40 => []
  | _ => []

def frameSlots : List (String × Sort) := [
  ("scope", .ref), ("epoch", .epoch), ("timeDomain", .ref), ("evidencePolicy", .ref), ("theory", .ref), ("frame", .frame), ("ownedUniverse", .universe)
]

inductive Term (unit : Nat) : Sort → Type where
  | source : Term unit .ref
  | target : Term unit .ref
  | witnessField {sort : Sort} (name : String) (declared : (name, sort) ∈ witnessSlots unit) : Term unit sort
  | frameField {sort : Sort} (name : String) (declared : (name, sort) ∈ frameSlots) : Term unit sort
  | variable {sort : Sort} (name : String) : Term unit sort

inductive Args (unit : Nat) : List Sort → Type where
  | nil : Args unit []
  | cons {sort : Sort} {tail : List Sort} : Term unit sort → Args unit tail → Args unit (sort :: tail)

structure Binder (unit : Nat) where
  name : String
  sort : Sort
  domain : String
  selectionRole : String
  joins : List (String × Sigma (Term unit))

inductive Constraint (unit : Nat) where
  | notEqual {sort : Sort} : Term unit sort → Term unit sort → Constraint unit

def termVariables {unit : Nat} {sort : Sort} : Term unit sort → List (String × Sort)
  | .variable name => [(name, sort)]
  | _ => []

def termParticipant {unit : Nat} {sort : Sort} : Term unit sort → Bool
  | .source => true
  | .target => true
  | .witnessField _ _ => true
  | _ => false

def argsVariables {unit : Nat} {sorts : List Sort} : Args unit sorts → List (String × Sort)
  | .nil => []
  | .cons head tail => termVariables head ++ argsVariables tail

def constraintVariables {unit : Nat} : Constraint unit → List (String × Sort)
  | .notEqual left right => termVariables left ++ termVariables right

def knownVariables (available needed : List (String × Sort)) : Bool :=
  needed.all fun key => available.contains key

def validBinderPrefix {unit : Nat} : List (String × Sort) → List (Binder unit) → Bool
  | _, [] => true
  | available, binder :: tail =>
      !binder.name.isEmpty && !binder.domain.isEmpty && !binder.selectionRole.isEmpty &&
      !(available.map Prod.fst).contains binder.name && !binder.joins.isEmpty &&
      (binder.joins.any fun join => termParticipant join.2.2) &&
      (binder.joins.all fun join => !join.1.isEmpty && knownVariables available (termVariables join.2.2)) &&
      validBinderPrefix ((binder.name, binder.sort) :: available) tail

def planValid {unit : Nat} {sorts : List Sort} (args : Args unit sorts)
    (binders : List (Binder unit)) (constraints : List (Constraint unit)) : Bool :=
  validBinderPrefix [] binders &&
  knownVariables (binders.map fun b => (b.name, b.sort)) (argsVariables args) &&
  (constraints.all fun c => knownVariables (binders.map fun b => (b.name, b.sort)) (constraintVariables c)) &&
  (binders.all fun b => (argsVariables args).contains (b.name,b.sort) ||
    binders.any fun later => later.joins.any fun join => (termVariables join.2.2).contains (b.name,b.sort))

structure Plan (unit : Nat) (sorts : List Sort) where
  obligationId : String
  sourceKind : String
  targetKind : String
  branchIndex : Nat
  arguments : Args unit sorts
  binders : List (Binder unit)
  constraints : List (Constraint unit)
  structurallyValid : planValid arguments binders constraints = true

-- This proof field certifies anchor syntax/typing only. No World, Meaning,
-- conclusion truth, source authenticity or countermodel is asserted here.
end CandidateConclusionAnchors
