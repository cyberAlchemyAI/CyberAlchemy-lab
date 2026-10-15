import CatalogRuntimeEncoding
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateCatalogSnapshots.RuntimeControls
open CandidateCatalogSnapshots
open RuntimeEncoding
open CandidateBindingAst (J)
open CandidateOriginalBytePipeline.RuntimeControls (source qualifiers bindings world claim textCapture)
open CandidateProfileEvidence.Controls (bootstrap)
open CandidateEvidenceResources.Controls (numbers)
abbrev fixtureMetadata := CandidateOriginalBytePipeline.RuntimeControls.metadata
def metadataAst := wrap "metadata-context" (encodeMetadata fixtureMetadata)
def payloadAst := wrap "payload-context" (encodePayload encodeString CandidateCapturedMetadata.Examples.payloads)
def ownedAst := wrap "owned-qualifier-context" (encodeOwned bindings)
def inputs : Inputs := ⟨source, qualifiers, capture metadataAst, capture payloadAst, capture ownedAst⟩
def limits : CandidateDigestCapture.Limits := ⟨200000, 1000000, 100⟩
def result (input : Inputs := inputs) (budget : CandidateDigestCapture.Limits := limits) :=
  run string bootstrap budget numbers input world claim
def tag : Except Refusal CandidateIntentSourcePipeline.Output → String
  | .ok _ => "prepared"
  | .error .catalog => "catalog-refused"
  | .error .relation => "relation-refused"
  | .error (.input .budget) => "budget-refused"
  | .error (.input (.source (index, _, _))) => "source-refused-" ++ toString index
  | .error (.input .relation) => "unreachable-input-relation"
partial def replaceField (key : String) (replacement : J) : J → J
  | .object entries => .object (entries.map fun (k, v) =>
      (k, if k = key then replacement else replaceField key replacement v))
  | .array values => .array (values.map (replaceField key replacement))
  | value => value
def missingOwners : J :=
  wrap "metadata-context" (.object ((match encodeMetadata fixtureMetadata with
    | .object entries => entries
    | _ => []).filter fun entry => entry.1 != "owners"))
def duplicateMetadata := {fixtureMetadata with records := fixtureMetadata.records ++ fixtureMetadata.records}
def conflictingPayload :=
  let original := CandidateCapturedMetadata.Examples.payloads
  let first := CandidateFiniteSourceCatalog.Examples.project
  {original with records := original.records ++ [{first with body := "different-unused-body"}]}
def conflictingOwned :=
  let entry := CandidateOwnedIntentQualifiers.Fixture.roleEntry
  {bindings with roles := {bindings.roles with
    records := bindings.roles.records ++ [{entry with body := {entry.body with token := "alias-conflict", target := {entry.body.target with code := "changed"}}}]}}

#eval tag (result)
#eval tag (result {inputs with metadata := capture (wrap "metadata-context" (encodeMetadata duplicateMetadata))})
#eval (metadata.decode (encodeMetadata duplicateMetadata)).map (fun context => context.records.length)
#eval tag (result {inputs with payload := capture (wrap "payload-context" (encodePayload encodeString conflictingPayload))})
#eval tag (result {inputs with owned := capture (wrap "owned-qualifier-context" (encodeOwned conflictingOwned))})
#eval tag (result {inputs with metadata := capture missingOwners})
#eval tag (result {inputs with metadata := capture (wrap "payload-context" (encodeMetadata fixtureMetadata))})
#eval tag (result {inputs with metadata := capture (replaceField "content" (.array [.number "256"]) metadataAst)})
#eval tag (result {inputs with metadata := capture (replaceField "epoch" (.number "42.0") metadataAst)})
#eval tag (result inputs {limits with maxCaptures := 4})
#eval tag (result inputs {limits with totalBytes := source.content.length + qualifiers.content.length})
#eval tag (result {inputs with owned := {inputs.owned with byteLength := 0}})
#eval tag (result {inputs with payload := textCapture "{\"unused\":1e1000000000}"})
#eval tag (result {inputs with metadata := textCapture "null"})
#eval byte.decode (.number "255")
#eval byte.decode (.number "-1")
#eval byte.decode (.number "255.0")
end RelationalSuccessor.CandidateCatalogSnapshots.RuntimeControls
