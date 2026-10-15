import PrimitiveDecoder
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonParser
open CandidateJsonBytes CandidateJsonTokens CandidateJsonStrings

-- Structural fuel decreases on every mutually recursive call. Grammar adequacy
-- of the wrapper budget is a separate proof target, not inferred from termination.
mutual
  def parseValueFuel : Nat → List Nat → Option (RawValue × List Nat)
    | 0, _ => none
    | fuel+1, input =>
      match input with
      | [] => none
      | first::tail =>
        if first = 91 then qualify ((parseArrayFuel fuel tail true).bind fun body => some (.array body.1,body.2))
        else if first = 123 then qualify ((parseObjectFuel fuel tail true).bind fun body => some (.object body.1,body.2))
        else decodePrimitive input

  def parseArrayFuel : Nat → List Nat → Bool → Option (List RawValue × List Nat)
    | 0, _, _ => none
    | fuel+1, input, allowEmpty =>
      let afterSpace := (scanWhitespace input).2
      match afterSpace with
      | [] => none
      | first::tail =>
        if first = 93 then if allowEmpty then some ([],tail) else none
        else (parseValueFuel fuel afterSpace).bind fun value =>
          match (scanWhitespace value.2).2 with
          | [] => none
          | delimiter::after =>
            if delimiter = 93 then some ([value.1],after)
            else if delimiter = 44 then (parseArrayFuel fuel after false).bind fun rest =>
              some (value.1::rest.1,rest.2)
            else none

  def parseObjectFuel : Nat → List Nat → Bool → Option (List (List Nat × RawValue) × List Nat)
    | 0, _, _ => none
    | fuel+1, input, allowEmpty =>
      let afterSpace := (scanWhitespace input).2
      match afterSpace with
      | [] => none
      | first::tail =>
        if first = 125 then if allowEmpty then some ([],tail) else none
        else (decodeQuoted afterSpace).bind fun key =>
          (takeWord [58] (scanWhitespace key.2).2).bind fun afterColon =>
            (parseValueFuel fuel (scanWhitespace afterColon).2).bind fun value =>
              match (scanWhitespace value.2).2 with
              | [] => none
              | delimiter::after =>
                if delimiter = 125 then some ([(key.1,value.1)],after)
                else if delimiter = 44 then (parseObjectFuel fuel after false).bind fun rest =>
                  some ((key.1,value.1)::rest.1,rest.2)
                else none
end

def parseValue (input : List Nat) : Option (RawValue × List Nat) := parseValueFuel (RecursionBudget input) input

def parseDocument (input : List Nat) : Option RawValue :=
  (parseValue (scanWhitespace input).2).bind fun parsed =>
    if (scanWhitespace parsed.2).2 = [] then some parsed.1 else none

def parseDocumentBytes (bytes : Bytes) : Option RawValue :=
  (decodeUtf8 bytes).bind parseDocument

theorem parse_value_fuel_zero (input : List Nat) : parseValueFuel 0 input = none := rfl

theorem parse_array_fuel_zero (input : List Nat) (allowEmpty : Bool) : parseArrayFuel 0 input allowEmpty = none := rfl

theorem parse_object_fuel_zero (input : List Nat) (allowEmpty : Bool) : parseObjectFuel 0 input allowEmpty = none := rfl

theorem primitive_value_dispatch (fuel : Nat) (first : Nat) (tail : List Nat)
    (notArray : first ≠ 91) (notObject : first ≠ 123) :
    parseValueFuel (fuel+1) (first::tail) = decodePrimitive (first::tail) := by
  simp only [parseValueFuel,if_neg notArray,if_neg notObject]

theorem byte_parser_composition (bytes : Bytes) (value : RawValue) :
    parseDocumentBytes bytes = some value ↔ ∃ input, StreamMeaning bytes input ∧ parseDocument input = some value := by
  simp only [parseDocumentBytes,Option.bind_eq_some_iff,decode_utf8_exact]

#print axioms parse_value_fuel_zero
#print axioms parse_array_fuel_zero
#print axioms parse_object_fuel_zero
#print axioms primitive_value_dispatch
#print axioms byte_parser_composition
end RelationalSuccessor.CandidateJsonParser
