import Std
namespace RelationalExtensions.Canonical
-- One structural tree avoids well-founded mutual-function reduction overhead.
-- Canonical typing admits nil/cons only inside arrays and field only inside records.
inductive IR where
  | null | natural (n : Nat) | boolean (b : Bool) | text (s : String)
  | array (xs : IR) | record (fields : IR)
  | nil | cons (head tail : IR) | field (key : String) (value tail : IR)
  deriving DecidableEq, Repr
inductive Meaning where
  | null | natural (n : Nat) | boolean (b : Bool) | scalars (s : List Nat)
  | array (xs : Meaning) | record (fields : Meaning)
  | nil | cons (head tail : Meaning) | field (key : List Nat) (value tail : Meaning)
  deriving DecidableEq, Repr
def scalars (s : String) : List Nat := s.toList.map Char.toNat
def denote : IR → Meaning
  | .null => .null
  | .natural n => .natural n
  | .boolean b => .boolean b
  | .text s => .scalars (scalars s)
  | .array xs => .array (denote xs)
  | .record fs => .record (denote fs)
  | .nil => .nil
  | .cons x xs => .cons (denote x) (denote xs)
  | .field k v fs => .field (scalars k) (denote v) (denote fs)
def orderedAfter (key : String) : IR → Bool
  | .nil => true
  | .field next _ _ => decide (key < next)
  | _ => false
-- Three independently checked shapes: JSON value, array spine, record spine.
def checks : IR → Bool × Bool × Bool
  | .null | .natural _ | .boolean _ | .text _ => (true,false,false)
  | .nil => (false,true,true)
  | .cons x xs => (false,(checks x).1 && (checks xs).2.1,false)
  | .field k v fs => (false,false,(checks v).1 && (checks fs).2.2 && orderedAfter k fs)
  | .array xs => ((checks xs).2.1,false,false)
  | .record fs => ((checks fs).2.2,false,false)
def canonical (ir : IR) : Bool := (checks ir).1
end RelationalExtensions.Canonical
