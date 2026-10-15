import AuthorityOwnership
import ProfileSelectionControls
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateProfileEvidence.Controls
open CandidateProfileSelection (declaredProfile)
def frame : Frame := CandidateProfileSelection.Controls.frame
def declaration := CandidateProfileSelection.Controls.declaration
def selection := CandidateProfileSelection.Controls.selection
def issuer := CandidateProfileSelection.Controls.issuer
def bootstrap := CandidateDigestCapture.Controls.profile
def root : RevisionRef := ⟨⟨"fixture","authority-policy","1"⟩,"synthetic-root"⟩
def grantRef : RevisionRef := ⟨⟨"fixture","grant","1"⟩,"synthetic-grant"⟩
def profile : CandidateProfileSelection.Stage := ⟨frame,bootstrap,[declaration],[selection],declaredProfile declaration⟩
def declarationIssue : Issue := ⟨declaration.entry.ref,declaration.entry.sourceKind,issuer,declaration.entry.ownerReview,declaration.entry.content.map UInt8.toNat⟩
def selectionIssue : Issue := ⟨selection.entry.ref,selection.entry.sourceKind,issuer,selection.entry.ownerReview,selection.entry.content.map UInt8.toNat⟩
def grant : Grant := ⟨grantRef,issuer,["declare","select"],frame.scope⟩
def declarationReview : Review := ⟨declaration.entry.ownerReview,declaration.entry.ref,.accepted,.clear,100⟩
def selectionReview : Review := ⟨selection.entry.ownerReview,selection.entry.ref,.accepted,.clear,100⟩
def authority : Authority := ⟨root,bootstrap,[declaration.entry.ref],[selection.entry.ref],
  [declarationIssue,selectionIssue],[grant],[declarationReview,selectionReview]⟩
def captured : CapturedAuthority := ⟨⟨authorityVersion,⟨"fixture","authority-snapshot","1"⟩,authorityKind,
  ⟨"profile-authority-snapshot",authority,frame⟩,issuer⟩,⟨[3],1,bootstrap.ref,"uncomputed-typed-authority-digest"⟩⟩
def withAuthority (a : Authority) : CapturedAuthority := {captured with record:={captured.record with body:={captured.record.body with target:=a}}}
def dataCheck (a : CapturedAuthority) : Bool := authorityCheck bootstrap frame root captured.entry.ref a && evidenceRowsCheck frame profile a
def changedRef (ref : RevisionRef) : RevisionRef := {ref with digest:="changed"}

theorem positive_batched_review_and_dual_action_grant : dataCheck captured=true := by decide

theorem missing_issuance : dataCheck (withAuthority {authority with issues:=[]})=false := by decide

theorem missing_entitlement : dataCheck (withAuthority {authority with grants:=[]})=false := by decide

theorem missing_review : dataCheck (withAuthority {authority with reviews:=[]})=false := by decide

theorem source_bytes_changed_same_count : dataCheck (withAuthority {authority with issues:=[{declarationIssue with bytes:=[9]},selectionIssue]})=false := by decide

theorem wrong_issuer : dataCheck (withAuthority {authority with issues:=[{declarationIssue with issuer:=changedRef issuer},selectionIssue]})=false := by decide

theorem wrong_source_reference : dataCheck (withAuthority {authority with issues:=[{declarationIssue with source:=changedRef declaration.entry.ref},selectionIssue]})=false := by decide

theorem wrong_source_kind : dataCheck (withAuthority {authority with issues:=[{declarationIssue with kind:="other"},selectionIssue]})=false := by decide

theorem wrong_issuance_review_reference : dataCheck (withAuthority {authority with issues:=[{declarationIssue with ownerReview:=changedRef issuer},selectionIssue]})=false := by decide

theorem wrong_grant_principal : dataCheck (withAuthority {authority with grants:=[{grant with principal:=changedRef issuer}]})=false := by decide

theorem wrong_grant_scope : dataCheck (withAuthority {authority with grants:=[{grant with scope:=changedRef frame.scope}]})=false := by decide

theorem missing_declare_action : dataCheck (withAuthority {authority with grants:=[{grant with actions:=["select"]}]})=false := by decide

theorem missing_select_action : dataCheck (withAuthority {authority with grants:=[{grant with actions:=["declare"]}]})=false := by decide

theorem wrong_review_reference : dataCheck (withAuthority {authority with reviews:=[{declarationReview with ref:=changedRef issuer},selectionReview]})=false := by decide

theorem wrong_review_subject : dataCheck (withAuthority {authority with reviews:=[{declarationReview with source:=changedRef declaration.entry.ref},selectionReview]})=false := by decide

theorem wrong_review_decision : dataCheck (withAuthority {authority with reviews:=[{declarationReview with decision:=.rejected},selectionReview]})=false := by decide

theorem wrong_revocation : dataCheck (withAuthority {authority with reviews:=[{declarationReview with revocation:=.revoked},selectionReview]})=false := by decide

theorem wrong_expiry : dataCheck (withAuthority {authority with reviews:=[{declarationReview with expiry:=101},selectionReview]})=false := by decide

theorem wrong_root : dataCheck (withAuthority {authority with trustRoot:=changedRef root})=false := by decide

theorem wrong_bootstrap : dataCheck (withAuthority {authority with bootstrap:={bootstrap with encoding:="upperhex64"}})=false := by decide

theorem wrong_expected_authority_reference : authorityCheck bootstrap frame root (changedRef captured.entry.ref) captured=false := by decide

theorem wrong_authority_full_frame : dataCheck {captured with record:={captured.record with body:={captured.record.body with frame:={frame with epoch:=43}}}}=false := by decide

theorem wrong_profile_full_frame : evidenceRowsCheck frame {profile with frame:={frame with epoch:=43}} captured=false := by decide

theorem omitted_manifest : dataCheck (withAuthority {authority with declarations:=[]})=false := by decide

theorem extra_manifest : dataCheck (withAuthority {authority with declarations:=[declaration.entry.ref,declaration.entry.ref]})=false := by decide

theorem wrong_manifest_reference : dataCheck (withAuthority {authority with selections:=[changedRef selection.entry.ref]})=false := by decide

theorem identical_duplicate_facts : dataCheck (withAuthority {authority with issues:=[declarationIssue,selectionIssue,declarationIssue],grants:=[grant,grant],reviews:=[declarationReview,selectionReview,declarationReview]})=true := by decide

theorem unused_issuance_equivocation : dataCheck (withAuthority {authority with issues:=[declarationIssue,selectionIssue,{declarationIssue with bytes:=[9]}]})=false := by decide

theorem unused_grant_equivocation : dataCheck (withAuthority {authority with grants:=[grant,{grant with actions:=["select"]}]})=false := by decide

theorem unused_review_pair_equivocation : dataCheck (withAuthority {authority with reviews:=[declarationReview,selectionReview,{declarationReview with decision:=.rejected}]})=false := by decide

theorem review_reference_key_equivocation : dataCheck (withAuthority {authority with reviews:=[declarationReview,selectionReview,{selectionReview with ref:=changedRef issuer}]})=false := by decide

theorem byte_value_outside_domain : coherenceCheck {authority with issues:=[{declarationIssue with bytes:=[300]}]}=false := by decide

theorem unsupported_grant_action : coherenceCheck {authority with grants:=[{grant with actions:=["admin"]}]}=false := by decide

theorem reordered_manifest : evidenceRowsCheck frame {profile with declarations:=[declaration,{declaration with record:={declaration.record with bindingKey:=⟨"fixture","other-declaration","1"⟩}}]} (withAuthority {authority with declarations:=[⟨⟨"fixture","other-declaration","1"⟩,declaration.entry.ref.digest⟩,declaration.entry.ref]})=false := by decide

def unavailableRoot : RootPolicy := ⟨fun _ _ _=>False⟩
theorem positive_structural_data_cannot_supply_authenticity :
    ¬unavailableRoot.authoritativeSnapshot root frame captured.envelope := by intro impossible;exact impossible
theorem absent_root_blocks_profile_ownership (declarations selections : List CandidateBindingCapture.Envelope) (ref : RevisionRef) :
    ¬CandidateProfileSelection.OwnedProfileMeaning
      (interpretedRequirements unavailableRoot bootstrap ⟨10000,100000,100⟩ root captured.entry.ref captured.envelope captured)
      bootstrap ⟨10000,100000,100⟩ declarations selections frame ref := by
  apply absent_boundary_blocks_owned_profile
  exact positive_structural_data_cannot_supply_authenticity
#print axioms positive_batched_review_and_dual_action_grant
#print axioms missing_issuance
#print axioms missing_entitlement
#print axioms missing_review
#print axioms source_bytes_changed_same_count
#print axioms wrong_issuer
#print axioms wrong_source_reference
#print axioms wrong_source_kind
#print axioms wrong_issuance_review_reference
#print axioms wrong_grant_principal
#print axioms wrong_grant_scope
#print axioms missing_declare_action
#print axioms missing_select_action
#print axioms wrong_review_reference
#print axioms wrong_review_subject
#print axioms wrong_review_decision
#print axioms wrong_revocation
#print axioms wrong_expiry
#print axioms wrong_root
#print axioms wrong_bootstrap
#print axioms wrong_expected_authority_reference
#print axioms wrong_authority_full_frame
#print axioms wrong_profile_full_frame
#print axioms omitted_manifest
#print axioms extra_manifest
#print axioms wrong_manifest_reference
#print axioms identical_duplicate_facts
#print axioms unused_issuance_equivocation
#print axioms unused_grant_equivocation
#print axioms unused_review_pair_equivocation
#print axioms review_reference_key_equivocation
#print axioms byte_value_outside_domain
#print axioms unsupported_grant_action
#print axioms reordered_manifest
#print axioms positive_structural_data_cannot_supply_authenticity
#print axioms absent_root_blocks_profile_ownership
end RelationalSuccessor.CandidateProfileEvidence.Controls
