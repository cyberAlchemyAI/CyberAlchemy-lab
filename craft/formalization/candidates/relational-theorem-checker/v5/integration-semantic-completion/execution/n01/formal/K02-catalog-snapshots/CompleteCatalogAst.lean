import OriginalBytePolicy
import BindingRecord
set_option autoImplicit false
namespace RelationalSuccessor.CandidateCatalogSnapshots
open CandidateBindingAst
abbrev RawRecord := CandidateIntentRecordShape.RawRecord

def StringMeaning (value : J) (output : String) : Prop := value = .string output
def decodeString : J → Option String
  | .string output => some output
  | _ => none
theorem string_exact (value : J) (output : String) :
    decodeString value = some output ↔ StringMeaning value output := by
  cases value <;> simp [decodeString, StringMeaning]
def string : Decoder String := ⟨decodeString, StringMeaning, string_exact⟩

def ByteMeaning (value : J) (output : UInt8) : Prop :=
  ∃ n, CandidateNumberParser.AstEpochMeaning value n ∧ n < 256 ∧ UInt8.ofNat n = output
def decodeByte (value : J) : Option UInt8 :=
  match CandidateNumberParser.epochAdapter.decode value with
  | none => none
  | some n => if n < 256 then some (UInt8.ofNat n) else none
theorem byte_exact (value : J) (output : UInt8) :
    decodeByte value = some output ↔ ByteMeaning value output := by
  constructor
  · intro accepted
    cases parsed : CandidateNumberParser.epochAdapter.decode value with
    | none => simp only [decodeByte, parsed] at accepted; contradiction
    | some n =>
      simp only [decodeByte, parsed] at accepted
      split at accepted
      · rename_i bound
        exact ⟨n, (CandidateNumberParser.epochAdapter.exact _ _).mp parsed, bound, Option.some.inj accepted⟩
      · contradiction
  · rintro ⟨n, meaning, bound, same⟩
    have parsed := (CandidateNumberParser.epochAdapter.exact _ _).mpr meaning
    simp only [decodeByte, parsed, if_pos bound, same]
def byte : Decoder UInt8 := ⟨decodeByte, ByteMeaning, byte_exact⟩
def bytes := array byte

def sourceRoleName : CandidateSourceResolution.Role → String
  | .intent => "intent"
  | .decision => "decision"
  | .subject => "subject"
  | .satisfactionTest => "satisfaction-test"
def SourceRoleMeaning (value : J) (output : CandidateSourceResolution.Role) : Prop :=
  value = .string (sourceRoleName output)
def decodeSourceRole : J → Option CandidateSourceResolution.Role
  | .string "intent" => some .intent
  | .string "decision" => some .decision
  | .string "subject" => some .subject
  | .string "satisfaction-test" => some .satisfactionTest
  | _ => none
theorem source_role_exact (value : J) (output : CandidateSourceResolution.Role) :
    decodeSourceRole value = some output ↔ SourceRoleMeaning value output := by
  cases output <;> cases value <;> simp [decodeSourceRole, SourceRoleMeaning, sourceRoleName]
  all_goals split <;> simp_all
  all_goals split <;> simp_all
  all_goals split <;> simp_all
  all_goals split <;> simp_all
def sourceRole : Decoder CandidateSourceResolution.Role :=
  ⟨decodeSourceRole, SourceRoleMeaning, source_role_exact⟩
def rawRecord : Decoder RawRecord :=
  ⟨CandidateJsonSource.decodeRecord, CandidateJsonSource.SchemaAstMeaning, CandidateJsonSource.decode_record_exact⟩

def snapshotVersion : String := "cyberalchemy-lab-original-context-snapshot/candidate-v1"

def artifactKeys : List String := ["ref", "sourceKind", "body", "content", "ownerReview"]
def artifactFields {α : Type} (body : Decoder α) : Fields (CandidateFiniteSourceCatalog.Artifact α) :=
  mapFields (cons (reference) (cons (string) (cons (body) (cons (bytes) (cons (reference) (empty)))))) (fun output => ⟨output.1, output.2.1, output.2.2.1, output.2.2.2.1, output.2.2.2.2.1⟩)
def artifact {α : Type} (body : Decoder α) : Decoder (CandidateFiniteSourceCatalog.Artifact α) := object artifactKeys (artifactFields body)
def ArtifactMeaning {α : Type} (body : Decoder α) (value : J) (output : CandidateFiniteSourceCatalog.Artifact α) : Prop :=
  ObjectMeaning artifactKeys (artifactFields body) value output
theorem artifact_exact {α : Type} (body : Decoder α) (value : J) (output : CandidateFiniteSourceCatalog.Artifact α) :
    (artifact body).decode value = some output ↔ ArtifactMeaning body value output :=
  object_exact artifactKeys (artifactFields body) value output

def identityKeys : List String := ["ref", "source", "token", "frame"]
def identityFields  : Fields (CandidateCapturedMetadata.IdentityBinding) :=
  mapFields (cons (reference) (cons (reference) (cons (string) (cons (CandidateBindingRecords.frame) (empty))))) (fun output => ⟨output.1, output.2.1, output.2.2.1, output.2.2.2.1⟩)
def identity  : Decoder (CandidateCapturedMetadata.IdentityBinding) := object identityKeys (identityFields)
def IdentityMeaning  (value : J) (output : CandidateCapturedMetadata.IdentityBinding) : Prop :=
  ObjectMeaning identityKeys (identityFields) value output
theorem identity_exact  (value : J) (output : CandidateCapturedMetadata.IdentityBinding) :
    (identity).decode value = some output ↔ IdentityMeaning value output :=
  object_exact identityKeys (identityFields) value output

def ownerKeys : List String := ["ref", "source", "token", "holder", "scope", "frame"]
def ownerFields  : Fields (CandidateCapturedMetadata.OwnerBinding) :=
  mapFields (cons (reference) (cons (reference) (cons (string) (cons (reference) (cons (reference) (cons (CandidateBindingRecords.frame) (empty))))))) (fun output => ⟨output.1, output.2.1, output.2.2.1, output.2.2.2.1, output.2.2.2.2.1, output.2.2.2.2.2.1⟩)
def owner  : Decoder (CandidateCapturedMetadata.OwnerBinding) := object ownerKeys (ownerFields)
def OwnerMeaning  (value : J) (output : CandidateCapturedMetadata.OwnerBinding) : Prop :=
  ObjectMeaning ownerKeys (ownerFields) value output
theorem owner_exact  (value : J) (output : CandidateCapturedMetadata.OwnerBinding) :
    (owner).decode value = some output ↔ OwnerMeaning value output :=
  object_exact ownerKeys (ownerFields) value output

def scopeKeys : List String := ["ref", "source", "token", "scope", "ownerBinding", "frame"]
def scopeFields  : Fields (CandidateCapturedMetadata.ScopeBinding) :=
  mapFields (cons (reference) (cons (reference) (cons (string) (cons (reference) (cons (reference) (cons (CandidateBindingRecords.frame) (empty))))))) (fun output => ⟨output.1, output.2.1, output.2.2.1, output.2.2.2.1, output.2.2.2.2.1, output.2.2.2.2.2.1⟩)
def scope  : Decoder (CandidateCapturedMetadata.ScopeBinding) := object scopeKeys (scopeFields)
def ScopeMeaning  (value : J) (output : CandidateCapturedMetadata.ScopeBinding) : Prop :=
  ObjectMeaning scopeKeys (scopeFields) value output
theorem scope_exact  (value : J) (output : CandidateCapturedMetadata.ScopeBinding) :
    (scope).decode value = some output ↔ ScopeMeaning value output :=
  object_exact scopeKeys (scopeFields) value output

def receiptKeys : List String := ["ref", "schema", "artifact", "frame", "identity", "owner", "scope"]
def receiptFields  : Fields (CandidateCapturedMetadata.Receipt) :=
  mapFields (cons (reference) (cons (reference) (cons (artifact rawRecord) (cons (CandidateBindingRecords.frame) (cons (identity) (cons (owner) (cons (scope) (empty)))))))) (fun output => ⟨output.1, output.2.1, output.2.2.1, output.2.2.2.1, output.2.2.2.2.1, output.2.2.2.2.2.1, output.2.2.2.2.2.2.1⟩)
def receipt  : Decoder (CandidateCapturedMetadata.Receipt) := object receiptKeys (receiptFields)
def ReceiptMeaning  (value : J) (output : CandidateCapturedMetadata.Receipt) : Prop :=
  ObjectMeaning receiptKeys (receiptFields) value output
theorem receipt_exact  (value : J) (output : CandidateCapturedMetadata.Receipt) :
    (receipt).decode value = some output ↔ ReceiptMeaning value output :=
  object_exact receiptKeys (receiptFields) value output

def metadataKeys : List String := ["frame", "schema", "records", "roots", "identities", "owners", "scopes"]
def metadataFields  : Fields (CandidateCapturedMetadata.Context) :=
  mapFields (cons (CandidateBindingRecords.frame) (cons (reference) (cons (array receipt) (cons (array receipt) (cons (array identity) (cons (array owner) (cons (array scope) (empty)))))))) (fun output => ⟨output.1, output.2.1, output.2.2.1, output.2.2.2.1, output.2.2.2.2.1, output.2.2.2.2.2.1, output.2.2.2.2.2.2.1⟩)
def metadata  : Decoder (CandidateCapturedMetadata.Context) := object metadataKeys (metadataFields)
def MetadataMeaning  (value : J) (output : CandidateCapturedMetadata.Context) : Prop :=
  ObjectMeaning metadataKeys (metadataFields) value output
theorem metadata_exact  (value : J) (output : CandidateCapturedMetadata.Context) :
    (metadata).decode value = some output ↔ MetadataMeaning value output :=
  object_exact metadataKeys (metadataFields) value output

def bindingKeys : List String := ["role", "token", "ref"]
def bindingFields  : Fields (CandidateFiniteSourceCatalog.Binding) :=
  mapFields (cons (sourceRole) (cons (string) (cons (reference) (empty)))) (fun output => ⟨output.1, output.2.1, output.2.2.1⟩)
def binding  : Decoder (CandidateFiniteSourceCatalog.Binding) := object bindingKeys (bindingFields)
def BindingMeaning  (value : J) (output : CandidateFiniteSourceCatalog.Binding) : Prop :=
  ObjectMeaning bindingKeys (bindingFields) value output
theorem binding_exact  (value : J) (output : CandidateFiniteSourceCatalog.Binding) :
    (binding).decode value = some output ↔ BindingMeaning value output :=
  object_exact bindingKeys (bindingFields) value output

def approvalKeys : List String := ["role", "artifact", "frame"]
def approvalFields {α : Type} (body : Decoder α) : Fields (CandidateFiniteSourceCatalog.Approval α) :=
  mapFields (cons (sourceRole) (cons (artifact body) (cons (CandidateBindingRecords.frame) (empty)))) (fun output => ⟨output.1, output.2.1, output.2.2.1⟩)
def approval {α : Type} (body : Decoder α) : Decoder (CandidateFiniteSourceCatalog.Approval α) := object approvalKeys (approvalFields body)
def ApprovalMeaning {α : Type} (body : Decoder α) (value : J) (output : CandidateFiniteSourceCatalog.Approval α) : Prop :=
  ObjectMeaning approvalKeys (approvalFields body) value output
theorem approval_exact {α : Type} (body : Decoder α) (value : J) (output : CandidateFiniteSourceCatalog.Approval α) :
    (approval body).decode value = some output ↔ ApprovalMeaning body value output :=
  object_exact approvalKeys (approvalFields body) value output

def payloadKeys : List String := ["frame", "records", "bindings", "roots"]
def payloadFields {α : Type} (body : Decoder α) : Fields (CandidateFiniteSourceCatalog.Capture α) :=
  mapFields (cons (CandidateBindingRecords.frame) (cons (array (artifact body)) (cons (array binding) (cons (array (approval body)) (empty))))) (fun output => ⟨output.1, output.2.1, output.2.2.1, output.2.2.2.1⟩)
def payload {α : Type} (body : Decoder α) : Decoder (CandidateFiniteSourceCatalog.Capture α) := object payloadKeys (payloadFields body)
def PayloadMeaning {α : Type} (body : Decoder α) (value : J) (output : CandidateFiniteSourceCatalog.Capture α) : Prop :=
  ObjectMeaning payloadKeys (payloadFields body) value output
theorem payload_exact {α : Type} (body : Decoder α) (value : J) (output : CandidateFiniteSourceCatalog.Capture α) :
    (payload body).decode value = some output ↔ PayloadMeaning body value output :=
  object_exact payloadKeys (payloadFields body) value output

def catalogKeys : List String := ["frame", "records", "roots"]
def catalogFields {α : Type} (target : Decoder α) : Fields (CandidateOwnedBindings.Catalog α) :=
  mapFields (cons (CandidateBindingRecords.frame) (cons (array (artifact (CandidateBindingRecords.body target))) (cons (array (artifact (CandidateBindingRecords.body target))) (empty)))) (fun output => ⟨output.1, output.2.1, output.2.2.1⟩)
def catalog {α : Type} (target : Decoder α) : Decoder (CandidateOwnedBindings.Catalog α) := object catalogKeys (catalogFields target)
def CatalogMeaning {α : Type} (target : Decoder α) (value : J) (output : CandidateOwnedBindings.Catalog α) : Prop :=
  ObjectMeaning catalogKeys (catalogFields target) value output
theorem catalog_exact {α : Type} (target : Decoder α) (value : J) (output : CandidateOwnedBindings.Catalog α) :
    (catalog target).decode value = some output ↔ CatalogMeaning target value output :=
  object_exact catalogKeys (catalogFields target) value output

def ownedKeys : List String := ["resolutions", "roles"]
def ownedFields  : Fields (CandidateOwnedIntentQualifiers.Context) :=
  mapFields (cons (catalog CandidateBindingAst.resolution) (cons (catalog CandidateBindingAst.role) (empty))) (fun output => ⟨output.1, output.2.1⟩)
def owned  : Decoder (CandidateOwnedIntentQualifiers.Context) := object ownedKeys (ownedFields)
def OwnedMeaning  (value : J) (output : CandidateOwnedIntentQualifiers.Context) : Prop :=
  ObjectMeaning ownedKeys (ownedFields) value output
theorem owned_exact  (value : J) (output : CandidateOwnedIntentQualifiers.Context) :
    (owned).decode value = some output ↔ OwnedMeaning value output :=
  object_exact ownedKeys (ownedFields) value output

def snapshotKeys : List String := ["schema_version", "kind", "context"]
def snapshotFields {α : Type} (kind : String) (context : Decoder α) : Fields (α) :=
  mapFields (cons (CandidateBindingRecords.constant snapshotVersion) (cons (CandidateBindingRecords.constant kind) (cons (context) (empty)))) (fun output => output.2.2.1)
def snapshot {α : Type} (kind : String) (context : Decoder α) : Decoder (α) := object snapshotKeys (snapshotFields kind context)
def SnapshotMeaning {α : Type} (kind : String) (context : Decoder α) (value : J) (output : α) : Prop :=
  ObjectMeaning snapshotKeys (snapshotFields kind context) value output
theorem snapshot_exact {α : Type} (kind : String) (context : Decoder α) (value : J) (output : α) :
    (snapshot kind context).decode value = some output ↔ SnapshotMeaning kind context value output :=
  object_exact snapshotKeys (snapshotFields kind context) value output

#print axioms string_exact
#print axioms byte_exact
#print axioms source_role_exact
#print axioms artifact_exact
#print axioms identity_exact
#print axioms owner_exact
#print axioms scope_exact
#print axioms receipt_exact
#print axioms metadata_exact
#print axioms binding_exact
#print axioms approval_exact
#print axioms payload_exact
#print axioms catalog_exact
#print axioms owned_exact
#print axioms snapshot_exact
end RelationalSuccessor.CandidateCatalogSnapshots
