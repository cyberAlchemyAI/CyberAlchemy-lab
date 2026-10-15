import TokenResolution

set_option autoImplicit false

namespace RelationalSuccessor.CandidateFiniteSourceCatalog
open RelationalSuccessor
abbrev Role := CandidateSourceResolution.Role

structure Artifact (α : Type) where
  ref : RevisionRef
  sourceKind : String
  body : α
  content : List UInt8
  ownerReview : RevisionRef
  deriving DecidableEq, Repr

structure Binding where
  role : Role
  token : String
  ref : RevisionRef
  deriving DecidableEq, Repr

def Binding.key (binding : Binding) : Role × String := (binding.role, binding.token)

-- These full approval records are independently captured context, not flags on
-- the submitted proposal. Their authenticity is an explicit later obligation.
structure Approval (α : Type) where
  role : Role
  artifact : Artifact α
  frame : Frame
  deriving DecidableEq, Repr

structure Capture (α : Type) where
  frame : Frame
  records : List (Artifact α)
  bindings : List Binding
  roots : List (Approval α)
  deriving DecidableEq, Repr

def UniqueBy {τ κ : Type} (key : τ → κ) (values : List τ) : Prop :=
  ∀ a ∈ values, ∀ b ∈ values, key a = key b → a = b

def uniqueCheck {τ κ : Type} [DecidableEq τ] [DecidableEq κ]
    (key : τ → κ) (values : List τ) : Bool :=
  values.all (fun a => values.all (fun b => decide (key a = key b → a = b)))

theorem unique_check_exact {τ κ : Type} [DecidableEq τ] [DecidableEq κ]
    (key : τ → κ) (values : List τ) : uniqueCheck key values = true ↔ UniqueBy key values := by
  simp only [uniqueCheck, UniqueBy, List.all_eq_true, decide_eq_true_eq]

-- This helper is internal; the entrypoints below fix the artifact/binding keys.
def lookup {τ κ : Type} [DecidableEq κ] (key : τ → κ) : List τ → κ → Option τ
  | [], _ => none
  | first :: rest, wanted => if key first = wanted then some first else lookup key rest wanted

theorem lookup_sound {τ κ : Type} [DecidableEq κ] (key : τ → κ)
    (values : List τ) (wanted : κ) (value : τ)
    (found : lookup key values wanted = some value) : value ∈ values ∧ key value = wanted := by
  induction values with
  | nil => simp [lookup] at found
  | cons first rest ih =>
    unfold lookup at found
    split at found
    · rename_i equal; cases found; exact ⟨by simp, equal⟩
    · have tail := ih found; exact ⟨by simp [tail.1], tail.2⟩

theorem lookup_complete {τ κ : Type} [DecidableEq κ] (key : τ → κ)
    (values : List τ) (wanted : κ) (value : τ) (unique : UniqueBy key values)
    (member : value ∈ values) (matching : key value = wanted) :
    lookup key values wanted = some value := by
  induction values with
  | nil => simp at member
  | cons first rest ih =>
    simp only [List.mem_cons] at member
    unfold lookup
    split
    · rename_i found
      have equal : first = value := unique first (by simp) value (by simp only [List.mem_cons]; exact member)
        (found.trans matching.symm)
      simp [equal]
    · rename_i missing
      rcases member with head | tail
      · subst value; exact False.elim (missing matching)
      · exact ih (by intro a ha b hb equal; exact unique a (by simp [ha]) b (by simp [hb]) equal) tail

def allArtifacts {α : Type} (capture : Capture α) : List (Artifact α) :=
  capture.records ++ capture.roots.map Approval.artifact

def RoleApproved {α : Type} (capture : Capture α) (role : Role) (artifact : Artifact α) : Prop :=
  ∃ root ∈ capture.roots, root.role = role ∧ root.artifact = artifact ∧ root.frame = capture.frame

def RecordApproved {α : Type} (capture : Capture α) (artifact : Artifact α) : Prop :=
  ∃ root ∈ capture.roots, root.artifact = artifact ∧ root.frame = capture.frame

def recordApprovalCheck {α : Type} [DecidableEq α] (capture : Capture α) (artifact : Artifact α) : Bool :=
  capture.roots.any (fun root => decide (root.artifact = artifact ∧ root.frame = capture.frame))

theorem record_approval_check_exact {α : Type} [DecidableEq α]
    (capture : Capture α) (artifact : Artifact α) :
    recordApprovalCheck capture artifact = true ↔ RecordApproved capture artifact := by
  simp [recordApprovalCheck, RecordApproved, List.any_eq_true]

def BindingMeaning {α : Type} (capture : Capture α) (binding : Binding) : Prop :=
  binding.token ≠ "" ∧ ∃ artifact ∈ capture.records,
    artifact.ref = binding.ref ∧ RoleApproved capture binding.role artifact

def bindingCheck {α : Type} [DecidableEq α] (capture : Capture α) (binding : Binding) : Bool :=
  decide (binding.token ≠ "") && capture.records.any (fun artifact =>
    decide (artifact.ref = binding.ref) && capture.roots.any (fun root =>
      decide (root.role = binding.role ∧ root.artifact = artifact ∧ root.frame = capture.frame)))

theorem binding_check_exact {α : Type} [DecidableEq α] (capture : Capture α) (binding : Binding) :
    bindingCheck capture binding = true ↔ BindingMeaning capture binding := by
  simp [bindingCheck, BindingMeaning, RoleApproved, List.any_eq_true]

structure CaptureMeaning {α : Type} (capture : Capture α) : Prop where
  artifacts : UniqueBy (fun artifact => artifact.ref.key) (allArtifacts capture)
  bindings : UniqueBy Binding.key capture.bindings
  recordsApproved : ∀ artifact ∈ capture.records, RecordApproved capture artifact
  bindingsApproved : ∀ binding ∈ capture.bindings, BindingMeaning capture binding
  rootsFrame : ∀ root ∈ capture.roots, root.frame = capture.frame

def captureCheck {α : Type} [DecidableEq α] (capture : Capture α) : Bool :=
  uniqueCheck (fun artifact => artifact.ref.key) (allArtifacts capture) &&
  uniqueCheck Binding.key capture.bindings &&
  capture.records.all (recordApprovalCheck capture) &&
  capture.bindings.all (bindingCheck capture) &&
  capture.roots.all (fun root => decide (root.frame = capture.frame))

theorem capture_check_exact {α : Type} [DecidableEq α] (capture : Capture α) :
    captureCheck capture = true ↔ CaptureMeaning capture := by
  simp only [captureCheck, Bool.and_eq_true, unique_check_exact, List.all_eq_true,
    record_approval_check_exact, binding_check_exact, decide_eq_true_eq]
  constructor
  · rintro ⟨⟨⟨⟨a, b⟩, c⟩, d⟩, e⟩; exact ⟨a, b, c, d, e⟩
  · intro h; exact ⟨⟨⟨⟨h.artifacts, h.bindings⟩, h.recordsApproved⟩, h.bindingsApproved⟩, h.rootsFrame⟩

theorem capture_records_unique_ref {α : Type} (capture : Capture α) (valid : CaptureMeaning capture) :
    UniqueBy Artifact.ref capture.records := by
  intro a ha b hb same
  exact valid.artifacts a (by simp [allArtifacts, ha]) b (by simp [allArtifacts, hb])
    (congrArg RevisionRef.key same)

structure ResolvedMeaning {α : Type} (capture : Capture α) (expected : Frame)
    (role : Role) (token : String) (artifact : Artifact α) : Prop where
  captureValid : CaptureMeaning capture
  frame : capture.frame = expected
  nonempty : token ≠ ""
  binding : ∃ binding ∈ capture.bindings, binding.key = (role, token) ∧ binding.ref = artifact.ref
  owned : artifact ∈ capture.records
  approved : RoleApproved capture role artifact

def resolveRecord {α : Type} [DecidableEq α] (capture : Capture α)
    (expected : Frame) (role : Role) (token : String) : Option (Artifact α) :=
  if captureCheck capture then
    if capture.frame = expected then
      match lookup Binding.key capture.bindings (role, token) with
      | none => none
      | some binding => lookup Artifact.ref capture.records binding.ref
    else none
  else none

theorem resolve_record_exact {α : Type} [DecidableEq α] (capture : Capture α)
    (expected : Frame) (role : Role) (token : String) (artifact : Artifact α) :
    resolveRecord capture expected role token = some artifact ↔
      ResolvedMeaning capture expected role token artifact := by
  constructor
  · intro accepted
    unfold resolveRecord at accepted
    split at accepted
    · rename_i checked
      have valid := (capture_check_exact capture).mp checked
      split at accepted
      · rename_i frame
        cases found : lookup Binding.key capture.bindings (role, token) with
        | none => simp [found] at accepted
        | some binding =>
          simp only [found] at accepted
          have bs := lookup_sound Binding.key capture.bindings (role, token) binding found
          have value := lookup_sound Artifact.ref capture.records binding.ref artifact accepted
          have qualifies := valid.bindingsApproved binding bs.1
          rcases qualifies with ⟨nonempty, owned, member, exactRef, approval⟩
          have equal : owned = artifact := valid.artifacts owned (by simp [allArtifacts, member])
            artifact (by simp [allArtifacts, value.1]) (congrArg RevisionRef.key (exactRef.trans value.2.symm))
          have keyParts : binding.role = role ∧ binding.token = token := by
            simpa [Binding.key] using bs.2
          subst owned
          refine ⟨valid, frame, ?_, ⟨binding, bs.1, bs.2, value.2.symm⟩, value.1, ?_⟩
          · simpa [keyParts.2] using nonempty
          · simpa [keyParts.1] using approval
      · simp at accepted
    · simp at accepted
  · intro meaning
    rcases meaning.binding with ⟨binding, member, key, exactRef⟩
    have found := lookup_complete Binding.key capture.bindings (role, token) binding
      meaning.captureValid.bindings member key
    have value := lookup_complete Artifact.ref capture.records binding.ref artifact
      (capture_records_unique_ref capture meaning.captureValid) meaning.owned exactRef.symm
    simp [resolveRecord, (capture_check_exact capture).mpr meaning.captureValid, meaning.frame, found, value]

theorem aliases_share_complete_record {α : Type} [DecidableEq α] (capture : Capture α)
    (expected : Frame) (roleA roleB : Role) (tokenA tokenB : String) (a b : Artifact α)
    (ha : resolveRecord capture expected roleA tokenA = some a)
    (hb : resolveRecord capture expected roleB tokenB = some b) (same : a.ref.key = b.ref.key) : a = b := by
  have ma := (resolve_record_exact capture expected roleA tokenA a).mp ha
  have mb := (resolve_record_exact capture expected roleB tokenB b).mp hb
  exact ma.captureValid.artifacts a (by simp [allArtifacts, ma.owned])
    b (by simp [allArtifacts, mb.owned]) same

theorem conflicting_artifacts_refuse {α : Type} [DecidableEq α] (capture : Capture α)
    (a b : Artifact α) (ha : a ∈ allArtifacts capture) (hb : b ∈ allArtifacts capture)
    (same : a.ref.key = b.ref.key) (different : a ≠ b) : captureCheck capture = false := by
  cases checked : captureCheck capture with
  | false => rfl
  | true => exact False.elim (different (((capture_check_exact capture).mp checked).artifacts a ha b hb same))

theorem conflicting_bindings_refuse {α : Type} [DecidableEq α] (capture : Capture α)
    (a b : Binding) (ha : a ∈ capture.bindings) (hb : b ∈ capture.bindings)
    (same : a.key = b.key) (different : a ≠ b) : captureCheck capture = false := by
  cases checked : captureCheck capture with
  | false => rfl
  | true => exact False.elim (different (((capture_check_exact capture).mp checked).bindings a ha b hb same))

theorem unapproved_record_refuses {α : Type} [DecidableEq α] (capture : Capture α)
    (artifact : Artifact α) (member : artifact ∈ capture.records)
    (unapproved : ¬ RecordApproved capture artifact) : captureCheck capture = false := by
  cases checked : captureCheck capture with
  | false => rfl
  | true => exact False.elim (unapproved (((capture_check_exact capture).mp checked).recordsApproved artifact member))

theorem stale_root_frame_refuses {α : Type} [DecidableEq α] (capture : Capture α)
    (root : Approval α) (member : root ∈ capture.roots) (wrong : root.frame ≠ capture.frame) :
    captureCheck capture = false := by
  cases checked : captureCheck capture with
  | false => rfl
  | true => exact False.elim (wrong (((capture_check_exact capture).mp checked).rootsFrame root member))

theorem wrong_frame_refuses_record {α : Type} [DecidableEq α] (capture : Capture α)
    (expected : Frame) (role : Role) (token : String) (wrong : capture.frame ≠ expected) :
    resolveRecord capture expected role token = none := by
  unfold resolveRecord
  split
  · exact if_neg wrong
  · rfl

def LegalExtension {α : Type} (old next : Capture α) : Prop :=
  CaptureMeaning old ∧ CaptureMeaning next ∧ old.frame = next.frame ∧
  (∀ record ∈ old.records, record ∈ next.records) ∧
  (∀ binding ∈ old.bindings, binding ∈ next.bindings) ∧
  (∀ root ∈ old.roots, root ∈ next.roots)

theorem extension_preserves_record_binding {α : Type} [DecidableEq α]
    (old next : Capture α) (expected : Frame) (role : Role) (token : String) (artifact : Artifact α)
    (extension : LegalExtension old next) (resolved : resolveRecord old expected role token = some artifact) :
    resolveRecord next expected role token = some artifact := by
  have oldMeaning := (resolve_record_exact old expected role token artifact).mp resolved
  refine (resolve_record_exact next expected role token artifact).mpr
    ⟨extension.2.1, extension.2.2.1.symm.trans oldMeaning.frame, oldMeaning.nonempty, ?_,
      extension.2.2.2.1 artifact oldMeaning.owned, ?_⟩
  · rcases oldMeaning.binding with ⟨binding, member, key, exactRef⟩
    exact ⟨binding, extension.2.2.2.2.1 binding member, key, exactRef⟩
  · rcases oldMeaning.approved with ⟨root, member, correctRole, exactArtifact, frame⟩
    exact ⟨root, extension.2.2.2.2.2 root member, correctRole, exactArtifact, frame.trans extension.2.2.1⟩

#print axioms unique_check_exact
#print axioms lookup_sound
#print axioms lookup_complete
#print axioms record_approval_check_exact
#print axioms binding_check_exact
#print axioms capture_check_exact
#print axioms capture_records_unique_ref
#print axioms resolve_record_exact
#print axioms aliases_share_complete_record
#print axioms conflicting_artifacts_refuse
#print axioms conflicting_bindings_refuse
#print axioms unapproved_record_refuses
#print axioms stale_root_frame_refuses
#print axioms wrong_frame_refuses_record
#print axioms extension_preserves_record_binding
end RelationalSuccessor.CandidateFiniteSourceCatalog
