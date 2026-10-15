import DigestCaptureControls
open RelationalSuccessor.CandidateDigestCapture
open RelationalSuccessor.CandidateDigestCapture.Controls
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor
def outcomeTag {α : Type} : CaptureOutcome α → String
  | .invalidEnvelope => "invalid-envelope"
  | .digestRefused reason => "digest:" ++ reprStr reason
  | .byteStage reason => match reason with
    | .invalidEnvelope => "unreachable-byte-envelope"
    | .recordRefused rec => match rec with
      | .invalidSyntax => "invalid-syntax"
      | .unsupportedScalar _ => "unsupported-scalar"
      | .invalidRecord _ => "invalid-record"
      | .decoded _ => "unreachable-decoded-refusal"
    | .staleFrame _ => "stale-frame"
    | .prepared _ => "prepared"
#eval outcomeTag (classifyCheckedCapture profile 2621 CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionFrame resolutionCapture)
#eval (prepareResolutionDigest profile 2621 resolutionFrame resolutionCapture).isSome
#eval outcomeTag (classifyCheckedCapture profile 2621 CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionFrame {resolutionCapture with byteLength:=2622})
#eval outcomeTag (classifyCheckedCapture profile 2621 CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionFrame {resolutionCapture with digest:="uncomputed fixture digest"})
#eval outcomeTag (classifyCheckedCapture profile 2621 CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionFrame {resolutionCapture with digestProfile:={profile.ref with digest:="other"}})
#eval outcomeTag (classifyCheckedCapture profile 2620 CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionFrame resolutionCapture)
#eval outcomeTag (classifyCheckedCapture profile 2621 CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution {resolutionFrame with epoch:=43} resolutionCapture)
#eval outcomeTag (classifyCheckedCapture profile 2621 CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionFrame {resolutionCapture with content:=0::resolutionCapture.content.drop 1})
#eval outcomeTag (classifyCheckedCapture profile 2621 CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionFrame {resolutionCapture with content:=resolutionCapture.content.take 2620,byteLength:=2620})
#eval outcomeTag (classifyCheckedCapture profile 2622 CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionFrame {resolutionCapture with content:=resolutionCapture.content++[32],byteLength:=2622})
#eval (prepareResolutionCatalogDigest profile ⟨2621,5242,2⟩ resolutionFrame [resolutionCapture] [resolutionCapture]).isSome
#eval (prepareResolutionCatalogDigest profile ⟨2621,5242,1⟩ resolutionFrame [resolutionCapture] [resolutionCapture]).isSome
#eval (prepareResolutionCatalogDigest profile ⟨2621,5241,2⟩ resolutionFrame [resolutionCapture] [resolutionCapture]).isSome
#eval (prepareResolutionCatalogDigest profile ⟨2621,7863,3⟩ resolutionFrame [resolutionCapture] [resolutionCapture,{resolutionCapture with digestProfile:={profile.ref with digest:="other"}}]).isSome
#eval ((prepareResolutionCatalogDigest profile ⟨2621,5242,2⟩ resolutionFrame [resolutionCapture] [resolutionCapture]).map fun stage => (stage.records.map (fun output=>output.envelope))==[resolutionCapture]).getD false
#eval outcomeTag (classifyCheckedCapture profile 1848 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame roleCapture)
#eval (prepareRoleDigest profile 1848 roleFrame roleCapture).isSome
#eval outcomeTag (classifyCheckedCapture profile 1848 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame {roleCapture with byteLength:=1849})
#eval outcomeTag (classifyCheckedCapture profile 1848 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame {roleCapture with digest:="uncomputed fixture digest"})
#eval outcomeTag (classifyCheckedCapture profile 1848 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame {roleCapture with digestProfile:={profile.ref with digest:="other"}})
#eval outcomeTag (classifyCheckedCapture profile 1847 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame roleCapture)
#eval outcomeTag (classifyCheckedCapture profile 1848 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role {roleFrame with epoch:=43} roleCapture)
#eval outcomeTag (classifyCheckedCapture profile 1848 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame {roleCapture with content:=0::roleCapture.content.drop 1})
#eval outcomeTag (classifyCheckedCapture profile 1848 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame {roleCapture with content:=roleCapture.content.take 1847,byteLength:=1847})
#eval outcomeTag (classifyCheckedCapture profile 1849 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame {roleCapture with content:=roleCapture.content++[32],byteLength:=1849})
#eval (prepareRoleCatalogDigest profile ⟨1848,3696,2⟩ roleFrame [roleCapture] [roleCapture]).isSome
#eval (prepareRoleCatalogDigest profile ⟨1848,3696,1⟩ roleFrame [roleCapture] [roleCapture]).isSome
#eval (prepareRoleCatalogDigest profile ⟨1848,3695,2⟩ roleFrame [roleCapture] [roleCapture]).isSome
#eval (prepareRoleCatalogDigest profile ⟨1848,5544,3⟩ roleFrame [roleCapture] [roleCapture,{roleCapture with digestProfile:={profile.ref with digest:="other"}}]).isSome
#eval ((prepareRoleCatalogDigest profile ⟨1848,3696,2⟩ roleFrame [roleCapture] [roleCapture]).map fun stage => (stage.records.map (fun output=>output.envelope))==[roleCapture]).getD false
#eval outcomeTag (classifyCheckedCapture profile 0 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame emptyCapture)
#eval outcomeTag (classifyCheckedCapture profile 2 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame (CandidateBindingCapture.Envelope.mk [192,128] 2 profile.ref "4df51a863599ce9b7e9cac29d2144a68d0509897aa26626ded17edb0c761bd52"))
#eval outcomeTag (classifyCheckedCapture profile 8 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame (CandidateBindingCapture.Envelope.mk [34,92,117,68,56,48,48,34] 8 profile.ref "e2abb8b90faadf0e98d5e6382fa5f354e814aaa72ce1155de80231de88c7724d"))
#eval outcomeTag (classifyCheckedCapture profile 4 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame (CandidateBindingCapture.Envelope.mk [110,117,108,108] 4 profile.ref "74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b"))
end RelationalSuccessor
