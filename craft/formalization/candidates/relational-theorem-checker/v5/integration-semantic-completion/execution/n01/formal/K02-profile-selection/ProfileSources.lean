import DigestCaptureCatalog
set_option autoImplicit false
namespace RelationalSuccessor.CandidateProfileSelection
open CandidateBindingAst (Decoder Fields J object cons mapFields empty nonempty reference ObjectMeaning)

inductive ReviewPosture where
  | missing | accepted | rejected
  deriving DecidableEq, Repr
inductive RevocationPosture where
  | unknown | clear | revoked
  deriving DecidableEq, Repr

def reviewName : ReviewPosture → String
  | .missing=>"missing" | .accepted=>"accepted" | .rejected=>"rejected"
def revocationName : RevocationPosture → String
  | .unknown=>"unknown" | .clear=>"clear" | .revoked=>"revoked"
def ReviewMeaning (value : J) (output : ReviewPosture) : Prop := value=.string (reviewName output)
def RevocationMeaning (value : J) (output : RevocationPosture) : Prop := value=.string (revocationName output)
def decodeReview : J → Option ReviewPosture
  | .string "missing"=>some .missing | .string "accepted"=>some .accepted | .string "rejected"=>some .rejected | _=>none
def decodeRevocation : J → Option RevocationPosture
  | .string "unknown"=>some .unknown | .string "clear"=>some .clear | .string "revoked"=>some .revoked | _=>none

theorem review_exact (value : J) (output : ReviewPosture) : decodeReview value=some output ↔ ReviewMeaning value output := by
  cases output <;> cases value <;> simp [decodeReview,ReviewMeaning,reviewName]
  all_goals split <;> simp_all
  all_goals split <;> simp_all
  all_goals split <;> simp_all

theorem revocation_exact (value : J) (output : RevocationPosture) : decodeRevocation value=some output ↔ RevocationMeaning value output := by
  cases output <;> cases value <;> simp [decodeRevocation,RevocationMeaning,revocationName]
  all_goals split <;> simp_all
  all_goals split <;> simp_all
  all_goals split <;> simp_all

def reviewDecoder : Decoder ReviewPosture := ⟨decodeReview,ReviewMeaning,review_exact⟩
def revocationDecoder : Decoder RevocationPosture := ⟨decodeRevocation,RevocationMeaning,revocation_exact⟩
structure Settings where
  algorithm : String
  encoding : String
  issuer : RevisionRef
  review : ReviewPosture
  revocation : RevocationPosture
  expiry : Nat
  deriving DecidableEq, Repr
structure Selection where
  declaration : RevisionRef
  issuer : RevisionRef
  review : ReviewPosture
  revocation : RevocationPosture
  expiry : Nat
  deriving DecidableEq, Repr

def settingsKeys : List String := ["algorithm","encoding","issuer","review_posture","revocation_posture","expiry_epoch"]
def selectionKeys : List String := ["declaration_ref","issuer","review_posture","revocation_posture","expiry_epoch"]
def settingsFields : Fields Settings := mapFields
  (cons nonempty (cons nonempty (cons reference (cons reviewDecoder (cons revocationDecoder (cons CandidateNumberParser.epochAdapter empty))))))
  (fun x=>⟨x.1,x.2.1,x.2.2.1,x.2.2.2.1,x.2.2.2.2.1,x.2.2.2.2.2.1⟩)
def selectionFields : Fields Selection := mapFields
  (cons reference (cons reference (cons reviewDecoder (cons revocationDecoder (cons CandidateNumberParser.epochAdapter empty)))))
  (fun x=>⟨x.1,x.2.1,x.2.2.1,x.2.2.2.1,x.2.2.2.2.1⟩)
def settingsDecoder : Decoder Settings := object settingsKeys settingsFields
def selectionDecoder : Decoder Selection := object selectionKeys selectionFields

def SettingsMeaning (value : J) (output : Settings) : Prop := ObjectMeaning settingsKeys settingsFields value output
def SelectionMeaning (value : J) (output : Selection) : Prop := ObjectMeaning selectionKeys selectionFields value output

theorem settings_exact (value : J) (output : Settings) : settingsDecoder.decode value=some output ↔ SettingsMeaning value output :=
  CandidateBindingAst.object_exact settingsKeys settingsFields value output

theorem selection_exact (value : J) (output : Selection) : selectionDecoder.decode value=some output ↔ SelectionMeaning value output :=
  CandidateBindingAst.object_exact selectionKeys selectionFields value output

def declarationVersion : String := "cyberalchemy-lab-digest-profile-declaration/candidate-v1"
def declarationKind : String := "digest-profile-declaration"
def selectionVersion : String := "cyberalchemy-lab-digest-profile-selection/candidate-v1"
def selectionKind : String := "digest-profile-selection"
abbrev Declaration := CandidateBindingCapture.Prepared Settings
abbrev SelectionRecord := CandidateBindingCapture.Prepared Selection

def declaredProfile (record : Declaration) : CandidateDigest.Profile :=
  ⟨record.entry.ref,record.record.body.target.algorithm,record.record.body.target.encoding⟩

def DeclarationEligible (frame : Frame) (record : Declaration) : Prop :=
  record.record.body.frame=frame ∧ record.record.body.token="declare-profile" ∧ record.record.body.target.review=.accepted ∧
  record.record.body.target.revocation=.clear ∧ frame.epoch<record.record.body.target.expiry

def SelectionEligible (frame : Frame) (record : SelectionRecord) : Prop :=
  record.record.body.frame=frame ∧ record.record.body.token="select-profile" ∧ record.record.body.target.review=.accepted ∧
  record.record.body.target.revocation=.clear ∧ frame.epoch<record.record.body.target.expiry
instance (frame : Frame) (record : Declaration) : Decidable (DeclarationEligible frame record) := by unfold DeclarationEligible;infer_instance
instance (frame : Frame) (record : SelectionRecord) : Decidable (SelectionEligible frame record) := by unfold SelectionEligible;infer_instance
#print axioms review_exact
#print axioms revocation_exact
#print axioms settings_exact
#print axioms selection_exact
end RelationalSuccessor.CandidateProfileSelection
