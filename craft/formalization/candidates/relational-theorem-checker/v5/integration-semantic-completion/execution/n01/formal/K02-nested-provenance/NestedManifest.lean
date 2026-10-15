import NestedSources
import ReuseCollection
set_option autoImplicit false
namespace RelationalSuccessor.CandidateNestedProvenance
open CandidateBindingAst (Decoder)
open CandidateBindingCapture (Envelope)
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits originalByteCount)
open CandidateEvidenceResources (NumericLimits)
open CandidatePreflightReuse (CertifiedInput)

def PairMeaning {α : Type} (body : Decoder α) (profile : Profile) (budget : Nat) (numbers : NumericLimits)
    (frame : Frame) : List (Expected α) → List Envelope → Prop
  | [], [] => True
  | expected::rest, capture::captures =>
    ItemMeaning body profile budget numbers frame expected capture ∧ PairMeaning body profile budget numbers frame rest captures
  | _, _ => False

def checkCached {α : Type} [DecidableEq α] {profile : Profile} {budget : Nat} {numbers : NumericLimits}
    (body : Decoder α) (frame : Frame) : List (Expected α) → List (CertifiedInput profile budget numbers) → Bool
  | [], [] => true
  | expected::rest, input::inputs => cachedItemCheck body frame expected input && checkCached body frame rest inputs
  | _, _ => false

theorem cached_pairs_exact {α : Type} [DecidableEq α] {profile : Profile} {budget : Nat} {numbers : NumericLimits}
    (body : Decoder α) (frame : Frame) (expected : List (Expected α)) (inputs : List (CertifiedInput profile budget numbers)) :
    checkCached body frame expected inputs = true ↔
      PairMeaning body profile budget numbers frame expected (inputs.map fun input => input.val.capture) := by
  induction expected generalizing inputs with
  | nil => cases inputs <;> simp [checkCached, PairMeaning]
  | cons first rest ih =>
    cases inputs with
    | nil => simp [checkCached, PairMeaning]
    | cons input inputs => simp only [checkCached, List.map_cons, PairMeaning, Bool.and_eq_true, certified_item_exact, ih]

theorem pairs_exact_manifest {α : Type} (body : Decoder α) (profile : Profile) (budget : Nat) (numbers : NumericLimits)
    (frame : Frame) (expected : List (Expected α)) (captures : List Envelope)
    (meaning : PairMeaning body profile budget numbers frame expected captures) :
    captures = expected.map (envelope profile) := by
  induction expected generalizing captures with
  | nil => cases captures <;> simp [PairMeaning] at meaning ⊢
  | cons first rest ih =>
    cases captures with
    | nil => simp [PairMeaning] at meaning
    | cons capture captures =>
      simp only [PairMeaning] at meaning
      simp only [List.map_cons, meaning.1.1, ih captures meaning.2]

theorem pairs_all_preflight {α : Type} (body : Decoder α) (profile : Profile) (budget : Nat) (numbers : NumericLimits)
    (frame : Frame) (expected : List (Expected α)) (captures : List Envelope)
    (meaning : PairMeaning body profile budget numbers frame expected captures) :
    CandidateEvidenceResources.AllPreflightMeaning profile budget numbers captures := by
  induction expected generalizing captures with
  | nil => cases captures <;> simp [PairMeaning, CandidateEvidenceResources.AllPreflightMeaning] at meaning ⊢
  | cons first rest ih =>
    cases captures with
    | nil => simp [PairMeaning] at meaning
    | cons capture captures =>
      simp only [PairMeaning] at meaning
      intro value member
      rcases List.mem_cons.mp member with head | tail
      · subst value; exact meaning.1.2.1
      · exact ih captures meaning.2 value tail

theorem pairs_all_expected {α : Type} (body : Decoder α) (profile : Profile) (budget : Nat) (numbers : NumericLimits)
    (frame : Frame) (expected : List (Expected α)) (captures : List Envelope)
    (meaning : PairMeaning body profile budget numbers frame expected captures) :
    ∀ value ∈ expected, ItemMeaning body profile budget numbers frame value (envelope profile value) := by
  induction expected generalizing captures with
  | nil => simp
  | cons first rest ih =>
    cases captures with
    | nil => simp [PairMeaning] at meaning
    | cons capture captures =>
      simp only [PairMeaning] at meaning
      intro value member
      rcases List.mem_cons.mp member with head | tail
      · subst value; rw [←meaning.1.1]; exact meaning.1
      · exact ih captures meaning.2 value tail

def NestedBudgetMeaning (limits : Limits) (captures : List Envelope) : Prop :=
  captures.length ≤ limits.maxCaptures ∧ originalByteCount captures ≤ limits.totalBytes ∧
    ∀ capture ∈ captures, capture.content.length ≤ limits.perCaptureBytes
def nestedBudgetCheck (limits : Limits) (captures : List Envelope) : Bool :=
  decide (captures.length ≤ limits.maxCaptures) && decide (originalByteCount captures ≤ limits.totalBytes) &&
    captures.all (fun capture => decide (capture.content.length ≤ limits.perCaptureBytes))
theorem nested_budget_exact (limits : Limits) (captures : List Envelope) :
    nestedBudgetCheck limits captures = true ↔ NestedBudgetMeaning limits captures := by
  simp only [nestedBudgetCheck, NestedBudgetMeaning, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, and_assoc]

theorem collect_exists_from_all_preflight (profile : Profile) (budget : Nat) (numbers : NumericLimits) (captures : List Envelope)
    (meaning : CandidateEvidenceResources.AllPreflightMeaning profile budget numbers captures) :
    ∃ inputs, CandidatePreflightReuse.collect profile budget numbers captures = .ok inputs := by
  have missing := (CandidateEvidenceResources.all_preflight_exact profile budget numbers captures).mpr meaning
  have same := CandidatePreflightReuse.collected_refusal_equal_legacy profile budget numbers captures
  rw [missing] at same
  cases found : CandidatePreflightReuse.collect profile budget numbers captures with
  | error reason => simp only [found, CandidatePreflightReuse.failed] at same; contradiction
  | ok inputs => exact ⟨inputs,rfl⟩

inductive Refusal where
  | budget
  | manifest
  | preflight (failure : CandidatePreflightReuse.Failure)
  | document
  deriving DecidableEq, Repr

def NestedMeaning {α : Type} (body : Decoder α) (profile : Profile) (limits : Limits) (numbers : NumericLimits)
    (frame : Frame) (expected : List (Expected α)) (captures : List Envelope) : Prop :=
  NestedBudgetMeaning limits captures ∧ PairMeaning body profile limits.perCaptureBytes numbers frame expected captures

def runNested {α : Type} [DecidableEq α] (body : Decoder α) (profile : Profile) (limits : Limits) (numbers : NumericLimits)
    (frame : Frame) (expected : List (Expected α)) (captures : List Envelope) : Except Refusal Unit :=
  if nestedBudgetCheck limits captures then
    if captures = expected.map (envelope profile) then
      match CandidatePreflightReuse.collect profile limits.perCaptureBytes numbers captures with
      | .error reason => .error (.preflight reason)
      | .ok inputs => if checkCached body frame expected inputs then .ok () else .error .document
    else .error .manifest
  else .error .budget

theorem nested_run_sound {α : Type} [DecidableEq α] (body : Decoder α) (profile : Profile) (limits : Limits) (numbers : NumericLimits)
    (frame : Frame) (expected : List (Expected α)) (captures : List Envelope)
    (accepted : runNested body profile limits numbers frame expected captures = .ok ()) :
    NestedMeaning body profile limits numbers frame expected captures := by
  unfold runNested at accepted
  split at accepted
  · rename_i budget
    split at accepted
    · cases collected : CandidatePreflightReuse.collect profile limits.perCaptureBytes numbers captures with
      | error reason => simp only [collected] at accepted; contradiction
      | ok inputs =>
        simp only [collected] at accepted
        split at accepted
        · rename_i checked
          have pair := (cached_pairs_exact body frame expected inputs).mp checked
          have retained := CandidatePreflightReuse.collected_original_inputs _ _ _ _ _ collected
          rw [retained] at pair
          exact ⟨(nested_budget_exact _ _).mp budget,pair⟩
        · contradiction
    · contradiction
  · contradiction

theorem nested_run_complete {α : Type} [DecidableEq α] (body : Decoder α) (profile : Profile) (limits : Limits) (numbers : NumericLimits)
    (frame : Frame) (expected : List (Expected α)) (captures : List Envelope)
    (meaning : NestedMeaning body profile limits numbers frame expected captures) :
    runNested body profile limits numbers frame expected captures = .ok () := by
  have budget := (nested_budget_exact _ _).mpr meaning.1
  have manifest := pairs_exact_manifest _ _ _ _ _ _ _ meaning.2
  have preflight := pairs_all_preflight _ _ _ _ _ _ _ meaning.2
  rcases collect_exists_from_all_preflight _ _ _ _ preflight with ⟨inputs,collected⟩
  have retained := CandidatePreflightReuse.collected_original_inputs _ _ _ _ _ collected
  have pair : PairMeaning body profile limits.perCaptureBytes numbers frame expected (inputs.map fun input => input.val.capture) := by
    rw [retained]; exact meaning.2
  have checked := (cached_pairs_exact body frame expected inputs).mpr pair
  unfold runNested
  rw [budget]
  simp only [if_true]
  rw [if_pos manifest, collected]
  simp only [checked,if_true]

theorem nested_run_exact {α : Type} [DecidableEq α] (body : Decoder α) (profile : Profile) (limits : Limits) (numbers : NumericLimits)
    (frame : Frame) (expected : List (Expected α)) (captures : List Envelope) :
    runNested body profile limits numbers frame expected captures = .ok () ↔
      NestedMeaning body profile limits numbers frame expected captures :=
  ⟨nested_run_sound _ _ _ _ _ _ _,nested_run_complete _ _ _ _ _ _ _⟩

#print axioms cached_pairs_exact
#print axioms pairs_exact_manifest
#print axioms pairs_all_preflight
#print axioms pairs_all_expected
#print axioms nested_budget_exact
#print axioms collect_exists_from_all_preflight
#print axioms nested_run_sound
#print axioms nested_run_complete
#print axioms nested_run_exact
end RelationalSuccessor.CandidateNestedProvenance
