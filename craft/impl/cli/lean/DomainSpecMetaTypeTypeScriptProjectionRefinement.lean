import DomainSpecMetaTypeCompilerRefinement

namespace DomainSpec.MetaTypeTypeScriptProjectionRefinement

open DomainSpec.MetaTypeKernel
open DomainSpec.MetaTypeCompilerRefinement

structure TypeScriptProjectionPayload (Graph : Type) where
  graph : Graph
  projectId : String
  sourceManifestSha256 : String
  sourceBytesSha256 : String
  graphSha256 : String
  deriving Repr

def lowerTypeScriptProjection {Graph : Type} (payload : TypeScriptProjectionPayload Graph) :
    CheckedProjectionInput Graph :=
  {
    graph := payload.graph
    certificate := {
      graphSha256 := payload.graphSha256
      sourceIdentity := {
        projectId := payload.projectId
        sourceManifestSha256 := payload.sourceManifestSha256
        sourceBytesSha256 := payload.sourceBytesSha256
      }
    }
  }

theorem lowerTypeScriptProjection_refines_checked_input {Graph : Type}
    (payload : TypeScriptProjectionPayload Graph) :
    (lowerTypeScriptProjection payload).graph = payload.graph ∧
    (lowerTypeScriptProjection payload).certificate.graphSha256 = payload.graphSha256 ∧
    (lowerTypeScriptProjection payload).certificate.sourceIdentity.projectId = payload.projectId ∧
    (lowerTypeScriptProjection payload).certificate.sourceIdentity.sourceManifestSha256 = payload.sourceManifestSha256 ∧
    (lowerTypeScriptProjection payload).certificate.sourceIdentity.sourceBytesSha256 = payload.sourceBytesSha256 := by
  exact ⟨rfl, rfl, rfl, rfl, rfl⟩

end DomainSpec.MetaTypeTypeScriptProjectionRefinement
