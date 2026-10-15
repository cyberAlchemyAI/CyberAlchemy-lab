import AuthorityOwnership
set_option autoImplicit false
namespace RelationalSuccessor.CandidateEvidenceResources
open CandidateDecimal (Parts fractionDigits fractionLength digitsValue positiveExponent negativeExponent)

structure NumericLimits where
  maxTokenCharacters : Nat
  maxMantissaDigits : Nat
  maxExponentDigits : Nat
  maxExponentMagnitude : Nat
  deriving DecidableEq, Repr
def exponentDigits (parts : Parts) : List Nat := (parts.exponent.map fun exponent=>exponent.digits).getD []
def exponentMagnitude (parts : Parts) : Nat := digitsValue (exponentDigits parts)
def PartsWorkMeaning (limits : NumericLimits) (parts : Parts) : Prop :=
  parts.integer.length+(fractionDigits parts).length≤limits.maxMantissaDigits ∧
    (exponentDigits parts).length≤limits.maxExponentDigits ∧ exponentMagnitude parts≤limits.maxExponentMagnitude
def partsWorkCheck (limits : NumericLimits) (parts : Parts) : Bool :=
  if parts.integer.length+(fractionDigits parts).length≤limits.maxMantissaDigits then
    if (exponentDigits parts).length≤limits.maxExponentDigits then
      decide (exponentMagnitude parts≤limits.maxExponentMagnitude)
    else false
  else false
theorem parts_work_exact (limits : NumericLimits) (parts : Parts) : partsWorkCheck limits parts=true ↔ PartsWorkMeaning limits parts := by
  simp [partsWorkCheck,PartsWorkMeaning]

def TokenWorkMeaning (limits : NumericLimits) (token : String) : Prop :=
  token.toList.length≤limits.maxTokenCharacters ∧
    ∃ parts,CandidateNumberParser.Representation token.toList parts ∧ PartsWorkMeaning limits parts
def tokenWorkCheck (limits : NumericLimits) (token : String) : Bool :=
  if token.toList.length≤limits.maxTokenCharacters then
    match CandidateNumberParser.parseToken token with
    | none=>false
    | some parts=>partsWorkCheck limits parts
  else false
theorem token_work_exact (limits : NumericLimits) (token : String) : tokenWorkCheck limits token=true ↔ TokenWorkMeaning limits token := by
  constructor
  · intro accepted
    unfold tokenWorkCheck at accepted
    split at accepted
    · rename_i length
      cases parsed : CandidateNumberParser.parseToken token with
      | none=>simp only [parsed] at accepted;contradiction
      | some parts=>exact ⟨length,parts,(CandidateNumberParser.parse_token_exact token parts).mp parsed,
          (parts_work_exact limits parts).mp (by simpa only [parsed] using accepted)⟩
    · contradiction
  · rintro ⟨length,parts,represented,bounds⟩
    simp only [tokenWorkCheck,if_pos length,(CandidateNumberParser.parse_token_exact token parts).mpr represented]
    exact (parts_work_exact limits parts).mpr bounds

theorem decimal_power_exponents_bounded (limits : NumericLimits) (parts : Parts) (bounds : PartsWorkMeaning limits parts) :
    fractionLength parts≤limits.maxMantissaDigits ∧ positiveExponent parts≤limits.maxExponentMagnitude ∧
      fractionLength parts+negativeExponent parts≤limits.maxMantissaDigits+limits.maxExponentMagnitude := by
  have fraction : fractionLength parts≤limits.maxMantissaDigits := by
    have h:=bounds.1
    unfold fractionLength at *
    omega
  have positive : positiveExponent parts≤limits.maxExponentMagnitude := by
    have magnitude:=bounds.2.2
    cases ex : parts.exponent with
    | none=>simp [positiveExponent,ex]
    | some exponent=>
      cases sign : exponent.sign <;> simp_all [positiveExponent,exponentMagnitude,exponentDigits]
  have negative : negativeExponent parts≤limits.maxExponentMagnitude := by
    have magnitude:=bounds.2.2
    cases ex : parts.exponent with
    | none=>simp [negativeExponent,ex]
    | some exponent=>
      cases sign : exponent.sign <;> simp_all [negativeExponent,exponentMagnitude,exponentDigits]
  exact ⟨fraction,positive,by omega⟩

def firstUnsupported (limits : NumericLimits) : List String → Option String
  | []=>none
  | token::rest=>if tokenWorkCheck limits token then firstUnsupported limits rest else some token
def TokensWorkMeaning (limits : NumericLimits) (tokens : List String) : Prop := ∀ token∈tokens,TokenWorkMeaning limits token
theorem first_unsupported_none_exact (limits : NumericLimits) (tokens : List String) :
    firstUnsupported limits tokens=none ↔ TokensWorkMeaning limits tokens := by
  induction tokens with
  | nil=>simp [firstUnsupported,TokensWorkMeaning]
  | cons token rest ih=>
    simp only [firstUnsupported,TokensWorkMeaning,List.mem_cons,forall_eq_or_imp]
    cases checked : tokenWorkCheck limits token <;> simp [checked,ih,TokensWorkMeaning,←token_work_exact limits token]

theorem first_unsupported_is_actual_token (limits : NumericLimits) (tokens : List String) (token : String)
    (found : firstUnsupported limits tokens=some token) : token∈tokens ∧ ¬TokenWorkMeaning limits token := by
  induction tokens with
  | nil=>simp [firstUnsupported] at found
  | cons first rest ih=>
    unfold firstUnsupported at found
    split at found
    · have tail:=ih found;exact ⟨by simp [tail.1],tail.2⟩
    · rename_i bad
      cases found
      exact ⟨by simp,by intro meaning;exact bad ((token_work_exact limits token).mpr meaning)⟩
#print axioms parts_work_exact
#print axioms token_work_exact
#print axioms decimal_power_exponents_bounded
#print axioms first_unsupported_none_exact
#print axioms first_unsupported_is_actual_token
end RelationalSuccessor.CandidateEvidenceResources
