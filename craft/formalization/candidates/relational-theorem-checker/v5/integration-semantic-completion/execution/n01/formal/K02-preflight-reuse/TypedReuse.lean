import CertifiedPreflight
set_option autoImplicit false
namespace RelationalSuccessor.CandidatePreflightReuse
open CandidateBindingCapture (Prepared)
open CandidateDigest (Profile)
open CandidateEvidenceResources (NumericLimits)

def prepareInput {α : Type} {profile : Profile} {budget : Nat} {numbers : NumericLimits}
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame)
    (input : CertifiedInput profile budget numbers) : Option (Prepared α) :=
  CandidateBindingCapture.prepare version kind target frame input.val.capture input.val.ast

theorem cached_preparation_exact {α : Type} {profile : Profile} {budget : Nat} {numbers : NumericLimits}
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame)
    (input : CertifiedInput profile budget numbers) (prepared : Prepared α) :
    prepareInput version kind target frame input=some prepared ↔
      CandidateDigestCapture.DigestPreparedMeaning profile budget version kind target frame input.val.capture prepared := by
  constructor
  · intro found
    exact ⟨⟨input.val.ast,input.property.2.2.1,
      (CandidateBindingCapture.prepare_exact version kind target frame input.val.capture input.val.ast prepared).mp found⟩,input.property.2.1⟩
  · rintro ⟨⟨ast,parsed,data⟩,_⟩
    have same:=CandidateScalarConversion.scalar_byte_meaning_unique input.val.capture.content ast input.val.ast parsed input.property.2.2.1
    rw [same] at data
    exact (CandidateBindingCapture.prepare_exact version kind target frame input.val.capture input.val.ast prepared).mpr data

theorem cached_preparation_equal_legacy {α : Type} {profile : Profile} {budget : Nat} {numbers : NumericLimits}
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame)
    (input : CertifiedInput profile budget numbers) :
    prepareInput version kind target frame input=CandidateDigestCapture.prepareDigestBytes profile budget version kind target frame input.val.capture := by
  apply Option.ext
  intro prepared
  exact (cached_preparation_exact version kind target frame input prepared).trans
    (CandidateDigestCapture.digest_capture_exact profile budget version kind target frame input.val.capture prepared).symm

def prepareMany {α : Type} {profile : Profile} {budget : Nat} {numbers : NumericLimits}
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) :
    List (CertifiedInput profile budget numbers) → Option (List (Prepared α))
  | []=>some []
  | input::inputs=>(prepareInput version kind target frame input).bind fun prepared=>
      (prepareMany version kind target frame inputs).map fun outputs=>prepared::outputs

theorem cached_many_equal_legacy {α : Type} {profile : Profile} {budget : Nat} {numbers : NumericLimits}
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame)
    (inputs : List (CertifiedInput profile budget numbers)) :
    prepareMany version kind target frame inputs=
      CandidateDigestCapture.prepareManyDigest profile budget version kind target frame (inputs.map fun input=>input.val.capture) := by
  induction inputs with
  | nil=>rfl
  | cons input inputs ih=>simp only [prepareMany,List.map_cons,CandidateDigestCapture.prepareManyDigest,cached_preparation_equal_legacy,ih]

theorem cached_many_exact {α : Type} {profile : Profile} {budget : Nat} {numbers : NumericLimits}
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame)
    (inputs : List (CertifiedInput profile budget numbers)) (outputs : List (Prepared α)) :
    prepareMany version kind target frame inputs=some outputs ↔
      CandidateDigestCapture.DigestManyMeaning profile budget version kind target frame (inputs.map fun input=>input.val.capture) outputs := by
  rw [cached_many_equal_legacy]
  exact CandidateDigestCapture.digest_many_exact profile budget version kind target frame _ outputs

theorem cached_many_retains_original_inputs {α : Type} {profile : Profile} {budget : Nat} {numbers : NumericLimits}
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame)
    (inputs : List (CertifiedInput profile budget numbers)) (outputs : List (Prepared α))
    (found : prepareMany version kind target frame inputs=some outputs) :
    outputs.map Prepared.envelope=inputs.map fun input=>input.val.capture :=
  CandidateDigestCapture.digest_many_retains_envelopes ((cached_many_exact version kind target frame inputs outputs).mp found)
#print axioms cached_preparation_exact
#print axioms cached_preparation_equal_legacy
#print axioms cached_many_equal_legacy
#print axioms cached_many_exact
#print axioms cached_many_retains_original_inputs
end RelationalSuccessor.CandidatePreflightReuse
