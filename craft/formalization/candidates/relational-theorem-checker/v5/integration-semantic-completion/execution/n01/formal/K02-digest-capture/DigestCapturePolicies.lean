import DigestCapture
set_option autoImplicit false
namespace RelationalSuccessor.CandidateDigestCapture
open CandidateBindingCapture (Envelope Prepared Policies CaptureMeaning)
open CandidateDigest (Profile ProfileMeaning DigestMeaning VerifiedDigestMeaning)

def CaptureDigestMeaning (profile : Profile) (ref : RevisionRef) (bytes : List UInt8) (digest : String) : Prop :=
  ProfileMeaning profile ref ∧ DigestMeaning bytes digest

def withDigestPolicy {α : Type} (profile : Profile) (policies : Policies α) : Policies α :=
  { policies with
    parses := CandidateScalarConversion.ScalarByteDocumentMeaning
    digest := CaptureDigestMeaning profile }

theorem installed_parse_policy {α : Type} (profile : Profile) (policies : Policies α)
    (bytes : List UInt8) (ast : CandidateBindingCapture.J) :
    (withDigestPolicy profile policies).parses bytes ast ↔ CandidateScalarConversion.ScalarByteDocumentMeaning bytes ast := Iff.rfl

theorem installed_digest_policy {α : Type} (profile : Profile) (policies : Policies α)
    (ref : RevisionRef) (bytes : List UInt8) (digest : String) :
    (withDigestPolicy profile policies).digest ref bytes digest ↔
      ProfileMeaning profile ref ∧ DigestMeaning bytes digest := Iff.rfl

theorem authentication_schema_review_unchanged {α : Type} (profile : Profile) (policies : Policies α) :
    (withDigestPolicy profile policies).ownedDigestProfile=policies.ownedDigestProfile ∧
    (withDigestPolicy profile policies).schema=policies.schema ∧
    (withDigestPolicy profile policies).reviewed=policies.reviewed := ⟨rfl,rfl,rfl⟩

theorem checked_capture_construction {α : Type} (profile : Profile) (policies : Policies α)
    (budget : Nat) (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (prepared : Prepared α)
    (meaning : DigestPreparedMeaning profile budget version kind target frame capture prepared)
    (owned : policies.ownedDigestProfile frame capture.digestProfile)
    (schema : ∀ ast, CandidateScalarConversion.ScalarByteDocumentMeaning capture.content ast →
      policies.schema frame version kind ast)
    (reviewed : policies.reviewed frame prepared.entry) :
    ∃ ast, CaptureMeaning (withDigestPolicy profile policies) version kind target frame capture ast prepared := by
  rcases meaning.1 with ⟨ast,parsed,data⟩
  exact ⟨ast,data,parsed,⟨meaning.2.1,meaning.2.2.2.2⟩,owned,schema ast parsed,reviewed⟩

theorem capture_implies_checked_preparation {α : Type} (profile : Profile) (policies : Policies α)
    (budget : Nat) (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (ast : CandidateBindingCapture.J) (prepared : Prepared α)
    (meaning : CaptureMeaning (withDigestPolicy profile policies) version kind target frame capture ast prepared)
    (bounded : capture.content.length≤budget) :
    prepareDigestBytes profile budget version kind target frame capture=some prepared := by
  apply (digest_capture_exact profile budget version kind target frame capture prepared).mpr
  refine ⟨⟨ast,meaning.bytesParse,meaning.preparedData⟩,meaning.digest.1,?_,bounded,meaning.digest.2⟩
  rcases meaning.digest.2 with ⟨_,_,_,padding,_,_,_⟩
  exact padding.1

theorem absent_profile_ownership_blocks_complete_capture {α : Type} (profile : Profile) (policies : Policies α)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame)
    (capture : Envelope) (ast : CandidateBindingCapture.J) (prepared : Prepared α)
    (absent : ¬policies.ownedDigestProfile frame capture.digestProfile) :
    ¬CaptureMeaning (withDigestPolicy profile policies) version kind target frame capture ast prepared := by
  intro meaning;exact absent meaning.ownedProfile

theorem absent_schema_blocks_complete_capture {α : Type} (profile : Profile) (policies : Policies α)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame)
    (capture : Envelope) (ast : CandidateBindingCapture.J) (prepared : Prepared α)
    (absent : ¬policies.schema frame version kind ast) :
    ¬CaptureMeaning (withDigestPolicy profile policies) version kind target frame capture ast prepared := by
  intro meaning;exact absent meaning.schema

theorem absent_review_blocks_complete_capture {α : Type} (profile : Profile) (policies : Policies α)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame)
    (capture : Envelope) (ast : CandidateBindingCapture.J) (prepared : Prepared α)
    (absent : ¬policies.reviewed frame prepared.entry) :
    ¬CaptureMeaning (withDigestPolicy profile policies) version kind target frame capture ast prepared := by
  intro meaning;exact absent meaning.reviewed
#print axioms installed_parse_policy
#print axioms installed_digest_policy
#print axioms authentication_schema_review_unchanged
#print axioms checked_capture_construction
#print axioms capture_implies_checked_preparation
#print axioms absent_profile_ownership_blocks_complete_capture
#print axioms absent_schema_blocks_complete_capture
#print axioms absent_review_blocks_complete_capture
end RelationalSuccessor.CandidateDigestCapture
