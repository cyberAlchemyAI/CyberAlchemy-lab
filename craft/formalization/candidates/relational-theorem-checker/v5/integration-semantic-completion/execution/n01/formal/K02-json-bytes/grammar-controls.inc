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
