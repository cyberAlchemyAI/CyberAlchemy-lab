import Std
set_option autoImplicit false
namespace RelationalSuccessor.CandidateDigest
abbrev Bytes := List UInt8
abbrev Words := List UInt32
structure State where
  a : UInt32
  b : UInt32
  c : UInt32
  d : UInt32
  e : UInt32
  f : UInt32
  g : UInt32
  h : UInt32
  deriving DecidableEq, Repr

def initial : State := ⟨0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
  0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19⟩
def constants : Words := [
  0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
  0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
  0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
  0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
  0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
  0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
  0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
  0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2]
def rotate (x : UInt32) (n : Nat) : UInt32 :=
  (x >>> UInt32.ofNat n) ||| (x <<< UInt32.ofNat (32-n))
def large0 (x : UInt32) : UInt32 := rotate x 2 ^^^ rotate x 13 ^^^ rotate x 22
def large1 (x : UInt32) : UInt32 := rotate x 6 ^^^ rotate x 11 ^^^ rotate x 25
def small0 (x : UInt32) : UInt32 := rotate x 7 ^^^ rotate x 18 ^^^ (x >>> 3)
def small1 (x : UInt32) : UInt32 := rotate x 17 ^^^ rotate x 19 ^^^ (x >>> 10)
def choose (x y z : UInt32) : UInt32 := (x &&& y) ^^^ ((~~~x) &&& z)
def majority (x y z : UInt32) : UInt32 := (x &&& y) ^^^ (x &&& z) ^^^ (y &&& z)
def nextWord (acc : Words) : UInt32 :=
  small1 (acc.getD (acc.length-2) 0) + acc.getD (acc.length-7) 0 +
    small0 (acc.getD (acc.length-15) 0) + acc.getD (acc.length-16) 0
-- The schedule derivation has no call to its executable loop.
inductive ScheduleMeaning : Nat → Words → Words → Prop
  | done (seed : Words) : ScheduleMeaning 0 seed seed
  | step {n : Nat} {seed result : Words}
      (tail : ScheduleMeaning n (seed ++ [nextWord seed]) result) :
      ScheduleMeaning (n+1) seed result

def beBytes (width value : Nat) : Bytes :=
  (List.range width).map fun i => UInt8.ofNat ((value / 256^(width-1-i)) % 256)
def PaddingMeaning (input padded : Bytes) : Prop := input.length < 2^61 ∧
  ∃ k : Nat, k < 64 ∧ (input.length+1+k+8)%64=0 ∧
    padded = input ++ [128] ++ List.replicate k 0 ++ beBytes 8 (input.length*8)
-- Independent ordered lossless block partition.
inductive BlocksMeaning : Bytes → List Bytes → Prop
  | nil : BlocksMeaning [] []
  | cons {block rest : Bytes} {blocks : List Bytes}
      (width : block.length = 64) (tail : BlocksMeaning rest blocks) :
      BlocksMeaning (block ++ rest) (block :: blocks)
def wordAt (block : Bytes) (i : Nat) : UInt32 := UInt32.ofNat (
  (block.getD (4*i) 0).toNat * 16777216 +
  (block.getD (4*i+1) 0).toNat * 65536 +
  (block.getD (4*i+2) 0).toNat * 256 + (block.getD (4*i+3) 0).toNat)
def seedWords (block : Bytes) : Words := (List.range 16).map (wordAt block)
def RoundMeaning (k w : UInt32) (s out : State) : Prop :=
  ∃ t1 t2 : UInt32,
    t1 = s.h + large1 s.e + choose s.e s.f s.g + k + w ∧
    t2 = large0 s.a + majority s.a s.b s.c ∧
    out = ⟨t1+t2,s.a,s.b,s.c,s.d+t1,s.e,s.f,s.g⟩
inductive RoundsMeaning : List (UInt32 × UInt32) → State → State → Prop
  | done (s : State) : RoundsMeaning [] s s
  | step {k w : UInt32} {pairs : List (UInt32 × UInt32)} {s mid out : State}
      (head : RoundMeaning k w s mid) (tail : RoundsMeaning pairs mid out) :
      RoundsMeaning ((k,w)::pairs) s out

def addState (x y : State) : State :=
  ⟨x.a+y.a,x.b+y.b,x.c+y.c,x.d+y.d,x.e+y.e,x.f+y.f,x.g+y.g,x.h+y.h⟩
def BlockMeaning (block : Bytes) (s out : State) : Prop := block.length=64 ∧
  ∃ schedule working, ScheduleMeaning 48 (seedWords block) schedule ∧
    RoundsMeaning (constants.zip schedule) s working ∧ out=addState s working
inductive MessageMeaning : List Bytes → State → State → Prop
  | done (s : State) : MessageMeaning [] s s
  | step {block : Bytes} {blocks : List Bytes} {s mid out : State}
      (head : BlockMeaning block s mid) (tail : MessageMeaning blocks mid out) :
      MessageMeaning (block::blocks) s out

def hexDigit (n : Nat) : Char := Char.ofNat (if n<10 then 48+n else 87+n)
def wordHex (w : UInt32) : List Char :=
  (List.range 8).map fun i => hexDigit ((w.toNat / 16^(7-i)) % 16)
def stateHex (s : State) : String := String.ofList
  ([s.a,s.b,s.c,s.d,s.e,s.f,s.g,s.h].flatMap wordHex)
def HexCharMeaning (c : Char) : Prop := (48≤c.toNat ∧ c.toNat≤57) ∨ (97≤c.toNat ∧ c.toNat≤102)
instance (c : Char) : Decidable (HexCharMeaning c) := by unfold HexCharMeaning; infer_instance
def HexMeaning (digest : String) : Prop := digest.length=64 ∧ ∀ c ∈ digest.toList, HexCharMeaning c
instance (digest : String) : Decidable (HexMeaning digest) := by unfold HexMeaning; infer_instance
def DigestMeaning (input : Bytes) (digest : String) : Prop :=
  ∃ padded blocks finalState, PaddingMeaning input padded ∧ BlocksMeaning padded blocks ∧
    MessageMeaning blocks initial finalState ∧ digest = stateHex finalState
end RelationalSuccessor.CandidateDigest
