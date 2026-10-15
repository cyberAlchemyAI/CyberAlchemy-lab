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
noncomputable def denote : IR → Meaning := IR.rec
  (motive := fun _ => Meaning)
  .null (fun n => .natural n) (fun b => .boolean b) (fun s => .scalars (scalars s))
  (fun _ ih => .array ih) (fun _ ih => .record ih) .nil
  (fun _ _ ihx ihxs => .cons ihx ihxs)
  (fun k _ _ ihv ihfs => .field (scalars k) ihv ihfs)
def orderedAfter (key : String) : IR → Bool
  | .nil => true
  | .field next _ _ => decide (key < next)
  | _ => false
-- Three independently checked shapes: JSON value, array spine, record spine.
noncomputable def checks : IR → Bool × Bool × Bool := IR.rec
  (motive := fun _ => Bool × Bool × Bool)
  (true,false,false) (fun _ => (true,false,false)) (fun _ => (true,false,false))
  (fun _ => (true,false,false))
  (fun _ cx => (cx.2.1,false,false))
  (fun _ cf => (cf.2.2,false,false))
  (false,true,true)
  (fun _ _ cx cxs => (false,cx.1 && cxs.2.1,false))
  (fun k _ fs cv cfs => (false,false,cv.1 && cfs.2.2 && orderedAfter k fs))
noncomputable def canonical (ir : IR) : Bool := (checks ir).1
end RelationalExtensions.Canonical
