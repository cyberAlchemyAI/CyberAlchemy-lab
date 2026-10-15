namespace RelationalGateClosure

inductive Gate where
  | r06 | g4
  deriving DecidableEq, Repr

inductive Answer where
  | accepted | revisions | undecided
  deriving DecidableEq, Repr

structure Binding where
  path : String
  digest : String
  deriving DecidableEq, Repr

structure Challenge where
  gate : Gate
  scope : String
  mandatory : List Binding
  deriving DecidableEq, Repr

structure Feedback where
  gate : Gate
  scope : String
  reviewed : List Binding
  first : Answer
  second : Answer
  -- A faithfully captured human response is an explicit premise. This model
  -- does not authenticate an external person from a JSON field or quote.
  faithfullyCaptured : Bool
  candidateOnly : Bool
  deriving DecidableEq, Repr

structure State where
  r06 : Bool
  g4 : Bool
  prior : List Binding
  history : List Gate
  deriving DecidableEq, Repr

-- The independent target requires every mandatory identity and excludes any
-- extra/substituted binding. Order is not part of the review meaning.
def Reviewed (c : Challenge) (f : Feedback) : Prop :=
  c.mandatory ≠ [] ∧ c.mandatory.Nodup ∧ f.reviewed.Nodup ∧
  (∀ b ∈ c.mandatory, b ∈ f.reviewed) ∧
  (∀ b ∈ f.reviewed, b ∈ c.mandatory)

def checkedBindings (c : Challenge) (f : Feedback) : Bool :=
  !c.mandatory.isEmpty && decide c.mandatory.Nodup && decide f.reviewed.Nodup &&
  c.mandatory.all f.reviewed.contains && f.reviewed.all c.mandatory.contains

theorem binding_check_exact (c : Challenge) (f : Feedback) :
    checkedBindings c f = true ↔ Reviewed c f := by
  simp [checkedBindings, Reviewed, List.all_eq_true, and_assoc]

def Prerequisite (s : State) : Gate → Prop
  | .r06 => s.r06 = false ∧ s.g4 = false
  | .g4 => s.r06 = true ∧ s.g4 = false

instance (s : State) (g : Gate) : Decidable (Prerequisite s g) := by
  cases g <;> unfold Prerequisite <;> infer_instance

def Eligible (s : State) (c : Challenge) (f : Feedback) : Prop :=
  Prerequisite s c.gate ∧ f.gate = c.gate ∧ f.scope = c.scope ∧
  Reviewed c f ∧ f.first = .accepted ∧ f.second = .accepted ∧
  f.faithfullyCaptured = true ∧ f.candidateOnly = true

def checkedEligible (s : State) (c : Challenge) (f : Feedback) : Bool :=
  decide (Prerequisite s c.gate) && decide (f.gate = c.gate) &&
  decide (f.scope = c.scope) && checkedBindings c f &&
  decide (f.first = .accepted) && decide (f.second = .accepted) &&
  f.faithfullyCaptured && f.candidateOnly

theorem eligibility_exact (s : State) (c : Challenge) (f : Feedback) :
    checkedEligible s c f = true ↔ Eligible s c f := by
  simp [checkedEligible, Eligible, binding_check_exact, and_assoc]

def advance (s : State) (g : Gate) : State :=
  match g with
  | .r06 => { s with r06 := true, history := s.history ++ [.r06] }
  | .g4 => { s with g4 := true, history := s.history ++ [.g4] }

def transition (s : State) (c : Challenge) (f : Feedback) : Option State :=
  if checkedEligible s c f then some (advance s c.gate) else none

theorem transition_exact (s : State) (c : Challenge) (f : Feedback) (out : State) :
    transition s c f = some out ↔ Eligible s c f ∧ out = advance s c.gate := by
  unfold transition
  split
  · rename_i h; simp [(eligibility_exact s c f).mp h, eq_comm]
  · rename_i h
    have hn : ¬ Eligible s c f := fun he => h ((eligibility_exact s c f).mpr he)
    simp [hn]

theorem acceptance_requires_all_bindings (s : State) (c : Challenge) (f : Feedback)
    (out : State) (h : transition s c f = some out) :
    ∀ b ∈ c.mandatory, b ∈ f.reviewed :=
  ((transition_exact s c f out).mp h).1.2.2.2.1.2.2.2.1

theorem different_scope_cannot_accept (s : State) (c : Challenge) (f : Feedback)
    (h : f.scope ≠ c.scope) : transition s c f = none := by
  unfold transition
  split
  · rename_i he
    exact False.elim (h ((eligibility_exact s c f).mp he).2.2.1)
  · rfl

theorem nonpositive_feedback_cannot_accept (s : State) (c : Challenge) (f : Feedback)
    (h : f.first ≠ .accepted ∨ f.second ≠ .accepted) : transition s c f = none := by
  unfold transition
  split
  · rename_i he
    have e := (eligibility_exact s c f).mp he
    rcases h with hf | hs
    · exact False.elim (hf e.2.2.2.2.1)
    · exact False.elim (hs e.2.2.2.2.2.1)
  · rfl

theorem g4_requires_r06 (s : State) (c : Challenge) (f : Feedback) (out : State)
    (hg : c.gate = .g4) (h : transition s c f = some out) : s.r06 = true := by
  have hp := ((transition_exact s c f out).mp h).1.1
  rw [hg] at hp
  exact hp.1

theorem prior_evidence_preserved (s : State) (c : Challenge) (f : Feedback) (out : State)
    (h : transition s c f = some out) : out.prior = s.prior := by
  rw [((transition_exact s c f out).mp h).2]
  cases c.gate <;> rfl

theorem history_appended (s : State) (c : Challenge) (f : Feedback) (out : State)
    (h : transition s c f = some out) : out.history = s.history ++ [c.gate] := by
  rw [((transition_exact s c f out).mp h).2]
  cases c.gate <;> rfl

#print axioms binding_check_exact
#print axioms eligibility_exact
#print axioms transition_exact
#print axioms acceptance_requires_all_bindings
#print axioms different_scope_cannot_accept
#print axioms nonpositive_feedback_cannot_accept
#print axioms g4_requires_r06
#print axioms prior_evidence_preserved
#print axioms history_appended
end RelationalGateClosure
