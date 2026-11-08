import DelegationSemantics
import ObligationSemantics

namespace Stress

def checkActs (ds : List Delegation) (s : Snapshot) (e : ActsEdge)
    (action : String) (redelegated : Bool) : Verdict :=
  if ¬ ActsInventoryValid ds s e action then .invalid
  else if ¬ DelegationResolved ds e then .unknown
  else if ¬ InterpretationKnown ds s e then .unknown
  else if redelegated = true ∧ PermitsRedelegation ds e then .unknown
  else if ActsHolds ds s e action redelegated then .yes else .no

def candidateFacts (g : Graph) : List Fact :=
  g.inheritances.flatMap fun e => g.contracts.flatMap fun c =>
    c.norms.map fun n => { edge := e, norm := n }

def closure (g : Graph) : List Fact :=
  ((candidateFacts g).filter fun f => decide (Origin g f)).eraseDups

def conflicts (g : Graph) : List (Fact × Fact) :=
  (closure g).flatMap fun f => (closure g).filterMap fun h =>
    if ConflictPair f h then some (f,h) else none

def workUnits (g : Graph) : Nat := (candidateFacts g).length + (closure g).length * (closure g).length

def checkInheritance (g : Graph) (budget : Nat) : Verdict :=
  if ¬ GraphValid g then .invalid
  else if ¬ InheritanceKnown g then .unknown
  else if ¬ InheritanceMatches g then .invalid
  else if workUnits g > budget then .unknown
  else .yes

abbrev StepShape (steps : List Step) (s : Step) (i : Nat) : Prop :=
  match s.rule with
  | .propagate => s.parent = none
  | .forward => match s.parent with
    | none => False
    | some p => p < i ∧ match steps[p]? with
      | none => False
      | some prior => prior.fact = s.fact

abbrev ReplayShape (steps : List Step) : Prop :=
  ∀ pair ∈ steps.zipIdx, StepShape steps pair.1 pair.2

abbrev CertificateValid (g : Graph) (steps : List Step) : Prop :=
  ReplayShape steps ∧ ∀ s ∈ steps, Origin g s.fact

instance (steps : List Step) (s : Step) (i : Nat) : Decidable (StepShape steps s i) := by
  unfold StepShape
  cases hr : s.rule with
  | propagate => infer_instance
  | forward =>
    cases hp : s.parent with
    | none => infer_instance
    | some p =>
      simp only
      cases steps[p]? <;> simp only <;> infer_instance

instance (steps : List Step) : Decidable (ReplayShape steps) := by
  unfold ReplayShape
  infer_instance

instance (g : Graph) (steps : List Step) : Decidable (CertificateValid g steps) := by
  unfold CertificateValid
  infer_instance

def checkCertificate (g : Graph) (steps : List Step) : Bool := decide (CertificateValid g steps)

end Stress
