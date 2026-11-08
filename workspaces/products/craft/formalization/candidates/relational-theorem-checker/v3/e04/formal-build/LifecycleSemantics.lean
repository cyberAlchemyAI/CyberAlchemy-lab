import Std
namespace RelationalExtensions.Lifecycle
structure Ref where
  id : String
  version : String
  deriving DecidableEq, Repr
inductive Truth where
  | yes | no | unknown
  deriving DecidableEq, Repr
structure State where
  store : String
  context : Ref
  epoch : Nat
  head : Ref
  generation : Nat
  history : List Ref
  evidence : List String
  deriving DecidableEq, Repr
structure Change where
  store : String
  context : Ref
  epoch : Nat
  predecessor : Ref
  successor : Ref
  expected : Nat
  declared : Bool
  eligibility : Truth
  reviewHead : Ref
  reviewSuccessor : Ref
  reviewGeneration : Nat
  reviewContext : Ref
  reviewEpoch : Nat
  reviewed : Bool
  evidence : String
  deriving DecidableEq, Repr
def Policy (s : State) (c : Change) : Prop :=
  s.head ∈ s.history ∧ c.store = s.store ∧ c.context = s.context ∧ c.epoch = s.epoch ∧
  c.predecessor = s.head ∧ c.expected = s.generation ∧ c.successor ∉ s.history ∧
  c.declared = true ∧ c.eligibility = .yes ∧ c.reviewed = true ∧
  c.reviewHead = s.head ∧ c.reviewSuccessor = c.successor ∧ c.reviewGeneration = s.generation ∧
  c.reviewContext = s.context ∧ c.reviewEpoch = s.epoch
instance (s : State) (c : Change) : Decidable (Policy s c) := inferInstanceAs (Decidable (_ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _))
def advance (s : State) (c : Change) : State :=
  { s with head := c.successor, generation := s.generation + 1, history := s.history ++ [c.successor], evidence := s.evidence ++ [c.evidence] }
def transition (s : State) (c : Change) : Option State :=
  if Policy s c then some (advance s c) else none
theorem transition_exact (s : State) (c : Change) (out : State) :
    transition s c = some out ↔ Policy s c ∧ out = advance s c := by
  unfold transition
  split
  · rename_i h; simp [h, eq_comm]
  · rename_i h; simp [h]
theorem history_and_evidence_preserved (s : State) (c : Change) (out : State)
    (h : transition s c = some out) :
    out.history = s.history ++ [c.successor] ∧ out.evidence = s.evidence ++ [c.evidence] ∧
    out.head = c.successor ∧ out.generation = s.generation+1 := by
  rw [((transition_exact s c out).mp h).2]
  exact ⟨rfl, rfl, rfl, rfl⟩
theorem no_historical_reactivation (s : State) (c : Change) (out : State)
    (h : transition s c = some out) : c.successor ∉ s.history :=
  ((transition_exact s c out).mp h).1.2.2.2.2.2.2.1
theorem declaration_alone_cannot_transition (s : State) (c : Change)
    (h : c.eligibility ≠ .yes) : transition s c = none := by
  unfold transition
  split
  · rename_i hp
    exact False.elim (h hp.2.2.2.2.2.2.2.2.1)
  · rfl
#print axioms transition_exact
#print axioms history_and_evidence_preserved
#print axioms no_historical_reactivation
#print axioms declaration_alone_cannot_transition
end RelationalExtensions.Lifecycle
