import ResourceDiagnostics
import AuthorityControls
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateEvidenceResources.Controls
def numbers : NumericLimits := ⟨256,128,4,1024⟩
def limits : CandidateDigestCapture.Limits := ⟨2,6,3⟩
def capture : CandidateBindingCapture.Envelope := ⟨[1,2],2,CandidateProfileEvidence.Controls.bootstrap.ref,"typed-uncomputed-digest"⟩

theorem decimal_spelling_supported : tokenWorkCheck numbers "42.0"=true := by decide

theorem exponent_spelling_supported : tokenWorkCheck numbers "4.2e1"=true := by decide

theorem negative_zero_supported : tokenWorkCheck numbers "-0"=true := by decide

theorem exponent_uppercase_signed_supported : tokenWorkCheck numbers "4.2E+1"=true := by decide

theorem maximum_exponent_supported : tokenWorkCheck numbers "1e1024"=true := by decide

theorem excessive_exponent_magnitude_refused : tokenWorkCheck numbers "1e1025"=false := by decide

theorem huge_positive_exponent_refused : tokenWorkCheck numbers "1e1000000000"=false := by decide

theorem huge_negative_exponent_refused : tokenWorkCheck numbers "1e-1000000000"=false := by decide

theorem long_zero_exponent_refused : tokenWorkCheck numbers "1e00000"=false := by decide

theorem mantissa_limit_refused : tokenWorkCheck {numbers with maxMantissaDigits:=2} "123"=false := by decide

theorem character_limit_refused : tokenWorkCheck {numbers with maxTokenCharacters:=2} "42.0"=false := by decide

theorem malformed_number_refused : tokenWorkCheck numbers "01"=false := by decide

-- Resource eligibility does not assert integrality or successful typed decoding.
theorem fractional_value_is_resource_eligible : tokenWorkCheck numbers "0.5"=true := by decide

theorem all_three_captures_counted : combinedBudgetCheck limits capture [capture] [capture]=true := by decide

theorem authority_inclusive_count_refused : combinedBudgetCheck {limits with maxCaptures:=2} capture [capture] [capture]=false := by decide

theorem authority_inclusive_bytes_refused : combinedBudgetCheck {limits with totalBytes:=4} capture [capture] [capture]=false := by decide

theorem authority_per_capture_bytes_refused : combinedBudgetCheck {limits with perCaptureBytes:=1} capture [] []=false := by decide

theorem dishonest_byte_count_still_charged : combinedBudgetCheck {limits with totalBytes:=1} {capture with byteLength:=0} [] []=false := by decide

-- Fake typed captures above never establish valid digests, issuance or ownership.
#print axioms decimal_spelling_supported
#print axioms exponent_spelling_supported
#print axioms negative_zero_supported
#print axioms exponent_uppercase_signed_supported
#print axioms maximum_exponent_supported
#print axioms excessive_exponent_magnitude_refused
#print axioms huge_positive_exponent_refused
#print axioms huge_negative_exponent_refused
#print axioms long_zero_exponent_refused
#print axioms mantissa_limit_refused
#print axioms character_limit_refused
#print axioms malformed_number_refused
#print axioms fractional_value_is_resource_eligible
#print axioms all_three_captures_counted
#print axioms authority_inclusive_count_refused
#print axioms authority_inclusive_bytes_refused
#print axioms authority_per_capture_bytes_refused
#print axioms dishonest_byte_count_still_charged
end RelationalSuccessor.CandidateEvidenceResources.Controls
