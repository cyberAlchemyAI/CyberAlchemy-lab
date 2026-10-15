import NumberPrefixDecoder
set_option autoImplicit false
set_option maxRecDepth 8192
namespace RelationalSuccessor.CandidateJsonTokens.Controls
open CandidateJsonTokens CandidateJsonBytes
theorem whole_number_00 : decodeWholeNumber [48] = some "0" := by decide

theorem whole_number_01 : decodeWholeNumber [45,48] = some "-0" := by decide

theorem whole_number_02 : decodeWholeNumber [49] = some "1" := by decide

theorem whole_number_03 : decodeWholeNumber [49,48] = some "10" := by decide

theorem whole_number_04 : decodeWholeNumber [45,49,48] = some "-10" := by decide

theorem whole_number_05 : decodeWholeNumber [52,50,46,48] = some "42.0" := by decide

theorem whole_number_06 : decodeWholeNumber [52,46,50,101,49] = some "4.2e1" := by decide

theorem whole_number_07 : decodeWholeNumber [52,46,50,69,43,49] = some "4.2E+1" := by decide

theorem whole_number_08 : decodeWholeNumber [45,49,50,46,51,52,101,45,53,54] = some "-12.34e-56" := by decide

theorem whole_number_09 : decodeWholeNumber [49,101,48] = some "1e0" := by decide

theorem whole_number_10 : decodeWholeNumber [49,69,45,48] = some "1E-0" := by decide

theorem whole_number_11 : decodeWholeNumber [48,101,43,49,50,51,52,53,54,55,56,57] = some "0e+123456789" := by decide

theorem whole_number_12 : decodeWholeNumber [49,46,48,101,45,48,48,48,50] = some "1.0e-0002" := by decide

theorem whole_number_13 : decodeWholeNumber [57,48,48,55,49,57,57,50,53,52,55,52,48,57,57,51] = some "9007199254740993" := by decide

theorem whole_number_14 : decodeWholeNumber [49,101,57,57,57,57,57,57,57,57,57] = some "1e999999999" := by decide

theorem whole_number_15 : decodeWholeNumber [] = none := by decide

theorem whole_number_16 : decodeWholeNumber [45] = none := by decide

theorem whole_number_17 : decodeWholeNumber [43,49] = none := by decide

theorem whole_number_18 : decodeWholeNumber [48,48] = none := by decide

theorem whole_number_19 : decodeWholeNumber [48,49] = none := by decide

theorem whole_number_20 : decodeWholeNumber [45,48,48] = none := by decide

theorem whole_number_21 : decodeWholeNumber [45,48,49] = none := by decide

theorem whole_number_22 : decodeWholeNumber [46,49] = none := by decide

theorem whole_number_23 : decodeWholeNumber [49,46] = none := by decide

theorem whole_number_24 : decodeWholeNumber [49,101] = none := by decide

theorem whole_number_25 : decodeWholeNumber [49,69,43] = none := by decide

theorem whole_number_26 : decodeWholeNumber [49,101,45] = none := by decide

theorem whole_number_27 : decodeWholeNumber [49,101,101,50] = none := by decide

theorem whole_number_28 : decodeWholeNumber [49,46,50,46,51] = none := by decide

theorem whole_number_29 : decodeWholeNumber [45,45,49] = none := by decide

theorem whole_number_30 : decodeWholeNumber [49,43,50] = none := by decide

theorem whole_number_31 : decodeWholeNumber [78,97,78] = none := by decide

theorem whole_number_32 : decodeWholeNumber [73,110,102,105,110,105,116,121] = none := by decide

theorem whole_number_33 : decodeWholeNumber [49,97] = none := by decide

theorem whole_number_34 : decodeWholeNumber [32,49] = none := by decide

theorem whole_number_35 : decodeWholeNumber [49,32] = none := by decide

theorem whole_number_36 : decodeWholeNumber [1633] = none := by decide

theorem whole_number_37 : decodeWholeNumber [48,120,49,48] = none := by decide

theorem number_comma : decodeNumber [52,50,44,48] = some ("42",[44,48]) := by decide

theorem number_close_array : decodeNumber [52,46,50,101,49,93] = some ("4.2e1",[93]) := by decide

theorem number_close_object : decodeNumber [45,48,125] = some ("-0",[125]) := by decide

theorem number_space : decodeNumber [49,32,9] = some ("1",[32,9]) := by decide

theorem number_unknown_suffix : decodeNumber [49,97,98,99] = some ("1",[97,98,99]) := by decide

theorem number_incomplete_exponent : decodeNumber [49,101,93] = none := by decide

theorem number_leading_zero : decodeNumber [48,49,44] = none := by decide

theorem number_adjacent_sign : decodeNumber [49,45,50,44] = none := by decide

theorem number_partial_fraction : decodeNumber [49,46,44] = none := by decide

theorem number_upper_exp : decodeNumber [49,69,43,48,50,13] = some ("1E+02",[13]) := by decide

theorem null_prefix : decodeLiteral [110,117,108,108,44,49] = some (.null,[44,49]) := by rfl

theorem false_prefix : decodeLiteral [102,97,108,115,101,93] = some (.boolean false,[93]) := by rfl

theorem true_prefix : decodeLiteral [116,114,117,101,125] = some (.boolean true,[125]) := by rfl

theorem true_unknown_suffix : decodeLiteral [116,114,117,101,120] = some (.boolean true,[120]) := by rfl

theorem null_unclosed : decodeLiteral [110,117,108] = none := by rfl

theorem false_upper : decodeLiteral [70,97,108,115,101] = none := by rfl

theorem true_upper : decodeLiteral [84,82,85,69] = none := by rfl

theorem literal_missing : decodeLiteral [] = none := by rfl

theorem literal_space : decodeLiteral [32,110,117,108,108] = none := by rfl

theorem ws_all : scanWhitespace [32,9,10,13,110] = ([32,9,10,13],[110]) := by decide

theorem ws_empty : scanWhitespace [] = ([],[]) := by decide

theorem ws_no_trim : scanWhitespace [49,32] = ([],[49,32]) := by decide

theorem ws_nonbreaking : scanWhitespace [160,32] = ([],[160,32]) := by decide

theorem ws_vertical_tab : scanWhitespace [11,32] = ([],[11,32]) := by decide

theorem ws_only : scanWhitespace [9,9,32] = ([9,9,32],[]) := by decide

#print axioms whole_number_00
#print axioms whole_number_01
#print axioms whole_number_02
#print axioms whole_number_03
#print axioms whole_number_04
#print axioms whole_number_05
#print axioms whole_number_06
#print axioms whole_number_07
#print axioms whole_number_08
#print axioms whole_number_09
#print axioms whole_number_10
#print axioms whole_number_11
#print axioms whole_number_12
#print axioms whole_number_13
#print axioms whole_number_14
#print axioms whole_number_15
#print axioms whole_number_16
#print axioms whole_number_17
#print axioms whole_number_18
#print axioms whole_number_19
#print axioms whole_number_20
#print axioms whole_number_21
#print axioms whole_number_22
#print axioms whole_number_23
#print axioms whole_number_24
#print axioms whole_number_25
#print axioms whole_number_26
#print axioms whole_number_27
#print axioms whole_number_28
#print axioms whole_number_29
#print axioms whole_number_30
#print axioms whole_number_31
#print axioms whole_number_32
#print axioms whole_number_33
#print axioms whole_number_34
#print axioms whole_number_35
#print axioms whole_number_36
#print axioms whole_number_37
#print axioms number_comma
#print axioms number_close_array
#print axioms number_close_object
#print axioms number_space
#print axioms number_unknown_suffix
#print axioms number_incomplete_exponent
#print axioms number_leading_zero
#print axioms number_adjacent_sign
#print axioms number_partial_fraction
#print axioms number_upper_exp
#print axioms null_prefix
#print axioms false_prefix
#print axioms true_prefix
#print axioms true_unknown_suffix
#print axioms null_unclosed
#print axioms false_upper
#print axioms true_upper
#print axioms literal_missing
#print axioms literal_space
#print axioms ws_all
#print axioms ws_empty
#print axioms ws_no_trim
#print axioms ws_nonbreaking
#print axioms ws_vertical_tab
#print axioms ws_only
end RelationalSuccessor.CandidateJsonTokens.Controls
