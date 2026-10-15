import MetadataControls2

set_option autoImplicit false
namespace RelationalSuccessor.CandidateCapturedMetadata.RuntimeProbe
open RelationalSuccessor.CandidateCapturedMetadata
open RelationalSuccessor.CandidateCapturedMetadata.Examples

-- Executable probes only. These do not serve as proof declarations.
#eval contextCheck context
#eval (resolve context frame sourceRef).isSome
#eval (decodeSource context frame sourceRef originalBytes ast).isSome
#eval (decodeResolution context payloads frame sourceRef originalBytes ast).isSome
#eval (decodeResolution Controls.missing_root payloads frame sourceRef originalBytes ast).isNone
#eval (decodeSource context frame sourceRef [0] ast).isNone
#eval (decodeSource context frame sourceRef originalBytes
  (RelationalSuccessor.CandidateJsonSource.encodeRecord MoreControls.renamedOwnerBody)).isNone
#eval (resolve MoreControls.receiptConflict frame sourceRef).isNone
#eval (resolve MoreControls.byteConflict frame sourceRef).isNone
end RelationalSuccessor.CandidateCapturedMetadata.RuntimeProbe
