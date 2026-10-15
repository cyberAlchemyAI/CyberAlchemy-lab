import OriginalBytePolicy
import PipelineFixture
import ResourceControls
import AuthorityControls
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateOriginalBytePipeline.RuntimeControls
open CandidateOriginalBytePipeline
open CandidateProfileEvidence.Controls (bootstrap)
open CandidateEvidenceResources.Controls (numbers)
abbrev Old := CandidateCapturedMetadata.Examples.context
def source : CandidateBindingCapture.Envelope :=
  let bytes := CandidateCapturedMetadata.Examples.originalBytes
  ⟨bytes, bytes.length, bootstrap.ref, (CandidateDigest.digestBytes bytes).getD "uncomputed"⟩
def textCapture (text : String) : CandidateBindingCapture.Envelope :=
  let bytes := text.toUTF8.toList
  ⟨bytes, bytes.length, bootstrap.ref, (CandidateDigest.digestBytes bytes).getD "uncomputed"⟩
def qualifiers := textCapture "{\"intent_resolution_ref\":\"resolution:original\",\"addressing_role\":\"investigation\"}"
def limits : CandidateDigestCapture.Limits := ⟨50000, 100000, 100⟩
def inputs : Inputs := ⟨source, qualifiers, []⟩

-- Coherent synthetic contexts using the actual source hash. These do not provide
-- authentic owners or a raw-to-typed catalog adapter; all catalog roots are controls.
def sourceRef : RevisionRef :=
  {CandidateCapturedMetadata.Examples.sourceRef with digest := source.digest}
def identity : CandidateCapturedMetadata.IdentityBinding :=
  {CandidateCapturedMetadata.Examples.identity with source := sourceRef}
def owner : CandidateCapturedMetadata.OwnerBinding :=
  {CandidateCapturedMetadata.Examples.owner with source := sourceRef}
def scope : CandidateCapturedMetadata.ScopeBinding :=
  {CandidateCapturedMetadata.Examples.scope with source := sourceRef}
def receipt : CandidateCapturedMetadata.Receipt :=
  {CandidateCapturedMetadata.Examples.receipt with
    artifact := {CandidateCapturedMetadata.Examples.artifact with ref := sourceRef}
    identity := identity, owner := owner, scope := scope}
def metadata : CandidateCapturedMetadata.Context :=
  {Old with records := [receipt], roots := [receipt], identities := [identity], owners := [owner], scopes := [scope]}
def projected : CandidateCapturedMetadata.Projected :=
  ⟨receipt, CandidateCapturedMetadata.Examples.payload⟩
def selection : CandidateIntentAddressing.Selection :=
  {CandidateIntentSourceContract.Fixture.selection with resolution := projected.resolution.ref}
def claim : CandidateIntentAddressing.Claim :=
  {CandidateIntentSourceContract.Fixture.claim with
    resolution := projected.resolution
    resolutionQualifier := projected.resolution.ref
    selection := selection}
def world : CandidateIntentSourceContract.FramedWorld :=
  {CandidateIntentSourceContract.Fixture.framed with
    world := {CandidateIntentSourceContract.Fixture.world with resolutions := [projected.resolution], selections := [selection]}}
def resolutionEntry : CandidateOwnedBindings.Entry CandidateIntentAddressing.Resolution :=
  {CandidateOwnedIntentQualifiers.Fixture.resolutionEntry with
    body := {CandidateOwnedIntentQualifiers.Fixture.resolutionEntry.body with target := projected.resolution}}
def bindings : CandidateOwnedIntentQualifiers.Context :=
  {CandidateOwnedIntentQualifiers.Fixture.context with
    resolutions := {CandidateOwnedIntentQualifiers.Fixture.context.resolutions with records := [resolutionEntry], roots := [resolutionEntry]}}
def result (input : Inputs := inputs) (budget : CandidateDigestCapture.Limits := limits) : Except Refusal CandidateIntentSourcePipeline.Output :=
  run bootstrap budget numbers input metadata CandidateCapturedMetadata.Examples.payloads bindings world claim
def tag : Except Refusal CandidateIntentSourcePipeline.Output → String
  | .ok _ => "prepared"
  | .error .budget => "budget-refused"
  | .error (.source (index, _, reason)) =>
    "source-" ++ toString index ++ ":" ++ reprStr reason
  | .error .relation => "relation-refused"

#eval tag (result)
#eval tag (result {inputs with catalogs := [textCapture "null", textCapture "null"]})
#eval tag (result inputs {limits with maxCaptures := 1})
#eval tag (result inputs {limits with totalBytes := source.content.length})
#eval tag (result {inputs with source := {source with byteLength := 0}})
#eval tag (result {inputs with qualifiers := {qualifiers with digest := "bad"}})
#eval tag (result {inputs with catalogs := [textCapture "[", textCapture "null"]})
#eval tag (result {inputs with catalogs := [textCapture "null", textCapture "{\"unused\":1e1000000000}"]})
#eval tag (result {inputs with qualifiers := textCapture "null"})
#eval tag (run bootstrap limits numbers inputs CandidateIntentSourcePipeline.Fixture.metadata
  CandidateIntentSourcePipeline.Fixture.payloads CandidateIntentSourcePipeline.Fixture.bindings
  CandidateIntentSourcePipeline.Fixture.world CandidateIntentSourcePipeline.Fixture.claim)
#eval tag (result {inputs with source := textCapture "{}"})
#eval tag (run bootstrap limits numbers inputs metadata CandidateCapturedMetadata.Examples.payloads bindings
  {world with frame := {world.frame with epoch := 43}} claim)
end RelationalSuccessor.CandidateOriginalBytePipeline.RuntimeControls
