import Lean

set_option autoImplicit false

namespace CandidateLessonUse

structure Ref where
  id : String
  revision : Nat
  deriving DecidableEq, Repr

structure Frame where
  session : Ref
  owner : Ref
  scope : Ref
  snapshot : Ref
  epoch : Nat
  deriving DecidableEq, Repr

inductive Posture where
  | selected | presented | used | declined
  deriving DecidableEq, Repr

structure Application where
  ref : Ref
  lesson : Ref
  assessment : Ref
  posture : Posture
  frame : Frame
  conflicts : List Ref
  overrides : List Ref
  deriving DecidableEq, Repr

structure Assessment where
  ref : Ref
  application : Ref
  lesson : Ref
  frame : Frame
  basis : String
  deriving DecidableEq, Repr

structure Instruction where
  ref : Ref
  owner : Ref
  scope : Ref
  deriving DecidableEq, Repr

structure Policy where
  ref : Ref
  owner : Ref
  scope : Ref
  start : Nat
  finish : Nat
  ranks : List (Ref × Nat)
  deriving DecidableEq, Repr

structure DispositionEvidence where
  ref : Ref
  application : Ref
  lesson : Ref
  frame : Frame
  posture : Posture
  instruction : Ref
  basis : String
  deriving DecidableEq, Repr

structure Conflict where
  ref : Ref
  application : Ref
  frame : Frame
  winner : Ref
  loser : Ref
  deriving DecidableEq, Repr

structure Override where
  ref : Ref
  application : Ref
  frame : Frame
  conflict : Ref
  instruction : Ref
  basis : String
  deriving DecidableEq, Repr

structure Claim where
  application : Application
  target : Ref
  lessonQualifier : Ref
  postureQualifier : Posture
  assessmentQualifier : Ref
  precedenceQualifier : Ref
  assessment : Assessment
  policy : Policy
  disposition : DispositionEvidence
  frame : Frame
  deriving DecidableEq, Repr

structure World where
  applications : List Application
  lessons : List Ref
  assessments : List Assessment
  policies : List Policy
  instructions : List Instruction
  evidence : List DispositionEvidence
  conflicts : List Conflict
  overrides : List Override
  frames : List Frame
  deriving DecidableEq, Repr

-- These are independently captured typed catalogs, not authenticated raw sources.
def ExactJoins (c : Claim) : Prop :=
  c.application.lesson = c.target ∧ c.lessonQualifier = c.target ∧
  c.application.posture = c.postureQualifier ∧
  c.application.assessment = c.assessment.ref ∧
  c.assessmentQualifier = c.assessment.ref ∧
  c.precedenceQualifier = c.policy.ref ∧
  c.application.frame = c.frame ∧
  c.assessment.application = c.application.ref ∧
  c.assessment.lesson = c.target ∧ c.assessment.frame = c.frame ∧
  c.disposition.application = c.application.ref ∧
  c.disposition.lesson = c.target ∧ c.disposition.frame = c.frame ∧
  c.disposition.posture = c.application.posture

def Captured (w : World) (c : Claim) : Prop :=
  c.application ∈ w.applications ∧ c.target ∈ w.lessons ∧
  c.assessment ∈ w.assessments ∧ c.policy ∈ w.policies ∧
  c.disposition ∈ w.evidence ∧ c.frame ∈ w.frames

def SupportedDisposition (c : Claim) : Prop :=
  (c.application.posture = .used ∨ c.application.posture = .declined) ∧
  c.disposition.basis ≠ "" ∧ c.assessment.basis ≠ ""

def Ranked (p : Policy) (r : Ref) : Prop :=
  ∃ entry ∈ p.ranks, entry.1 = r

def Dominates (p : Policy) (winner loser : Ref) : Prop :=
  ∃ winning ∈ p.ranks, ∃ losing ∈ p.ranks,
    winning.1 = winner ∧ losing.1 = loser ∧ losing.2 < winning.2

def OwnedInstruction (w : World) (c : Claim) (r : Ref) : Prop :=
  ∃ instruction ∈ w.instructions, instruction.ref = r ∧
    instruction.owner = c.frame.owner ∧ instruction.scope = c.frame.scope

-- Finite quantification makes policy interpretation executable without treating
-- arbitrary source order as precedence. Rank direction is a proposed profile.
def PolicyMeaning (w : World) (c : Claim) : Prop :=
  c.policy.owner = c.frame.owner ∧ c.policy.scope = c.frame.scope ∧
  c.policy.start ≤ c.frame.epoch ∧ c.frame.epoch ≤ c.policy.finish ∧
  (c.policy.ranks.map Prod.fst).Nodup ∧
  OwnedInstruction w c c.disposition.instruction ∧
  Ranked c.policy c.disposition.instruction

def RelevantConflict (c : Claim) (r : Conflict) : Prop :=
  r.application = c.application.ref ∧ r.frame = c.frame

def RelevantOverride (c : Claim) (r : Override) : Prop :=
  r.application = c.application.ref ∧ r.frame = c.frame

def ConflictMeaning (w : World) (c : Claim) : Prop :=
  (∀ r ∈ w.conflicts, RelevantConflict c r →
    r.ref ∈ c.application.conflicts ∧ r.winner = c.disposition.instruction ∧
    OwnedInstruction w c r.winner ∧ OwnedInstruction w c r.loser ∧
    Dominates c.policy r.winner r.loser) ∧
  (∀ r ∈ c.application.conflicts,
    ∃ actual ∈ w.conflicts, actual.ref = r ∧ RelevantConflict c actual)

def OverrideMeaning (w : World) (c : Claim) : Prop :=
  (∀ r ∈ w.overrides, RelevantOverride c r →
    r.ref ∈ c.application.overrides ∧ r.basis ≠ "" ∧
    r.instruction = c.disposition.instruction ∧
    ∃ conflict ∈ w.conflicts, conflict.ref = r.conflict ∧
      RelevantConflict c conflict ∧ conflict.ref ∈ c.application.conflicts ∧
      conflict.winner = r.instruction) ∧
  (∀ r ∈ c.application.overrides,
    ∃ actual ∈ w.overrides, actual.ref = r ∧ RelevantOverride c actual)

def AppliesLesson (w : World) (c : Claim) : Prop :=
  ExactJoins c ∧ Captured w c ∧ SupportedDisposition c ∧
  PolicyMeaning w c ∧ ConflictMeaning w c ∧ OverrideMeaning w c

instance (c : Claim) : Decidable (ExactJoins c) := inferInstanceAs (Decidable (_ ∧ _))
instance (w : World) (c : Claim) : Decidable (Captured w c) := inferInstanceAs (Decidable (_ ∧ _))
instance (c : Claim) : Decidable (SupportedDisposition c) := inferInstanceAs (Decidable (_ ∧ _))
instance (p : Policy) (r : Ref) : Decidable (Ranked p r) :=
  inferInstanceAs (Decidable (∃ entry ∈ p.ranks, entry.1 = r))
instance (p : Policy) (winner loser : Ref) : Decidable (Dominates p winner loser) :=
  inferInstanceAs (Decidable (∃ winning ∈ p.ranks, ∃ losing ∈ p.ranks,
    winning.1 = winner ∧ losing.1 = loser ∧ losing.2 < winning.2))
instance (w : World) (c : Claim) (r : Ref) : Decidable (OwnedInstruction w c r) :=
  inferInstanceAs (Decidable (∃ instruction ∈ w.instructions, instruction.ref = r ∧
    instruction.owner = c.frame.owner ∧ instruction.scope = c.frame.scope))
instance (w : World) (c : Claim) : Decidable (PolicyMeaning w c) := inferInstanceAs (Decidable (_ ∧ _))
instance (c : Claim) (r : Conflict) : Decidable (RelevantConflict c r) := inferInstanceAs (Decidable (_ ∧ _))
instance (c : Claim) (r : Override) : Decidable (RelevantOverride c r) := inferInstanceAs (Decidable (_ ∧ _))
instance (w : World) (c : Claim) : Decidable (ConflictMeaning w c) :=
  inferInstanceAs (Decidable ((_ : Prop) ∧ (_ : Prop)))
instance (w : World) (c : Claim) : Decidable (OverrideMeaning w c) :=
  inferInstanceAs (Decidable ((_ : Prop) ∧ (_ : Prop)))
instance (w : World) (c : Claim) : Decidable (AppliesLesson w c) :=
  inferInstanceAs (Decidable ((_ : Prop) ∧ (_ : Prop)))

-- Diagnostics check the independent predicates, grouped by actual correction.
def checks (w : World) (c : Claim) : List (String × Bool) :=
  [("exact-revision-and-frame", decide (ExactJoins c)),
   ("missing-captured-record", decide (Captured w c)),
   ("unsupported-disposition", decide (SupportedDisposition c)),
   ("unresolved-precedence", decide (PolicyMeaning w c)),
   ("conflict-basis", decide (ConflictMeaning w c)),
   ("override-basis", decide (OverrideMeaning w c))]

def check (w : World) (c : Claim) : Bool := (checks w c).all (fun entry => entry.2)
def diagnostics (w : World) (c : Claim) : List String :=
  ((checks w c).filter (fun entry => !entry.2)).map Prod.fst

theorem check_exact (w : World) (c : Claim) :
    check w c = true ↔ AppliesLesson w c := by
  simp [check, checks, AppliesLesson]

theorem diagnostics_exact (w : World) (c : Claim) :
    diagnostics w c = [] ↔ AppliesLesson w c := by
  simp [diagnostics, checks, AppliesLesson]

theorem exact_qualifiers (w : World) (c : Claim) (h : AppliesLesson w c) :
    ExactJoins c := h.1

theorem supported_only (w : World) (c : Claim) (h : AppliesLesson w c) :
    c.application.posture = .used ∨ c.application.posture = .declined := h.2.2.1.1

theorem selected_insufficient (w : World) (c : Claim)
    (h : c.application.posture = .selected) : ¬ AppliesLesson w c := by
  intro qualified
  have disposition := supported_only w c qualified
  simp [h] at disposition

theorem presented_insufficient (w : World) (c : Claim)
    (h : c.application.posture = .presented) : ¬ AppliesLesson w c := by
  intro qualified
  have disposition := supported_only w c qualified
  simp [h] at disposition

theorem evidence_required (w : World) (c : Claim) (h : AppliesLesson w c) :
    c.disposition ∈ w.evidence := h.2.1.2.2.2.2.1

theorem conflict_retained (w : World) (c : Claim) (h : AppliesLesson w c)
    (r : Conflict) (captured : r ∈ w.conflicts) (relevant : RelevantConflict c r) :
    r.ref ∈ c.application.conflicts := (h.2.2.2.2.1.1 r captured relevant).1

theorem override_retained (w : World) (c : Claim) (h : AppliesLesson w c)
    (r : Override) (captured : r ∈ w.overrides) (relevant : RelevantOverride c r) :
    r.ref ∈ c.application.overrides := (h.2.2.2.2.2.1 r captured relevant).1

structure Ledger where
  rows : List (Ref × Claim)
  authorityRoots : List Ref
  ownership : List (Ref × Ref)
  identities : List (Ref × Ref)
  admissions : List Ref
  runtime : List String
  deriving DecidableEq, Repr

-- This is candidate relation recording only, with explicit revision conflicts.
def record (key : Ref) (c : Claim) (s : Ledger) : Option Ledger :=
  match s.rows.find? (fun entry => entry.1 == key) with
  | none => some { s with rows := s.rows ++ [(key, c)] }
  | some entry => if entry.2 = c then some s else none

theorem record_preserves (key : Ref) (c : Claim) (before after : Ledger)
    (h : record key c before = some after) :
    after.authorityRoots = before.authorityRoots ∧
    after.ownership = before.ownership ∧ after.identities = before.identities ∧
    after.admissions = before.admissions ∧ after.runtime = before.runtime := by
  unfold record at h
  split at h
  · cases h
    exact ⟨rfl, rfl, rfl, rfl, rfl⟩
  · split at h
    · cases h
      exact ⟨rfl, rfl, rfl, rfl, rfl⟩
    · cases h

theorem same_revision_conflict (key : Ref) (c : Claim) (s : Ledger)
    (entry : Ref × Claim)
    (found : s.rows.find? (fun row => row.1 == key) = some entry)
    (different : entry.2 ≠ c) : record key c s = none := by
  simp [record, found, different]

theorem identical_retry (key : Ref) (c : Claim) (s : Ledger)
    (entry : Ref × Claim)
    (found : s.rows.find? (fun row => row.1 == key) = some entry)
    (identical : entry.2 = c) : record key c s = some s := by
  simp [record, found, identical]

def recordQualified (w : World) (key : Ref) (c : Claim) (s : Ledger) : Option Ledger :=
  if check w c then record key c s else none

theorem qualified_record_requires_meaning (w : World) (key : Ref) (c : Claim)
    (before after : Ledger) (h : recordQualified w key c before = some after) :
    AppliesLesson w c := by
  unfold recordQualified at h
  split at h
  · rename_i qualified
    exact (check_exact w c).mp qualified
  · cases h

theorem qualified_record_preserves (w : World) (key : Ref) (c : Claim)
    (before after : Ledger) (h : recordQualified w key c before = some after) :
    after.authorityRoots = before.authorityRoots ∧
    after.ownership = before.ownership ∧ after.identities = before.identities ∧
    after.admissions = before.admissions ∧ after.runtime = before.runtime := by
  unfold recordQualified at h
  split at h
  · exact record_preserves key c before after h
  · cases h

theorem unsupported_record_refused (w : World) (key : Ref) (c : Claim)
    (s : Ledger) (h : ¬ AppliesLesson w c) : recordQualified w key c s = none := by
  have refused : check w c ≠ true := fun accepted => h ((check_exact w c).mp accepted)
  simp [recordQualified, refused]

end CandidateLessonUse
