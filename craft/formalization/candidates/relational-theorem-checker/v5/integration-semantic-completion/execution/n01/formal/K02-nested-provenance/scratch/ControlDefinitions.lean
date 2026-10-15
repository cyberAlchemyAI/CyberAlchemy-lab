import NestedFixture
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateNestedProvenance.RuntimeControls
open CandidateNestedProvenance
open RelationalSuccessor.CandidateNestedProvenance.GeneratedFixture (authority authorityRef declaration declarationRef selection source qualifiers metadata payload owned nested)
open CandidateProfileEvidence.Controls (bootstrap root)
open CandidateEvidenceResources.Controls (numbers)
open CandidateCatalogSnapshots (string)
open CandidateCatalogSnapshots.RuntimeEncoding (capture wrap encodePayload encodeString encodeOwned)
def relation : CandidateCatalogSnapshots.Inputs := ⟨source,qualifiers,metadata,payload,owned⟩
def catalogs : CandidateCatalogSnapshots.Catalogs String :=
  (decodeRawCatalogs string relation).getD ⟨CandidateOriginalBytePipeline.RuntimeControls.metadata,
    CandidateCapturedMetadata.Examples.payloads,CandidateOriginalBytePipeline.RuntimeControls.bindings⟩
def frame := catalogs.metadata.frame
def mapRef (ref : RevisionRef) : RevisionRef :=
  ((catalogs.payload.records.find? fun artifact => artifact.ref.key == ref.key).map fun artifact => artifact.ref).getD ref
def projected : CandidateCapturedMetadata.Projected :=
  (CandidateCapturedMetadata.decodeResolution catalogs.metadata catalogs.payload frame
    CandidateOriginalBytePipeline.RuntimeControls.sourceRef source.content
    ((CandidateScalarConversion.parseScalarDocumentBytes source.content).getD .null)).getD CandidateOriginalBytePipeline.RuntimeControls.projected
def newSubject : CandidateIntentAddressing.Subject :=
  {CandidateOriginalBytePipeline.RuntimeControls.claim.subject with ref := mapRef CandidateOriginalBytePipeline.RuntimeControls.claim.subject.ref}
def newIntent : CandidateIntentAddressing.Intent :=
  {CandidateOriginalBytePipeline.RuntimeControls.claim.intent with ref := mapRef CandidateOriginalBytePipeline.RuntimeControls.claim.intent.ref}
def newSelection : CandidateIntentAddressing.Selection :=
  {CandidateOriginalBytePipeline.RuntimeControls.claim.selection with subject := newSubject.ref, ownerDecision := projected.resolution.ownerDecision,resolution := projected.resolution.ref,frame := frame}
def claim : CandidateIntentAddressing.Claim :=
  {CandidateOriginalBytePipeline.RuntimeControls.claim with subject := newSubject,intent := newIntent, resolution := projected.resolution,resolutionQualifier := projected.resolution.ref,selection := newSelection}
def world : CandidateIntentSourcePipeline.FramedWorld :=
  let old := CandidateOriginalBytePipeline.RuntimeControls.world
  {old with frame := frame,world := {old.world with
    subjects := old.world.subjects.map fun subject => {subject with ref := mapRef subject.ref},
    intents := old.world.intents.map fun intent => {intent with ref := mapRef intent.ref},
    resolutions := [projected.resolution],decisions := old.world.decisions.map mapRef,
    tests := old.world.tests.map mapRef,selections := [newSelection]}}
def parent : CandidateSelectedRelation.Inputs := ⟨authority,[declaration],[selection],relation⟩
def inputs : Inputs := ⟨parent,nested⟩
def limits : CandidateDigestCapture.Limits := ⟨200000,1000000,100⟩
def result (input : Inputs := inputs) (budget : CandidateDigestCapture.Limits := limits) :=
  runFull string bootstrap budget numbers root authorityRef input world claim
def nestedTag : Except Refusal Unit → String
  | .ok _ => "prepared"
  | .error .budget => "nested-budget-refused"
  | .error .manifest => "nested-manifest-refused"
  | .error (.preflight (index,_,.numericRefused _)) => "nested-numeric-refused-" ++ toString index
  | .error (.preflight (index,_,.scalarRefused)) => "nested-scalar-refused-" ++ toString index
  | .error (.preflight (index,_,.digestRefused _)) => "nested-digest-refused-" ++ toString index
  | .error (.preflight (index,_,.invalidEnvelope)) => "nested-envelope-refused-" ++ toString index
  | .error (.preflight (_,_,.ready)) => "unreachable-ready-refusal"
  | .error .document => "nested-document-refused"
def tag : Except FullRefusal (Output String) → String
  | .ok _ => "prepared"
  | .error .budget => "full-budget-refused"
  | .error (.parent _) => "parent-refused"
  | .error .catalog => "catalog-refused"
  | .error (.nested .budget) => "nested-budget-refused"
  | .error (.nested .manifest) => "nested-manifest-refused"
  | .error (.nested (.preflight (index,_,_))) => "nested-preflight-" ++ toString index
  | .error (.nested .document) => "nested-document-refused"
def selected (input : CandidateBindingCapture.Envelope) := {input with digestProfile := declarationRef}
def mismatchedBody (artifact : CandidateFiniteSourceCatalog.Artifact String) :=
  if artifact.ref.key.artifact = "runtime:unapproved-cutover" then {artifact with body := "different-body"} else artifact
def mismatchedPayload : CandidateFiniteSourceCatalog.Capture String := {catalogs.payload with records := catalogs.payload.records.map mismatchedBody, roots := catalogs.payload.roots.map (fun (approval : CandidateFiniteSourceCatalog.Approval String) => {approval with artifact := mismatchedBody approval.artifact})}
def bodyMismatch := {inputs with parent := {parent with relation := {relation with
  payload := selected (capture (wrap "payload-context" (encodePayload encodeString mismatchedPayload)))}}}
def wrongReview {α : Type} (entry : CandidateOwnedBindings.Entry α) :=
  {entry with ownerReview := {entry.ownerReview with digest := "changed-owner-review"}}
def changedOwnedReview := {catalogs.owned with roles := {catalogs.owned.roles with
  records := catalogs.owned.roles.records.map wrongReview,roots := catalogs.owned.roles.roots.map wrongReview}}
def reviewMismatch := {inputs with parent := {parent with relation := {relation with
  owned := selected (capture (wrap "owned-qualifier-context" (encodeOwned changedOwnedReview)))}}}
def wrongKey {α : Type} (entry : CandidateOwnedBindings.Entry α) :=
  {entry with ref := {entry.ref with key := {entry.ref.key with artifact := "changed-binding-key"}}}
def changedOwnedKey := {catalogs.owned with roles := {catalogs.owned.roles with
  records := catalogs.owned.roles.records.map wrongKey,roots := catalogs.owned.roles.roots.map wrongKey}}
def keyMismatch := {inputs with parent := {parent with relation := {relation with
  owned := selected (capture (wrap "owned-qualifier-context" (encodeOwned changedOwnedKey)))}}}
def directItem (text body : String) : Expected String :=
  let cap := selected (CandidateOriginalBytePipeline.RuntimeControls.textCapture text)
  .payload ⟨⟨⟨"fixture","direct-item","1"⟩,cap.digest⟩,"synthetic-record",body,cap.content,
    CandidateProfileEvidence.Controls.issuer⟩
def direct (item : Expected String) :=
  runNested string ⟨declarationRef,bootstrap.algorithm,bootstrap.encoding⟩ limits numbers frame
    [item] [envelope ⟨declarationRef,bootstrap.algorithm,bootstrap.encoding⟩ item]
def priorCatalogs : CandidateCatalogSnapshots.Catalogs String :=
  ⟨CandidateOriginalBytePipeline.RuntimeControls.metadata,CandidateCapturedMetadata.Examples.payloads,
    CandidateOriginalBytePipeline.RuntimeControls.bindings⟩
def priorInputs : Inputs :=
  let old := CandidateSelectedRelation.RuntimeControls.inputs
  ⟨old,(required priorCatalogs).map (envelope ⟨CandidateSelectedRelation.GeneratedFixture.declarationRef,
    bootstrap.algorithm,bootstrap.encoding⟩)⟩

end RelationalSuccessor.CandidateNestedProvenance.RuntimeControls
