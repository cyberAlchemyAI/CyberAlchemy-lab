import DecimalGrammar
set_option autoImplicit false
namespace RelationalSuccessor.CandidateDecimal.Controls
open RelationalSuccessor.CandidateDecimal

def ordinary_integerParts : Parts := ⟨false,[4,2],none,none⟩
theorem ordinary_integer : decodeWitness (.number "42") ordinary_integerParts = some 42 := by decide

def integral_decimalParts : Parts := ⟨false,[4,2],(some [0]),none⟩
theorem integral_decimal : decodeWitness (.number "42.0") integral_decimalParts = some 42 := by decide

def scaled_positive_exponentParts : Parts := ⟨false,[4],(some [2]),(some ⟨false,.unsigned,[1]⟩)⟩
theorem scaled_positive_exponent : decodeWitness (.number "4.2e1") scaled_positive_exponentParts = some 42 := by decide

def scaled_negative_exponentParts : Parts := ⟨false,[4,2,0],none,(some ⟨false,.minus,[1]⟩)⟩
theorem scaled_negative_exponent : decodeWitness (.number "420e-1") scaled_negative_exponentParts = some 42 := by decide

def zero_integerParts : Parts := ⟨false,[0],none,none⟩
theorem zero_integer : decodeWitness (.number "0") zero_integerParts = some 0 := by decide

def negative_zeroParts : Parts := ⟨true,[0],none,none⟩
theorem negative_zero : decodeWitness (.number "-0") negative_zeroParts = some 0 := by decide

def negative_decimal_zeroParts : Parts := ⟨true,[0],(some [0]),none⟩
theorem negative_decimal_zero : decodeWitness (.number "-0.0") negative_decimal_zeroParts = some 0 := by decide

def signed_upper_exponentParts : Parts := ⟨false,[4,2],none,(some ⟨true,.plus,[0,0,0]⟩)⟩
theorem signed_upper_exponent : decodeWitness (.number "42E+000") signed_upper_exponentParts = some 42 := by decide

def unsigned_upper_exponentParts : Parts := ⟨false,[4],(some [2]),(some ⟨true,.unsigned,[1]⟩)⟩
theorem unsigned_upper_exponent : decodeWitness (.number "4.2E1") unsigned_upper_exponentParts = some 42 := by decide

def negative_exponent_zeroParts : Parts := ⟨false,[0],none,(some ⟨true,.minus,[0,0,0,0,4]⟩)⟩
theorem negative_exponent_zero : decodeWitness (.number "0E-00004") negative_exponent_zeroParts = some 0 := by decide

def fraction_is_not_epochParts : Parts := ⟨false,[0],(some [5]),none⟩
theorem fraction_is_not_epoch : decodeWitness (.number "0.5") fraction_is_not_epochParts = none := by decide

def negative_nonzeroParts : Parts := ⟨true,[4,2],none,none⟩
theorem negative_nonzero : decodeWitness (.number "-42") negative_nonzeroParts = none := by decide

def negative_exponent_fractionParts : Parts := ⟨false,[4,2],none,(some ⟨false,.minus,[1]⟩)⟩
theorem negative_exponent_fraction : decodeWitness (.number "42e-1") negative_exponent_fractionParts = none := by decide

def fraction_and_exponent_cancelParts : Parts := ⟨false,[0],(some [4,2]),(some ⟨false,.unsigned,[2]⟩)⟩
theorem fraction_and_exponent_cancel : decodeWitness (.number "0.42e2") fraction_and_exponent_cancelParts = some 42 := by decide

def negative_fractionParts : Parts := ⟨true,[0],(some [5]),none⟩
theorem negative_fraction : decodeWitness (.number "-0.5") negative_fractionParts = none := by decide

def negative_scaled_integerParts : Parts := ⟨true,[4],(some [2]),(some ⟨false,.unsigned,[1]⟩)⟩
theorem negative_scaled_integer : decodeWitness (.number "-4.2e1") negative_scaled_integerParts = none := by decide

def integral_trailing_zeroesParts : Parts := ⟨false,[4,2],(some [0,0,0]),none⟩
theorem integral_trailing_zeroes : decodeWitness (.number "42.000") integral_trailing_zeroesParts = some 42 := by decide

def tiny_nonzero_fractionParts : Parts := ⟨false,[4,2],(some [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]),none⟩
theorem tiny_nonzero_fraction : decodeWitness (.number "42.0000000000000001") tiny_nonzero_fractionParts = none := by decide

def beyond_float_exact_integerParts : Parts := ⟨false,[9,0,0,7,1,9,9,2,5,4,7,4,0,9,9,3],none,none⟩
theorem beyond_float_exact_integer : decodeWitness (.number "9007199254740993") beyond_float_exact_integerParts = some 9007199254740993 := by decide

def large_exact_powerParts : Parts := ⟨false,[1],none,(some ⟨false,.unsigned,[2,0]⟩)⟩
theorem large_exact_power : decodeWitness (.number "1e20") large_exact_powerParts = some 100000000000000000000 := by decide

def signed_positive_exponentParts : Parts := ⟨false,[2],none,(some ⟨true,.plus,[3]⟩)⟩
theorem signed_positive_exponent : decodeWitness (.number "2E+3") signed_positive_exponentParts = some 2000 := by decide

def minus_zero_exponentParts : Parts := ⟨false,[4,2],none,(some ⟨false,.minus,[0]⟩)⟩
theorem minus_zero_exponent : decodeWitness (.number "42e-0") minus_zero_exponentParts = some 42 := by decide

def fraction_at_zero_epochParts : Parts := ⟨false,[0],(some [0,0,0]),(some ⟨false,.minus,[1,2]⟩)⟩
theorem fraction_at_zero_epoch : decodeWitness (.number "0.000e-12") fraction_at_zero_epochParts = some 0 := by decide

def huge_positive_exponent_zeroParts : Parts := ⟨false,[0],none,(some ⟨false,.unsigned,[1,0,0,0,0,0,0,0,0,0,0,0,0]⟩)⟩
theorem huge_positive_exponent_zero : decodeWitness (.number "0e1000000000000") huge_positive_exponent_zeroParts = some 0 := by decide

def huge_negative_exponent_zeroParts : Parts := ⟨true,[0],none,(some ⟨false,.minus,[1,0,0,0,0,0,0,0,0,0,0,0,0]⟩)⟩
theorem huge_negative_exponent_zero : decodeWitness (.number "-0e-1000000000000") huge_negative_exponent_zeroParts = some 0 := by decide

def empty_integerParts : Parts := ⟨false,[],none,none⟩
theorem empty_integer : decodeWitness (.number "") empty_integerParts = none := by decide

def leading_zero_integerParts : Parts := ⟨false,[0,1],none,none⟩
theorem leading_zero_integer : decodeWitness (.number "01") leading_zero_integerParts = none := by decide

def empty_fractionParts : Parts := ⟨false,[4,2],some [],none⟩
theorem empty_fraction : decodeWitness (.number "42.") empty_fractionParts = none := by decide

def empty_exponentParts : Parts := ⟨false,[4,2],none,some ⟨false,.unsigned,[]⟩⟩
theorem empty_exponent : decodeWitness (.number "42e") empty_exponentParts = none := by decide

def empty_plus_exponentParts : Parts := ⟨false,[4,2],none,some ⟨false,.plus,[]⟩⟩
theorem empty_plus_exponent : decodeWitness (.number "42e+") empty_plus_exponentParts = none := by decide

def empty_minus_exponentParts : Parts := ⟨false,[4,2],none,some ⟨false,.minus,[]⟩⟩
theorem empty_minus_exponent : decodeWitness (.number "42e-") empty_minus_exponentParts = none := by decide

def out_of_range_digitParts : Parts := ⟨false,[10],none,none⟩
theorem out_of_range_digit : decodeWitness (.number "?") out_of_range_digitParts = none := by decide

def unicode_digitParts : Parts := ordinary_integerParts
theorem unicode_digit : decodeWitness (.number "\u0664\u0662") unicode_digitParts = none := by decide

def leading_plusParts : Parts := ordinary_integerParts
theorem leading_plus : decodeWitness (.number "+42") leading_plusParts = none := by decide

def leading_spaceParts : Parts := ordinary_integerParts
theorem leading_space : decodeWitness (.number " 42") leading_spaceParts = none := by decide

def trailing_spaceParts : Parts := ordinary_integerParts
theorem trailing_space : decodeWitness (.number "42 ") trailing_spaceParts = none := by decide

def not_a_numberParts : Parts := ordinary_integerParts
theorem not_a_number : decodeWitness (.number "NaN") not_a_numberParts = none := by decide

def infinityParts : Parts := ordinary_integerParts
theorem infinity : decodeWitness (.number "Infinity") infinityParts = none := by decide

def different_numberParts : Parts := ordinary_integerParts
theorem different_number : decodeWitness (.number "43") different_numberParts = none := by decide

theorem string_is_not_number : decodeWitness (.string "42") ordinary_integerParts = none := by decide

theorem boolean_is_not_number : decodeWitness (.boolean true) ordinary_integerParts = none := by decide

theorem null_is_not_number : decodeWitness .null ordinary_integerParts = none := by decide

theorem equivalent_spellings_same_epoch : decodeWitness (.number "42") ordinary_integerParts = decodeWitness (.number "4.2e1") scaled_positive_exponentParts := by decide

theorem ordinary_independent_value : EpochMeaning ordinary_integerParts 42 := (decode_parts_exact ordinary_integerParts 42).mp (by decide)

theorem scaled_independent_value : EpochMeaning scaled_positive_exponentParts 42 := (decode_parts_exact scaled_positive_exponentParts 42).mp (by decide)

theorem negative_zero_independent_value : EpochMeaning negative_zeroParts 0 := (decode_parts_exact negative_zeroParts 0).mp (by decide)

#print axioms ordinary_integer
#print axioms integral_decimal
#print axioms scaled_positive_exponent
#print axioms scaled_negative_exponent
#print axioms zero_integer
#print axioms negative_zero
#print axioms negative_decimal_zero
#print axioms signed_upper_exponent
#print axioms unsigned_upper_exponent
#print axioms negative_exponent_zero
#print axioms fraction_is_not_epoch
#print axioms negative_nonzero
#print axioms negative_exponent_fraction
#print axioms fraction_and_exponent_cancel
#print axioms negative_fraction
#print axioms negative_scaled_integer
#print axioms integral_trailing_zeroes
#print axioms tiny_nonzero_fraction
#print axioms beyond_float_exact_integer
#print axioms large_exact_power
#print axioms signed_positive_exponent
#print axioms minus_zero_exponent
#print axioms fraction_at_zero_epoch
#print axioms huge_positive_exponent_zero
#print axioms huge_negative_exponent_zero
#print axioms empty_integer
#print axioms leading_zero_integer
#print axioms empty_fraction
#print axioms empty_exponent
#print axioms empty_plus_exponent
#print axioms empty_minus_exponent
#print axioms out_of_range_digit
#print axioms unicode_digit
#print axioms leading_plus
#print axioms leading_space
#print axioms trailing_space
#print axioms not_a_number
#print axioms infinity
#print axioms different_number
#print axioms string_is_not_number
#print axioms boolean_is_not_number
#print axioms null_is_not_number
#print axioms equivalent_spellings_same_epoch
#print axioms ordinary_independent_value
#print axioms scaled_independent_value
#print axioms negative_zero_independent_value
end RelationalSuccessor.CandidateDecimal.Controls
