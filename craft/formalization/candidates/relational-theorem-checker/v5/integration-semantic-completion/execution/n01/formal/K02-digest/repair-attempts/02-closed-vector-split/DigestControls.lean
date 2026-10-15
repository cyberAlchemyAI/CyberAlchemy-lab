import DigestProfile
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateDigest.Controls
open CandidateDigest
-- Synthetic reference only; these fields carry no authentic owner/review evidence.
def fixtureRef : RevisionRef := ⟨⟨"fixture-owner","digest-profile","candidate-1"⟩,"synthetic-uncomputed-profile-digest"⟩
def fixtureProfile : Profile := ⟨fixtureRef,"sha256-fips1804-2015","lowerhex64"⟩
def emptyDigest : String := "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
def abcDigest : String := "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
theorem empty_vector : digestBytes []=some emptyDigest := by decide
theorem abc_vector : digestBytes [97,98,99]=some abcDigest := by decide
theorem empty_vector_meaning : DigestMeaning [] emptyDigest := (digest_exact [] emptyDigest).mp empty_vector
theorem abc_vector_meaning : DigestMeaning [97,98,99] abcDigest := (digest_exact _ _).mp abc_vector
-- The profile is not authenticated by these examples.
theorem changed_owner_refused :
    classifyDigest fixtureProfile {fixtureRef with key:={fixtureRef.key with owner:="other"}} [] emptyDigest 0=.unsupportedProfile := by decide
theorem changed_artifact_refused :
    classifyDigest fixtureProfile {fixtureRef with key:={fixtureRef.key with artifact:="other"}} [] emptyDigest 0=.unsupportedProfile := by decide
theorem changed_revision_refused :
    classifyDigest fixtureProfile {fixtureRef with key:={fixtureRef.key with revision:="other"}} [] emptyDigest 0=.unsupportedProfile := by decide
theorem changed_profile_digest_refused :
    classifyDigest fixtureProfile {fixtureRef with digest:="other"} [] emptyDigest 0=.unsupportedProfile := by decide
theorem unsupported_algorithm_refused :
    classifyDigest {fixtureProfile with algorithm:="sha1"} fixtureRef [] emptyDigest 0=.unsupportedProfile := by decide
theorem unsupported_encoding_refused :
    classifyDigest {fixtureProfile with encoding:="upperhex64"} fixtureRef [] emptyDigest 0=.unsupportedProfile := by decide
theorem short_digest_refused :
    classifyDigest fixtureProfile fixtureRef [] "abc" 0=.malformedDigest := by decide
theorem uppercase_digest_refused :
    classifyDigest fixtureProfile fixtureRef [] "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855" 0=.malformedDigest := by decide
theorem excessive_budget_refusal :
    classifyDigest fixtureProfile fixtureRef [97,98,99] abcDigest 2=.byteBudgetExceeded := by decide
end RelationalSuccessor.CandidateDigest.Controls
