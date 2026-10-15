import Std
namespace RelationalExtensions.Canonical
mutual
inductive IR where
  | null | natural (n : Nat) | boolean (b : Bool) | text (s : String)
  | array (xs : Sequence) | record (fields : Fields)
  deriving DecidableEq, Repr
inductive Sequence where
  | nil | cons (head : IR) (tail : Sequence)
  deriving DecidableEq, Repr
inductive Fields where
  | nil | cons (key : String) (value : IR) (tail : Fields)
  deriving DecidableEq, Repr
end
mutual
inductive Meaning where
  | null | natural (n : Nat) | boolean (b : Bool) | scalars (s : List Nat)
  | array (xs : Meanings) | record (fields : NamedMeanings)
  deriving DecidableEq, Repr
inductive Meanings where
  | nil | cons (head : Meaning) (tail : Meanings)
  deriving DecidableEq, Repr
inductive NamedMeanings where
  | nil | cons (key : List Nat) (value : Meaning) (tail : NamedMeanings)
  deriving DecidableEq, Repr
end
def scalars (s : String) : List Nat := s.toList.map Char.toNat
mutual
def denote : IR → Meaning
  | .null => .null
  | .natural n => .natural n
  | .boolean b => .boolean b
  | .text s => .scalars (scalars s)
  | .array xs => .array (denoteSequence xs)
  | .record fs => .record (denoteFields fs)
def denoteSequence : Sequence → Meanings
  | .nil => .nil
  | .cons x xs => .cons (denote x) (denoteSequence xs)
def denoteFields : Fields → NamedMeanings
  | .nil => .nil
  | .cons k v fs => .cons (scalars k) (denote v) (denoteFields fs)
end
def ordered : Fields → Bool
  | .nil => true
  | .cons _ _ .nil => true
  | .cons k _ (.cons next v rest) => decide (k < next) && ordered (.cons next v rest)
mutual
def canonical : IR → Bool
  | .null | .natural _ | .boolean _ | .text _ => true
  | .array xs => canonicalSequence xs
  | .record fs => ordered fs && canonicalFields fs
def canonicalSequence : Sequence → Bool
  | .nil => true
  | .cons x xs => canonical x && canonicalSequence xs
def canonicalFields : Fields → Bool
  | .nil => true
  | .cons _ v fs => canonical v && canonicalFields fs
end
end RelationalExtensions.Canonical
