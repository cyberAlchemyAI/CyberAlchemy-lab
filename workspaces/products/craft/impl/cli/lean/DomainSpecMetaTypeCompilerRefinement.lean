import DomainSpecMetaTypeKernel

namespace DomainSpec.MetaTypeCompilerRefinement

open DomainSpec.MetaTypeKernel

structure CheckedProjectionInput (Graph : Type) where
  graph : Graph
  certificate : GraphCertificate
  deriving Repr

def compileChecked {Graph : Type} (theory : Theory Graph)
    (input : CheckedProjectionInput Graph) : Option GraphCertificate :=
  if checkCertificate theory input.graph input.certificate then
    some input.certificate
  else
    none

theorem compiler_always_emits_checking_certificate {Graph : Type} (theory : Theory Graph)
    (input : CheckedProjectionInput Graph) (certificate : GraphCertificate)
    (compiled : compileChecked theory input = some certificate) :
    certificate = input.certificate ∧
    checkCertificate theory input.graph certificate = true := by
  unfold compileChecked at compiled
  split at compiled
  next checked =>
    cases compiled
    exact ⟨rfl, checked⟩
  next rejected =>
    contradiction

theorem compile_success_implies_static_conformance {Graph : Type} (theory : Theory Graph)
    (input : CheckedProjectionInput Graph) (certificate : GraphCertificate)
    (compiled : compileChecked theory input = some certificate) :
    GraphDigestBound theory input.graph certificate ∧
    SourceIdentityBound theory input.graph certificate ∧
    StaticConforms theory input.graph := by
  obtain ⟨_, checked⟩ := compiler_always_emits_checking_certificate theory input certificate compiled
  exact certificate_check_sound theory input.graph certificate checked

end DomainSpec.MetaTypeCompilerRefinement
