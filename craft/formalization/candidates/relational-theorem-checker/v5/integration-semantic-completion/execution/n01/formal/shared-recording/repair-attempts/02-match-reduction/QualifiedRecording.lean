import SharedSemantics

set_option autoImplicit false

namespace RelationalSuccessor.CandidateRecording
open RelationalSuccessor

structure Envelope (α : Type) where
  ref : RevisionRef
  body : α
  deriving DecidableEq, Repr

structure State (α β : Type) where
  protectedState : β
  records : List (Envelope α)

inductive Outcome where
  | appended | retained | unqualified | malformedStore | revisionConflict
  deriving DecidableEq, Repr

structure Result (α β : Type) where
  outcome : Outcome
  state : State α β

-- An independently specified store invariant, rather than a supplied validity flag.
def StoreMeaning {α : Type} : List (Envelope α) → Prop
  | [] => True
  | first :: rest => StoreMeaning rest ∧
      ∀ later ∈ rest, first.ref.key ≠ later.ref.key

def storeCheck {α : Type} : List (Envelope α) → Bool
  | [] => true
  | first :: rest => storeCheck rest &&
      rest.all (fun later => decide (first.ref.key ≠ later.ref.key))

def lookup {α : Type} : List (Envelope α) → RevisionKey → Option (Envelope α)
  | [], _ => none
  | first :: rest, key => if first.ref.key = key then some first else lookup rest key

-- The generic proof requires a checker/meaning equivalence. Concrete adapters fix
-- the checker; the eventual public interface must not accept a caller's callback.
def submit {α β : Type} [DecidableEq α] (check : Envelope α → Bool)
    (before : State α β) (proposal : Envelope α) : Result α β :=
  if check proposal then
    if storeCheck before.records then
      match lookup before.records proposal.ref.key with
      | none => ⟨.appended, { before with records := before.records ++ [proposal] }⟩
      | some existing => if existing = proposal then ⟨.retained, before⟩
          else ⟨.revisionConflict, before⟩
    else ⟨.malformedStore, before⟩
  else ⟨.unqualified, before⟩

theorem store_check_exact {α : Type} (records : List (Envelope α)) :
    storeCheck records = true ↔ StoreMeaning records := by
  induction records with
  | nil => simp [storeCheck, StoreMeaning]
  | cons first rest ih => simp [storeCheck, StoreMeaning, ih, List.all_eq_true]

theorem lookup_sound {α : Type} (records : List (Envelope α)) (key : RevisionKey)
    (record : Envelope α) (found : lookup records key = some record) :
    record ∈ records ∧ record.ref.key = key := by
  induction records with
  | nil => simp [lookup] at found
  | cons first rest ih =>
    unfold lookup at found
    split at found
    · rename_i same; cases found
      exact ⟨by simp, same⟩
    · have tail := ih found
      exact ⟨by simp [tail.1], tail.2⟩

theorem lookup_none_exact {α : Type} (records : List (Envelope α)) (key : RevisionKey) :
    lookup records key = none ↔ ∀ record ∈ records, record.ref.key ≠ key := by
  induction records with
  | nil => simp [lookup]
  | cons first rest ih =>
    unfold lookup
    split
    · rename_i same
      constructor
      · intro impossible; cases impossible
      · intro missing
        exact False.elim (missing first (by simp) same)
    · rename_i different
      constructor
      · intro missing record member
        have parts := ih.mp missing
        simp only [List.mem_cons] at member
        rcases member with atHead | atTail
        · subst record; exact different
        · exact parts record atTail
      · intro missing
        exact ih.mpr (by intro record member; exact missing record (by simp [member]))

theorem append_preserves_store_meaning {α : Type} (records : List (Envelope α))
    (proposal : Envelope α) (valid : StoreMeaning records)
    (fresh : ∀ record ∈ records, record.ref.key ≠ proposal.ref.key) :
    StoreMeaning (records ++ [proposal]) := by
  induction records with
  | nil => simp [StoreMeaning]
  | cons first rest ih =>
    refine ⟨ih valid.1 (by intro record member; exact fresh record (by simp [member])), ?_⟩
    intro later member
    rcases List.mem_append.mp member with old | new
    · exact valid.2 later old
    · have same : later = proposal := List.mem_singleton.mp new
      subst later; exact fresh first (by simp)

theorem unqualified_preserves_state {α β : Type} [DecidableEq α]
    (check : Envelope α → Bool) (before : State α β) (proposal : Envelope α)
    (unqualified : check proposal = false) :
    submit check before proposal = ⟨.unqualified, before⟩ := by
  simp [submit, unqualified]

theorem malformed_store_refuses {α β : Type} [DecidableEq α]
    (check : Envelope α → Bool) (before : State α β) (proposal : Envelope α)
    (qualified : check proposal = true) (malformed : storeCheck before.records = false) :
    submit check before proposal = ⟨.malformedStore, before⟩ := by
  simp [submit, qualified, malformed]

theorem conflicting_revision_refuses {α β : Type} [DecidableEq α]
    (check : Envelope α → Bool) (before : State α β) (proposal existing : Envelope α)
    (qualified : check proposal = true) (valid : storeCheck before.records = true)
    (found : lookup before.records proposal.ref.key = some existing) (different : existing ≠ proposal) :
    submit check before proposal = ⟨.revisionConflict, before⟩ := by
  simp [submit, qualified, valid, found, different]

theorem identical_revision_retained {α β : Type} [DecidableEq α]
    (check : Envelope α → Bool) (before : State α β) (proposal : Envelope α)
    (qualified : check proposal = true) (valid : storeCheck before.records = true)
    (found : lookup before.records proposal.ref.key = some proposal) :
    submit check before proposal = ⟨.retained, before⟩ := by
  simp [submit, qualified, valid, found]

theorem fresh_qualified_revision_appended {α β : Type} [DecidableEq α]
    (check : Envelope α → Bool) (before : State α β) (proposal : Envelope α)
    (qualified : check proposal = true) (valid : storeCheck before.records = true)
    (missing : lookup before.records proposal.ref.key = none) :
    submit check before proposal =
      ⟨.appended, { before with records := before.records ++ [proposal] }⟩ := by
  simp [submit, qualified, valid, missing]

theorem submit_preserves_protected_state {α β : Type} [DecidableEq α]
    (check : Envelope α → Bool) (before : State α β) (proposal : Envelope α) :
    (submit check before proposal).state.protectedState = before.protectedState := by
  unfold submit
  split
  · split
    · cases found : lookup before.records proposal.ref.key with
      | none => rfl
      | some existing => split <;> rfl
    · rfl
  · rfl

def Succeeded (outcome : Outcome) : Prop := outcome = .appended ∨ outcome = .retained

theorem successful_submission_is_qualified {α β : Type} [DecidableEq α]
    (check : Envelope α → Bool) (before : State α β) (proposal : Envelope α)
    (success : Succeeded (submit check before proposal).outcome) : check proposal = true := by
  unfold submit at success
  split at success
  · assumption
  · simp [Succeeded] at success

theorem successful_submission_has_meaning {α β : Type} [DecidableEq α]
    (meaning : Envelope α → Prop) (check : Envelope α → Bool)
    (exactCheck : ∀ record, check record = true ↔ meaning record)
    (before : State α β) (proposal : Envelope α)
    (success : Succeeded (submit check before proposal).outcome) : meaning proposal :=
  (exactCheck proposal).mp (successful_submission_is_qualified check before proposal success)

theorem submit_preserves_store_meaning {α β : Type} [DecidableEq α]
    (check : Envelope α → Bool) (before : State α β) (proposal : Envelope α)
    (valid : StoreMeaning before.records) :
    StoreMeaning (submit check before proposal).state.records := by
  unfold submit
  split
  · split
    · cases found : lookup before.records proposal.ref.key with
      | none =>
        exact append_preserves_store_meaning before.records proposal valid
          ((lookup_none_exact before.records proposal.ref.key).mp found)
      | some existing => split <;> exact valid
    · exact valid
  · exact valid

-- Qualification precedes the duplicate check: an existing row does not seed a
-- new successful qualification after its witness or context is no longer valid.
theorem existing_record_does_not_bypass_qualification {α β : Type} [DecidableEq α]
    (check : Envelope α → Bool) (before : State α β) (proposal : Envelope α)
    (_existing : proposal ∈ before.records) (unqualified : check proposal = false) :
    submit check before proposal = ⟨.unqualified, before⟩ :=
  unqualified_preserves_state check before proposal unqualified

#print axioms store_check_exact
#print axioms lookup_sound
#print axioms lookup_none_exact
#print axioms append_preserves_store_meaning
#print axioms unqualified_preserves_state
#print axioms malformed_store_refuses
#print axioms conflicting_revision_refuses
#print axioms identical_revision_retained
#print axioms fresh_qualified_revision_appended
#print axioms submit_preserves_protected_state
#print axioms successful_submission_is_qualified
#print axioms successful_submission_has_meaning
#print axioms submit_preserves_store_meaning
#print axioms existing_record_does_not_bypass_qualification
end RelationalSuccessor.CandidateRecording
