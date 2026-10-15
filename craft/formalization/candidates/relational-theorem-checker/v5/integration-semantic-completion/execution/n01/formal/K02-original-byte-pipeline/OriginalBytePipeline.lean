import OriginalSourceBatch
set_option autoImplicit false
namespace RelationalSuccessor.CandidateOriginalBytePipeline
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits)
open CandidateEvidenceResources (NumericLimits)
open CandidatePreflightReuse (CertifiedInput)
open CandidateIntentSourcePipeline (Metadata Bindings FramedWorld Claim Output)

-- The original relation record is passed to the original complete source decoder.
def runPrepared {α : Type} [DecidableEq α] {profile : Profile} {limits : Limits}
    {numbers : NumericLimits} {inputs : Inputs}
    (metadata : Metadata) (payloads : CandidateFiniteSourceCatalog.Capture α)
    (bindings : Bindings) (world : FramedWorld) (claim : Claim)
    (batch : Batch profile limits numbers inputs) : Option Output :=
  match batch.val with
  | source :: qualifiers :: _ =>
    match CandidateIntentSourcePipeline.run metadata payloads bindings world
        source.val.capture.content source.val.ast qualifiers.val.ast claim with
    | none => none
    | some output =>
      if output.resolution.ref.digest = source.val.capture.digest then some output else none
  | _ => none

def PreparedMeaning {α : Type} {profile : Profile} {limits : Limits} {numbers : NumericLimits}
    {inputs : Inputs} (metadata : Metadata) (payloads : CandidateFiniteSourceCatalog.Capture α)
    (bindings : Bindings) (world : FramedWorld) (claim : Claim)
    (batch : Batch profile limits numbers inputs) (output : Output) : Prop :=
  ∃ source qualifiers rest, batch.val = source :: qualifiers :: rest ∧
    CandidateIntentSourcePipeline.Meaning metadata payloads bindings world
      source.val.capture.content source.val.ast qualifiers.val.ast claim output ∧
    output.resolution.ref.digest = source.val.capture.digest

theorem prepared_exact {α : Type} [DecidableEq α] {profile : Profile} {limits : Limits}
    {numbers : NumericLimits} {inputs : Inputs} (metadata : Metadata)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (bindings : Bindings)
    (world : FramedWorld) (claim : Claim) (batch : Batch profile limits numbers inputs) (output : Output) :
    runPrepared metadata payloads bindings world claim batch = some output ↔
      PreparedMeaning metadata payloads bindings world claim batch output := by
  constructor
  · intro accepted
    unfold runPrepared at accepted
    cases first : batch.val with
    | nil => simp only [first] at accepted; contradiction
    | cons source tail =>
      cases second : tail with
      | nil => simp only [first, second] at accepted; contradiction
      | cons qualifiers rest =>
        simp only [first, second] at accepted
        cases found : CandidateIntentSourcePipeline.run metadata payloads bindings world
            source.val.capture.content source.val.ast qualifiers.val.ast claim with
        | none => simp only [found] at accepted; contradiction
        | some actual =>
          simp only [found] at accepted
          split at accepted
          · rename_i digest
            have same := Option.some.inj accepted
            subst actual
            exact ⟨source, qualifiers, rest, by rw [first, second],
              (CandidateIntentSourcePipeline.run_exact _ _ _ _ _ _ _ _ _).mp found, digest⟩
          · contradiction
  · rintro ⟨source, qualifiers, rest, captures, meaning, digest⟩
    have found := (CandidateIntentSourcePipeline.run_exact _ _ _ _ _ _ _ _ _).mpr meaning
    simp only [runPrepared, captures, found, if_pos digest]

-- Meaning is stated on original bytes, independently of the new executable.
def Meaning {α : Type} (profile : Profile) (limits : Limits) (numbers : NumericLimits)
    (inputs : Inputs) (metadata : Metadata) (payloads : CandidateFiniteSourceCatalog.Capture α)
    (bindings : Bindings) (world : FramedWorld) (claim : Claim) (output : Output) : Prop :=
  BudgetMeaning limits inputs ∧
    CandidateEvidenceResources.AllPreflightMeaning profile limits.perCaptureBytes numbers inputs.captures ∧
    ∃ sourceAst qualifierAst,
      CandidateScalarConversion.ScalarByteDocumentMeaning inputs.source.content sourceAst ∧
      CandidateScalarConversion.ScalarByteDocumentMeaning inputs.qualifiers.content qualifierAst ∧
      CandidateIntentSourcePipeline.Meaning metadata payloads bindings world inputs.source.content
        sourceAst qualifierAst claim output ∧ output.resolution.ref.digest = inputs.source.digest

theorem prepared_original_meaning {α : Type} [DecidableEq α] {profile : Profile} {limits : Limits}
    {numbers : NumericLimits} {inputs : Inputs} (metadata : Metadata)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (bindings : Bindings)
    (world : FramedWorld) (claim : Claim) (batch : Batch profile limits numbers inputs) (output : Output) :
    runPrepared metadata payloads bindings world claim batch = some output ↔
      Meaning profile limits numbers inputs metadata payloads bindings world claim output := by
  have shape := batch.property.2
  cases first : batch.val with
  | nil => simp only [first, List.map_nil, Inputs.captures] at shape; contradiction
  | cons source tail =>
    cases second : tail with
    | nil => simp only [first, second, List.map_cons, List.map_nil, Inputs.captures, List.cons.injEq] at shape; simp at shape
    | cons qualifiers rest =>
      simp only [first, second, List.map_cons, Inputs.captures, List.cons.injEq] at shape
      have sourceExact := shape.1
      have qualifierExact := shape.2.1
      rw [prepared_exact]
      constructor
      · rintro ⟨s, q, r, captures, pipeline, digest⟩
        rw [first, second] at captures
        cases List.cons.inj captures |>.1
        cases List.cons.inj (List.cons.inj captures |>.2) |>.1
        refine ⟨batch.property.1, batch_all_preflight _ _ _ _ batch, source.val.ast, qualifiers.val.ast, ?_, ?_, ?_, ?_⟩
        · rw [←sourceExact]; exact source.property.2.2.1
        · rw [←qualifierExact]; exact qualifiers.property.2.2.1
        · rw [←sourceExact]; exact pipeline
        · rw [←sourceExact]; exact digest
      · rintro ⟨_, _, sourceAst, qualifierAst, sourceParsed, qualifierParsed, pipeline, digest⟩
        have sourceSame : source.val.ast = sourceAst :=
          CandidateScalarConversion.scalar_byte_meaning_unique inputs.source.content _ _
            (by rw [←sourceExact]; exact source.property.2.2.1) sourceParsed
        have qualifierSame : qualifiers.val.ast = qualifierAst :=
          CandidateScalarConversion.scalar_byte_meaning_unique inputs.qualifiers.content _ _
            (by rw [←qualifierExact]; exact qualifiers.property.2.2.1) qualifierParsed
        refine ⟨source, qualifiers, rest, by rw [first, second], ?_, ?_⟩
        · rw [sourceExact, sourceSame, qualifierSame]; exact pipeline
        · rw [sourceExact]; exact digest

def run {α : Type} [DecidableEq α] (profile : Profile) (limits : Limits) (numbers : NumericLimits)
    (inputs : Inputs) (metadata : Metadata) (payloads : CandidateFiniteSourceCatalog.Capture α)
    (bindings : Bindings) (world : FramedWorld) (claim : Claim) : Except Refusal Output :=
  match checkedBatch profile limits numbers inputs with
  | .error reason => .error reason
  | .ok batch => match runPrepared metadata payloads bindings world claim batch with
    | none => .error .relation
    | some output => .ok output

theorem run_sound {α : Type} [DecidableEq α] (profile : Profile) (limits : Limits) (numbers : NumericLimits)
    (inputs : Inputs) (metadata : Metadata) (payloads : CandidateFiniteSourceCatalog.Capture α)
    (bindings : Bindings) (world : FramedWorld) (claim : Claim) (output : Output)
    (accepted : run profile limits numbers inputs metadata payloads bindings world claim = .ok output) :
    Meaning profile limits numbers inputs metadata payloads bindings world claim output := by
  unfold run at accepted
  cases checked : checkedBatch profile limits numbers inputs with
  | error reason => simp only [checked] at accepted; contradiction
  | ok batch =>
    simp only [checked] at accepted
    cases found : runPrepared metadata payloads bindings world claim batch with
    | none => simp only [found] at accepted; contradiction
    | some actual =>
      simp only [found, Except.ok.injEq] at accepted
      subst actual
      exact (prepared_original_meaning _ _ _ _ _ _ _).mp found

theorem run_complete {α : Type} [DecidableEq α] (profile : Profile) (limits : Limits) (numbers : NumericLimits)
    (inputs : Inputs) (metadata : Metadata) (payloads : CandidateFiniteSourceCatalog.Capture α)
    (bindings : Bindings) (world : FramedWorld) (claim : Claim) (output : Output)
    (meaning : Meaning profile limits numbers inputs metadata payloads bindings world claim output) :
    run profile limits numbers inputs metadata payloads bindings world claim = .ok output := by
  have prepared := (prepare_exists_exact profile limits numbers inputs).mpr ⟨meaning.1, meaning.2.1⟩
  rcases prepared with ⟨captures, accepted⟩
  have erased := checked_batch_exact profile limits numbers inputs
  cases checked : checkedBatch profile limits numbers inputs with
  | error reason => rw [checked, accepted] at erased; contradiction
  | ok batch =>
    have found := (prepared_original_meaning metadata payloads bindings world claim batch output).mpr meaning
    simp only [run, checked, found]

theorem run_exact {α : Type} [DecidableEq α] (profile : Profile) (limits : Limits) (numbers : NumericLimits)
    (inputs : Inputs) (metadata : Metadata) (payloads : CandidateFiniteSourceCatalog.Capture α)
    (bindings : Bindings) (world : FramedWorld) (claim : Claim) (output : Output) :
    run profile limits numbers inputs metadata payloads bindings world claim = .ok output ↔
      Meaning profile limits numbers inputs metadata payloads bindings world claim output :=
  ⟨run_sound _ _ _ _ _ _ _ _ _ _, run_complete _ _ _ _ _ _ _ _ _ _⟩

#print axioms prepared_exact
#print axioms prepared_original_meaning
#print axioms run_sound
#print axioms run_complete
#print axioms run_exact
end RelationalSuccessor.CandidateOriginalBytePipeline
