import CaptureByteOutcomes
set_option autoImplicit false
namespace RelationalSuccessor.CandidateBindingBytes
open CandidateBindingCapture (Envelope Prepared CatalogStage ProfileAlignmentMeaning profileAlignmentCheck profile_alignment_exact)

inductive BytesManyMeaning {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) : List Envelope → List (Prepared α) → Prop
  | nil : BytesManyMeaning version kind target frame [] []
  | cons (input : Envelope) (prepared : Prepared α) (inputs : List Envelope) (outputs : List (Prepared α))
      (head : PreparedBytesMeaning version kind target frame input prepared)
      (tail : BytesManyMeaning version kind target frame inputs outputs) :
      BytesManyMeaning version kind target frame (input::inputs) (prepared::outputs)

def prepareManyBytes {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) : List Envelope → Option (List (Prepared α))
  | [] => some []
  | input::inputs =>
    match prepareBytes version kind target frame input with
    | none => none
    | some prepared =>
      match prepareManyBytes version kind target frame inputs with
      | none => none
      | some outputs => some (prepared::outputs)

theorem prepare_many_bytes_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (inputs : List Envelope) (outputs : List (Prepared α)) :
    prepareManyBytes version kind target frame inputs = some outputs ↔
      BytesManyMeaning version kind target frame inputs outputs := by
  constructor
  · intro accepted
    induction inputs generalizing outputs with
    | nil => simp only [prepareManyBytes,Option.some.injEq] at accepted; subst outputs; exact .nil
    | cons input inputs ih =>
      unfold prepareManyBytes at accepted
      cases head : prepareBytes version kind target frame input with
      | none => simp [head] at accepted
      | some prepared =>
        simp only [head] at accepted
        cases tail : prepareManyBytes version kind target frame inputs with
        | none => simp [tail] at accepted
        | some rest =>
          simp only [tail,Option.some.injEq] at accepted
          subst outputs
          exact .cons input prepared inputs rest
            ((prepare_bytes_exact version kind target frame input prepared).mp head) (ih rest tail)
  · intro meaning
    induction meaning with
    | nil => rfl
    | cons input prepared inputs outputs head tail ih =>
      simp only [prepareManyBytes,(prepare_bytes_exact version kind target frame input prepared).mpr head,ih]

theorem many_bytes_preserves_length {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (inputs : List Envelope) (outputs : List (Prepared α))
    (meaning : BytesManyMeaning version kind target frame inputs outputs) : outputs.length = inputs.length := by
  induction meaning with
  | nil => rfl
  | cons input prepared inputs outputs head tail ih => simp only [List.length_cons,ih]

theorem many_bytes_output_provenance {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (inputs : List Envelope) (outputs : List (Prepared α))
    (meaning : BytesManyMeaning version kind target frame inputs outputs) :
    ∀ prepared ∈ outputs, ∃ input ∈ inputs,
      PreparedBytesMeaning version kind target frame input prepared := by
  induction meaning with
  | nil => intro prepared member; simp at member
  | cons input prepared inputs outputs head tail ih =>
    intro output member
    simp only [List.mem_cons] at member
    rcases member with same | rest
    · subst output; exact ⟨input,by simp,head⟩
    · rcases ih output rest with ⟨origin,member,meaning⟩
      exact ⟨origin,by simp [member],meaning⟩

structure BytesCatalogMeaning {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (targetKey : α → RevisionKey) (frame : Frame) (digestProfile : RevisionRef) (records roots : List Envelope)
    (stage : CatalogStage α) : Prop where
  records : BytesManyMeaning version kind target frame records stage.records
  roots : BytesManyMeaning version kind target frame roots stage.roots
  frame : stage.frame = frame
  profile : stage.digestProfile = digestProfile
  profiles : ProfileAlignmentMeaning digestProfile stage.records stage.roots
  structural : CandidateOwnedBindings.CatalogMeaning stage.catalog kind targetKey

def prepareCatalogBytes {α : Type} [DecidableEq α] (version kind : String) (target : CandidateBindingAst.Decoder α)
    (targetKey : α → RevisionKey) (frame : Frame) (digestProfile : RevisionRef) (records roots : List Envelope) : Option (CatalogStage α) :=
  match prepareManyBytes version kind target frame records,prepareManyBytes version kind target frame roots with
  | some preparedRecords,some preparedRoots =>
    let stage : CatalogStage α := ⟨frame,digestProfile,preparedRecords,preparedRoots⟩
    if profileAlignmentCheck digestProfile preparedRecords preparedRoots &&
        CandidateOwnedBindings.catalogCheck stage.catalog kind targetKey then some stage else none
  | _,_ => none

theorem prepare_bytes_catalog_exact {α : Type} [DecidableEq α] (version kind : String) (target : CandidateBindingAst.Decoder α)
    (targetKey : α → RevisionKey) (frame : Frame) (digestProfile : RevisionRef) (records roots : List Envelope)
    (stage : CatalogStage α) :
    prepareCatalogBytes version kind target targetKey frame digestProfile records roots = some stage ↔
      BytesCatalogMeaning version kind target targetKey frame digestProfile records roots stage := by
  constructor
  · intro accepted
    unfold prepareCatalogBytes at accepted
    cases decodedRecords : prepareManyBytes version kind target frame records with
    | none => simp [decodedRecords] at accepted
    | some preparedRecords =>
      cases decodedRoots : prepareManyBytes version kind target frame roots with
      | none => simp [decodedRecords,decodedRoots] at accepted
      | some preparedRoots =>
        simp only [decodedRecords,decodedRoots] at accepted
        split at accepted
        · rename_i checked
          have parts : profileAlignmentCheck digestProfile preparedRecords preparedRoots = true ∧
              CandidateOwnedBindings.catalogCheck (CatalogStage.mk frame digestProfile preparedRecords preparedRoots).catalog kind targetKey = true := by
            simpa only [Bool.and_eq_true] using checked
          cases accepted
          exact ⟨(prepare_many_bytes_exact version kind target frame records preparedRecords).mp decodedRecords,
            (prepare_many_bytes_exact version kind target frame roots preparedRoots).mp decodedRoots,rfl,rfl,
            (profile_alignment_exact digestProfile preparedRecords preparedRoots).mp parts.1,
            (CandidateOwnedBindings.catalog_check_exact _ kind targetKey).mp parts.2⟩
        · simp at accepted
  · intro meaning
    have dr := (prepare_many_bytes_exact version kind target frame records stage.records).mpr meaning.records
    have do' := (prepare_many_bytes_exact version kind target frame roots stage.roots).mpr meaning.roots
    have same : CatalogStage.mk frame digestProfile stage.records stage.roots = stage := by
      cases stage with
      | mk actualFrame actualProfile actualRecords actualRoots =>
        have sameFrame : actualFrame = frame := meaning.frame
        have sameProfile : actualProfile = digestProfile := meaning.profile
        cases sameFrame; cases sameProfile
        rfl
    have checked := (CandidateOwnedBindings.catalog_check_exact stage.catalog kind targetKey).mpr meaning.structural
    have profiles := (profile_alignment_exact digestProfile stage.records stage.roots).mpr meaning.profiles
    simp only [prepareCatalogBytes,dr,do',same,profiles,checked,Bool.and_true,if_true]

-- The public entrypoints fix both schema and relation-target identity selectors.
def prepareResolutionCatalogBytes (frame : Frame) (digestProfile : RevisionRef) (records roots : List Envelope) : Option (CatalogStage CandidateIntentAddressing.Resolution) :=
  prepareCatalogBytes CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind
    CandidateBindingAst.resolution (fun target => target.ref.key) frame digestProfile records roots

def prepareRoleCatalogBytes (frame : Frame) (digestProfile : RevisionRef) (records roots : List Envelope) : Option (CatalogStage CandidateIntentAddressing.Role) :=
  prepareCatalogBytes CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind
    CandidateBindingAst.role (fun target => target.ref.key) frame digestProfile records roots

#print axioms prepare_many_bytes_exact
#print axioms many_bytes_preserves_length
#print axioms many_bytes_output_provenance
#print axioms prepare_bytes_catalog_exact
end RelationalSuccessor.CandidateBindingBytes
