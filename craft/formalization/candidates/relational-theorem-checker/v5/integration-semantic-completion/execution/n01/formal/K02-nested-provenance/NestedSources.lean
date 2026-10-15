import SelectedRelationPipeline
import TypedReuse
set_option autoImplicit false
namespace RelationalSuccessor.CandidateNestedProvenance
open CandidateBindingAst (J Decoder)
open CandidateBindingCapture (Envelope)
open CandidateDigest (Profile)
open CandidateEvidenceResources (NumericLimits)
abbrev Artifact (α : Type) := CandidateFiniteSourceCatalog.Artifact α
inductive Expected (α : Type) where
  | metadata (value : Artifact CandidateIntentRecordShape.RawRecord)
  | payload (value : Artifact α)
  | resolution (value : CandidateOwnedBindings.Entry CandidateIntentAddressing.Resolution)
  | role (value : CandidateOwnedBindings.Entry CandidateIntentAddressing.Role)
  deriving DecidableEq, Repr

def Expected.content {α : Type} : Expected α → List UInt8
  | .metadata a => a.content
  | .payload a => a.content
  | .resolution a => a.content
  | .role a => a.content
def Expected.ref {α : Type} : Expected α → RevisionRef
  | .metadata a => a.ref
  | .payload a => a.ref
  | .resolution a => a.ref
  | .role a => a.ref
def envelope {α : Type} (profile : Profile) (value : Expected α) : Envelope :=
  ⟨value.content, value.content.length, profile.ref, value.ref.digest⟩
def required {α : Type} (catalogs : CandidateCatalogSnapshots.Catalogs α) : List (Expected α) :=
  (CandidateCapturedMetadata.allArtifacts catalogs.metadata).map Expected.metadata ++
    (CandidateFiniteSourceCatalog.allArtifacts catalogs.payload).map Expected.payload ++
    (CandidateOwnedBindings.allEntries catalogs.owned.resolutions).map Expected.resolution ++
    (CandidateOwnedBindings.allEntries catalogs.owned.roles).map Expected.role

def ownedRecord {α : Type} (version : String) (value : CandidateOwnedBindings.Entry α) : CandidateBindingRecords.Record α :=
  ⟨version,value.ref.key,value.sourceKind,value.body,value.ownerReview⟩
def DocumentMeaning {α : Type} (body : Decoder α) (frame : Frame) (expected : Expected α) (ast : J) : Prop :=
  match expected with
  | .metadata a => CandidateJsonSource.SchemaAstMeaning ast a.body ∧ a.sourceKind = a.body.kind
  | .payload a => body.Meaning ast a.body
  | .resolution a =>
    CandidateBindingRecords.RecordMeaning CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind
      CandidateBindingAst.resolution ast (ownedRecord CandidateBindingRecords.resolutionVersion a) ∧
      a.body.frame = frame ∧ a.sourceKind = CandidateBindingRecords.resolutionKind
  | .role a =>
    CandidateBindingRecords.RecordMeaning CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind
      CandidateBindingAst.role ast (ownedRecord CandidateBindingRecords.roleVersion a) ∧
      a.body.frame = frame ∧ a.sourceKind = CandidateBindingRecords.roleKind

def documentCheck {α : Type} [DecidableEq α] (body : Decoder α) (frame : Frame) (expected : Expected α) (ast : J) : Bool :=
  match expected with
  | .metadata a => decide (CandidateJsonSource.decodeRecord ast = some a.body) && decide (a.sourceKind = a.body.kind)
  | .payload a => decide (body.decode ast = some a.body)
  | .resolution a =>
    decide (CandidateBindingRecords.resolutionRecord.decode ast = some (ownedRecord CandidateBindingRecords.resolutionVersion a)) &&
      decide (a.body.frame = frame) && decide (a.sourceKind = CandidateBindingRecords.resolutionKind)
  | .role a =>
    decide (CandidateBindingRecords.roleRecord.decode ast = some (ownedRecord CandidateBindingRecords.roleVersion a)) &&
      decide (a.body.frame = frame) && decide (a.sourceKind = CandidateBindingRecords.roleKind)

theorem document_check_exact {α : Type} [DecidableEq α] (body : Decoder α) (frame : Frame) (expected : Expected α) (ast : J) :
    documentCheck body frame expected ast = true ↔ DocumentMeaning body frame expected ast := by
  cases expected <;> simp only [documentCheck, DocumentMeaning, Bool.and_eq_true, decide_eq_true_eq,
    CandidateJsonSource.decode_record_exact, body.exact, CandidateBindingRecords.resolution_record_exact,
    CandidateBindingRecords.role_record_exact, and_assoc]

def ItemMeaning {α : Type} (body : Decoder α) (profile : Profile) (budget : Nat) (numbers : NumericLimits)
    (frame : Frame) (expected : Expected α) (capture : Envelope) : Prop :=
  capture = envelope profile expected ∧
    CandidateEvidenceResources.PreflightMeaning profile budget numbers capture ∧
    ∃ ast, CandidateScalarConversion.ScalarByteDocumentMeaning capture.content ast ∧
      DocumentMeaning body frame expected ast

def cachedItemCheck {α : Type} [DecidableEq α] {profile : Profile} {budget : Nat} {numbers : NumericLimits}
    (body : Decoder α) (frame : Frame) (expected : Expected α)
    (input : CandidatePreflightReuse.CertifiedInput profile budget numbers) : Bool :=
  decide (input.val.capture = envelope profile expected) && documentCheck body frame expected input.val.ast

theorem certified_item_exact {α : Type} [DecidableEq α] {profile : Profile} {budget : Nat} {numbers : NumericLimits}
    (body : Decoder α) (frame : Frame) (expected : Expected α)
    (input : CandidatePreflightReuse.CertifiedInput profile budget numbers) :
    cachedItemCheck body frame expected input = true ↔
      ItemMeaning body profile budget numbers frame expected input.val.capture := by
  simp only [cachedItemCheck, Bool.and_eq_true, decide_eq_true_eq, document_check_exact]
  constructor
  · rintro ⟨same,document⟩
    exact ⟨same,⟨input.property.1,input.property.2.1,input.val.ast,input.property.2.2.1,input.property.2.2.2⟩, input.val.ast,input.property.2.2.1,document⟩
  · rintro ⟨same,_,ast,parsed,document⟩
    have unique := CandidateScalarConversion.scalar_byte_meaning_unique input.val.capture.content
      input.val.ast ast input.property.2.2.1 parsed
    exact ⟨same,by rw [unique]; exact document⟩

theorem item_full_bytes_and_digest {α : Type} (body : Decoder α) (profile : Profile) (budget : Nat) (numbers : NumericLimits)
    (frame : Frame) (expected : Expected α) (capture : Envelope)
    (meaning : ItemMeaning body profile budget numbers frame expected capture) :
    capture.content = expected.content ∧ capture.byteLength = expected.content.length ∧
      capture.digestProfile = profile.ref ∧ capture.digest = expected.ref.digest := by
  rw [meaning.1]
  exact ⟨rfl,rfl,rfl,rfl⟩

theorem complete_ordered_occurrence_count {α : Type} (catalogs : CandidateCatalogSnapshots.Catalogs α) :
    (required catalogs).length =
      catalogs.metadata.records.length + catalogs.metadata.roots.length +
      catalogs.payload.records.length + catalogs.payload.roots.length +
      catalogs.owned.resolutions.records.length + catalogs.owned.resolutions.roots.length +
      catalogs.owned.roles.records.length + catalogs.owned.roles.roots.length := by
  simp only [required, CandidateCapturedMetadata.allArtifacts, CandidateCapturedMetadata.allReceipts,
    CandidateFiniteSourceCatalog.allArtifacts, CandidateOwnedBindings.allEntries,
    List.length_append, List.length_map]
  omega

#print axioms document_check_exact
#print axioms certified_item_exact
#print axioms item_full_bytes_and_digest
#print axioms complete_ordered_occurrence_count
end RelationalSuccessor.CandidateNestedProvenance
