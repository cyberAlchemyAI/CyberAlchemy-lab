import MetadataProjection
import JsonFixture
import CatalogFixtures

set_option autoImplicit false

namespace RelationalSuccessor.CandidateCapturedMetadata.Examples
open RelationalSuccessor
open CandidateCapturedMetadata

abbrev revision := CandidateIntentSource.SourceFixture.revision
abbrev raw := CandidateJsonSource.Examples.sourceRecord
abbrev ast := CandidateJsonSource.Examples.sourceAst
abbrev frame := CandidateFiniteSourceCatalog.Examples.frame
abbrev payloads := CandidateFiniteSourceCatalog.Examples.capture
abbrev payload := CandidateFiniteSourceCatalog.Examples.expectedFixture

def sourceRef : RevisionRef := revision raw.node_id
-- Exact bytes of the original source fixture; all roots/frames/assignments below
-- are synthetic. Carrying real fixture bytes does not authenticate their capture.
def originalBytes : List UInt8 := [123,10,32,32,34,97,117,116,104,111,114,105,116,121,95,101,102,102,101,99,116,34,58,32,34,110,111,110,101,34,44,10,32,32,34,99,104,97,108,108,101,110,103,101,95,114,111,117,116,101,34,58,32,34,114,111,117,116,101,58,97,114,116,105,102,97,99,116,45,116,121,112,101,45,99,104,97,108,108,101,110,103,101,34,44,10,32,32,34,99,108,97,105,109,95,99,101,105,108,105,110,103,34,58,32,34,82,101,97,108,105,115,116,105,99,32,73,110,116,101,110,116,32,82,101,115,111,108,117,116,105,111,110,32,101,120,97,109,112,108,101,32,102,111,114,32,99,97,110,100,105,100,97,116,101,32,114,101,118,105,101,119,32,111,110,108,121,46,34,44,10,32,32,34,101,118,105,100,101,110,99,101,95,114,101,102,115,34,58,32,91,10,32,32,32,32,34,101,118,105,100,101,110,99,101,58,105,110,116,101,110,116,45,114,101,115,111,108,117,116,105,111,110,45,101,120,97,109,112,108,101,34,10,32,32,93,44,10,32,32,34,107,105,110,100,34,58,32,34,105,110,116,101,110,116,45,114,101,115,111,108,117,116,105,111,110,34,44,10,32,32,34,108,105,102,101,99,121,99,108,101,95,115,116,97,116,101,34,58,32,34,99,97,110,100,105,100,97,116,101,34,44,10,32,32,34,110,97,109,101,34,58,32,34,69,120,97,109,112,108,101,32,73,110,116,101,110,116,32,82,101,115,111,108,117,116,105,111,110,34,44,10,32,32,34,110,111,100,101,95,105,100,34,58,32,34,105,110,116,101,110,116,45,114,101,115,111,108,117,116,105,111,110,58,101,120,97,109,112,108,101,45,48,48,49,34,44,10,32,32,34,111,119,110,101,114,95,114,101,102,34,58,32,34,114,111,108,101,58,97,114,116,105,102,97,99,116,45,116,121,112,101,45,111,119,110,101,114,34,44,10,32,32,34,112,97,121,108,111,97,100,34,58,32,123,10,32,32,32,32,34,101,120,99,108,117,100,101,100,95,115,117,98,106,101,99,116,95,114,101,102,115,34,58,32,91,10,32,32,32,32,32,32,34,114,117,110,116,105,109,101,58,117,110,97,112,112,114,111,118,101,100,45,99,117,116,111,118,101,114,34,10,32,32,32,32,93,44,10,32,32,32,32,34,105,110,116,101,110,116,95,114,101,102,34,58,32,34,105,110,116,101,110,116,58,99,111,109,112,108,101,116,101,45,108,97,98,45,109,111,100,101,108,34,44,10,32,32,32,32,34,111,119,110,101,114,95,100,101,99,105,115,105,111,110,95,114,101,102,34,58,32,34,100,101,99,105,115,105,111,110,58,115,101,108,101,99,116,45,108,97,98,45,109,111,100,101,108,45,119,111,114,107,34,44,10,32,32,32,32,34,115,97,116,105,115,102,97,99,116,105,111,110,95,116,101,115,116,95,114,101,102,115,34,58,32,91,10,32,32,32,32,32,32,34,116,101,115,116,58,97,108,108,45,100,101,102,105,110,105,116,105,111,110,115,45,114,101,97,108,105,122,101,100,34,44,10,32,32,32,32,32,32,34,116,101,115,116,58,97,108,108,45,114,101,108,97,116,105,111,110,115,45,99,108,111,115,101,100,34,10,32,32,32,32,93,44,10,32,32,32,32,34,115,101,108,101,99,116,101,100,95,115,117,98,106,101,99,116,95,114,101,102,115,34,58,32,91,10,32,32,32,32,32,32,34,112,114,111,106,101,99,116,58,108,97,98,45,115,101,109,97,110,116,105,99,45,103,111,118,101,114,110,97,110,99,101,34,44,10,32,32,32,32,32,32,34,103,111,97,108,58,99,111,109,112,108,101,116,101,45,105,110,116,101,103,114,97,116,101,100,45,109,111,100,101,108,34,10,32,32,32,32,93,10,32,32,125,44,10,32,32,34,114,101,108,97,116,105,111,110,95,114,101,102,115,34,58,32,91,10,32,32,32,32,123,10,32,32,32,32,32,32,34,99,111,117,110,116,101,114,112,97,114,116,95,107,105,110,100,34,58,32,34,99,104,97,108,108,101,110,103,101,45,101,118,101,110,116,34,44,10,32,32,32,32,32,32,34,99,111,117,110,116,101,114,112,97,114,116,95,114,101,102,34,58,32,34,99,104,97,108,108,101,110,103,101,45,101,118,101,110,116,58,101,120,97,109,112,108,101,45,48,48,49,34,44,10,32,32,32,32,32,32,34,100,105,114,101,99,116,105,111,110,34,58,32,34,116,97,114,103,101,116,34,44,10,32,32,32,32,32,32,34,114,101,108,97,116,105,111,110,95,107,105,110,100,95,114,101,102,34,58,32,34,114,101,108,97,116,105,111,110,46,99,104,97,108,108,101,110,103,101,115,34,10,32,32,32,32,125,10,32,32,93,44,10,32,32,34,115,99,104,101,109,97,95,118,101,114,115,105,111,110,34,58,32,34,99,121,98,101,114,97,108,99,104,101,109,121,45,108,97,98,45,105,110,116,101,110,116,45,114,101,115,111,108,117,116,105,111,110,47,118,49,34,44,10,32,32,34,115,99,111,112,101,95,114,101,102,34,58,32,34,115,99,111,112,101,58,108,97,98,45,105,110,116,101,103,114,97,116,101,100,45,109,111,100,101,108,34,44,10,32,32,34,115,117,99,99,101,115,115,111,114,95,114,101,102,115,34,58,32,91,93,10,125,10]

def artifact : Artifact RawRecord :=
  ⟨sourceRef, raw.kind, raw, originalBytes, revision "review:source-fixture"⟩
def identity : IdentityBinding :=
  ⟨revision "binding:identity", sourceRef, raw.node_id, frame⟩
def owner : OwnerBinding :=
  ⟨revision "binding:owner", sourceRef, raw.owner_ref, revision "principal:fixture-holder", frame.scope, frame⟩
def scope : ScopeBinding :=
  ⟨revision "binding:scope", sourceRef, raw.scope_ref, frame.scope, owner.ref, frame⟩
def receipt : Receipt :=
  ⟨revision "receipt:source-fixture", revision "schema:intent-resolution-v1", artifact, frame, identity, owner, scope⟩
def context : Context :=
  ⟨frame, receipt.schema, [receipt], [receipt], [identity], [owner], [scope]⟩

theorem fixture_receipt_meaning : ReceiptMeaning context receipt := by
  constructor <;> simp [context, receipt, artifact, identity, owner, scope]

theorem fixture_context_meaning : ContextMeaning context := by
  constructor
  · simp [UniqueBy, CandidateFiniteSourceCatalog.UniqueBy, allArtifacts, allReceipts, context]
  · simp [UniqueBy, CandidateFiniteSourceCatalog.UniqueBy, allReceipts, context]
  · simp [UniqueBy, CandidateFiniteSourceCatalog.UniqueBy, context]
  · simp [UniqueBy, CandidateFiniteSourceCatalog.UniqueBy, context]
  · simp [UniqueBy, CandidateFiniteSourceCatalog.UniqueBy, context]
  · intro actual member
    have same : actual = receipt := by simpa [context] using member
    subst actual; exact fixture_receipt_meaning
  · intro actual member
    have same : actual = receipt := by simpa [context] using member
    subst actual; exact fixture_receipt_meaning

theorem fixture_metadata_resolves : resolve context frame sourceRef = some receipt :=
  (resolve_exact context frame sourceRef receipt).mpr
    ⟨fixture_context_meaning, rfl, rfl, by simp [context], fixture_receipt_meaning⟩

theorem fixture_AST_matches : CandidateJsonSource.decodeRecord ast = some raw := by decide

theorem original_bytes_and_AST_bind : decodeSource context frame sourceRef originalBytes ast = some receipt :=
  (decode_source_exact context frame sourceRef originalBytes ast receipt).mpr
    ⟨(resolve_exact context frame sourceRef receipt).mp fixture_metadata_resolves,
      rfl, (CandidateJsonSource.decode_record_exact ast raw).mp fixture_AST_matches⟩

theorem fixture_payload_decodes : CandidateFiniteSourceCatalog.IntentPayload.decode payloads frame raw.payload = some payload := by decide

theorem complete_structural_projection :
    decodeResolution context payloads frame sourceRef originalBytes ast = some ⟨receipt, payload⟩ :=
  (decode_resolution_exact context payloads frame sourceRef originalBytes ast ⟨receipt, payload⟩).mpr
    ⟨(decode_source_exact context frame sourceRef originalBytes ast receipt).mp original_bytes_and_AST_bind,
      (CandidateFiniteSourceCatalog.IntentPayload.guarded_decode_exact payloads frame raw.payload payload).mp fixture_payload_decodes⟩

#print axioms fixture_receipt_meaning
#print axioms fixture_context_meaning
#print axioms fixture_metadata_resolves
#print axioms fixture_AST_matches
#print axioms original_bytes_and_AST_bind
#print axioms fixture_payload_decodes
#print axioms complete_structural_projection
end RelationalSuccessor.CandidateCapturedMetadata.Examples
