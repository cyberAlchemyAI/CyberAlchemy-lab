namespace DomainSpec.MetaTypeKernel

structure SourceIdentity where
  projectId : String
  sourceManifestSha256 : String
  sourceBytesSha256 : String
  deriving DecidableEq, BEq, Repr

structure GraphCertificate where
  graphSha256 : String
  sourceIdentity : SourceIdentity
  deriving DecidableEq, BEq, Repr

structure Theory (Graph : Type) where
  staticConforms : Graph → Bool
  graphDigest : Graph → String
  sourceIdentity : Graph → SourceIdentity

def GraphDigestBound {Graph : Type} (theory : Theory Graph) (graph : Graph)
    (certificate : GraphCertificate) : Prop :=
  certificate.graphSha256 = theory.graphDigest graph

def SourceIdentityBound {Graph : Type} (theory : Theory Graph) (graph : Graph)
    (certificate : GraphCertificate) : Prop :=
  certificate.sourceIdentity = theory.sourceIdentity graph

def StaticConforms {Graph : Type} (theory : Theory Graph) (graph : Graph) : Prop :=
  theory.staticConforms graph = true

def checkCertificate {Graph : Type} (theory : Theory Graph) (graph : Graph)
    (certificate : GraphCertificate) : Bool :=
  decide (certificate.graphSha256 = theory.graphDigest graph) &&
  decide (certificate.sourceIdentity = theory.sourceIdentity graph) &&
  theory.staticConforms graph

theorem certificate_check_sound {Graph : Type} (theory : Theory Graph) (graph : Graph)
    (certificate : GraphCertificate)
    (checked : checkCertificate theory graph certificate = true) :
    GraphDigestBound theory graph certificate ∧
    SourceIdentityBound theory graph certificate ∧
    StaticConforms theory graph := by
  simp [checkCertificate] at checked
  exact ⟨checked.1.1, checked.1.2, checked.2⟩

end DomainSpec.MetaTypeKernel
