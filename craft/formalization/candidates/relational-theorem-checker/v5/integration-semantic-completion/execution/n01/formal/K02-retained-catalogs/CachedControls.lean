import CachedNestedEntry
import NestedControls
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateRetainedCatalogs.RuntimeControls
open CandidateCatalogSnapshots (string)
open CandidateProfileEvidence.Controls (bootstrap root)
open CandidateEvidenceResources.Controls (numbers)
open CandidateNestedProvenance (Inputs)
open CandidateNestedProvenance.GeneratedFixture
open CandidateNestedProvenance.RuntimeControls

def sameResult : Except CandidateNestedProvenance.FullRefusal (CandidateNestedProvenance.Output String) →
    Except CandidateNestedProvenance.FullRefusal (CandidateNestedProvenance.Output String) → Bool
  | .ok a, .ok b => decide (a = b)
  | .error a, .error b => decide (a = b)
  | _, _ => false

def cachedResult (input : Inputs := inputs) (budget : CandidateDigestCapture.Limits := limits) :=
  runCachedFull string bootstrap budget numbers root authorityRef input world claim
def parity (input : Inputs := inputs) (budget : CandidateDigestCapture.Limits := limits) : Bool :=
  sameResult (cachedResult input budget) (result input budget)
def priorParity : Bool :=
  sameResult (runCachedFull string bootstrap limits numbers root CandidateSelectedRelation.GeneratedFixture.authorityRef priorInputs
    CandidateOriginalBytePipeline.RuntimeControls.world CandidateOriginalBytePipeline.RuntimeControls.claim)
  (CandidateNestedProvenance.runFull string bootstrap limits numbers root CandidateSelectedRelation.GeneratedFixture.authorityRef priorInputs
    CandidateOriginalBytePipeline.RuntimeControls.world CandidateOriginalBytePipeline.RuntimeControls.claim)

#eval parity
#eval parity inputs {limits with maxCaptures := 27}
#eval parity inputs {limits with totalBytes := CandidateDigestCapture.originalByteCount parent.captures}
#eval parity {inputs with nested := nested.drop 1}
#eval parity {inputs with nested := nested.eraseDups}
#eval parity {inputs with nested := nested.reverse}
#eval parity {inputs with nested := nested.map fun cap => {cap with digestProfile := bootstrap.ref}}
#eval parity bodyMismatch
#eval parity reviewMismatch
#eval parity keyMismatch
#eval parity {inputs with nested := []} {limits with maxCaptures := 0}
#eval priorParity
#eval tag (cachedResult)
#eval inputs.captures.length
#eval nested.length
#eval (cachedResult).toOption.map (fun output => output.catalogs == catalogs)
#eval (cachedResult).toOption.map (fun output => output.parent.evidence.profile.frame == world.frame)
#eval (runSelected string bootstrap limits numbers root authorityRef parent world claim).toOption.map (fun state => state.state.batch.val.map (fun item => item.val.capture) == parent.relation.original.captures)
end RelationalSuccessor.CandidateRetainedCatalogs.RuntimeControls
