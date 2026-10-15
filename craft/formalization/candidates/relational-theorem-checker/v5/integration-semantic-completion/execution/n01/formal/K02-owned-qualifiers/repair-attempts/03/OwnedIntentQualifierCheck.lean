import OwnedBindingCatalog
import FramedIntentJoin
import IntentQualifiers

set_option autoImplicit false
namespace RelationalSuccessor.CandidateOwnedIntentQualifiers
open RelationalSuccessor
abbrev Resolution := CandidateIntentAddressing.Resolution
abbrev Role := CandidateIntentAddressing.Role
abbrev Claim := CandidateIntentAddressing.Claim
abbrev Projected := CandidateCapturedMetadata.Projected
abbrev FramedWorld := CandidateIntentSourceContract.FramedWorld
abbrev Raw := CandidateIntentSourceContract.Qualifiers.Raw
abbrev BindingCatalog (α : Type) := CandidateOwnedBindings.Catalog α

def resolutionKind : String := "intent-resolution-qualifier-binding"
def roleKind : String := "intent-addressing-role-binding"
def resolutionKey (resolution : Resolution) : RevisionKey := resolution.ref.key
def roleKey (role : Role) : RevisionKey := role.ref.key

structure Context where
  resolutions : BindingCatalog Resolution
  roles : BindingCatalog Role
  deriving DecidableEq, Repr

structure Meaning (context : Context) (world : FramedWorld) (projected : Projected)
    (raw : Raw) (claim : Claim) : Prop where
  resolution : CandidateOwnedBindings.Resolved context.resolutions resolutionKind resolutionKey
    world.frame raw.intent_resolution_ref claim.resolution
  role : CandidateOwnedBindings.Resolved context.roles roleKind roleKey
    world.frame raw.addressing_role claim.role
  roleCode : raw.addressing_role = claim.role.code
  joined : CandidateIntentSourceContract.Joined world projected claim

def check (context : Context) (world : FramedWorld) (projected : Projected) (raw : Raw) (claim : Claim) : Bool :=
  match CandidateOwnedBindings.resolve context.resolutions resolutionKind resolutionKey world.frame raw.intent_resolution_ref,
        CandidateOwnedBindings.resolve context.roles roleKind roleKey world.frame raw.addressing_role with
  | some resolution, some role =>
      decide (resolution = claim.resolution) && decide (role = claim.role) &&
      decide (raw.addressing_role = role.code) && CandidateIntentSourceContract.joinCheck world projected claim
  | _, _ => false

theorem check_exact (context : Context) (world : FramedWorld) (projected : Projected) (raw : Raw) (claim : Claim) :
    check context world projected raw claim = true ↔ Meaning context world projected raw claim := by
  constructor
  · intro checked
    cases resolutionFound : CandidateOwnedBindings.resolve context.resolutions resolutionKind resolutionKey world.frame raw.intent_resolution_ref with
    | none => simp [check, resolutionFound] at checked
    | some resolution =>
      cases roleFound : CandidateOwnedBindings.resolve context.roles roleKind roleKey world.frame raw.addressing_role with
      | none => simp [check, resolutionFound, roleFound] at checked
      | some role =>
        simp only [check, resolutionFound, roleFound, Bool.and_eq_true, decide_eq_true_eq] at checked
        rcases checked with ⟨⟨⟨resolutionExact, roleExact⟩, code⟩, joined⟩
        subst resolution
        subst role
        exact ⟨(CandidateOwnedBindings.resolve_exact _ _ _ _ _ _).mp resolutionFound,
          (CandidateOwnedBindings.resolve_exact _ _ _ _ _ _).mp roleFound, code,
          (CandidateIntentSourceContract.join_check_exact _ _ _).mp joined⟩
  · intro meaning
    have resolutionFound := (CandidateOwnedBindings.resolve_exact _ _ _ _ _ _).mpr meaning.resolution
    have roleFound := (CandidateOwnedBindings.resolve_exact _ _ _ _ _ _).mpr meaning.role
    simp only [check, resolutionFound, roleFound, Bool.and_eq_true, decide_eq_true_eq]
    exact ⟨⟨⟨rfl, rfl⟩, meaning.roleCode⟩,
      (CandidateIntentSourceContract.join_check_exact _ _ _).mpr meaning.joined⟩

theorem successful_tokens_nonempty (context : Context) (world : FramedWorld) (projected : Projected)
    (raw : Raw) (claim : Claim) (accepted : check context world projected raw claim = true) :
    raw.intent_resolution_ref ≠ "" ∧ raw.addressing_role ≠ "" := by
  have meaning := (check_exact context world projected raw claim).mp accepted
  exact ⟨CandidateOwnedBindings.resolved_token_nonempty _ _ _ _ _ _
      ((CandidateOwnedBindings.resolve_exact _ _ _ _ _ _).mpr meaning.resolution),
    CandidateOwnedBindings.resolved_token_nonempty _ _ _ _ _ _
      ((CandidateOwnedBindings.resolve_exact _ _ _ _ _ _).mpr meaning.role)⟩

theorem successful_role_and_selection_exact (context : Context) (world : FramedWorld) (projected : Projected)
    (raw : Raw) (claim : Claim) (accepted : check context world projected raw claim = true) :
    claim.role.subjectKind = claim.subject.kind ∧ claim.selection.role = claim.role.ref ∧
      claim.selection.frame = world.frame ∧ raw.addressing_role = claim.addressingRole := by
  have meaning := (check_exact context world projected raw claim).mp accepted
  exact ⟨meaning.joined.addresses.roleKind, meaning.joined.addresses.selectionRole,
    meaning.joined.fullFrame, meaning.roleCode.trans meaning.joined.addresses.roleQualifier.symm⟩

-- These candidate policy meanings require a separate authenticity proposition.
-- Captured catalog checks alone cannot supply the trusted-root premise.
def ResolutionTokenMeaning (authentic : BindingCatalog Resolution → Prop) (context : Context)
    (frame : Frame) (token : String) (ref : RevisionRef) : Prop :=
  authentic context.resolutions ∧ ∃ resolution,
    CandidateOwnedBindings.Resolved context.resolutions resolutionKind resolutionKey frame token resolution ∧
    resolution.ref = ref

def AddressingRoleMeaning (authentic : BindingCatalog Role → Prop) (context : Context)
    (frame : Frame) (kind : CandidateIntentAddressing.SubjectKind) (role : Role) (token : String) : Prop :=
  authentic context.roles ∧ CandidateOwnedBindings.Resolved context.roles roleKind roleKey frame token role ∧
    role.subjectKind = kind ∧ token = role.code

theorem captured_checks_need_authentic_roots (context : Context) (world : FramedWorld) (projected : Projected)
    (raw : Raw) (claim : Claim) (accepted : check context world projected raw claim = true)
    (resolutionAuthentic : BindingCatalog Resolution → Prop) (roleAuthentic : BindingCatalog Role → Prop)
    (authenticResolutions : resolutionAuthentic context.resolutions) (authenticRoles : roleAuthentic context.roles) :
    ResolutionTokenMeaning resolutionAuthentic context world.frame raw.intent_resolution_ref claim.resolutionQualifier ∧
    AddressingRoleMeaning roleAuthentic context world.frame claim.subject.kind claim.role raw.addressing_role := by
  have meaning := (check_exact context world projected raw claim).mp accepted
  exact ⟨⟨authenticResolutions, claim.resolution, meaning.resolution,
      meaning.joined.addresses.resolutionQualifier.symm⟩,
    ⟨authenticRoles, meaning.role, meaning.joined.addresses.roleKind, meaning.roleCode⟩⟩

#print axioms check_exact
#print axioms successful_tokens_nonempty
#print axioms successful_role_and_selection_exact
#print axioms captured_checks_need_authentic_roots
end RelationalSuccessor.CandidateOwnedIntentQualifiers
