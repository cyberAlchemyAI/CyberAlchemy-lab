import Std
namespace RelationalExtensions.Canonical
-- One structural tree avoids well-founded mutual-function reduction overhead.
-- Canonical typing admits nil/cons only inside arrays and field only inside records.
inductive IR where
  | null | natural (n : Nat) | boolean (b : Bool) | text (s : List Nat)
  | array (xs : IR) | record (fields : IR)
  | nil | cons (head tail : IR) | field (key : List Nat) (value tail : IR)
  deriving DecidableEq, Repr
inductive Meaning where
  | null | natural (n : Nat) | boolean (b : Bool) | scalars (s : List Nat)
  | array (xs : Meaning) | record (fields : Meaning)
  | nil | cons (head tail : Meaning) | field (key : List Nat) (value tail : Meaning)
  deriving DecidableEq, Repr
def validScalar (n : Nat) : Bool := decide (n ≤ 1114111 ∧ (n < 55296 ∨ 57344 ≤ n))
def validScalars (ns : List Nat) : Bool := ns.all validScalar
noncomputable def denote : IR → Meaning := IR.rec
  (motive := fun _ => Meaning)
  .null (fun n => .natural n) (fun b => .boolean b) (fun s => .scalars s)
  (fun _ ih => .array ih) (fun _ ih => .record ih) .nil
  (fun _ _ ihx ihxs => .cons ihx ihxs)
  (fun k _ _ ihv ihfs => .field k ihv ihfs)
def orderedAfter (key : List Nat) : IR → Bool
  | .nil => true
  | .field next _ _ => decide (compare key next = .lt)
  | _ => false
-- Three independently checked shapes: JSON value, array spine, record spine.
noncomputable def checks : IR → Bool × Bool × Bool := IR.rec
  (motive := fun _ => Bool × Bool × Bool)
  (true,false,false) (fun _ => (true,false,false)) (fun _ => (true,false,false))
  (fun ns => (validScalars ns,false,false))
  (fun _ cx => (cx.2.1,false,false))
  (fun _ cf => (cf.2.2,false,false))
  (false,true,true)
  (fun _ _ cx cxs => (false,cx.1 && cxs.2.1,false))
  (fun k _ fs cv cfs => (false,false,validScalars k && cv.1 && cfs.2.2 && orderedAfter k fs))
noncomputable def canonical (ir : IR) : Bool := (checks ir).1
end RelationalExtensions.Canonical
