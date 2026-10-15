import DigestCaptureOutcomes
set_option autoImplicit false
namespace RelationalSuccessor.CandidateDigestCapture
open CandidateBindingCapture (Envelope Prepared CatalogStage)
open CandidateDigest (Profile)

structure Limits where
  perCaptureBytes : Nat
  totalBytes : Nat
  maxCaptures : Nat
  deriving DecidableEq, Repr

def originalByteCount (inputs : List Envelope) : Nat := (inputs.map fun e => e.content.length).sum

def CatalogBudgetMeaning (limits : Limits) (records roots : List Envelope) : Prop :=
  records.length+roots.length≤limits.maxCaptures ∧ originalByteCount (records++roots)≤limits.totalBytes
instance (limits : Limits) (records roots : List Envelope) : Decidable (CatalogBudgetMeaning limits records roots) := by
  unfold CatalogBudgetMeaning;infer_instance

def catalogBudgetCheck (limits : Limits) (records roots : List Envelope) : Bool := decide (CatalogBudgetMeaning limits records roots)
theorem catalog_budget_exact (limits : Limits) (records roots : List Envelope) :
    catalogBudgetCheck limits records roots=true ↔ CatalogBudgetMeaning limits records roots := by
  simp only [catalogBudgetCheck,decide_eq_true_eq]

inductive DigestManyMeaning {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) :
    List Envelope → List (Prepared α) → Prop
  | nil : DigestManyMeaning profile budget version kind target frame [] []
  | cons {input : Envelope} {prepared : Prepared α} {inputs : List Envelope} {outputs : List (Prepared α)}
      (head : DigestPreparedMeaning profile budget version kind target frame input prepared)
      (tail : DigestManyMeaning profile budget version kind target frame inputs outputs) :
      DigestManyMeaning profile budget version kind target frame (input::inputs) (prepared::outputs)

def prepareManyDigest {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame) :
    List Envelope → Option (List (Prepared α))
  | [] => some []
  | input::inputs => (prepareDigestBytes profile budget version kind target frame input).bind fun prepared =>
    (prepareManyDigest profile budget version kind target frame inputs).map fun outputs => prepared::outputs

theorem digest_many_exact {α : Type} (profile : Profile) (budget : Nat)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (frame : Frame)
    (inputs : List Envelope) (outputs : List (Prepared α)) :
    prepareManyDigest profile budget version kind target frame inputs=some outputs ↔
      DigestManyMeaning profile budget version kind target frame inputs outputs := by
  constructor
  · intro accepted
    induction inputs generalizing outputs with
    | nil => simp only [prepareManyDigest,Option.some.injEq] at accepted;subst outputs;exact .nil
    | cons input inputs ih =>
      unfold prepareManyDigest at accepted
      cases head : prepareDigestBytes profile budget version kind target frame input with
      | none => simp only [head,Option.bind_none] at accepted;contradiction
      | some prepared =>
        simp only [head,Option.bind_some] at accepted
        cases tail : prepareManyDigest profile budget version kind target frame inputs with
        | none => simp only [tail,Option.map_none] at accepted;contradiction
        | some rest =>
          simp only [tail,Option.map_some,Option.some.injEq] at accepted;subst outputs
          exact .cons ((digest_capture_exact profile budget version kind target frame input prepared).mp head) (ih rest tail)
  · intro meaning
    induction meaning with
    | nil => rfl
    | cons head tail ih =>
      simp only [prepareManyDigest,(digest_capture_exact profile budget version kind target frame _ _).mpr head,Option.bind_some,ih,Option.map_some]

theorem digest_many_length {α : Type} {profile : Profile} {budget : Nat}
    {version kind : String} {target : CandidateBindingAst.Decoder α} {frame : Frame}
    {inputs : List Envelope} {outputs : List (Prepared α)}
    (meaning : DigestManyMeaning profile budget version kind target frame inputs outputs) : outputs.length=inputs.length := by
  induction meaning with
  | nil => rfl
  | cons head tail ih => simp only [List.length_cons,ih]

theorem digest_many_forgets_to_bytes {α : Type} {profile : Profile} {budget : Nat}
    {version kind : String} {target : CandidateBindingAst.Decoder α} {frame : Frame}
    {inputs : List Envelope} {outputs : List (Prepared α)}
    (meaning : DigestManyMeaning profile budget version kind target frame inputs outputs) :
    CandidateBindingBytes.BytesManyMeaning version kind target frame inputs outputs := by
  induction meaning with
  | nil => exact .nil
  | cons head tail ih => exact .cons _ _ _ _ head.1 ih

theorem digest_many_retains_envelopes {α : Type} {profile : Profile} {budget : Nat}
    {version kind : String} {target : CandidateBindingAst.Decoder α} {frame : Frame}
    {inputs : List Envelope} {outputs : List (Prepared α)}
    (meaning : DigestManyMeaning profile budget version kind target frame inputs outputs) :
    outputs.map Prepared.envelope=inputs := by
  induction meaning with
  | nil => rfl
  | cons head tail ih =>
    simp only [List.map_cons,(digest_capture_retains_envelope _ _ _ _ _ _ _ _ head).1,ih]

theorem digest_many_provenance {α : Type} {profile : Profile} {budget : Nat}
    {version kind : String} {target : CandidateBindingAst.Decoder α} {frame : Frame}
    {inputs : List Envelope} {outputs : List (Prepared α)}
    (meaning : DigestManyMeaning profile budget version kind target frame inputs outputs) :
    ∀ output ∈ outputs, ∃ input ∈ inputs, DigestPreparedMeaning profile budget version kind target frame input output := by
  induction meaning with
  | nil => intro output member;simp at member
  | @cons input prepared inputs outputs head tail ih =>
    intro output member
    simp only [List.mem_cons] at member
    rcases member with eq | rest
    · subst output;exact ⟨input,by simp,head⟩
    · rcases ih output rest with ⟨origin,mem,source⟩;exact ⟨origin,by simp [mem],source⟩

theorem digest_many_profiles {α : Type} {profile : Profile} {budget : Nat}
    {version kind : String} {target : CandidateBindingAst.Decoder α} {frame : Frame}
    {inputs : List Envelope} {outputs : List (Prepared α)}
    (meaning : DigestManyMeaning profile budget version kind target frame inputs outputs) :
    ∀ output ∈ outputs, output.envelope.digestProfile=profile.ref := by
  intro output member
  rcases digest_many_provenance meaning output member with ⟨input,_,checked⟩
  have eq := (digest_capture_retains_envelope _ _ _ _ _ _ _ _ checked).1
  exact eq ▸ checked.2.1.1.symm

structure DigestCatalogMeaning {α : Type} (profile : Profile) (limits : Limits)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (targetKey : α → RevisionKey)
    (frame : Frame) (records roots : List Envelope) (stage : CatalogStage α) : Prop where
  supportedProfile : CandidateDigest.ProfileMeaning profile profile.ref
  budget : CatalogBudgetMeaning limits records roots
  records : DigestManyMeaning profile limits.perCaptureBytes version kind target frame records stage.records
  roots : DigestManyMeaning profile limits.perCaptureBytes version kind target frame roots stage.roots
  frame : stage.frame=frame
  profile : stage.digestProfile=profile.ref
  structural : CandidateOwnedBindings.CatalogMeaning stage.catalog kind targetKey

def prepareCatalogDigest {α : Type} [DecidableEq α] (profile : Profile) (limits : Limits)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (targetKey : α → RevisionKey)
    (frame : Frame) (records roots : List Envelope) : Option (CatalogStage α) :=
  if decide (CandidateDigest.ProfileMeaning profile profile.ref) then
   if catalogBudgetCheck limits records roots then
    match prepareManyDigest profile limits.perCaptureBytes version kind target frame records,
        prepareManyDigest profile limits.perCaptureBytes version kind target frame roots with
    | some checkedRecords,some checkedRoots =>
      let stage : CatalogStage α := ⟨frame,profile.ref,checkedRecords,checkedRoots⟩
      if CandidateOwnedBindings.catalogCheck stage.catalog kind targetKey then some stage else none
    | _,_ => none
   else none
  else none

theorem digest_catalog_exact {α : Type} [DecidableEq α] (profile : Profile) (limits : Limits)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (targetKey : α → RevisionKey)
    (frame : Frame) (records roots : List Envelope) (stage : CatalogStage α) :
    prepareCatalogDigest profile limits version kind target targetKey frame records roots=some stage ↔
      DigestCatalogMeaning profile limits version kind target targetKey frame records roots stage := by
  constructor
  · intro accepted
    unfold prepareCatalogDigest at accepted
    split at accepted
    · rename_i supported
      split at accepted
      · rename_i bounded
        cases dr : prepareManyDigest profile limits.perCaptureBytes version kind target frame records with
        | none => simp only [dr] at accepted;contradiction
        | some preparedRecords =>
          cases dt : prepareManyDigest profile limits.perCaptureBytes version kind target frame roots with
          | none => simp only [dr,dt] at accepted;contradiction
          | some preparedRoots =>
            simp only [dr,dt] at accepted
            split at accepted
            · rename_i checked
              cases accepted
              exact ⟨(of_decide_eq_true supported),(catalog_budget_exact limits records roots).mp bounded,
                (digest_many_exact profile _ version kind target frame records preparedRecords).mp dr,
                (digest_many_exact profile _ version kind target frame roots preparedRoots).mp dt,rfl,rfl,
                (CandidateOwnedBindings.catalog_check_exact _ kind targetKey).mp checked⟩
            · contradiction
      · contradiction
    · contradiction
  · intro meaning
    have dr := (digest_many_exact profile _ version kind target frame records stage.records).mpr meaning.records
    have dt := (digest_many_exact profile _ version kind target frame roots stage.roots).mpr meaning.roots
    have same : CatalogStage.mk frame profile.ref stage.records stage.roots=stage := by
      cases stage with
      | mk actualFrame actualProfile actualRecords actualRoots =>
        have f : actualFrame=frame := meaning.frame
        have p : actualProfile=profile.ref := meaning.profile
        cases f;cases p;rfl
    simp only [prepareCatalogDigest,decide_eq_true meaning.supportedProfile,if_true,(catalog_budget_exact limits records roots).mpr meaning.budget,if_true,dr,dt,same,
      (CandidateOwnedBindings.catalog_check_exact stage.catalog kind targetKey).mpr meaning.structural,if_true]

def prepareResolutionCatalogDigest (profile : Profile) (limits : Limits) (frame : Frame) (records roots : List Envelope) :
    Option (CatalogStage CandidateIntentAddressing.Resolution) :=
  prepareCatalogDigest profile limits CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind
    CandidateBindingAst.resolution (fun v=>v.ref.key) frame records roots
def prepareRoleCatalogDigest (profile : Profile) (limits : Limits) (frame : Frame) (records roots : List Envelope) :
    Option (CatalogStage CandidateIntentAddressing.Role) :=
  prepareCatalogDigest profile limits CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind
    CandidateBindingAst.role (fun v=>v.ref.key) frame records roots

theorem digest_catalog_forgets_to_bytes {α : Type} (profile : Profile) (limits : Limits)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (targetKey : α → RevisionKey)
    (frame : Frame) (records roots : List Envelope) (stage : CatalogStage α)
    (meaning : DigestCatalogMeaning profile limits version kind target targetKey frame records roots stage) :
    CandidateBindingBytes.BytesCatalogMeaning version kind target targetKey frame profile.ref records roots stage := by
  refine ⟨digest_many_forgets_to_bytes meaning.records,digest_many_forgets_to_bytes meaning.roots,
    meaning.frame,meaning.profile,?_,meaning.structural⟩
  intro output member
  rcases List.mem_append.mp member with record | root
  · exact digest_many_profiles meaning.records output record
  · exact digest_many_profiles meaning.roots output root

theorem digest_catalog_retains_ordered_inputs {α : Type} (profile : Profile) (limits : Limits)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (targetKey : α → RevisionKey)
    (frame : Frame) (records roots : List Envelope) (stage : CatalogStage α)
    (meaning : DigestCatalogMeaning profile limits version kind target targetKey frame records roots stage) :
    stage.records.map Prepared.envelope=records ∧ stage.roots.map Prepared.envelope=roots :=
  ⟨digest_many_retains_envelopes meaning.records,digest_many_retains_envelopes meaning.roots⟩

theorem digest_catalog_output_limits {α : Type} (profile : Profile) (limits : Limits)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (targetKey : α → RevisionKey)
    (frame : Frame) (records roots : List Envelope) (stage : CatalogStage α)
    (meaning : DigestCatalogMeaning profile limits version kind target targetKey frame records roots stage) :
    stage.records.length+stage.roots.length≤limits.maxCaptures ∧
      originalByteCount (stage.records.map Prepared.envelope++stage.roots.map Prepared.envelope)≤limits.totalBytes := by
  refine ⟨?_,?_⟩
  · simpa only [digest_many_length meaning.records,digest_many_length meaning.roots] using meaning.budget.1
  · simpa only [digest_many_retains_envelopes meaning.records,digest_many_retains_envelopes meaning.roots] using meaning.budget.2

theorem digest_catalog_none_exact {α : Type} [DecidableEq α] (profile : Profile) (limits : Limits)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (targetKey : α → RevisionKey)
    (frame : Frame) (records roots : List Envelope) :
    prepareCatalogDigest profile limits version kind target targetKey frame records roots=none ↔
      ¬∃stage,DigestCatalogMeaning profile limits version kind target targetKey frame records roots stage := by
  constructor
  · intro refused;rintro ⟨stage,meaning⟩
    have accepted := (digest_catalog_exact profile limits version kind target targetKey frame records roots stage).mpr meaning
    rw [refused] at accepted;contradiction
  · intro absent
    cases eq : prepareCatalogDigest profile limits version kind target targetKey frame records roots with
    | none => rfl
    | some stage => exact False.elim (absent ⟨stage,(digest_catalog_exact profile limits version kind target targetKey frame records roots stage).mp eq⟩)

theorem catalog_budget_refuses {α : Type} [DecidableEq α] (profile : Profile) (limits : Limits)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (targetKey : α → RevisionKey)
    (frame : Frame) (records roots : List Envelope) (bad : ¬CatalogBudgetMeaning limits records roots) :
    prepareCatalogDigest profile limits version kind target targetKey frame records roots=none := by
  apply (digest_catalog_none_exact profile limits version kind target targetKey frame records roots).mpr
  rintro ⟨stage,meaning⟩;exact bad meaning.budget

theorem catalog_bad_profile_refuses {α : Type} [DecidableEq α] (profile : Profile) (limits : Limits)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (targetKey : α → RevisionKey)
    (frame : Frame) (records roots : List Envelope) (bad : ¬CandidateDigest.ProfileMeaning profile profile.ref) :
    prepareCatalogDigest profile limits version kind target targetKey frame records roots=none := by
  apply (digest_catalog_none_exact profile limits version kind target targetKey frame records roots).mpr
  rintro ⟨stage,meaning⟩;exact bad meaning.supportedProfile

theorem catalog_each_input_digest {α : Type} (profile : Profile) (limits : Limits)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (targetKey : α → RevisionKey)
    (frame : Frame) (records roots : List Envelope) (stage : CatalogStage α)
    (meaning : DigestCatalogMeaning profile limits version kind target targetKey frame records roots stage) :
    ∀ input ∈ records++roots,
      CandidateDigest.VerifiedDigestMeaning profile input.digestProfile input.content input.digest limits.perCaptureBytes := by
  have every {inputs : List Envelope} {outputs : List (Prepared α)}
      (m : DigestManyMeaning profile limits.perCaptureBytes version kind target frame inputs outputs) :
      ∀ input ∈ inputs,CandidateDigest.VerifiedDigestMeaning profile input.digestProfile input.content input.digest limits.perCaptureBytes := by
    induction m with
    | nil => intro input member;simp at member
    | @cons input prepared inputs outputs head tail ih =>
      intro item member
      rcases List.mem_cons.mp member with eq | rest
      · subst item;exact head.2
      · exact ih item rest
  intro input member
  rcases List.mem_append.mp member with record | root
  · exact every meaning.records input record
  · exact every meaning.roots input root

theorem catalog_bad_input_refuses {α : Type} [DecidableEq α] (profile : Profile) (limits : Limits)
    (version kind : String) (target : CandidateBindingAst.Decoder α) (targetKey : α → RevisionKey)
    (frame : Frame) (records roots : List Envelope) (input : Envelope) (member : input ∈ records++roots)
    (bad : ¬CandidateDigest.VerifiedDigestMeaning profile input.digestProfile input.content input.digest limits.perCaptureBytes) :
    prepareCatalogDigest profile limits version kind target targetKey frame records roots=none := by
  apply (digest_catalog_none_exact profile limits version kind target targetKey frame records roots).mpr
  rintro ⟨stage,meaning⟩
  exact bad (catalog_each_input_digest profile limits version kind target targetKey frame records roots stage meaning input member)
#print axioms catalog_budget_exact
#print axioms digest_many_exact
#print axioms digest_many_length
#print axioms digest_many_forgets_to_bytes
#print axioms digest_many_retains_envelopes
#print axioms digest_many_provenance
#print axioms digest_many_profiles
#print axioms digest_catalog_exact
#print axioms digest_catalog_forgets_to_bytes
#print axioms digest_catalog_retains_ordered_inputs
#print axioms digest_catalog_output_limits
#print axioms digest_catalog_none_exact
#print axioms catalog_budget_refuses
#print axioms catalog_bad_profile_refuses
#print axioms catalog_each_input_digest
#print axioms catalog_bad_input_refuses
end RelationalSuccessor.CandidateDigestCapture
