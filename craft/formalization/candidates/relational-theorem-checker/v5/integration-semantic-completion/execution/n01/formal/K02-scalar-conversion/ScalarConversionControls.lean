import ScalarDocumentComposition

set_option autoImplicit false

namespace RelationalSuccessor.CandidateScalarConversion

theorem string_control_00 : decodeString [] = some (String.ofList []) := by rfl

theorem string_control_01 : decodeString [0] = some (String.ofList [Char.ofNat 0]) := by rfl

theorem string_control_02 : decodeString [8,9,10,13] = some (String.ofList [Char.ofNat 8,Char.ofNat 9,Char.ofNat 10,Char.ofNat 13]) := by rfl

theorem string_control_03 : decodeString [34,92] = some (String.ofList [Char.ofNat 34,Char.ofNat 92]) := by rfl

theorem string_control_04 : decodeString [65] = some (String.ofList [Char.ofNat 65]) := by rfl

theorem string_control_05 : decodeString [55295] = some (String.ofList [Char.ofNat 55295]) := by rfl

theorem string_control_06 : decodeString [57344] = some (String.ofList [Char.ofNat 57344]) := by rfl

theorem string_control_07 : decodeString [65535] = some (String.ofList [Char.ofNat 65535]) := by rfl

theorem string_control_08 : decodeString [55296,56320] = some (String.ofList [Char.ofNat 65536]) := by rfl

theorem string_control_09 : decodeString [56319,57343] = some (String.ofList [Char.ofNat 1114111]) := by rfl

theorem string_control_10 : decodeString [55357,56832] = some (String.ofList [Char.ofNat 128512]) := by rfl

theorem string_control_11 : decodeString [65,55357,56832,66] = some (String.ofList [Char.ofNat 65,Char.ofNat 128512,Char.ofNat 66]) := by rfl

theorem string_control_12 : decodeString [55296] = none := by rfl

theorem string_control_13 : decodeString [56319] = none := by rfl

theorem string_control_14 : decodeString [56320] = none := by rfl

theorem string_control_15 : decodeString [57343] = none := by rfl

theorem string_control_16 : decodeString [55296,65] = none := by rfl

theorem string_control_17 : decodeString [55296,55296] = none := by rfl

theorem string_control_18 : decodeString [56320,55296] = none := by rfl

theorem string_control_19 : decodeString [65536] = none := by rfl

theorem string_control_20 : decodeString [1114112] = none := by rfl

theorem string_control_21 : decodeString [4294967296] = none := by rfl

theorem string_control_22 : decodeString [65,55296] = none := by rfl

theorem string_control_23 : decodeString [55296,56320,55296] = none := by rfl

theorem string_control_24 : decodeString [55296,56320,56320] = none := by rfl

theorem string_control_25 : decodeString [55296,56320,55296,56320] = some (String.ofList [Char.ofNat 65536,Char.ofNat 65536]) := by rfl

theorem string_control_26 : decodeString [55295,57344] = some (String.ofList [Char.ofNat 55295,Char.ofNat 57344]) := by rfl

theorem string_control_27 : decodeString [56319,56320] = some (String.ofList [Char.ofNat 1113088]) := by rfl

theorem string_control_28 : decodeString [55296,57343] = some (String.ofList [Char.ofNat 66559]) := by rfl

theorem string_control_29 : decodeString [0,55296,56320,0] = some (String.ofList [Char.ofNat 0,Char.ofNat 65536,Char.ofNat 0]) := by rfl

theorem string_control_30 : decodeString [55357,56832,55357,56832] = some (String.ofList [Char.ofNat 128512,Char.ofNat 128512]) := by rfl

theorem string_control_31 : decodeString [55296,56320,65536] = none := by rfl

theorem string_control_32 : decodeString [55296,65536] = none := by rfl

theorem string_control_33 : decodeString [57344,55296,56320] = some (String.ofList [Char.ofNat 57344,Char.ofNat 65536]) := by rfl

theorem nested_array_unsupported : convertValue (.array [.null,.string [55296]]) = none := by

  simp only [convertValue,convertValues,Option.bind_some] <;> rfl

theorem nested_object_key_unsupported : convertValue (.object [([55296],.null)]) = none := by

  simp only [convertValue,convertEntries,Option.bind_some] <;> rfl

theorem nested_object_value_unsupported : convertValue (.object [([97],.string [56320])]) = none := by

  simp only [convertValue,convertEntries,Option.bind_some] <;> rfl

theorem duplicate_entries_retained : convertValue (.object [([97],.null),([97],.boolean true)]) = some (.object [("a",.null),("a",.boolean true)]) := by

  simp only [convertValue,convertEntries,Option.bind_some] <;> rfl

theorem nested_valid_pair : convertValue (.array [.string [55357,56832],.number "-0.00e+000"]) = some (.array [.string "😀",.number "-0.00e+000"]) := by

  simp only [convertValue,convertValues,Option.bind_some] <;> rfl

theorem escaped_unpaired_is_unsupported : classifyBytes [34,92,117,100,56,48,48,34] = .unsupportedScalar (.string [55296]) := by

  unfold classifyBytes

  change (match convertValue (.string [55296]) with | none => ConversionOutcome.unsupportedScalar (.string [55296]) | some value => .converted value) = .unsupportedScalar (.string [55296])

  simp only [convertValue]

  rfl

theorem malformed_utf8_is_invalid : classifyBytes [34,255,34] = .invalidSyntax := by rfl

theorem different_key_spellings_retained : parseScalarDocumentBytes [123,34,97,34,58,110,117,108,108,44,34,92,117,48,48,54,49,34,58,116,114,117,101,125] = some (.object [("a",.null),("a",.boolean true)]) := by

  unfold parseScalarDocumentBytes

  change convertValue (.object [([97],.null),([97],.boolean true)]) = some (.object [("a",.null),("a",.boolean true)])

  exact duplicate_entries_retained

theorem decoded_duplicate_binding_key_refused : CandidateJsonSource.decodeObject ["a"] (.object [("a",.null),("a",.boolean true)]) = none := by rfl

#print axioms string_control_00

#print axioms string_control_01

#print axioms string_control_02

#print axioms string_control_03

#print axioms string_control_04

#print axioms string_control_05

#print axioms string_control_06

#print axioms string_control_07

#print axioms string_control_08

#print axioms string_control_09

#print axioms string_control_10

#print axioms string_control_11

#print axioms string_control_12

#print axioms string_control_13

#print axioms string_control_14

#print axioms string_control_15

#print axioms string_control_16

#print axioms string_control_17

#print axioms string_control_18

#print axioms string_control_19

#print axioms string_control_20

#print axioms string_control_21

#print axioms string_control_22

#print axioms string_control_23

#print axioms string_control_24

#print axioms string_control_25

#print axioms string_control_26

#print axioms string_control_27

#print axioms string_control_28

#print axioms string_control_29

#print axioms string_control_30

#print axioms string_control_31

#print axioms string_control_32

#print axioms string_control_33

#print axioms nested_array_unsupported

#print axioms nested_object_key_unsupported

#print axioms nested_object_value_unsupported

#print axioms duplicate_entries_retained

#print axioms nested_valid_pair

#print axioms escaped_unpaired_is_unsupported

#print axioms malformed_utf8_is_invalid

#print axioms different_key_spellings_retained

#print axioms decoded_duplicate_binding_key_refused

end RelationalSuccessor.CandidateScalarConversion
