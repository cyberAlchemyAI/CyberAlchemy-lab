import DigestProfile
import CaptureBytesCatalog
set_option autoImplicit false
namespace RelationalSuccessor.CandidateDigestCapture
open CandidateBindingCapture (Envelope EnvelopeMeaning Prepared)
open CandidateBindingBytes (PreparedBytesMeaning prepareBytes prepare_bytes_exact)
open CandidateDigest (Profile VerifiedDigestMeaning DigestMeaning ProfileMeaning digestCheck digest_check_exact)

def DigestPreparedMeaning {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (prepared : Prepared α) : Prop :=
  PreparedBytesMeaning version kind target frame capture prepared ∧
  VerifiedDigestMeaning profile capture.digestProfile capture.content capture.digest budget

def prepareDigestBytes {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) : Option (Prepared α) :=
  if CandidateBindingCapture.envelopeCheck capture then
    if digestCheck profile capture.digestProfile capture.content capture.digest budget then
      prepareBytes version kind target frame capture
    else none
  else none

theorem digest_capture_exact {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (prepared : Prepared α) :
    prepareDigestBytes profile budget version kind target frame capture=some prepared ↔
      DigestPreparedMeaning profile budget version kind target frame capture prepared := by
  constructor
  · intro accepted
    unfold prepareDigestBytes at accepted
    split at accepted
    · split at accepted
      · rename_i checked
        exact ⟨(prepare_bytes_exact version kind target frame capture prepared).mp accepted,
          (digest_check_exact profile capture.digestProfile capture.content capture.digest budget).mp checked⟩
      · contradiction
    · contradiction
  · rintro ⟨bytes,digest⟩
    rcases bytes with ⟨ast,parsed,data⟩
    have envelope := (CandidateBindingCapture.envelope_check_exact capture).mpr data.envelope
    have checked := (digest_check_exact profile capture.digestProfile capture.content capture.digest budget).mpr digest
    simp only [prepareDigestBytes,envelope,checked,if_true]
    exact (prepare_bytes_exact version kind target frame capture prepared).mpr ⟨ast,parsed,data⟩

theorem digest_capture_none_exact {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) :
    prepareDigestBytes profile budget version kind target frame capture=none ↔
      ¬ ∃ prepared, DigestPreparedMeaning profile budget version kind target frame capture prepared := by
  constructor
  · intro refused; rintro ⟨prepared,meaning⟩
    have accepted := (digest_capture_exact profile budget version kind target frame capture prepared).mpr meaning
    rw [refused] at accepted; contradiction
  · intro invalid
    cases eq : prepareDigestBytes profile budget version kind target frame capture with
    | none => rfl
    | some prepared => exact False.elim (invalid ⟨prepared,(digest_capture_exact profile budget version kind target frame capture prepared).mp eq⟩)

theorem digest_capture_unique {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (a b : Prepared α)
    (ha : DigestPreparedMeaning profile budget version kind target frame capture a)
    (hb : DigestPreparedMeaning profile budget version kind target frame capture b) : a=b :=
  CandidateBindingBytes.prepared_bytes_unique version kind target frame capture a b ha.1 hb.1

theorem digest_capture_retains_envelope {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (prepared : Prepared α)
    (meaning : DigestPreparedMeaning profile budget version kind target frame capture prepared) :
    prepared.envelope=capture ∧ prepared.envelope.byteLength=prepared.entry.content.length :=
  CandidateBindingBytes.prepared_bytes_retains_capture version kind target frame capture prepared meaning.1

theorem digest_entry_provenance {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (prepared : Prepared α)
    (meaning : DigestPreparedMeaning profile budget version kind target frame capture prepared) :
    prepared.entry.content=capture.content ∧ prepared.entry.ref.digest=capture.digest ∧
      DigestMeaning prepared.entry.content prepared.entry.ref.digest ∧
      profile.ref=prepared.envelope.digestProfile := by
  have fields := CandidateBindingBytes.prepared_bytes_entry_fields version kind target frame capture prepared meaning.1
  have same := (digest_capture_retains_envelope profile budget version kind target frame capture prepared meaning).1
  refine ⟨fields.2.2.2.2.1,fields.2.1,?_,?_⟩
  · simpa only [fields.2.2.2.2.1,fields.2.1] using meaning.2.2.2.2
  · simpa only [same] using meaning.2.1.1

theorem invalid_envelope_refuses {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (bad : ¬EnvelopeMeaning capture) :
    prepareDigestBytes profile budget version kind target frame capture=none := by
  apply (digest_capture_none_exact profile budget version kind target frame capture).mpr
  rintro ⟨prepared,⟨ast,_,data⟩,_⟩
  exact bad data.envelope

theorem unsupported_digest_refuses {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope)
    (bad : ¬VerifiedDigestMeaning profile capture.digestProfile capture.content capture.digest budget) :
    prepareDigestBytes profile budget version kind target frame capture=none := by
  apply (digest_capture_none_exact profile budget version kind target frame capture).mpr
  rintro ⟨prepared,_,meaning⟩;exact bad meaning

def prepareResolutionDigest (profile : Profile) (budget : Nat) (frame : Frame) (capture : Envelope) :
    Option (Prepared CandidateIntentAddressing.Resolution) :=
  prepareDigestBytes profile budget CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind
    CandidateBindingAst.resolution frame capture
def prepareRoleDigest (profile : Profile) (budget : Nat) (frame : Frame) (capture : Envelope) :
    Option (Prepared CandidateIntentAddressing.Role) :=
  prepareDigestBytes profile budget CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind
    CandidateBindingAst.role frame capture

theorem resolution_digest_exact (profile : Profile) (budget : Nat) (frame : Frame) (capture : Envelope)
    (prepared : Prepared CandidateIntentAddressing.Resolution) :
    prepareResolutionDigest profile budget frame capture=some prepared ↔
      DigestPreparedMeaning profile budget CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind
        CandidateBindingAst.resolution frame capture prepared :=
  digest_capture_exact profile budget _ _ _ frame capture prepared

theorem role_digest_exact (profile : Profile) (budget : Nat) (frame : Frame) (capture : Envelope)
    (prepared : Prepared CandidateIntentAddressing.Role) :
    prepareRoleDigest profile budget frame capture=some prepared ↔
      DigestPreparedMeaning profile budget CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind
        CandidateBindingAst.role frame capture prepared :=
  digest_capture_exact profile budget _ _ _ frame capture prepared
#print axioms digest_capture_exact
#print axioms digest_capture_none_exact
#print axioms digest_capture_unique
#print axioms digest_capture_retains_envelope
#print axioms digest_entry_provenance
#print axioms invalid_envelope_refuses
#print axioms unsupported_digest_refuses
#print axioms resolution_digest_exact
#print axioms role_digest_exact
end RelationalSuccessor.CandidateDigestCapture
