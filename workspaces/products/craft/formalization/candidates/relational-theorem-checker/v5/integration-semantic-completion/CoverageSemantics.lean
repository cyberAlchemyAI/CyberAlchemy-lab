import SharedSemantics

namespace RelationalSuccessor

inductive Method where
  | kernel | countermodel | independent
  | callerAssertion | retired
  deriving DecidableEq, Repr

structure Challenge where
  id : String
  kind : RevisionRef
  meaning : RevisionRef
  statement : String
  definitions : List RevisionRef
  frame : Frame
  dependencies : List RevisionRef
  premises : List String
  deriving DecidableEq, Repr

structure Obligation where
  challenge : Challenge
  methods : List Method
  deriving DecidableEq, Repr

structure Evidence where
  challenge : Challenge
  method : Method
  proof : RevisionRef
  sourceSnapshot : RevisionRef
  deriving DecidableEq, Repr

def Allowed : Method → Bool
  | .kernel | .countermodel | .independent => true
  | .callerAssertion | .retired => false

-- `verified` is the context's output of actual verification, not a list of
-- caller assertions. Its authenticity/soundness is an explicit premise.
def Matches (o : Obligation) (e : Evidence) (current : RevisionRef) : Prop :=
  e.challenge = o.challenge ∧ e.method ∈ o.methods ∧ Allowed e.method = true ∧
    e.sourceSnapshot = current ∧ o.challenge.frame.snapshot = current

def checkMatch (o : Obligation) (e : Evidence) (current : RevisionRef) : Bool :=
  decide (e.challenge = o.challenge) && decide (e.method ∈ o.methods) && Allowed e.method &&
    decide (e.sourceSnapshot = current) && decide (o.challenge.frame.snapshot = current)

theorem matching_exact (o : Obligation) (e : Evidence) (current : RevisionRef) :
    checkMatch o e current = true ↔ Matches o e current := by
  simp [checkMatch, Matches, and_assoc]

def Complete (required : List Obligation) (verified : List Evidence) (current : RevisionRef) : Prop :=
  ∀ o ∈ required, ∃ e ∈ verified, Matches o e current

def complete (required : List Obligation) (verified : List Evidence) (current : RevisionRef) : Bool :=
  required.all fun o => verified.any fun e => checkMatch o e current

theorem coverage_exact (required : List Obligation) (verified : List Evidence) (current : RevisionRef) :
    complete required verified current = true ↔ Complete required verified current := by
  simp [complete, Complete, List.all_eq_true, List.any_eq_true, matching_exact]

def ExactInventory (required submitted : List Obligation) : Prop :=
  required ≠ [] ∧ (required.map (fun o => o.challenge.id)).Nodup ∧
    submitted.Nodup ∧ (∀ o ∈ required, o ∈ submitted) ∧ (∀ o ∈ submitted, o ∈ required)

def inventory (required submitted : List Obligation) : Bool :=
  !required.isEmpty && decide (required.map (fun o => o.challenge.id)).Nodup && decide submitted.Nodup &&
    required.all submitted.contains && submitted.all required.contains

theorem inventory_exact (required submitted : List Obligation) :
    inventory required submitted = true ↔ ExactInventory required submitted := by
  simp [inventory, ExactInventory, List.all_eq_true, and_assoc]

-- required is independently derived from the owned profile/diff policy.
-- claimedEligible is deliberately not a qualification premise.
def qualify (required submitted : List Obligation) (verified : List Evidence)
    (current : RevisionRef) (_claimedEligible : Bool) : Bool :=
  inventory required submitted && complete required verified current

def Qualification (required submitted : List Obligation) (verified : List Evidence)
    (current : RevisionRef) : Prop :=
  ExactInventory required submitted ∧ Complete required verified current

theorem qualification_exact (required submitted : List Obligation) (verified : List Evidence)
    (current : RevisionRef) (claimed : Bool) :
    qualify required submitted verified current claimed = true ↔
      Qualification required submitted verified current := by
  simp [qualify, Qualification, inventory_exact, coverage_exact]

theorem caller_flag_cannot_change_qualification (required submitted : List Obligation)
    (verified : List Evidence) (current : RevisionRef) :
    qualify required submitted verified current true = qualify required submitted verified current false := rfl

theorem accepted_has_every_obligation (required submitted : List Obligation) (verified : List Evidence)
    (current : RevisionRef) (claimed : Bool) (h : qualify required submitted verified current claimed = true) :
    ∀ o ∈ required, ∃ e ∈ verified, Matches o e current :=
  ((qualification_exact required submitted verified current claimed).mp h).2

theorem no_evidence_cannot_qualify (required submitted : List Obligation) (current : RevisionRef)
    (o : Obligation) (ho : o ∈ required) (claimed : Bool) :
    qualify required submitted [] current claimed = false := by
  cases h : qualify required submitted [] current claimed with
  | false => rfl
  | true =>
    rcases accepted_has_every_obligation required submitted [] current claimed h o ho with ⟨e, he, _⟩
    simp at he

theorem missing_submitted_obligation_refuses (required submitted : List Obligation)
    (verified : List Evidence) (current : RevisionRef) (o : Obligation)
    (hr : o ∈ required) (hs : o ∉ submitted) (claimed : Bool) :
    qualify required submitted verified current claimed = false := by
  cases h : qualify required submitted verified current claimed with
  | false => rfl
  | true =>
    have hi := ((qualification_exact required submitted verified current claimed).mp h).1
    exact False.elim (hs (hi.2.2.2.1 o hr))

theorem retirement_never_discharges (o : Obligation) (e : Evidence) (current : RevisionRef)
    (h : e.method = .retired) : checkMatch o e current = false := by
  simp [checkMatch, h, Allowed]

theorem assertion_never_discharges (o : Obligation) (e : Evidence) (current : RevisionRef)
    (h : e.method = .callerAssertion) : checkMatch o e current = false := by
  simp [checkMatch, h, Allowed]

theorem changed_challenge_refuses (o : Obligation) (e : Evidence) (current : RevisionRef)
    (h : e.challenge ≠ o.challenge) : checkMatch o e current = false := by
  simp [checkMatch, h]

theorem stale_snapshot_refuses (o : Obligation) (e : Evidence) (current : RevisionRef)
    (h : e.sourceSnapshot ≠ current) : checkMatch o e current = false := by
  simp [checkMatch, h]

-- This semantic soundness premise is later supplied by actual kernel checks
-- and source-mapping proofs. Coverage alone cannot make an unsound verifier
-- or a wrongly interpreted source statement sound.
def VerifierSound (verified : List Evidence) (Holds : Challenge → Prop) : Prop :=
  ∀ e ∈ verified, Holds e.challenge

theorem qualification_implies_semantic_truth (required submitted : List Obligation)
    (verified : List Evidence) (current : RevisionRef) (claimed : Bool)
    (Holds : Challenge → Prop) (sound : VerifierSound verified Holds)
    (h : qualify required submitted verified current claimed = true) :
    ∀ o ∈ required, Holds o.challenge := by
  intro o ho
  rcases accepted_has_every_obligation required submitted verified current claimed h o ho with ⟨e, he, hm⟩
  have hp := sound e he
  rw [hm.1] at hp
  exact hp

def FullInherited (original : List String) (discharged : List Obligation) : Prop :=
  original.Nodup ∧ (discharged.map (fun o => o.challenge.id)).Nodup ∧
    ∀ id, id ∈ original ↔ id ∈ discharged.map (fun o => o.challenge.id)

theorem full_coverage_has_exact_original_ids (original : List String) (discharged : List Obligation)
    (h : FullInherited original discharged) :
    ∀ id, id ∈ original ↔ id ∈ discharged.map (fun o => o.challenge.id) := h.2.2

#print axioms matching_exact
#print axioms coverage_exact
#print axioms inventory_exact
#print axioms qualification_exact
#print axioms caller_flag_cannot_change_qualification
#print axioms accepted_has_every_obligation
#print axioms no_evidence_cannot_qualify
#print axioms missing_submitted_obligation_refuses
#print axioms retirement_never_discharges
#print axioms assertion_never_discharges
#print axioms changed_challenge_refuses
#print axioms stale_snapshot_refuses
#print axioms qualification_implies_semantic_truth
#print axioms full_coverage_has_exact_original_ids

end RelationalSuccessor
