import DigestMeaning
set_option autoImplicit false
namespace RelationalSuccessor.CandidateDigest

def extendSchedule : Nat → Words → Words
  | 0, seed => seed
  | n+1, seed => extendSchedule n (seed ++ [nextWord seed])
def runRound (k w : UInt32) (s : State) : State :=
  let t1 := s.h + large1 s.e + choose s.e s.f s.g + k + w
  let t2 := large0 s.a + majority s.a s.b s.c
  ⟨t1+t2,s.a,s.b,s.c,s.d+t1,s.e,s.f,s.g⟩
def runRounds : List (UInt32 × UInt32) → State → State
  | [], s => s
  | (k,w)::rest, s => runRounds rest (runRound k w s)
def runBlock (block : Bytes) (s : State) : Option State :=
  if block.length=64 then
    some (addState s (runRounds (constants.zip (extendSchedule 48 (seedWords block))) s))
  else none
def runMessage : List Bytes → State → Option State
  | [], s => some s
  | block::rest, s => (runBlock block s).bind (runMessage rest)
def zeroCount (length : Nat) : Nat :=
  if length%64<56 then 55-length%64 else 119-length%64
def pad (input : Bytes) : Option Bytes :=
  if input.length < 2^61 then
    some (input ++ [128] ++ List.replicate (zeroCount input.length) 0 ++ beBytes 8 (input.length*8))
  else none

def splitBlocks (input : Bytes) : Option (List Bytes) :=
  if input=[] then some []
  else if _enough : 64 ≤ input.length then
    (splitBlocks (input.drop 64)).map fun blocks => input.take 64 :: blocks
  else none
termination_by input.length
decreasing_by simp only [List.length_drop]; omega

def digestBytes (input : Bytes) : Option String :=
  (pad input).bind fun padded => (splitBlocks padded).bind fun blocks =>
    (runMessage blocks initial).map stateHex
end RelationalSuccessor.CandidateDigest
