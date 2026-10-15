import CapturedCatalogPipeline
import OriginalByteRuntimeControls
import Lean
set_option autoImplicit false
namespace RelationalSuccessor.CandidateCatalogSnapshots.RuntimeEncoding
open CandidateBindingAst (J)
-- Fixture encoders only. Their translation is not a general proved serializer.
-- The checked byte parser and exact context decoders validate their actual output.
def encodeString (s : String) : J := .string s
def encodeBytes (bytes : List UInt8) : J := .array (bytes.map fun b => .number (toString b.toNat))
def encodeList {α : Type} (encode : α → J) (values : List α) : J := .array (values.map encode)
def encodeKey (key : RevisionKey) : J := .object [("owner",.string key.owner),("artifact",.string key.artifact),("revision",.string key.revision)]
def encodeRef (ref : RevisionRef) : J := .object [("key",encodeKey ref.key),("digest",.string ref.digest)]

def encodeFrame  (value : Frame) : J :=
  .object [("profile", (encodeRef) value.profile), ("subject", (encodeRef) value.subject), ("target", (encodeRef) value.target), ("context", (encodeRef) value.context), ("scope", (encodeRef) value.scope), ("snapshot", (encodeRef) value.snapshot), ("epoch", (fun n => .number (toString n)) value.epoch), ("timeDomain", (encodeString) value.timeDomain)]

def encodeRawPayload  (value : CandidateIntentSource.RawPayload) : J :=
  .object [("intent_ref", (encodeString) value.intent_ref), ("owner_decision_ref", (encodeString) value.owner_decision_ref), ("selected_subject_refs", (encodeList encodeString) value.selected_subject_refs), ("satisfaction_test_refs", (encodeList encodeString) value.satisfaction_test_refs), ("excluded_subject_refs", (encodeList encodeString) value.excluded_subject_refs)]

def encodeRawRelation  (value : CandidateIntentRecordShape.RawRelationRef) : J :=
  .object [("relation_kind_ref", (encodeString) value.relation_kind_ref), ("direction", (encodeString) value.direction), ("counterpart_kind", (encodeString) value.counterpart_kind), ("counterpart_ref", (encodeString) value.counterpart_ref)]

def encodeRawRecord  (value : RawRecord) : J :=
  .object [("schema_version", (encodeString) value.schema_version), ("node_id", (encodeString) value.node_id), ("kind", (encodeString) value.kind), ("name", (encodeString) value.name), ("lifecycle_state", (encodeString) value.lifecycle_state), ("authority_effect", (encodeString) value.authority_effect), ("owner_ref", (encodeString) value.owner_ref), ("scope_ref", (encodeString) value.scope_ref), ("evidence_refs", (encodeList encodeString) value.evidence_refs), ("challenge_route", (encodeString) value.challenge_route), ("successor_refs", (encodeList encodeString) value.successor_refs), ("relation_refs", (encodeList encodeRawRelation) value.relation_refs), ("payload", (encodeRawPayload) value.payload), ("claim_ceiling", (encodeString) value.claim_ceiling)]

def encodeResolution  (value : CandidateIntentAddressing.Resolution) : J :=
  .object [("ref", (encodeRef) value.ref), ("scope", (encodeRef) value.scope), ("intent", (encodeRef) value.intent), ("ownerDecision", (encodeRef) value.ownerDecision), ("selectedSubjects", (encodeList encodeRef) value.selectedSubjects), ("excludedSubjects", (encodeList encodeRef) value.excludedSubjects), ("satisfactionTests", (encodeList encodeRef) value.satisfactionTests)]

def encodeRole  (value : CandidateIntentAddressing.Role) : J :=
  .object [("ref", (encodeRef) value.ref), ("code", (encodeString) value.code), ("subjectKind", (fun k => .string (CandidateBindingAst.subjectName k)) value.subjectKind)]

def encodeBody {α : Type} (encode : α → J) (value : CandidateOwnedBindings.Body α) : J :=
  .object [("token", (encodeString) value.token), ("target", (encode) value.target), ("frame", (encodeFrame) value.frame)]

def encodeArtifact {α : Type} (encode : α → J) (value : CandidateFiniteSourceCatalog.Artifact α) : J :=
  .object [("ref", (encodeRef) value.ref), ("sourceKind", (encodeString) value.sourceKind), ("body", (encode) value.body), ("content", (encodeBytes) value.content), ("ownerReview", (encodeRef) value.ownerReview)]

def encodeIdentity  (value : CandidateCapturedMetadata.IdentityBinding) : J :=
  .object [("ref", (encodeRef) value.ref), ("source", (encodeRef) value.source), ("token", (encodeString) value.token), ("frame", (encodeFrame) value.frame)]

def encodeOwner  (value : CandidateCapturedMetadata.OwnerBinding) : J :=
  .object [("ref", (encodeRef) value.ref), ("source", (encodeRef) value.source), ("token", (encodeString) value.token), ("holder", (encodeRef) value.holder), ("scope", (encodeRef) value.scope), ("frame", (encodeFrame) value.frame)]

def encodeScope  (value : CandidateCapturedMetadata.ScopeBinding) : J :=
  .object [("ref", (encodeRef) value.ref), ("source", (encodeRef) value.source), ("token", (encodeString) value.token), ("scope", (encodeRef) value.scope), ("ownerBinding", (encodeRef) value.ownerBinding), ("frame", (encodeFrame) value.frame)]

def encodeReceipt  (value : CandidateCapturedMetadata.Receipt) : J :=
  .object [("ref", (encodeRef) value.ref), ("schema", (encodeRef) value.schema), ("artifact", (encodeArtifact encodeRawRecord) value.artifact), ("frame", (encodeFrame) value.frame), ("identity", (encodeIdentity) value.identity), ("owner", (encodeOwner) value.owner), ("scope", (encodeScope) value.scope)]

def encodeMetadata  (value : CandidateCapturedMetadata.Context) : J :=
  .object [("frame", (encodeFrame) value.frame), ("schema", (encodeRef) value.schema), ("records", (encodeList encodeReceipt) value.records), ("roots", (encodeList encodeReceipt) value.roots), ("identities", (encodeList encodeIdentity) value.identities), ("owners", (encodeList encodeOwner) value.owners), ("scopes", (encodeList encodeScope) value.scopes)]

def encodeBinding  (value : CandidateFiniteSourceCatalog.Binding) : J :=
  .object [("role", (fun r => .string (sourceRoleName r)) value.role), ("token", (encodeString) value.token), ("ref", (encodeRef) value.ref)]

def encodeApproval {α : Type} (encode : α → J) (value : CandidateFiniteSourceCatalog.Approval α) : J :=
  .object [("role", (fun r => .string (sourceRoleName r)) value.role), ("artifact", (encodeArtifact encode) value.artifact), ("frame", (encodeFrame) value.frame)]

def encodePayload {α : Type} (encode : α → J) (value : CandidateFiniteSourceCatalog.Capture α) : J :=
  .object [("frame", (encodeFrame) value.frame), ("records", (encodeList (encodeArtifact encode)) value.records), ("bindings", (encodeList encodeBinding) value.bindings), ("roots", (encodeList (encodeApproval encode)) value.roots)]

def encodeCatalog {α : Type} (encode : α → J) (value : CandidateOwnedBindings.Catalog α) : J :=
  .object [("frame", (encodeFrame) value.frame), ("records", (encodeList (encodeArtifact (encodeBody encode))) value.records), ("roots", (encodeList (encodeArtifact (encodeBody encode))) value.roots)]

def encodeOwned  (value : CandidateOwnedIntentQualifiers.Context) : J :=
  .object [("resolutions", (encodeCatalog encodeResolution) value.resolutions), ("roles", (encodeCatalog encodeRole) value.roles)]

def wrap (kind : String) (context : J) : J :=
  .object [("schema_version",.string snapshotVersion),("kind",.string kind),("context",context)]
partial def render : J → String
  | .null => "null"
  | .boolean b => if b then "true" else "false"
  | .number token => token
  | .string text => (Lean.Json.str text).compress
  | .array values => "[" ++ String.intercalate "," (values.map render) ++ "]"
  | .object entries => "{" ++ String.intercalate "," (entries.map fun (key,value) => (Lean.Json.str key).compress ++ ":" ++ render value) ++ "}"
def capture (ast : J) : CandidateBindingCapture.Envelope :=
  CandidateOriginalBytePipeline.RuntimeControls.textCapture (render ast)
end RelationalSuccessor.CandidateCatalogSnapshots.RuntimeEncoding
