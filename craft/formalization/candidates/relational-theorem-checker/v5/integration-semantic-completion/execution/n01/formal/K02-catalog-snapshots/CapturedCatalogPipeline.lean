import CompleteCatalogAst
set_option autoImplicit false
namespace RelationalSuccessor.CandidateCatalogSnapshots
open CandidateBindingAst (J)
open CandidateBindingCapture (Envelope)
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits)
open CandidateEvidenceResources (NumericLimits)
open CandidatePreflightReuse (CertifiedInput)
open CandidateOriginalBytePipeline (Batch)
open CandidateIntentSourcePipeline (FramedWorld Claim Output)

structure Inputs where
  source : Envelope
  qualifiers : Envelope
  metadata : Envelope
  payload : Envelope
  owned : Envelope
  deriving DecidableEq, Repr
def Inputs.original (inputs : Inputs) : CandidateOriginalBytePipeline.Inputs :=
  ⟨inputs.source, inputs.qualifiers, [inputs.metadata, inputs.payload, inputs.owned]⟩
structure Catalogs (α : Type) where
  metadata : CandidateCapturedMetadata.Context
  payload : CandidateFiniteSourceCatalog.Capture α
  owned : CandidateOwnedIntentQualifiers.Context
  deriving DecidableEq, Repr

def CatalogAstMeaning {α : Type} (body : CandidateBindingAst.Decoder α)
    (metadataAst payloadAst ownedAst : J) (output : Catalogs α) : Prop :=
  SnapshotMeaning "metadata-context" metadata metadataAst output.metadata ∧
    SnapshotMeaning "payload-context" (payload body) payloadAst output.payload ∧
    SnapshotMeaning "owned-qualifier-context" owned ownedAst output.owned
def decodeCatalogs {α : Type} (body : CandidateBindingAst.Decoder α)
    (metadataAst payloadAst ownedAst : J) : Option (Catalogs α) :=
  match (snapshot "metadata-context" metadata).decode metadataAst,
        (snapshot "payload-context" (payload body)).decode payloadAst,
        (snapshot "owned-qualifier-context" owned).decode ownedAst with
  | some m, some p, some o => some ⟨m, p, o⟩
  | _, _, _ => none
theorem decode_catalogs_exact {α : Type} (body : CandidateBindingAst.Decoder α)
    (metadataAst payloadAst ownedAst : J) (output : Catalogs α) :
    decodeCatalogs body metadataAst payloadAst ownedAst = some output ↔
      CatalogAstMeaning body metadataAst payloadAst ownedAst output := by
  constructor
  · intro accepted
    cases m : (snapshot "metadata-context" metadata).decode metadataAst with
    | none => simp only [decodeCatalogs, m] at accepted; contradiction
    | some md =>
      cases p : (snapshot "payload-context" (payload body)).decode payloadAst with
      | none => simp only [decodeCatalogs, m, p] at accepted; contradiction
      | some pd =>
        cases o : (snapshot "owned-qualifier-context" owned).decode ownedAst with
        | none => simp only [decodeCatalogs, m, p, o] at accepted; contradiction
        | some od =>
          simp only [decodeCatalogs, m, p, o, Option.some.injEq] at accepted
          subst output
          exact ⟨(snapshot_exact _ _ _ _).mp m, (snapshot_exact _ _ _ _).mp p, (snapshot_exact _ _ _ _).mp o⟩
  · rintro ⟨m, p, o⟩
    have md := (snapshot_exact _ _ _ _).mpr m
    have pd := (snapshot_exact _ _ _ _).mpr p
    have od := (snapshot_exact _ _ _ _).mpr o
    simp only [decodeCatalogs, md, pd, od]

def CapturedMeaning {α : Type} (body : CandidateBindingAst.Decoder α)
    (inputs : Inputs) (output : Catalogs α) : Prop :=
  ∃ metadataAst payloadAst ownedAst,
    CandidateScalarConversion.ScalarByteDocumentMeaning inputs.metadata.content metadataAst ∧
    CandidateScalarConversion.ScalarByteDocumentMeaning inputs.payload.content payloadAst ∧
    CandidateScalarConversion.ScalarByteDocumentMeaning inputs.owned.content ownedAst ∧
    CatalogAstMeaning body metadataAst payloadAst ownedAst output

theorem batch_shape (profile : Profile) (limits : Limits) (numbers : NumericLimits) (inputs : Inputs)
    (batch : Batch profile limits numbers inputs.original) :
    ∃ s q m p o, batch.val = [s, q, m, p, o] ∧
      s.val.capture = inputs.source ∧ q.val.capture = inputs.qualifiers ∧
      m.val.capture = inputs.metadata ∧ p.val.capture = inputs.payload ∧ o.val.capture = inputs.owned := by
  have same := batch.property.2
  cases a : batch.val with
  | nil => simp [a, Inputs.original, CandidateOriginalBytePipeline.Inputs.captures] at same
  | cons s r1 =>
    cases b : r1 with
    | nil => simp [a, b, Inputs.original, CandidateOriginalBytePipeline.Inputs.captures] at same
    | cons q r2 =>
      cases c : r2 with
      | nil => simp [a, b, c, Inputs.original, CandidateOriginalBytePipeline.Inputs.captures] at same
      | cons m r3 =>
        cases d : r3 with
        | nil => simp [a, b, c, d, Inputs.original, CandidateOriginalBytePipeline.Inputs.captures] at same
        | cons p r4 =>
          cases e : r4 with
          | nil => simp [a, b, c, d, e, Inputs.original, CandidateOriginalBytePipeline.Inputs.captures] at same
          | cons o rest =>
            simp only [a, b, c, d, e, Inputs.original, CandidateOriginalBytePipeline.Inputs.captures,
              List.map_cons, List.cons.injEq] at same
            rcases same with ⟨hs, hq, hm, hp, ho, empty⟩
            have nilRest : rest = [] := List.map_eq_nil_iff.mp empty
            exact ⟨s, q, m, p, o, by rw [nilRest], hs, hq, hm, hp, ho⟩

def decodePrepared {α : Type} {profile : Profile} {limits : Limits} {numbers : NumericLimits}
    {inputs : Inputs} (body : CandidateBindingAst.Decoder α)
    (batch : Batch profile limits numbers inputs.original) : Option (Catalogs α) :=
  match batch.val with
  | [_, _, m, p, o] => decodeCatalogs body m.val.ast p.val.ast o.val.ast
  | _ => none
theorem prepared_catalogs_exact {α : Type} {profile : Profile} {limits : Limits} {numbers : NumericLimits}
    {inputs : Inputs} (body : CandidateBindingAst.Decoder α)
    (batch : Batch profile limits numbers inputs.original) (output : Catalogs α) :
    decodePrepared body batch = some output ↔ CapturedMeaning body inputs output := by
  rcases batch_shape _ _ _ _ batch with ⟨s, q, m, p, o, shape, _, _, hm, hp, ho⟩
  simp only [decodePrepared, shape, decode_catalogs_exact]
  constructor
  · intro meaning
    refine ⟨m.val.ast, p.val.ast, o.val.ast, ?_, ?_, ?_, meaning⟩
    · rw [←hm]; exact m.property.2.2.1
    · rw [←hp]; exact p.property.2.2.1
    · rw [←ho]; exact o.property.2.2.1
  · rintro ⟨ma, pa, oa, pm, pp, po, meaning⟩
    have sm : m.val.ast = ma := CandidateScalarConversion.scalar_byte_meaning_unique inputs.metadata.content _ _
      (by rw [←hm]; exact m.property.2.2.1) pm
    have sp : p.val.ast = pa := CandidateScalarConversion.scalar_byte_meaning_unique inputs.payload.content _ _
      (by rw [←hp]; exact p.property.2.2.1) pp
    have so : o.val.ast = oa := CandidateScalarConversion.scalar_byte_meaning_unique inputs.owned.content _ _
      (by rw [←ho]; exact o.property.2.2.1) po
    rw [sm, sp, so]
    exact meaning

inductive Refusal where
  | input (reason : CandidateOriginalBytePipeline.Refusal)
  | catalog
  | relation
  deriving DecidableEq, Repr
def runPrepared {α : Type} [DecidableEq α] {profile : Profile} {limits : Limits} {numbers : NumericLimits}
    {inputs : Inputs} (body : CandidateBindingAst.Decoder α)
    (batch : Batch profile limits numbers inputs.original) (world : FramedWorld) (claim : Claim) : Except Refusal Output :=
  match decodePrepared body batch with
  | none => .error .catalog
  | some catalogs =>
    match CandidateOriginalBytePipeline.runPrepared catalogs.metadata catalogs.payload catalogs.owned world claim batch with
    | none => .error .relation
    | some output => .ok output

def Meaning {α : Type} (body : CandidateBindingAst.Decoder α) (profile : Profile) (limits : Limits)
    (numbers : NumericLimits) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : Output) : Prop :=
  ∃ catalogs, CapturedMeaning body inputs catalogs ∧
    CandidateOriginalBytePipeline.Meaning profile limits numbers inputs.original catalogs.metadata
      catalogs.payload catalogs.owned world claim output
theorem prepared_relation_exact {α : Type} [DecidableEq α] {profile : Profile} {limits : Limits} {numbers : NumericLimits}
    {inputs : Inputs} (body : CandidateBindingAst.Decoder α)
    (batch : Batch profile limits numbers inputs.original) (world : FramedWorld) (claim : Claim) (output : Output) :
    runPrepared body batch world claim = .ok output ↔ Meaning body profile limits numbers inputs world claim output := by
  constructor
  · intro accepted
    cases decoded : decodePrepared body batch with
    | none => simp only [runPrepared, decoded] at accepted; contradiction
    | some catalogs =>
      simp only [runPrepared, decoded] at accepted
      cases found : CandidateOriginalBytePipeline.runPrepared catalogs.metadata catalogs.payload catalogs.owned world claim batch with
      | none => simp only [found] at accepted; contradiction
      | some actual =>
        simp only [found, Except.ok.injEq] at accepted
        subst actual
        exact ⟨catalogs, (prepared_catalogs_exact _ _ _).mp decoded,
          (CandidateOriginalBytePipeline.prepared_original_meaning _ _ _ _ _ _ _).mp found⟩
  · rintro ⟨catalogs, captured, original⟩
    have decoded := (prepared_catalogs_exact body batch catalogs).mpr captured
    have found := (CandidateOriginalBytePipeline.prepared_original_meaning catalogs.metadata catalogs.payload catalogs.owned world claim batch output).mpr original
    simp only [runPrepared, decoded, found]

def run {α : Type} [DecidableEq α] (body : CandidateBindingAst.Decoder α) (profile : Profile) (limits : Limits)
    (numbers : NumericLimits) (inputs : Inputs) (world : FramedWorld) (claim : Claim) : Except Refusal Output :=
  match CandidateOriginalBytePipeline.checkedBatch profile limits numbers inputs.original with
  | .error reason => .error (.input reason)
  | .ok batch => runPrepared body batch world claim

theorem run_sound {α : Type} [DecidableEq α] (body : CandidateBindingAst.Decoder α) (profile : Profile) (limits : Limits)
    (numbers : NumericLimits) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : Output)
    (accepted : run body profile limits numbers inputs world claim = .ok output) :
    Meaning body profile limits numbers inputs world claim output := by
  cases checked : CandidateOriginalBytePipeline.checkedBatch profile limits numbers inputs.original with
  | error reason => simp only [run, checked] at accepted; contradiction
  | ok batch =>
    have found : runPrepared body batch world claim = .ok output := by simpa only [run, checked] using accepted
    exact (prepared_relation_exact _ _ _ _ _).mp found
theorem run_complete {α : Type} [DecidableEq α] (body : CandidateBindingAst.Decoder α) (profile : Profile) (limits : Limits)
    (numbers : NumericLimits) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : Output)
    (meaning : Meaning body profile limits numbers inputs world claim output) :
    run body profile limits numbers inputs world claim = .ok output := by
  rcases meaning with ⟨catalogs, captured, original⟩
  rcases (CandidateOriginalBytePipeline.prepare_exists_exact _ _ _ _).mpr ⟨original.1, original.2.1⟩ with ⟨captures, accepted⟩
  have erased := CandidateOriginalBytePipeline.checked_batch_exact profile limits numbers inputs.original
  cases checked : CandidateOriginalBytePipeline.checkedBatch profile limits numbers inputs.original with
  | error reason => rw [checked, accepted] at erased; contradiction
  | ok batch =>
    have found := (prepared_relation_exact body batch world claim output).mpr ⟨catalogs, captured, original⟩
    simp only [run, checked, found]
theorem run_exact {α : Type} [DecidableEq α] (body : CandidateBindingAst.Decoder α) (profile : Profile) (limits : Limits)
    (numbers : NumericLimits) (inputs : Inputs) (world : FramedWorld) (claim : Claim) (output : Output) :
    run body profile limits numbers inputs world claim = .ok output ↔
      Meaning body profile limits numbers inputs world claim output :=
  ⟨run_sound _ _ _ _ _ _ _ _, run_complete _ _ _ _ _ _ _ _⟩

#print axioms decode_catalogs_exact
#print axioms batch_shape
#print axioms prepared_catalogs_exact
#print axioms prepared_relation_exact
#print axioms run_sound
#print axioms run_complete
#print axioms run_exact
end RelationalSuccessor.CandidateCatalogSnapshots
