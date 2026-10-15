import Utf8Meaning
set_option autoImplicit false
set_option maxRecDepth 8192
namespace RelationalSuccessor.CandidateJsonBytes

def decodeScalar : Bytes → Option (Nat × Bytes)
  | [] => none
  | a::rest =>
    if a.toNat < 128 then some (a.toNat,rest) else
      match rest with
      | [] => none
      | b::tail =>
        if TwoFirst a ∧ TailByte b then some (value2 a b,tail) else
          match tail with
          | [] => none
          | c::tail' =>
            if ThreeFirst a b ∧ TailByte b ∧ TailByte c then some (value3 a b c,tail') else
              match tail' with
              | [] => none
              | d::tail'' =>
                if FourFirst a b ∧ TailByte b ∧ TailByte c ∧ TailByte d then some (value4 a b c d,tail'') else none

def PrefixMeaning (bytes : Bytes) (value : Nat) (remaining : Bytes) : Prop :=
  ∃ word, bytes = word ++ remaining ∧ WordMeaning word value

theorem decode_scalar_sound (bytes : Bytes) (value : Nat) (remaining : Bytes)
    (decoded : decodeScalar bytes = some (value,remaining)) : PrefixMeaning bytes value remaining := by
  cases bytes with
  | nil => simp [decodeScalar] at decoded
  | cons a rest =>
    simp only [decodeScalar] at decoded
    split at decoded
    · rename_i ascii; cases decoded; exact ⟨[a],rfl,.one a ascii⟩
    · cases rest with
      | nil => simp at decoded
      | cons b tail =>
        dsimp only at decoded
        split at decoded
        · rename_i good
          have pair := Option.some.inj decoded
          have sameValue : value2 a b = value := congrArg Prod.fst pair
          have sameRest : tail = remaining := congrArg Prod.snd pair
          refine ⟨[a,b],?_,?_⟩
          · change a::b::tail = a::b::remaining
            rw [sameRest]
          · exact sameValue ▸ .two a b good.1 good.2
        · cases tail with
          | nil => simp at decoded
          | cons c tail' =>
            dsimp only at decoded
            split at decoded
            · rename_i good
              have pair := Option.some.inj decoded
              have sameValue : value3 a b c = value := congrArg Prod.fst pair
              have sameRest : tail' = remaining := congrArg Prod.snd pair
              refine ⟨[a,b,c],?_,?_⟩
              · change a::b::c::tail' = a::b::c::remaining
                rw [sameRest]
              · exact sameValue ▸ .three a b c good.1 good.2.1 good.2.2
            · cases tail' with
              | nil => simp at decoded
              | cons d tail'' =>
                dsimp only at decoded
                split at decoded
                · rename_i good
                  have pair := Option.some.inj decoded
                  have sameValue : value4 a b c d = value := congrArg Prod.fst pair
                  have sameRest : tail'' = remaining := congrArg Prod.snd pair
                  refine ⟨[a,b,c,d],?_,?_⟩
                  · change a::b::c::d::tail'' = a::b::c::d::remaining
                    rw [sameRest]
                  · exact sameValue ▸ .four a b c d good.1 good.2.1 good.2.2.1 good.2.2.2
                · simp at decoded

theorem decode_word_complete (word : Bytes) (value : Nat) (remaining : Bytes)
    (meaning : WordMeaning word value) : decodeScalar (word ++ remaining) = some (value,remaining) := by
  cases meaning with
  | one a ascii => simp [decodeScalar,ascii]
  | two a b first tail =>
    have noAscii : ¬ a.toNat < 128 := by unfold TwoFirst at first; omega
    simp [decodeScalar,noAscii,first,tail]
  | three a b c first tb tc =>
    have noAscii : ¬ a.toNat < 128 := by unfold ThreeFirst at first; omega
    have noTwo : ¬ TwoFirst a := by
      intro two; unfold TwoFirst ThreeFirst at *; omega
    simp [decodeScalar,noAscii,noTwo,first,tb,tc]
  | four a b c d first tb tc td =>
    have noAscii : ¬ a.toNat < 128 := by unfold FourFirst at first; omega
    have noTwo : ¬ TwoFirst a := by
      intro two; unfold TwoFirst FourFirst at *; omega
    have noThree : ¬ ThreeFirst a b := by
      intro three; unfold ThreeFirst FourFirst at *; omega
    simp [decodeScalar,noAscii,noTwo,noThree,first,tb,tc,td]

theorem decode_scalar_exact (bytes : Bytes) (value : Nat) (remaining : Bytes) :
    decodeScalar bytes = some (value,remaining) ↔ PrefixMeaning bytes value remaining := by
  constructor
  · exact decode_scalar_sound bytes value remaining
  · rintro ⟨word,same,meaning⟩; rw [same]; exact decode_word_complete word value remaining meaning

theorem decoded_scalar_and_progress (bytes : Bytes) (value : Nat) (remaining : Bytes)
    (decoded : decodeScalar bytes = some (value,remaining)) :
    Scalar value ∧ remaining.length < bytes.length := by
  rcases decode_scalar_sound bytes value remaining decoded with ⟨word,same,meaning⟩
  have length := (word_length_bounds word value meaning).1
  exact ⟨word_denotes_scalar word value meaning,by rw [same,List.length_append]; omega⟩

theorem prefix_meaning_unique (bytes : Bytes) (a b : Nat) (restA restB : Bytes)
    (left : PrefixMeaning bytes a restA) (right : PrefixMeaning bytes b restB) : a = b ∧ restA = restB := by
  have equal := ((decode_scalar_exact bytes a restA).mpr left).symm.trans ((decode_scalar_exact bytes b restB).mpr right)
  have pair := Option.some.inj equal
  exact ⟨congrArg Prod.fst pair,congrArg Prod.snd pair⟩

#print axioms decode_scalar_sound
#print axioms decode_word_complete
#print axioms decode_scalar_exact
#print axioms decoded_scalar_and_progress
#print axioms prefix_meaning_unique
end RelationalSuccessor.CandidateJsonBytes
