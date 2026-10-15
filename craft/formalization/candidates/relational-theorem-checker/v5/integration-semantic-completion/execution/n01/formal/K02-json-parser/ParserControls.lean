import RecursiveJsonParser
set_option autoImplicit false
set_option maxRecDepth 131072
set_option maxHeartbeats 4000000
namespace RelationalSuccessor.CandidateJsonParser.Controls
open CandidateJsonParser CandidateJsonBytes
theorem document_00 : parseDocument [110,117,108,108] = some (.null) := by rfl

theorem document_01 : parseDocument [102,97,108,115,101] = some (.boolean false) := by rfl

theorem document_02 : parseDocument [116,114,117,101] = some (.boolean true) := by rfl

theorem document_03 : parseDocument [48] = some (.number "0") := by rfl

theorem document_04 : parseDocument [45,48] = some (.number "-0") := by rfl

theorem document_05 : parseDocument [52,50,46,48] = some (.number "42.0") := by rfl

theorem document_06 : parseDocument [52,46,50,101,49] = some (.number "4.2e1") := by rfl

theorem document_07 : parseDocument [57,48,48,55,49,57,57,50,53,52,55,52,48,57,57,51] = some (.number "9007199254740993") := by rfl

theorem document_08 : parseDocument [34,34] = some (.string []) := by rfl

theorem document_09 : parseDocument [34,107,34] = some (.string [107]) := by rfl

theorem document_10 : parseDocument [34,92,117,48,48,54,98,34] = some (.string [107]) := by rfl

theorem document_11 : parseDocument [34,92,117,68,69,65,68,34] = some (.string [57005]) := by rfl

theorem document_12 : parseDocument [34,119070,34] = some (.string [55348,56606]) := by rfl

theorem document_13 : parseDocument [34,92,117,68,56,51,52,92,117,68,68,49,69,34] = some (.string [55348,56606]) := by rfl

theorem document_14 : parseDocument [91,93] = some (.array []) := by rfl

theorem document_15 : parseDocument [91,32,93] = some (.array []) := by rfl

theorem document_16 : parseDocument [123,125] = some (.object []) := by rfl

theorem document_17 : parseDocument [123,32,9,13,10,32,125] = some (.object []) := by rfl

theorem document_18 : parseDocument [91,110,117,108,108,44,116,114,117,101,44,102,97,108,115,101,93] = some (.array [.null,.boolean true,.boolean false]) := by rfl

theorem document_19 : parseDocument [91,52,50,44,52,50,46,48,44,52,46,50,101,49,93] = some (.array [.number "42",.number "42.0",.number "4.2e1"]) := by rfl

theorem document_20 : parseDocument [91,91,91,93,93,93] = some (.array [.array [.array []]]) := by rfl

theorem document_21 : parseDocument [123,34,107,34,58,110,117,108,108,125] = some (.object [([107],.null)]) := by rfl

theorem document_22 : parseDocument [123,34,107,34,58,110,117,108,108,44,34,92,117,48,48,54,98,34,58,116,114,117,101,125] = some (.object [([107],.null),([107],.boolean true)]) := by rfl

theorem document_23 : parseDocument [123,34,92,117,68,69,65,68,34,58,34,92,117,68,56,48,48,34,125] = some (.object [([57005],.string [55296])]) := by rfl

theorem document_24 : parseDocument [91,123,125,44,91,93,44,123,34,97,34,58,91,49,44,123,34,98,34,58,102,97,108,115,101,125,93,125,93] = some (.array [.object [],.array [],.object [([97],.array [.number "1",.object [([98],.boolean false)]])]]) := by rfl

theorem document_25 : parseDocument [32,9,10,32,123,32,34,120,34,32,58,32,91,32,49,32,44,32,50,32,93,32,44,32,34,121,34,32,58,32,123,32,34,122,34,32,58,32,34,92,110,34,32,125,32,125,32,13,10] = some (.object [([120],.array [.number "1",.number "2"]),([121],.object [([122],.string [10])])]) := by rfl

theorem document_26 : parseDocument [91,34,92,34,34,44,32,34,92,92,34,44,32,34,92,47,34,93] = some (.array [.string [34],.string [92],.string [47]]) := by rfl

theorem document_27 : parseDocument [123,34,98,34,58,49,44,34,97,34,58,50,44,34,98,34,58,51,125] = some (.object [([98],.number "1"),([97],.number "2"),([98],.number "3")]) := by rfl

theorem document_28 : parseDocument [] = none := by rfl

theorem document_29 : parseDocument [32] = none := by rfl

theorem document_30 : parseDocument [91] = none := by rfl

theorem document_31 : parseDocument [123] = none := by rfl

theorem document_32 : parseDocument [91,49,44,93] = none := by rfl

theorem document_33 : parseDocument [123,34,97,34,58,49,44,125] = none := by rfl

theorem document_34 : parseDocument [91,44,93] = none := by rfl

theorem document_35 : parseDocument [123,44,125] = none := by rfl

theorem document_36 : parseDocument [91,49,32,50,93] = none := by rfl

theorem document_37 : parseDocument [123,34,97,34,32,49,125] = none := by rfl

theorem document_38 : parseDocument [123,97,58,49,125] = none := by rfl

theorem document_39 : parseDocument [123,34,97,34,58,125] = none := by rfl

theorem document_40 : parseDocument [123,34,97,34,58,49,32,34,98,34,58,50,125] = none := by rfl

theorem document_41 : parseDocument [91,116,114,117,101,120,93] = none := by rfl

theorem document_42 : parseDocument [91,49,97,98,99,93] = none := by rfl

theorem document_43 : parseDocument [123,34,97,34,58,49,101,125] = none := by rfl

theorem document_44 : parseDocument [91,48,49,93] = none := by rfl

theorem document_45 : parseDocument [91,49,46,93] = none := by rfl

theorem document_46 : parseDocument [116,114,117,101,120] = none := by rfl

theorem document_47 : parseDocument [110,117,108,108,32,110,117,108,108] = none := by rfl

theorem document_48 : parseDocument [49,44,50] = none := by rfl

theorem document_49 : parseDocument [91,93,120] = none := by rfl

theorem document_50 : parseDocument [123,125,91,93] = none := by rfl

theorem document_51 : parseDocument [78,97,78] = none := by rfl

theorem document_52 : parseDocument [73,110,102,105,110,105,116,121] = none := by rfl

theorem document_53 : parseDocument [91,11,93] = none := by rfl

theorem document_54 : parseDocument [160,110,117,108,108] = none := by rfl

theorem document_55 : parseDocument [34,92,113,34] = none := by rfl

theorem document_56 : parseDocument [34,117,110,99,108,111,115,101,100] = none := by rfl

theorem document_57 : parseDocument [34,10,34] = none := by rfl

theorem document_58 : parseDocument [123,34,97,34,58,116,114,117,101,58,49,125] = none := by rfl

theorem document_59 : parseDocument [123,34,97,34,58,49,93] = none := by rfl

theorem document_60 : parseDocument [91,49,125] = none := by rfl

theorem document_61 : parseDocument [91,49,44,44,50,93] = none := by rfl

theorem byte_document_00 : parseDocumentBytes [110,117,108,108] = some (.null) := by rfl

theorem byte_document_05 : parseDocumentBytes [52,50,46,48] = some (.number "42.0") := by rfl

theorem byte_document_11 : parseDocumentBytes [34,92,117,68,69,65,68,34] = some (.string [57005]) := by rfl

theorem byte_document_12 : parseDocumentBytes [34,240,157,132,158,34] = some (.string [55348,56606]) := by rfl

theorem byte_document_14 : parseDocumentBytes [91,93] = some (.array []) := by rfl

theorem byte_document_22 : parseDocumentBytes [123,34,107,34,58,110,117,108,108,44,34,92,117,48,48,54,98,34,58,116,114,117,101,125] = some (.object [([107],.null),([107],.boolean true)]) := by rfl

theorem byte_document_25 : parseDocumentBytes [32,9,10,32,123,32,34,120,34,32,58,32,91,32,49,32,44,32,50,32,93,32,44,32,34,121,34,32,58,32,123,32,34,122,34,32,58,32,34,92,110,34,32,125,32,125,32,13,10] = some (.object [([120],.array [.number "1",.number "2"]),([121],.object [([122],.string [10])])]) := by rfl

theorem byte_document_28 : parseDocumentBytes [] = none := by rfl

theorem byte_document_32 : parseDocumentBytes [91,49,44,93] = none := by rfl

theorem byte_document_45 : parseDocumentBytes [91,49,46,93] = none := by rfl

theorem raw_surrogate : parseDocument [34,55296,34] = none := by rfl

theorem above_unicode : parseDocument [34,1114112,34] = none := by rfl

theorem byte_overlong : parseDocumentBytes [34,192,128,34] = none := by rfl

theorem byte_surrogate : parseDocumentBytes [34,237,160,128,34] = none := by rfl

theorem byte_truncated : parseDocumentBytes [34,240,159,34] = none := by rfl

theorem byte_bom : parseDocumentBytes [239,187,191,110,117,108,108] = none := by rfl

theorem primitive_true_unknown : decodePrimitive [116,114,117,101,120] = none := by rfl

theorem primitive_number_unknown : decodePrimitive [49,97] = none := by rfl

theorem primitive_string_unknown : decodePrimitive [34,97,34,97] = none := by rfl

theorem primitive_colon_refused : decodePrimitive [34,97,34,58] = none := by rfl

theorem primitive_array_refused : decodePrimitive [91,93] = none := by rfl

#print axioms document_00
#print axioms document_01
#print axioms document_02
#print axioms document_03
#print axioms document_04
#print axioms document_05
#print axioms document_06
#print axioms document_07
#print axioms document_08
#print axioms document_09
#print axioms document_10
#print axioms document_11
#print axioms document_12
#print axioms document_13
#print axioms document_14
#print axioms document_15
#print axioms document_16
#print axioms document_17
#print axioms document_18
#print axioms document_19
#print axioms document_20
#print axioms document_21
#print axioms document_22
#print axioms document_23
#print axioms document_24
#print axioms document_25
#print axioms document_26
#print axioms document_27
#print axioms document_28
#print axioms document_29
#print axioms document_30
#print axioms document_31
#print axioms document_32
#print axioms document_33
#print axioms document_34
#print axioms document_35
#print axioms document_36
#print axioms document_37
#print axioms document_38
#print axioms document_39
#print axioms document_40
#print axioms document_41
#print axioms document_42
#print axioms document_43
#print axioms document_44
#print axioms document_45
#print axioms document_46
#print axioms document_47
#print axioms document_48
#print axioms document_49
#print axioms document_50
#print axioms document_51
#print axioms document_52
#print axioms document_53
#print axioms document_54
#print axioms document_55
#print axioms document_56
#print axioms document_57
#print axioms document_58
#print axioms document_59
#print axioms document_60
#print axioms document_61
#print axioms byte_document_00
#print axioms byte_document_05
#print axioms byte_document_11
#print axioms byte_document_12
#print axioms byte_document_14
#print axioms byte_document_22
#print axioms byte_document_25
#print axioms byte_document_28
#print axioms byte_document_32
#print axioms byte_document_45
#print axioms raw_surrogate
#print axioms above_unicode
#print axioms byte_overlong
#print axioms byte_surrogate
#print axioms byte_truncated
#print axioms byte_bom
#print axioms primitive_true_unknown
#print axioms primitive_number_unknown
#print axioms primitive_string_unknown
#print axioms primitive_colon_refused
#print axioms primitive_array_refused
end RelationalSuccessor.CandidateJsonParser.Controls
