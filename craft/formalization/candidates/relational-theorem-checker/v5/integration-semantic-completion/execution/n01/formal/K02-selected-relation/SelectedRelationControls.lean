import SelectedProfileFixture
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateSelectedRelation.RuntimeControls
open CandidateSelectedRelation
open RelationalSuccessor.CandidateSelectedRelation.GeneratedFixture (authority authorityRef declaration declarationRef selection missingReview missingReviewRef)
open CandidateProfileEvidence.Controls (bootstrap root)
open CandidateEvidenceResources.Controls (numbers)
open CandidateCatalogSnapshots (string)
open CandidateOriginalBytePipeline.RuntimeControls (world claim textCapture)
def selected (capture : CandidateBindingCapture.Envelope) := {capture with digestProfile := declarationRef}
def relation : CandidateCatalogSnapshots.Inputs :=
  let prior := CandidateCatalogSnapshots.RuntimeControls.inputs
  ⟨selected prior.source, selected prior.qualifiers, selected prior.metadata, selected prior.payload, selected prior.owned⟩
def inputs : Inputs := ⟨authority,[declaration],[selection],relation⟩
def limits : CandidateDigestCapture.Limits := ⟨200000,1000000,100⟩
def result (input : Inputs := inputs) (budget : CandidateDigestCapture.Limits := limits)
    (context : CandidateIntentSourcePipeline.FramedWorld := world) (expectedRoot : RevisionRef := root)
    (expectedAuthority : RevisionRef := authorityRef) :=
  run string bootstrap budget numbers expectedRoot expectedAuthority input context claim
def tag : Except Refusal Output → String
  | .ok _ => "prepared"
  | .error .budget => "full-budget-refused"
  | .error (.profile .budgetRefused) => "profile-budget-refused"
  | .error (.profile (.sourceRefused index _ _)) => "profile-source-refused-" ++ toString index
  | .error (.profile (.data .profileDataRefused)) => "profile-data-refused"
  | .error (.profile (.data .authorityDataRefused)) => "authority-data-refused"
  | .error (.profile (.data .evidenceJoinRefused)) => "evidence-join-refused"
  | .error (.profile (.data (.prepared _))) => "unreachable-prepared-refusal"
  | .error (.relation .catalog) => "relation-catalog-refused"
  | .error (.relation .relation) => "relation-meaning-refused"
  | .error (.relation (.input .budget)) => "relation-budget-refused"
  | .error (.relation (.input (.source (index, _, _)))) => "relation-source-refused-" ++ toString index
  | .error (.relation (.input .relation)) => "unreachable-input-relation"
def honestAlteredDeclaration :=
  {declaration with content := declaration.content ++ [32], byteLength := declaration.byteLength + 1}
def sourceBootstrap := {relation with source := {relation.source with digestProfile := bootstrap.ref}}
def metadataBootstrap := {relation with metadata := {relation.metadata with digestProfile := bootstrap.ref}}
def badQualifier := {relation with qualifiers := {relation.qualifiers with byteLength := 0}}
def malformedCatalog := {relation with metadata := selected (textCapture "null")}
def unusedNumeric := {relation with payload := selected (textCapture "{\"unused\":1e1000000000}")}
def wrongRoleCatalog := {relation with metadata := selected (CandidateCatalogSnapshots.RuntimeEncoding.capture
  (CandidateCatalogSnapshots.RuntimeEncoding.wrap "payload-context" CandidateCatalogSnapshots.RuntimeControls.metadataAst))}

#eval tag (result)
#eval (result).toOption.map (fun output => output.evidence.profile.profile.ref == declarationRef)
#eval (result).toOption.map (fun output => output.evidence.profile.frame == world.frame)
#eval inputs.captures.length
#eval tag (result inputs {limits with maxCaptures := 7})
#eval tag (result inputs {limits with totalBytes := authority.content.length + declaration.content.length + selection.content.length})
#eval tag (result inputs {limits with perCaptureBytes := 1000})
#eval tag (result {inputs with authority := {authority with byteLength := 0}})
#eval tag (result {inputs with relation := badQualifier})
#eval tag (result {inputs with relation := sourceBootstrap})
#eval tag (result {inputs with relation := metadataBootstrap})
#eval tag (result inputs limits {world with frame := {world.frame with epoch := 43}})
#eval tag (result {inputs with declarations := []})
#eval tag (result {inputs with selections := []})
#eval tag (result {inputs with authority := missingReview} limits world root missingReviewRef)
#eval tag (result {inputs with relation := malformedCatalog})
#eval tag (result {inputs with relation := unusedNumeric})
#eval tag (result inputs limits world {root with digest := "wrong-root"})
#eval tag (result {inputs with declarations := [honestAlteredDeclaration]})
#eval tag (result {inputs with relation := wrongRoleCatalog})
#eval tag (result {inputs with relation := {relation with source := selected (textCapture "{}")}})
#eval tag (result {inputs with authority := {authority with byteLength := 0}} {limits with maxCaptures := 0})
end RelationalSuccessor.CandidateSelectedRelation.RuntimeControls
