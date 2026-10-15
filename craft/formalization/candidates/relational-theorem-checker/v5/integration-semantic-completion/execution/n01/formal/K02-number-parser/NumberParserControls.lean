import NumberEpochAst
set_option autoImplicit false
namespace RelationalSuccessor.CandidateNumberParser.Controls
open RelationalSuccessor.CandidateNumberParser
open RelationalSuccessor.CandidateDecimal

theorem ordinary_integer : decodeEpochAst (.number "42") = some 42 := by decide

theorem integral_decimal : decodeEpochAst (.number "42.0") = some 42 := by decide

theorem scaled_positive_exponent : decodeEpochAst (.number "4.2e1") = some 42 := by decide

theorem scaled_negative_exponent : decodeEpochAst (.number "420e-1") = some 42 := by decide

theorem zero_integer : decodeEpochAst (.number "0") = some 0 := by decide

theorem negative_zero : decodeEpochAst (.number "-0") = some 0 := by decide

theorem negative_decimal_zero : decodeEpochAst (.number "-0.0") = some 0 := by decide

theorem signed_upper_exponent : decodeEpochAst (.number "42E+000") = some 42 := by decide

theorem unsigned_upper_exponent : decodeEpochAst (.number "4.2E1") = some 42 := by decide

theorem negative_exponent_zero : decodeEpochAst (.number "0E-00004") = some 0 := by decide

theorem fraction_is_not_epoch : decodeEpochAst (.number "0.5") = none := by decide

theorem negative_nonzero : decodeEpochAst (.number "-42") = none := by decide

theorem negative_exponent_fraction : decodeEpochAst (.number "42e-1") = none := by decide

theorem fraction_and_exponent_cancel : decodeEpochAst (.number "0.42e2") = some 42 := by decide

theorem negative_fraction : decodeEpochAst (.number "-0.5") = none := by decide

theorem negative_scaled_integer : decodeEpochAst (.number "-4.2e1") = none := by decide

theorem integral_trailing_zeroes : decodeEpochAst (.number "42.000") = some 42 := by decide

theorem tiny_nonzero_fraction : decodeEpochAst (.number "42.0000000000000001") = none := by decide

theorem beyond_float_exact_integer : decodeEpochAst (.number "9007199254740993") = some 9007199254740993 := by decide

theorem large_exact_power : decodeEpochAst (.number "1e20") = some 100000000000000000000 := by decide

theorem signed_positive_exponent : decodeEpochAst (.number "2E+3") = some 2000 := by decide

theorem minus_zero_exponent : decodeEpochAst (.number "42e-0") = some 42 := by decide

theorem fraction_at_zero_epoch : decodeEpochAst (.number "0.000e-12") = some 0 := by decide

theorem huge_positive_exponent_zero : decodeEpochAst (.number "0e1000000000000") = some 0 := by decide

theorem huge_negative_exponent_zero : decodeEpochAst (.number "-0e-1000000000000") = some 0 := by decide

theorem empty_integer : decodeEpochAst (.number "") = none := by decide

theorem leading_zero_integer : decodeEpochAst (.number "01") = none := by decide

theorem empty_fraction : decodeEpochAst (.number "42.") = none := by decide

theorem empty_exponent : decodeEpochAst (.number "42e") = none := by decide

theorem empty_plus_exponent : decodeEpochAst (.number "42e+") = none := by decide

theorem empty_minus_exponent : decodeEpochAst (.number "42e-") = none := by decide

theorem out_of_range_digit : decodeEpochAst (.number "?") = none := by decide

theorem unicode_digit : decodeEpochAst (.number "٤٢") = none := by decide

theorem leading_plus : decodeEpochAst (.number "+42") = none := by decide

theorem leading_space : decodeEpochAst (.number " 42") = none := by decide

theorem trailing_space : decodeEpochAst (.number "42 ") = none := by decide

theorem not_a_number : decodeEpochAst (.number "NaN") = none := by decide

theorem infinity : decodeEpochAst (.number "Infinity") = none := by decide

theorem different_number : decodeEpochAst (.number "43") = some 43 := by decide

theorem ignored_suffix : decodeEpochAst (.number "42garbage") = none := by decide

theorem second_exponent : decodeEpochAst (.number "42e1e1") = none := by decide

theorem second_fraction : decodeEpochAst (.number "42.0.0") = none := by decide

theorem leading_line_break : decodeEpochAst (.number "\n42") = none := by decide

theorem negative_leading_zero : decodeEpochAst (.number "-01") = none := by decide

theorem fraction_without_integer : decodeEpochAst (.number ".42") = none := by decide

theorem large_exact_decimal : decodeEpochAst (.number "9007199254740993.0") = some 9007199254740993 := by decide

theorem string_is_not_number : decodeEpochAst (.string "42") = none := by decide

theorem boolean_is_not_number : decodeEpochAst (.boolean true) = none := by decide

theorem null_is_not_number : decodeEpochAst .null = none := by decide

theorem equivalent_spellings_same_epoch : decodeEpochAst (.number "42") = decodeEpochAst (.number "4.2e1") := by decide

theorem fraction_has_valid_syntax : ∃ parts, parseToken "0.5" = some parts := ⟨⟨false,[0],some [5],none⟩,by decide⟩

theorem raw_independent_epoch_meaning : TokenEpochMeaning "4.2e1" 42 := (token_epoch_exact "4.2e1" 42).mp scaled_positive_exponent

theorem adapter_uses_total_number_parser : epochAdapter.decode (.number "42.0") = some 42 := by decide

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
#print axioms ignored_suffix
#print axioms second_exponent
#print axioms second_fraction
#print axioms leading_line_break
#print axioms negative_leading_zero
#print axioms fraction_without_integer
#print axioms large_exact_decimal
#print axioms string_is_not_number
#print axioms boolean_is_not_number
#print axioms null_is_not_number
#print axioms equivalent_spellings_same_epoch
#print axioms fraction_has_valid_syntax
#print axioms raw_independent_epoch_meaning
#print axioms adapter_uses_total_number_parser
end RelationalSuccessor.CandidateNumberParser.Controls
