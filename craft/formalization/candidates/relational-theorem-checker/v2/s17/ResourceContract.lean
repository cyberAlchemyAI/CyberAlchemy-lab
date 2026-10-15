import ClosureAdequacy
namespace Successor.Resource
open Inference
structure Budget where
  groundCandidates : Nat
  atomCandidates : Nat
  conflictPairs : Nat
  steps : Nat
  deriving DecidableEq
-- Bounds are computed before constructing products. Operational exhaustion is
-- a separate outcome and cannot supply an absence or readiness certificate.
inductive Outcome where
  | complete | invalid | unsupported | unknownResource
  deriving DecidableEq
abbrev CanClaimAbsence (outcome : Outcome) (closureChecked : Bool) : Prop :=
  outcome = .complete ∧ closureChecked = true
theorem exhaustion_no_absence (checked : Bool) : ¬ CanClaimAbsence .unknownResource checked := by
  simp [CanClaimAbsence]
def assignmentBound (domain variables : Nat) : Nat := domain ^ variables
def groundBound (T : Theory) : Nat :=
  (T.rules.map fun r => assignmentBound T.domain.length r.variables.length).sum
def atomBound (T : Theory) : Nat :=
  (T.predicates.map fun p => assignmentBound T.domain.length p.sorts.length).sum
theorem sum_const (domain : List Value) (n : Nat) : (domain.map fun _ => n).sum = domain.length * n := by
  induction domain with
  | nil => simp
  | cons v rest ih => simp [ih,Nat.succ_mul,Nat.add_comm]
theorem choices_length (domain : List Value) (n : Nat) :
    (choices domain n).length = domain.length ^ n := by
  induction n with
  | zero => simp [choices]
  | succ n ih =>
      simp [choices,List.length_flatMap,List.length_map,ih,sum_const,Nat.pow_succ,Nat.mul_comm]
#print axioms choices_length
#print axioms exhaustion_no_absence
end Successor.Resource
