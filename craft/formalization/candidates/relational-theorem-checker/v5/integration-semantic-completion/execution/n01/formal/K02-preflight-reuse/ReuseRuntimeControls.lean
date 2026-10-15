import ReusableEntry
import ResourceControls
import AuthorityRuntimeControls
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidatePreflightReuse.RuntimeControls
open CandidateProfileEvidence.Controls (bootstrap frame root changedRef)
open CandidateProfileEvidence.RuntimeControls (capture0 capture1 capture2 capture3 capture5 authorityRef2 authorityRef3 authorityRef5 limits)
open CandidateEvidenceResources
open CandidateEvidenceResources.Controls (numbers)

def textCapture (text : String) : CandidateBindingCapture.Envelope :=
  let bytes:=text.toUTF8.toList
  ⟨bytes,bytes.length,bootstrap.ref,(CandidateDigest.digestBytes bytes).getD "uncomputed"⟩
def diagnosticRun (capture : CandidateBindingCapture.Envelope) (ref : RevisionRef) (declarations selections : List CandidateBindingCapture.Envelope) : Diagnostic :=
  diagnose (CandidatePreflightReuse.run bootstrap limits numbers frame root ref capture declarations selections)

#eval (diagnosticRun capture2 authorityRef2 [capture0] [capture1]).code
#eval (diagnose (CandidatePreflightReuse.run bootstrap {limits with maxCaptures:=2} numbers frame root authorityRef2 capture2 [capture0] [capture1])).code
#eval (diagnose (CandidatePreflightReuse.run bootstrap {limits with totalBytes:=capture0.content.length+capture1.content.length} numbers frame root authorityRef2 capture2 [capture0] [capture1])).code
#eval (diagnosticRun {capture2 with byteLength:=0} authorityRef2 [capture0] [capture1]).code
#eval (diagnosticRun (textCapture "{\"unused\":[1e1000000000]}") authorityRef2 [capture0] [capture1]).code
#eval (diagnosticRun (textCapture "{\"unused\":[1e-1000000000]}") authorityRef2 [capture0] [capture1]).numericToken
#eval (diagnosticRun (textCapture "{\"unused\":[1e1025]}") authorityRef2 [capture0] [capture1]).code
#eval (diagnosticRun (textCapture "[") authorityRef2 [capture0] [capture1]).code
#eval (diagnosticRun (textCapture "\"\\uD800\"") authorityRef2 [capture0] [capture1]).code
#eval (diagnosticRun {capture2 with digest:="bad"} authorityRef2 [capture0] [capture1]).code
#eval (diagnose (CandidatePreflightReuse.run {bootstrap with algorithm:="unsupported"} limits numbers frame root authorityRef2 capture2 [capture0] [capture1])).code
#eval (diagnose (CandidatePreflightReuse.run bootstrap limits numbers frame (changedRef root) authorityRef2 capture2 [capture0] [capture1])).code
#eval (diagnosticRun capture2 authorityRef2 [] []).code
#eval (diagnosticRun capture3 authorityRef3 [capture0] [capture1]).code
#eval (diagnosticRun capture5 authorityRef5 [capture0] [capture1]).code
#eval (diagnosticRun capture2 authorityRef2 [{capture0 with byteLength:=0}] [capture1]).sourceIndex
#eval (diagnosticRun capture2 authorityRef2 [capture0] [{capture1 with byteLength:=0}]).sourceIndex
#eval (diagnosticRun (textCapture "{\"unused\":[{\"inner\":1e1000000000}]}") authorityRef2 [capture0] [capture1]).numericToken
#eval (diagnosticRun (textCapture "{\"duplicate\":42,\"duplicate\":1e1000000000}") authorityRef2 [capture0] [capture1]).numericToken
#eval firstUnsupported numbers (numberTokens (.object [("extra",.array [.number "42.0",.number "4.2e1",.number "-0"])]))
#eval tokenWorkCheck numbers "123.000000000000000000000001"
#eval CandidateNumberParser.epochAdapter.decode (.number "123.000000000000000000000001")
end RelationalSuccessor.CandidatePreflightReuse.RuntimeControls
