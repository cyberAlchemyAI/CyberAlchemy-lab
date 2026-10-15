import CapturePolicies
set_option autoImplicit false
namespace RelationalSuccessor.CandidateBindingCapture
open RelationalSuccessor

structure Input where
  ast : J
  envelope : Envelope

inductive ManyMeaning {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) : List Input → List (Prepared α) → Prop
  | nil : ManyMeaning version kind target frame [] []
  | cons (input : Input) (prepared : Prepared α) (inputs : List Input) (outputs : List (Prepared α))
      (head : PreparedMeaning version kind target frame input.envelope input.ast prepared)
      (tail : ManyMeaning version kind target frame inputs outputs) :
      ManyMeaning version kind target frame (input::inputs) (prepared::outputs)

def prepareMany {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) : List Input → Option (List (Prepared α))
  | [] => some []
  | input::inputs =>
    match prepare version kind target frame input.envelope input.ast with
    | none => none
    | some prepared =>
      match prepareMany version kind target frame inputs with
      | none => none
      | some outputs => some (prepared::outputs)

theorem prepare_many_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (inputs : List Input) (outputs : List (Prepared α)) :
    prepareMany version kind target frame inputs = some outputs ↔
      ManyMeaning version kind target frame inputs outputs := by
  constructor
  · intro accepted
    induction inputs generalizing outputs with
    | nil => simp only [prepareMany,Option.some.injEq] at accepted; subst outputs; exact .nil
    | cons input inputs ih =>
      unfold prepareMany at accepted
      cases head : prepare version kind target frame input.envelope input.ast with
      | none => simp [head] at accepted
      | some prepared =>
        simp only [head] at accepted
        cases tail : prepareMany version kind target frame inputs with
        | none => simp [tail] at accepted
        | some rest =>
          simp only [tail,Option.some.injEq] at accepted
          subst outputs
          exact .cons input prepared inputs rest
            ((prepare_exact version kind target frame input.envelope input.ast prepared).mp head) (ih rest tail)
  · intro meaning
    induction meaning with
    | nil => rfl
    | cons input prepared inputs outputs head tail ih =>
      simp only [prepareMany,(prepare_exact version kind target frame input.envelope input.ast prepared).mpr head,ih]

theorem many_meaning_preserves_length {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (inputs : List Input) (outputs : List (Prepared α))
    (meaning : ManyMeaning version kind target frame inputs outputs) : outputs.length = inputs.length := by
  induction meaning with
  | nil => rfl
  | cons input prepared inputs outputs head tail ih => simp only [List.length_cons,ih]

theorem many_meaning_output_provenance {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (inputs : List Input) (outputs : List (Prepared α))
    (meaning : ManyMeaning version kind target frame inputs outputs) :
    ∀ prepared ∈ outputs, ∃ input ∈ inputs,
      PreparedMeaning version kind target frame input.envelope input.ast prepared := by
  induction meaning with
  | nil => intro prepared member; simp at member
  | cons input prepared inputs outputs head tail ih =>
    intro output member
    simp only [List.mem_cons] at member
    rcases member with same | rest
    · subst output; exact ⟨input,by simp,head⟩
    · rcases ih output rest with ⟨origin,member,meaning⟩
      exact ⟨origin,by simp [member],meaning⟩

def derivedCatalog {α : Type} (frame : Frame) (records roots : List (Prepared α)) : CandidateOwnedBindings.Catalog α :=
  ⟨frame,records.map Prepared.entry,roots.map Prepared.entry⟩

-- Retain envelopes and record versions beside the derived old catalog projection.
structure CatalogStage (α : Type) where
  frame : Frame
  digestProfile : RevisionRef
  records : List (Prepared α)
  roots : List (Prepared α)
  deriving DecidableEq, Repr

def CatalogStage.catalog {α : Type} (stage : CatalogStage α) : CandidateOwnedBindings.Catalog α :=
  derivedCatalog stage.frame stage.records stage.roots

def ProfileAlignmentMeaning {α : Type} (profile : RevisionRef) (records roots : List (Prepared α)) : Prop :=
  ∀ prepared ∈ records ++ roots, prepared.envelope.digestProfile = profile

def profileAlignmentCheck {α : Type} (profile : RevisionRef) (records roots : List (Prepared α)) : Bool :=
  (records ++ roots).all (fun prepared => decide (prepared.envelope.digestProfile = profile))

theorem profile_alignment_exact {α : Type} (profile : RevisionRef) (records roots : List (Prepared α)) :
    profileAlignmentCheck profile records roots = true ↔ ProfileAlignmentMeaning profile records roots := by
  simp only [profileAlignmentCheck,ProfileAlignmentMeaning,List.all_eq_true,decide_eq_true_eq]

structure CatalogMeaning {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (targetKey : α → RevisionKey) (frame : Frame) (digestProfile : RevisionRef) (records roots : List Input)
    (stage : CatalogStage α) : Prop where
  records : ManyMeaning version kind target frame records stage.records
  roots : ManyMeaning version kind target frame roots stage.roots
  frame : stage.frame = frame
  profile : stage.digestProfile = digestProfile
  profiles : ProfileAlignmentMeaning digestProfile stage.records stage.roots
  structural : CandidateOwnedBindings.CatalogMeaning stage.catalog kind targetKey

def prepareCatalog {α : Type} [DecidableEq α] (version kind : String) (target : CandidateBindingAst.Decoder α)
    (targetKey : α → RevisionKey) (frame : Frame) (digestProfile : RevisionRef) (records roots : List Input) : Option (CatalogStage α) :=
  match prepareMany version kind target frame records,prepareMany version kind target frame roots with
  | some preparedRecords,some preparedRoots =>
    let stage : CatalogStage α := ⟨frame,digestProfile,preparedRecords,preparedRoots⟩
    if profileAlignmentCheck digestProfile preparedRecords preparedRoots &&
        CandidateOwnedBindings.catalogCheck stage.catalog kind targetKey then some stage else none
  | _,_ => none

theorem prepare_catalog_exact {α : Type} [DecidableEq α] (version kind : String) (target : CandidateBindingAst.Decoder α)
    (targetKey : α → RevisionKey) (frame : Frame) (digestProfile : RevisionRef) (records roots : List Input)
    (stage : CatalogStage α) :
    prepareCatalog version kind target targetKey frame digestProfile records roots = some stage ↔
      CatalogMeaning version kind target targetKey frame digestProfile records roots stage := by
  constructor
  · intro accepted
    unfold prepareCatalog at accepted
    cases decodedRecords : prepareMany version kind target frame records with
    | none => simp [decodedRecords] at accepted
    | some preparedRecords =>
      cases decodedRoots : prepareMany version kind target frame roots with
      | none => simp [decodedRecords,decodedRoots] at accepted
      | some preparedRoots =>
        simp only [decodedRecords,decodedRoots] at accepted
        split at accepted
        · rename_i checked
          have parts : profileAlignmentCheck digestProfile preparedRecords preparedRoots = true ∧
              CandidateOwnedBindings.catalogCheck (CatalogStage.mk frame digestProfile preparedRecords preparedRoots).catalog kind targetKey = true := by
            simpa only [Bool.and_eq_true] using checked
          cases accepted
          exact ⟨(prepare_many_exact version kind target frame records preparedRecords).mp decodedRecords,
            (prepare_many_exact version kind target frame roots preparedRoots).mp decodedRoots,rfl,rfl,
            (profile_alignment_exact digestProfile preparedRecords preparedRoots).mp parts.1,
            (CandidateOwnedBindings.catalog_check_exact _ kind targetKey).mp parts.2⟩
        · simp at accepted
  · intro meaning
    have dr := (prepare_many_exact version kind target frame records stage.records).mpr meaning.records
    have do' := (prepare_many_exact version kind target frame roots stage.roots).mpr meaning.roots
    have same : CatalogStage.mk frame digestProfile stage.records stage.roots = stage := by
      cases stage with
      | mk actualFrame actualProfile actualRecords actualRoots =>
        have sameFrame : actualFrame = frame := meaning.frame
        have sameProfile : actualProfile = digestProfile := meaning.profile
        cases sameFrame; cases sameProfile
        rfl
    have checked := (CandidateOwnedBindings.catalog_check_exact stage.catalog kind targetKey).mpr meaning.structural
    have profiles := (profile_alignment_exact digestProfile stage.records stage.roots).mpr meaning.profiles
    simp only [prepareCatalog,dr,do',same,profiles,checked,Bool.and_true,if_true]

-- The public entrypoints fix both schema and relation-target identity selectors.
def prepareResolutionCatalog (frame : Frame) (digestProfile : RevisionRef) (records roots : List Input) : Option (CatalogStage CandidateIntentAddressing.Resolution) :=
  prepareCatalog CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind
    CandidateBindingAst.resolution (fun target => target.ref.key) frame digestProfile records roots

def prepareRoleCatalog (frame : Frame) (digestProfile : RevisionRef) (records roots : List Input) : Option (CatalogStage CandidateIntentAddressing.Role) :=
  prepareCatalog CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind
    CandidateBindingAst.role (fun target => target.ref.key) frame digestProfile records roots

#print axioms prepare_many_exact
#print axioms many_meaning_preserves_length
#print axioms many_meaning_output_provenance
#print axioms profile_alignment_exact
#print axioms prepare_catalog_exact
end RelationalSuccessor.CandidateBindingCapture
