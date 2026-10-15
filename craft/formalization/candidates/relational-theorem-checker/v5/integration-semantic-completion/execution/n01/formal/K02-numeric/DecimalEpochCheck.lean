import DecimalMeaning

set_option autoImplicit false
namespace RelationalSuccessor.CandidateDecimal

def decodeParts (parts : Parts) : Option Nat :=
  if validCheck parts then
    if mantissa parts = 0 then some 0
    else if parts.negative then none
    else if numerator parts % denominator parts = 0 then some (numerator parts / denominator parts) else none
  else none

theorem decode_parts_exact (parts : Parts) (epoch : Nat) :
    decodeParts parts = some epoch ↔ EpochMeaning parts epoch := by
  constructor
  · intro accepted
    unfold decodeParts at accepted
    split at accepted
    · rename_i checked
      split at accepted
      · rename_i zero
        have same : 0 = epoch := Option.some.inj accepted
        have numZero := (numerator_zero_iff parts).mpr zero
        exact ⟨(valid_check_exact parts).mp checked,Or.inr numZero,by simp [numZero,← same]⟩
      · rename_i nonzero
        split at accepted
        · cases accepted
        · rename_i notNegative
          have sign : parts.negative = false := by cases h : parts.negative <;> simp_all
          split at accepted
          · rename_i divisible
            have same : numerator parts / denominator parts = epoch := Option.some.inj accepted
            exact ⟨(valid_check_exact parts).mp checked,Or.inl sign,
              (Nat.div_mul_cancel (Nat.dvd_of_mod_eq_zero divisible)).symm.trans (by rw [same])⟩
          · cases accepted
    · cases accepted
  · intro meaning
    have checked := (valid_check_exact parts).mpr meaning.valid
    by_cases zero : mantissa parts = 0
    · have numZero := (numerator_zero_iff parts).mpr zero
      have valueZero : epoch * denominator parts = 0 := meaning.value.symm.trans numZero
      have epochZero : epoch = 0 := by
        rcases Nat.mul_eq_zero.mp valueZero with h | h
        · exact h
        · exact False.elim ((Nat.ne_of_gt (denominator_positive parts)) h)
      simp [decodeParts,checked,zero,epochZero]
    · have sign : parts.negative = false := by
        rcases meaning.sign with sign | numZero
        · exact sign
        · exact False.elim (zero ((numerator_zero_iff parts).mp numZero))
      have divisible : numerator parts % denominator parts = 0 := by
        rw [meaning.value,Nat.mul_comm]; exact Nat.mul_mod_right _ _
      have quotient : numerator parts / denominator parts = epoch := by
        rw [meaning.value]; exact Nat.mul_div_cancel _ (denominator_positive parts)
      simp [decodeParts,checked,zero,sign,divisible,quotient]

-- This AST entry point checks an explicit representation witness against the
-- complete token. It is not a total token parser or an authenticated provider.
structure AstMeaning (value : Ast) (parts : Parts) (epoch : Nat) : Prop where
  spelling : value = .number (spelling parts)
  value : EpochMeaning parts epoch

def decodeWitness (value : Ast) (parts : Parts) : Option Nat :=
  match value with
  | .number token => if token = spelling parts then decodeParts parts else none
  | _ => none

theorem decode_witness_exact (value : Ast) (parts : Parts) (epoch : Nat) :
    decodeWitness value parts = some epoch ↔ AstMeaning value parts epoch := by
  cases value with
  | number token =>
    constructor
    · intro accepted
      change (if token = spelling parts then decodeParts parts else none) = some epoch at accepted
      split at accepted
      · rename_i exactToken
        exact ⟨by rw [exactToken],(decode_parts_exact parts epoch).mp accepted⟩
      · cases accepted
    · intro meaning
      have same : token = spelling parts := by cases meaning.spelling; rfl
      simp [decodeWitness,same,(decode_parts_exact parts epoch).mpr meaning.value]
  | null => simp [decodeWitness]; intro h; cases h.spelling
  | boolean b => simp [decodeWitness]; intro h; cases h.spelling
  | string s => simp [decodeWitness]; intro h; cases h.spelling
  | array vs => simp [decodeWitness]; intro h; cases h.spelling
  | object es => simp [decodeWitness]; intro h; cases h.spelling

theorem invalid_parts_refuse (parts : Parts) (invalid : ¬ Valid parts) : decodeParts parts = none := by
  cases found : decodeParts parts with
  | none => rfl
  | some epoch => exact False.elim (invalid ((decode_parts_exact parts epoch).mp found).valid)

theorem nonintegral_parts_refuse (parts : Parts)
    (nonintegral : ∀ epoch, numerator parts ≠ epoch * denominator parts) : decodeParts parts = none := by
  cases found : decodeParts parts with
  | none => rfl
  | some epoch => exact False.elim (nonintegral epoch ((decode_parts_exact parts epoch).mp found).value)

theorem negative_nonzero_refuses (parts : Parts) (negative : parts.negative = true)
    (nonzero : numerator parts ≠ 0) : decodeParts parts = none := by
  cases found : decodeParts parts with
  | none => rfl
  | some epoch =>
    rcases ((decode_parts_exact parts epoch).mp found).sign with sign | zero
    · rw [negative] at sign; cases sign
    · exact False.elim (nonzero zero)

theorem token_substitution_refuses (token : String) (parts : Parts) (wrong : token ≠ spelling parts) :
    decodeWitness (.number token) parts = none := by simp [decodeWitness,wrong]

theorem accepted_witness_retains_exact_value (value : Ast) (parts : Parts) (epoch : Nat)
    (accepted : decodeWitness value parts = some epoch) : numerator parts = epoch * denominator parts :=
  ((decode_witness_exact value parts epoch).mp accepted).value.value

theorem negative_zero_is_allowed (parts : Parts) (valid : Valid parts) (zero : numerator parts = 0) :
    decodeParts parts = some 0 := by
  apply (decode_parts_exact parts 0).mpr
  exact ⟨valid,Or.inr zero,by simp [zero]⟩


theorem zero_mantissa_short_circuit (parts : Parts) (valid : Valid parts) (zero : mantissa parts = 0) :
    decodeParts parts = some 0 := by
  simp [decodeParts,(valid_check_exact parts).mpr valid,zero]

#print axioms decode_parts_exact
#print axioms decode_witness_exact
#print axioms invalid_parts_refuse
#print axioms nonintegral_parts_refuse
#print axioms negative_nonzero_refuses
#print axioms token_substitution_refuses
#print axioms accepted_witness_retains_exact_value
#print axioms negative_zero_is_allowed
#print axioms zero_mantissa_short_circuit
end RelationalSuccessor.CandidateDecimal
