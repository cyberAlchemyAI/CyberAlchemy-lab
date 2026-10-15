import Utf8Prefix
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonBytes

def decodeUtf8Fuel : Nat → Bytes → Option (List Nat)
  | 0,_ => none
  | fuel+1,bytes =>
    if bytes = [] then some [] else
      match decodeScalar bytes with
      | none => none
      | some (value,remaining) =>
        match decodeUtf8Fuel fuel remaining with
        | none => none
        | some values => some (value::values)

theorem decode_utf8_fuel_sound (fuel : Nat) (bytes : Bytes) (values : List Nat)
    (decoded : decodeUtf8Fuel fuel bytes = some values) : StreamMeaning bytes values := by
  induction fuel generalizing bytes values with
  | zero => simp [decodeUtf8Fuel] at decoded
  | succ fuel ih =>
    cases bytes with
    | nil => simp [decodeUtf8Fuel] at decoded; subst values; exact .nil
    | cons a tail =>
      have nonempty : (a::tail : Bytes) ≠ [] := by simp
      simp only [decodeUtf8Fuel,if_neg nonempty] at decoded
      cases head : decodeScalar (a::tail) with
      | none => simp [head] at decoded
      | some pair =>
        rcases pair with ⟨value,remaining⟩
        simp only [head] at decoded
        cases rest : decodeUtf8Fuel fuel remaining with
        | none => simp [rest] at decoded
        | some output =>
          simp only [rest,Option.some.injEq] at decoded
          subst values
          rcases decode_scalar_sound (a::tail) value remaining head with ⟨word,same,meaning⟩
          rw [same]
          exact .cons word remaining value output meaning (ih remaining output rest)

theorem decode_utf8_fuel_complete (bytes : Bytes) (values : List Nat) (meaning : StreamMeaning bytes values)
    (fuel : Nat) (adequate : bytes.length < fuel) : decodeUtf8Fuel fuel bytes = some values := by
  induction meaning generalizing fuel with
  | nil =>
    cases fuel with
    | zero => simp at adequate
    | succ fuel => simp [decodeUtf8Fuel]
  | cons word rest value values head tail ih =>
    have wordLength := (word_length_bounds word value head).1
    cases fuel with
    | zero => simp at adequate
    | succ fuel =>
      have bound : rest.length < fuel := by simp only [List.length_append] at adequate; omega
      have nonempty : word ++ rest ≠ [] := by
        intro same
        have length := congrArg List.length same
        simp only [List.length_append,List.length_nil] at length
        omega
      simp only [decodeUtf8Fuel,if_neg nonempty,decode_word_complete word value rest head,ih fuel bound]

def decodeUtf8 (bytes : Bytes) : Option (List Nat) := decodeUtf8Fuel (bytes.length+1) bytes

theorem decode_utf8_exact (bytes : Bytes) (values : List Nat) :
    decodeUtf8 bytes = some values ↔ StreamMeaning bytes values := by
  constructor
  · exact decode_utf8_fuel_sound (bytes.length+1) bytes values
  · intro meaning; exact decode_utf8_fuel_complete bytes values meaning (bytes.length+1) (by omega)

theorem decoded_stream_scalars (bytes : Bytes) (values : List Nat)
    (decoded : decodeUtf8 bytes = some values) : ∀ value ∈ values, Scalar value :=
  stream_scalar_values bytes values ((decode_utf8_exact bytes values).mp decoded)

theorem stream_meaning_unique (bytes : Bytes) (left right : List Nat)
    (ml : StreamMeaning bytes left) (mr : StreamMeaning bytes right) : left = right := by
  exact Option.some.inj (((decode_utf8_exact bytes left).mpr ml).symm.trans ((decode_utf8_exact bytes right).mpr mr))

theorem invalid_utf8_exact (bytes : Bytes) : decodeUtf8 bytes = none ↔ ¬ ∃ values, StreamMeaning bytes values := by
  constructor
  · intro refused represented
    rcases represented with ⟨values,meaning⟩
    have decoded := (decode_utf8_exact bytes values).mpr meaning
    rw [refused] at decoded
    cases decoded
  · intro invalid
    cases decoded : decodeUtf8 bytes with
    | none => rfl
    | some values => exact False.elim (invalid ⟨values,(decode_utf8_exact bytes values).mp decoded⟩)

#print axioms decode_utf8_fuel_sound
#print axioms decode_utf8_fuel_complete
#print axioms decode_utf8_exact
#print axioms decoded_stream_scalars
#print axioms stream_meaning_unique
#print axioms invalid_utf8_exact
end RelationalSuccessor.CandidateJsonBytes
