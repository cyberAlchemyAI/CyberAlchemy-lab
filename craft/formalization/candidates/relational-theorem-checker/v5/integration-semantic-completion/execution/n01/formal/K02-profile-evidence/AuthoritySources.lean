import ProfileSelectionEvidence
set_option autoImplicit false
namespace RelationalSuccessor.CandidateProfileEvidence
open CandidateBindingAst (Decoder Fields J object cons mapFields empty nonempty reference array ObjectMeaning)
open CandidateProfileSelection (ReviewPosture RevocationPosture reviewDecoder revocationDecoder)

structure Issue where
  source : RevisionRef
  kind : String
  issuer : RevisionRef
  ownerReview : RevisionRef
  bytes : List Nat
  deriving DecidableEq, Repr
structure Grant where
  ref : RevisionRef
  principal : RevisionRef
  actions : List String
  scope : RevisionRef
  deriving DecidableEq, Repr
structure Review where
  ref : RevisionRef
  source : RevisionRef
  decision : ReviewPosture
  revocation : RevocationPosture
  expiry : Nat
  deriving DecidableEq, Repr
structure Authority where
  trustRoot : RevisionRef
  bootstrap : CandidateDigest.Profile
  declarations : List RevisionRef
  selections : List RevisionRef
  issues : List Issue
  grants : List Grant
  reviews : List Review
  deriving DecidableEq, Repr

def profileKeys : List String := ["ref","algorithm","encoding"]
def profileFields : Fields CandidateDigest.Profile := mapFields
  (cons reference (cons nonempty (cons nonempty empty))) (fun x=>⟨x.1,x.2.1,x.2.2.1⟩)
def profileDecoder := object profileKeys profileFields
def issueKeys : List String := ["source_ref","source_kind","issuer","owner_review_ref","source_bytes"]
def issueFields : Fields Issue := mapFields
  (cons reference (cons nonempty (cons reference (cons reference (cons (array CandidateNumberParser.epochAdapter) empty)))))
  (fun x=>⟨x.1,x.2.1,x.2.2.1,x.2.2.2.1,x.2.2.2.2.1⟩)
def issueDecoder := object issueKeys issueFields
def grantKeys : List String := ["ref","principal","actions","scope"]
def grantFields : Fields Grant := mapFields
  (cons reference (cons reference (cons (array nonempty) (cons reference empty))))
  (fun x=>⟨x.1,x.2.1,x.2.2.1,x.2.2.2.1⟩)
def grantDecoder := object grantKeys grantFields
def reviewKeys : List String := ["ref","source_ref","decision","revocation","expiry_epoch"]
def reviewFields : Fields Review := mapFields
  (cons reference (cons reference (cons reviewDecoder (cons revocationDecoder (cons CandidateNumberParser.epochAdapter empty)))))
  (fun x=>⟨x.1,x.2.1,x.2.2.1,x.2.2.2.1,x.2.2.2.2.1⟩)
def reviewDecoder := object reviewKeys reviewFields
def authorityKeys : List String := ["trust_root","bootstrap","declaration_manifest","selection_manifest","issuances","entitlements","reviews"]
def authorityFields : Fields Authority := mapFields
  (cons reference (cons profileDecoder (cons (array reference) (cons (array reference)
    (cons (array issueDecoder) (cons (array grantDecoder) (cons (array reviewDecoder) empty)))))))
  (fun x=>⟨x.1,x.2.1,x.2.2.1,x.2.2.2.1,x.2.2.2.2.1,x.2.2.2.2.2.1,x.2.2.2.2.2.2.1⟩)
def authorityDecoder := object authorityKeys authorityFields
def AuthoritySourceMeaning (value : J) (output : Authority) : Prop := ObjectMeaning authorityKeys authorityFields value output

theorem profile_source_exact (value : J) (output : CandidateDigest.Profile) :
    profileDecoder.decode value=some output ↔ ObjectMeaning profileKeys profileFields value output :=
  CandidateBindingAst.object_exact profileKeys profileFields value output
theorem issue_source_exact (value : J) (output : Issue) :
    issueDecoder.decode value=some output ↔ ObjectMeaning issueKeys issueFields value output :=
  CandidateBindingAst.object_exact issueKeys issueFields value output
theorem grant_source_exact (value : J) (output : Grant) :
    grantDecoder.decode value=some output ↔ ObjectMeaning grantKeys grantFields value output :=
  CandidateBindingAst.object_exact grantKeys grantFields value output
theorem review_source_exact (value : J) (output : Review) :
    reviewDecoder.decode value=some output ↔ ObjectMeaning reviewKeys reviewFields value output :=
  CandidateBindingAst.object_exact reviewKeys reviewFields value output
theorem authority_source_exact (value : J) (output : Authority) :
    authorityDecoder.decode value=some output ↔ AuthoritySourceMeaning value output :=
  CandidateBindingAst.object_exact authorityKeys authorityFields value output

def authorityVersion := "cyberalchemy-lab-profile-authority-snapshot/candidate-v1"
def authorityKind := "profile-authority-snapshot"
abbrev CapturedAuthority := CandidateBindingCapture.Prepared Authority
#print axioms profile_source_exact
#print axioms issue_source_exact
#print axioms grant_source_exact
#print axioms review_source_exact
#print axioms authority_source_exact
end RelationalSuccessor.CandidateProfileEvidence
