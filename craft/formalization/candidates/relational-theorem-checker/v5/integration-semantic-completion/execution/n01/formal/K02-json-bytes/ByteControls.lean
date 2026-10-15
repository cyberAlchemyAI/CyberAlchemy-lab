import JsonDocumentMeaning
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonBytes.Controls
open RelationalSuccessor.CandidateJsonBytes

theorem utf8_empty : decodeUtf8 [] = some [] := by decide

theorem utf8_ASCII_boundaries : decodeUtf8 [0,127] = some [0,127] := by decide

theorem utf8_two_min : decodeUtf8 [194,128] = some [128] := by decide

theorem utf8_two_max : decodeUtf8 [223,191] = some [2047] := by decide

theorem utf8_three_min : decodeUtf8 [224,160,128] = some [2048] := by decide

theorem utf8_three_max : decodeUtf8 [239,191,191] = some [65535] := by decide

theorem utf8_before_surrogates : decodeUtf8 [237,159,191] = some [55295] := by decide

theorem utf8_after_surrogates : decodeUtf8 [238,128,128] = some [57344] := by decide

theorem utf8_four_min : decodeUtf8 [240,144,128,128] = some [65536] := by decide

theorem utf8_four_max : decodeUtf8 [244,143,191,191] = some [1114111] := by decide

theorem utf8_g_clef : decodeUtf8 [240,157,132,158] = some [119070] := by decide

theorem utf8_precomposed : decodeUtf8 [195,169] = some [233] := by decide

theorem utf8_decomposed : decodeUtf8 [101,204,129] = some [101,769] := by decide

theorem utf8_BOM_is_scalar : decodeUtf8 [239,187,191] = some [65279] := by decide

theorem utf8_C0_overlong : decodeUtf8 [192,128] = none := by decide

theorem utf8_C1_overlong : decodeUtf8 [193,191] = none := by decide

theorem utf8_E0_overlong : decodeUtf8 [224,128,128] = none := by decide

theorem utf8_F0_overlong : decodeUtf8 [240,128,128,128] = none := by decide

theorem utf8_surrogate_first : decodeUtf8 [237,160,128] = none := by decide

theorem utf8_surrogate_last : decodeUtf8 [237,191,191] = none := by decide

theorem utf8_above_max : decodeUtf8 [244,144,128,128] = none := by decide

theorem utf8_four_above_max : decodeUtf8 [244,191,191,191] = none := by decide

theorem utf8_F5_leader : decodeUtf8 [245,128,128,128] = none := by decide

theorem utf8_FF_leader : decodeUtf8 [255] = none := by decide

theorem utf8_tail_alone_low : decodeUtf8 [128] = none := by decide

theorem utf8_tail_alone_high : decodeUtf8 [191] = none := by decide

theorem utf8_bad_second : decodeUtf8 [194,0] = none := by decide

theorem utf8_bad_third : decodeUtf8 [226,130,32] = none := by decide

theorem utf8_bad_fourth : decodeUtf8 [240,144,128,0] = none := by decide

theorem utf8_truncated_two : decodeUtf8 [194] = none := by decide

theorem utf8_truncated_three_first : decodeUtf8 [226] = none := by decide

theorem utf8_truncated_three_second : decodeUtf8 [226,130] = none := by decide

theorem utf8_truncated_four_first : decodeUtf8 [240] = none := by decide

theorem utf8_truncated_four_second : decodeUtf8 [240,144] = none := by decide

theorem utf8_truncated_four_third : decodeUtf8 [240,144,128] = none := by decide

theorem utf8_valid_then_invalid : decodeUtf8 [65,192,128] = none := by decide

theorem utf8_mixed_script : decodeUtf8 [65,226,137,162,206,145,46] = some [65,8802,913,46] := by decide

theorem utf8_korean : decodeUtf8 [237,149,156,234,181,173,236,150,180] = some [54620,44397,50612] := by decide

theorem utf8_large_exact_number_bytes : decodeUtf8 [57,48,48,55,49,57,57,50,53,52,55,52,48,57,57,51,46,48] = some [57,48,48,55,49,57,57,50,53,52,55,52,48,57,57,51,46,48] := by decide

def keyRaw : List Nat := [34,107,34]
def keyEscaped : List Nat := [34,92,117,48,48,54,98,34]

theorem raw_key_meaning : StringMeaning keyRaw [107] := by
  refine ⟨[107],rfl,?_⟩
  have atom : StringUnitMeaning [107] [107] := by
    simpa only [scalarUnits,show 107 < 65536 from by decide,if_true] using
      StringUnitMeaning.raw 107 (by decide) (by decide) (by decide) (by decide)
  exact StringContentMeaning.cons [107] [] [107] [] atom .nil

theorem escaped_key_meaning : StringMeaning keyEscaped [107] := by
  refine ⟨[92,117,48,48,54,98],rfl,?_⟩
  have atom : StringUnitMeaning [92,117,48,48,54,98] [107] :=
    .hexadecimal 48 48 54 98 0 0 6 11 (.digit 0 (by decide)) (.digit 0 (by decide))
      (.digit 6 (by decide)) (.lower 1 (by decide))
  exact StringContentMeaning.cons _ [] [107] [] atom .nil

theorem unpaired_surrogate_string_meaning : StringMeaning [34,92,117,68,69,65,68,34] [57005] := by
  refine ⟨[92,117,68,69,65,68],rfl,?_⟩
  have atom : StringUnitMeaning [92,117,68,69,65,68] [57005] :=
    .hexadecimal 68 69 65 68 13 14 10 13 (.upper 3 (by decide)) (.upper 4 (by decide))
      (.upper 0 (by decide)) (.upper 3 (by decide))
  exact StringContentMeaning.cons _ [] [57005] [] atom .nil

theorem unpaired_surrogate_is_not_scalar : ¬ Scalar 57005 := by decide

theorem raw_nonBMP_string_meaning : StringMeaning [34,119070,34] [55348,56606] := by
  refine ⟨[119070],rfl,?_⟩
  have atom : StringUnitMeaning [119070] [55348,56606] := by
    simpa only [scalarUnits,show ¬ 119070 < 65536 from by decide,if_false] using
      StringUnitMeaning.raw 119070 (by decide) (by decide) (by decide) (by decide)
  exact StringContentMeaning.cons _ [] [55348,56606] [] atom .nil

theorem escaped_nonBMP_string_meaning : StringMeaning [34,92,117,68,56,51,52,92,117,68,68,49,69,34] [55348,56606] := by
  refine ⟨[92,117,68,56,51,52,92,117,68,68,49,69],rfl,?_⟩
  have first : StringUnitMeaning [92,117,68,56,51,52] [55348] :=
    .hexadecimal 68 56 51 52 13 8 3 4 (.upper 3 (by decide)) (.digit 8 (by decide))
      (.digit 3 (by decide)) (.digit 4 (by decide))
  have second : StringUnitMeaning [92,117,68,68,49,69] [56606] :=
    .hexadecimal 68 68 49 69 13 13 1 14 (.upper 3 (by decide)) (.upper 3 (by decide))
      (.digit 1 (by decide)) (.upper 4 (by decide))
  exact StringContentMeaning.cons _ _ [55348] [56606] first
    (StringContentMeaning.cons _ [] [56606] [] second .nil)

def nullWord : List Nat := [110,117,108,108]
def trueWord : List Nat := [116,114,117,101]
def duplicateObject : List Nat := [123] ++ keyRaw ++ [58] ++ nullWord ++ [44] ++ keyEscaped ++ [58] ++ trueWord ++ [125]

theorem duplicate_decoded_keys_preserved : ValueMeaning duplicateObject (.object [([107],.null),([107],.boolean true)]) := by
  have space : WhiteSpace [] := by intro code member; simp at member
  have last : MembersMeaning (keyEscaped ++ [] ++ [58] ++ [] ++ trueWord) [([107],.boolean true)] :=
    .one keyEscaped [] [] trueWord [107] (.boolean true) escaped_key_meaning space space .true
  have both : MembersMeaning (keyRaw ++ [] ++ [58] ++ [] ++ nullWord ++ [] ++ [44] ++ [] ++ (keyEscaped ++ [] ++ [58] ++ [] ++ trueWord)) [([107],.null),([107],.boolean true)] :=
    .cons keyRaw [] [] nullWord [] [] _ [107] .null _ raw_key_meaning space space .null space space last
  have object := ValueMeaning.object [] _ [] _ space both space
  simpa only [duplicateObject,List.nil_append,List.append_nil,List.append_assoc] using object

theorem unpaired_escape_is_byte_document_syntax : ByteDocumentMeaning [34,92,117,68,69,65,68,34] (.string [57005]) := by
  apply (byte_document_encoding_bridge _ _).mpr
  refine ⟨[34,92,117,68,69,65,68,34],by decide,[],[34,92,117,68,69,65,68,34],[],?_,?_,?_,rfl⟩
  · intro code member; simp at member
  · exact .string _ _ unpaired_surrogate_string_meaning
  · intro code member; simp at member

#print axioms utf8_empty
#print axioms utf8_ASCII_boundaries
#print axioms utf8_two_min
#print axioms utf8_two_max
#print axioms utf8_three_min
#print axioms utf8_three_max
#print axioms utf8_before_surrogates
#print axioms utf8_after_surrogates
#print axioms utf8_four_min
#print axioms utf8_four_max
#print axioms utf8_g_clef
#print axioms utf8_precomposed
#print axioms utf8_decomposed
#print axioms utf8_BOM_is_scalar
#print axioms utf8_C0_overlong
#print axioms utf8_C1_overlong
#print axioms utf8_E0_overlong
#print axioms utf8_F0_overlong
#print axioms utf8_surrogate_first
#print axioms utf8_surrogate_last
#print axioms utf8_above_max
#print axioms utf8_four_above_max
#print axioms utf8_F5_leader
#print axioms utf8_FF_leader
#print axioms utf8_tail_alone_low
#print axioms utf8_tail_alone_high
#print axioms utf8_bad_second
#print axioms utf8_bad_third
#print axioms utf8_bad_fourth
#print axioms utf8_truncated_two
#print axioms utf8_truncated_three_first
#print axioms utf8_truncated_three_second
#print axioms utf8_truncated_four_first
#print axioms utf8_truncated_four_second
#print axioms utf8_truncated_four_third
#print axioms utf8_valid_then_invalid
#print axioms utf8_mixed_script
#print axioms utf8_korean
#print axioms utf8_large_exact_number_bytes
#print axioms raw_key_meaning
#print axioms escaped_key_meaning
#print axioms unpaired_surrogate_string_meaning
#print axioms unpaired_surrogate_is_not_scalar
#print axioms raw_nonBMP_string_meaning
#print axioms escaped_nonBMP_string_meaning
#print axioms duplicate_decoded_keys_preserved
#print axioms unpaired_escape_is_byte_document_syntax
end RelationalSuccessor.CandidateJsonBytes.Controls
