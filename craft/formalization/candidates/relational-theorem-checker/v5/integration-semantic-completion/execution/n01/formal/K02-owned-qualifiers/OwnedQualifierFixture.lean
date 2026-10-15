import OwnedIntentQualifierCheck
import FramedJoinFixture

set_option autoImplicit false
namespace RelationalSuccessor.CandidateOwnedIntentQualifiers.Fixture
open RelationalSuccessor
open RelationalSuccessor.CandidateOwnedIntentQualifiers
abbrev Eframe := CandidateCapturedMetadata.Examples.frame
abbrev rev := CandidateCapturedMetadata.Examples.revision
abbrev Eprojected := CandidateIntentSourceContract.Fixture.projected
abbrev Erole := CandidateIntentSourceContract.Fixture.role
abbrev Eclaim := CandidateIntentSourceContract.Fixture.claim
abbrev Eworld := CandidateIntentSourceContract.Fixture.framed

def resolutionEntry : CandidateOwnedBindings.Entry Resolution :=
  ⟨rev "binding:resolution:1", resolutionKind, ⟨"resolution:original", Eprojected.resolution, Eframe⟩,
    [1, 2], rev "review:resolution:1"⟩
def roleEntry : CandidateOwnedBindings.Entry Role :=
  ⟨rev "binding:role:1", roleKind, ⟨Erole.code, Erole, Eframe⟩, [3, 4], rev "review:role:1"⟩
def context : Context :=
  ⟨⟨Eframe, [resolutionEntry], [resolutionEntry]⟩, ⟨Eframe, [roleEntry], [roleEntry]⟩⟩
def raw : Raw := ⟨"resolution:original", Erole.code⟩

theorem original_qualifiers_accept : check context Eworld Eprojected raw Eclaim = true := by decide

def aliasEntry : CandidateOwnedBindings.Entry Resolution :=
  { resolutionEntry with ref := rev "binding:resolution:alias", body := { resolutionEntry.body with token := "resolution:alias" } }
def aliases : Context :=
  { context with resolutions := ⟨Eframe, [resolutionEntry, aliasEntry], [resolutionEntry, aliasEntry]⟩ }
theorem consistent_alias_accepts :
    check aliases Eworld Eprojected ⟨"resolution:alias", Erole.code⟩ Eclaim = true := by decide

def secondApproval : CandidateOwnedBindings.Entry Resolution :=
  { resolutionEntry with ref := rev "binding:resolution:second-approval", content := [5], ownerReview := rev "review:resolution:second" }
def repeatedApproval : Context :=
  { context with resolutions := ⟨Eframe, [resolutionEntry, secondApproval], [resolutionEntry, secondApproval]⟩ }
theorem distinct_consistent_approvals_accept : check repeatedApproval Eworld Eprojected raw Eclaim = true := by decide

def duplicateEntry : Context :=
  { context with resolutions := ⟨Eframe, [resolutionEntry, resolutionEntry], [resolutionEntry]⟩ }
theorem identical_retry_accepts : check duplicateEntry Eworld Eprojected raw Eclaim = true := by decide

#print axioms original_qualifiers_accept
#print axioms consistent_alias_accepts
#print axioms distinct_consistent_approvals_accept
#print axioms identical_retry_accepts
end RelationalSuccessor.CandidateOwnedIntentQualifiers.Fixture
