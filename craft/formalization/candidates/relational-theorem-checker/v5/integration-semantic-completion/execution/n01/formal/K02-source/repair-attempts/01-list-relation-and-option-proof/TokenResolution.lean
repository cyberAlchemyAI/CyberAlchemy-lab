import SharedSemantics

set_option autoImplicit false

namespace RelationalSuccessor.CandidateSourceResolution
open RelationalSuccessor

inductive Role where
  | intent | decision | subject | satisfactionTest
  deriving DecidableEq, Repr

-- These are independently captured, role-specific catalog and approval inputs.
-- Capture authenticity and the raw-byte parser are outside this projection.
abbrev Catalog := Role → String → List RevisionRef
abbrev Roots := Role → List RevisionRef

def TokenMeaning (catalog : Catalog) (roots : Roots) (role : Role)
    (token : String) (ref : RevisionRef) : Prop :=
  token ≠ "" ∧ ref ∈ catalog role token ∧
    (∀ other ∈ catalog role token, other = ref) ∧ ref ∈ roots role

-- Identical repeated entries are permitted; conflicting values are refused.
-- No first-entry choice is accepted without checking every candidate value.
def resolve (catalog : Catalog) (roots : Roots) (role : Role)
    (token : String) : Option RevisionRef :=
  if token = "" then none else
    match catalog role token with
    | [] => none
    | first :: rest =>
      if rest.all (fun other => decide (other = first)) &&
          (roots role).any (fun approved => decide (approved = first))
      then some first else none

theorem resolve_exact (catalog : Catalog) (roots : Roots) (role : Role)
    (token : String) (ref : RevisionRef) :
    resolve catalog roots role token = some ref ↔ TokenMeaning catalog roots role token ref := by
  unfold resolve TokenMeaning
  by_cases empty : token = ""
  · simp [empty]
  · cases values : catalog role token with
    | nil => simp [empty, values]
    | cons first rest =>
      simp [empty, values, List.all_eq_true, List.any_eq_true]
      constructor
      · intro passed
        split at passed
        · rename_i valid
          cases passed
          exact ⟨rfl, valid.1, valid.2⟩
        · cases passed
      · rintro ⟨same, others, approved⟩
        subst ref
        simp [others, approved]

theorem ambiguous_token_refuses (catalog : Catalog) (roots : Roots) (role : Role)
    (token : String) (a b : RevisionRef) (ha : a ∈ catalog role token)
    (hb : b ∈ catalog role token) (different : a ≠ b) :
    resolve catalog roots role token = none := by
  cases found : resolve catalog roots role token with
  | none => rfl
  | some ref =>
    have exactMeaning := (resolve_exact catalog roots role token ref).mp found
    exact False.elim (different ((exactMeaning.2.2.1 a ha).trans
      (exactMeaning.2.2.1 b hb).symm))

theorem unrooted_token_cannot_resolve (catalog : Catalog) (roots : Roots) (role : Role)
    (token : String) (ref : RevisionRef) (missing : ref ∉ roots role) :
    resolve catalog roots role token ≠ some ref := by
  intro accepted
  exact missing ((resolve_exact catalog roots role token ref).mp accepted).2.2.2

theorem empty_token_refuses (catalog : Catalog) (roots : Roots) (role : Role) :
    resolve catalog roots role "" = none := by simp [resolve]

def ListMeaning (catalog : Catalog) (roots : Roots) (role : Role)
    (tokens : List String) (refs : List RevisionRef) : Prop :=
  List.Forall₂ (TokenMeaning catalog roots role) tokens refs

def decodeList (catalog : Catalog) (roots : Roots) (role : Role) :
    List String → Option (List RevisionRef)
  | [] => some []
  | token :: rest =>
      match resolve catalog roots role token, decodeList catalog roots role rest with
      | some ref, some refs => some (ref :: refs)
      | _, _ => none

theorem decode_list_exact (catalog : Catalog) (roots : Roots) (role : Role)
    (tokens : List String) (refs : List RevisionRef) :
    decodeList catalog roots role tokens = some refs ↔ ListMeaning catalog roots role tokens refs := by
  induction tokens generalizing refs with
  | nil => cases refs <;> simp [decodeList, ListMeaning]
  | cons token rest ih =>
    cases refs with
    | nil =>
      cases h : resolve catalog roots role token <;>
        cases t : decodeList catalog roots role rest <;> simp [decodeList, h, t, ListMeaning]
    | cons ref refs =>
      simp only [ListMeaning, List.forall₂_cons]
      rw [← resolve_exact, ← ih]
      cases h : resolve catalog roots role token <;>
        cases t : decodeList catalog roots role rest <;> simp [decodeList, h, t]

theorem decoded_list_length (catalog : Catalog) (roots : Roots) (role : Role)
    (tokens : List String) (refs : List RevisionRef)
    (decoded : decodeList catalog roots role tokens = some refs) : refs.length = tokens.length := by
  have meaning := (decode_list_exact catalog roots role tokens refs).mp decoded
  exact meaning.length_eq.symm

theorem failed_head_refuses (catalog : Catalog) (roots : Roots) (role : Role)
    (token : String) (rest : List String)
    (missing : resolve catalog roots role token = none) :
    decodeList catalog roots role (token :: rest) = none := by simp [decodeList, missing]

theorem failed_tail_refuses (catalog : Catalog) (roots : Roots) (role : Role)
    (token : String) (rest : List String)
    (missing : decodeList catalog roots role rest = none) :
    decodeList catalog roots role (token :: rest) = none := by
  cases h : resolve catalog roots role token <;> simp [decodeList, h, missing]

#print axioms resolve_exact
#print axioms ambiguous_token_refuses
#print axioms unrooted_token_cannot_resolve
#print axioms empty_token_refuses
#print axioms decode_list_exact
#print axioms decoded_list_length
#print axioms failed_head_refuses
#print axioms failed_tail_refuses
end RelationalSuccessor.CandidateSourceResolution
