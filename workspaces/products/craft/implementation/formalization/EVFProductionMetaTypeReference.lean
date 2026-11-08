import DomainSpecMetaTypeKernel

namespace DomainSpec.EVFProductionMetaTypeReference

open DomainSpec.MetaTypeKernel

def referenceTheory : Theory Nat where
  staticConforms := fun _ => true
  graphDigest := fun _ => "evf-production-reference-graph"
  sourceIdentity := fun _ => {
    projectId := "evf-production-reference"
    sourceManifestSha256 := "reference-manifest"
    sourceBytesSha256 := "reference-source"
  }

def referenceCertificate : GraphCertificate where
  graphSha256 := "evf-production-reference-graph"
  sourceIdentity := {
    projectId := "evf-production-reference"
    sourceManifestSha256 := "reference-manifest"
    sourceBytesSha256 := "reference-source"
  }

theorem certificate_sound_for_reference :
    GraphDigestBound referenceTheory 0 referenceCertificate ∧
    SourceIdentityBound referenceTheory 0 referenceCertificate ∧
    StaticConforms referenceTheory 0 := by
  apply certificate_check_sound
  decide

end DomainSpec.EVFProductionMetaTypeReference
