import QuotedStringDecoder
set_option autoImplicit false
set_option maxRecDepth 8192
namespace RelationalSuccessor.CandidateJsonStrings.Controls
open CandidateJsonStrings
theorem string_empty : decodeString [34,34] = some [] := by decide

theorem string_plain : decodeString [34,97,98,99,34] = some [97,98,99] := by decide

theorem string_quote : decodeString [34,92,34,34] = some [34] := by decide

theorem string_backslash : decodeString [34,92,92,34] = some [92] := by decide

theorem string_solidus : decodeString [34,92,47,34] = some [47] := by decide

theorem string_backspace : decodeString [34,92,98,34] = some [8] := by decide

theorem string_formfeed : decodeString [34,92,102,34] = some [12] := by decide

theorem string_newline : decodeString [34,92,110,34] = some [10] := by decide

theorem string_return : decodeString [34,92,114,34] = some [13] := by decide

theorem string_tab : decodeString [34,92,116,34] = some [9] := by decide

theorem string_all_simple : decodeString [34,92,34,92,92,92,47,92,98,92,102,92,110,92,114,92,116,34] = some [34,92,47,8,12,10,13,9] := by decide

theorem string_hex_zero : decodeString [34,92,117,48,48,48,48,34] = some [0] := by decide

theorem string_hex_lower : decodeString [34,92,117,48,48,54,98,34] = some [107] := by decide

theorem string_hex_upper : decodeString [34,92,117,48,48,65,70,34] = some [175] := by decide

theorem string_hex_mixed : decodeString [34,92,117,97,66,99,68,34] = some [43981] := by decide

theorem string_lone_high : decodeString [34,92,117,68,56,51,52,34] = some [55348] := by decide

theorem string_lone_low : decodeString [34,92,117,68,69,65,68,34] = some [57005] := by decide

theorem string_surrogate_pair : decodeString [34,92,117,68,56,51,52,92,117,68,68,49,69,34] = some [55348,56606] := by decide

theorem string_raw_supplementary : decodeString [34,119070,34] = some [55348,56606] := by decide

theorem string_raw_maximum : decodeString [34,1114111,34] = some [56319,57343] := by decide

theorem string_raw_delete : decodeString [34,127,34] = some [127] := by decide

theorem string_raw_space : decodeString [34,32,34] = some [32] := by decide

theorem string_missing_start : decodeString [97,98,99,34] = none := by decide

theorem string_unclosed : decodeString [34,97,98,99] = none := by decide

theorem string_unknown_escape : decodeString [34,92,113,34] = none := by decide

theorem string_short_hex : decodeString [34,92,117,48,49,50,34] = none := by decide

theorem string_bad_hex : decodeString [34,92,117,48,120,49,50,34] = none := by decide

theorem string_slash_unclosed : decodeString [34,92] = none := by decide

theorem string_raw_tab : decodeString [34,9,34] = none := by decide

theorem string_raw_zero : decodeString [34,0,34] = none := by decide

theorem string_raw_control31 : decodeString [34,31,34] = none := by decide

theorem string_trailing_text : decodeString [34,97,34,120] = none := by decide

theorem string_second_string : decodeString [34,97,34,34,98,34] = none := by decide

theorem string_raw_newline : decodeString [34,10,34] = none := by decide

theorem string_empty_input : decodeString [] = none := by decide

theorem string_quote_only : decodeString [34] = none := by decide

theorem string_raw_surrogate_refused : decodeString [34,55296,34] = none := by decide

theorem string_raw_above_max_refused : decodeString [34,1114112,34] = none := by decide

theorem prefix_comma : decodeQuoted [34,97,34,44,99] = some ([97],[44,99]) := by decide

theorem prefix_empty : decodeQuoted [34,34,58] = some ([],[58]) := by decide

theorem prefix_hex : decodeQuoted [34,92,117,48,48,54,98,34,125] = some ([107],[125]) := by decide

theorem prefix_lone_surrogate : decodeQuoted [34,92,117,68,69,65,68,34,44] = some ([57005],[44]) := by decide

theorem prefix_raw_supplementary : decodeQuoted [34,119070,34,93] = some ([55348,56606],[93]) := by decide

theorem prefix_unclosed : decodeQuoted [34,97] = none := by decide

theorem prefix_invalid_escape : decodeQuoted [34,92,113,34,44] = none := by decide

theorem prefix_missing_start : decodeQuoted [97,34] = none := by decide

theorem bytes_empty : decodeStringBytes [34,34] = some [] := by decide

theorem bytes_all_simple : decodeStringBytes [34,92,34,92,92,92,47,92,98,92,102,92,110,92,114,92,116,34] = some [34,92,47,8,12,10,13,9] := by decide

theorem bytes_lone_low : decodeStringBytes [34,92,117,68,69,65,68,34] = some [57005] := by decide

theorem bytes_surrogate_pair : decodeStringBytes [34,92,117,68,56,51,52,92,117,68,68,49,69,34] = some [55348,56606] := by decide

theorem bytes_raw_supplementary : decodeStringBytes [34,240,157,132,158,34] = some [55348,56606] := by decide

theorem bytes_unknown_escape : decodeStringBytes [34,92,113,34] = none := by decide

theorem bytes_trailing_text : decodeStringBytes [34,97,34,120] = none := by decide

theorem bytes_invalid_utf8 : decodeStringBytes [34,192,128,34] = none := by decide

theorem bytes_direct_surrogate : decodeStringBytes [34,237,160,128,34] = none := by decide

#print axioms string_empty
#print axioms string_plain
#print axioms string_quote
#print axioms string_backslash
#print axioms string_solidus
#print axioms string_backspace
#print axioms string_formfeed
#print axioms string_newline
#print axioms string_return
#print axioms string_tab
#print axioms string_all_simple
#print axioms string_hex_zero
#print axioms string_hex_lower
#print axioms string_hex_upper
#print axioms string_hex_mixed
#print axioms string_lone_high
#print axioms string_lone_low
#print axioms string_surrogate_pair
#print axioms string_raw_supplementary
#print axioms string_raw_maximum
#print axioms string_raw_delete
#print axioms string_raw_space
#print axioms string_missing_start
#print axioms string_unclosed
#print axioms string_unknown_escape
#print axioms string_short_hex
#print axioms string_bad_hex
#print axioms string_slash_unclosed
#print axioms string_raw_tab
#print axioms string_raw_zero
#print axioms string_raw_control31
#print axioms string_trailing_text
#print axioms string_second_string
#print axioms string_raw_newline
#print axioms string_empty_input
#print axioms string_quote_only
#print axioms string_raw_surrogate_refused
#print axioms string_raw_above_max_refused
#print axioms prefix_comma
#print axioms prefix_empty
#print axioms prefix_hex
#print axioms prefix_lone_surrogate
#print axioms prefix_raw_supplementary
#print axioms prefix_unclosed
#print axioms prefix_invalid_escape
#print axioms prefix_missing_start
#print axioms bytes_empty
#print axioms bytes_all_simple
#print axioms bytes_lone_low
#print axioms bytes_surrogate_pair
#print axioms bytes_raw_supplementary
#print axioms bytes_unknown_escape
#print axioms bytes_trailing_text
#print axioms bytes_invalid_utf8
#print axioms bytes_direct_surrogate
end RelationalSuccessor.CandidateJsonStrings.Controls
