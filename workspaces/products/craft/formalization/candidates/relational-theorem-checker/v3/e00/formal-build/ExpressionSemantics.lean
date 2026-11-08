namespace RelationalExtensions.Expression

inductive Truth where
  | yes | no | unknown
  deriving DecidableEq, Repr

structure Ref where
  id : String
  version : String
  deriving DecidableEq, Repr

structure Frame where
  profile : String
  context : Ref
  subject : Ref
  target : Ref
  scope : String
  epoch : Nat
  deriving DecidableEq, Repr

structure Key where
  frame : Frame
  condition : Ref
  deriving DecidableEq, Repr

inductive Expr where
  | atom (condition : Ref)
  | conj (left right : Expr)
  | disj (left right : Expr)
  | neg (operand : Expr)
  deriving DecidableEq, Repr

def tAnd : Truth → Truth → Truth
  | .no, _ => .no
  | _, .no => .no
  | .yes, .yes => .yes
  | _, _ => .unknown

def tOr : Truth → Truth → Truth
  | .yes, _ => .yes
  | _, .yes => .yes
  | .no, .no => .no
  | _, _ => .unknown

def tNot : Truth → Truth
  | .yes => .no
  | .no => .yes
  | .unknown => .unknown

def rails : Truth → Bool × Bool
  | .yes => (true, false)
  | .no => (false, true)
  | .unknown => (false, false)

-- Independent meaning: conjunction intersects positive support and unions
-- negative support; disjunction does the opposite, negation swaps support.
def meaning (frame : Frame) (env : Key → Truth) : Expr → Bool × Bool
  | .atom c => rails (env ⟨frame, c⟩)
  | .conj l r =>
    let a := meaning frame env l
    let b := meaning frame env r
    (a.1 && b.1, a.2 || b.2)
  | .disj l r =>
    let a := meaning frame env l
    let b := meaning frame env r
    (a.1 || b.1, a.2 && b.2)
  | .neg e =>
    let a := meaning frame env e
    (a.2, a.1)

def evaluate (frame : Frame) (env : Key → Truth) : Expr → Truth
  | .atom c => env ⟨frame, c⟩
  | .conj l r => tAnd (evaluate frame env l) (evaluate frame env r)
  | .disj l r => tOr (evaluate frame env l) (evaluate frame env r)
  | .neg e => tNot (evaluate frame env e)

theorem and_table (a b : Truth) :
    rails (tAnd a b) = ((rails a).1 && (rails b).1, (rails a).2 || (rails b).2) := by
  cases a <;> cases b <;> rfl

theorem or_table (a b : Truth) :
    rails (tOr a b) = ((rails a).1 || (rails b).1, (rails a).2 && (rails b).2) := by
  cases a <;> cases b <;> rfl

theorem not_table (a : Truth) : rails (tNot a) = ((rails a).2, (rails a).1) := by
  cases a <;> rfl

theorem evaluation_denotes (frame : Frame) (env : Key → Truth) (e : Expr) :
    rails (evaluate frame env e) = meaning frame env e := by
  induction e with
  | atom c => rfl
  | conj l r hl hr => simpa [evaluate, meaning, hl, hr] using and_table (evaluate frame env l) (evaluate frame env r)
  | disj l r hl hr => simpa [evaluate, meaning, hl, hr] using or_table (evaluate frame env l) (evaluate frame env r)
  | neg e he => simpa [evaluate, meaning, he] using not_table (evaluate frame env e)

theorem positive_iff_yes (t : Truth) : (rails t).1 = true ↔ t = .yes := by
  cases t <;> simp [rails]

def active (frame : Frame) (env : Key → Truth) (e : Expr) (potential : List String) : List String :=
  if evaluate frame env e = .yes then potential else []

theorem activation_exact (frame : Frame) (env : Key → Truth) (e : Expr)
    (potential : List String) (origin : String) :
    origin ∈ active frame env e potential ↔ origin ∈ potential ∧ (meaning frame env e).1 = true := by
  have equation := congrArg Prod.fst (evaluation_denotes frame env e)
  rw [← equation, positive_iff_yes]
  by_cases h : evaluate frame env e = .yes <;> simp [active, h]

theorem atom_exact_key (frame : Frame) (env : Key → Truth) (c : Ref) :
    evaluate frame env (.atom c) = env ⟨frame, c⟩ := rfl

def lookup (entries : List (Key × Truth)) (query : Key) : Truth :=
  match entries with
  | [] => .unknown
  | (key, value) :: rest => if key = query then value else lookup rest query

theorem missing_unknown (entries : List (Key × Truth)) (query : Key)
    (missing : ∀ pair ∈ entries, pair.1 ≠ query) : lookup entries query = .unknown := by
  induction entries with
  | nil => rfl
  | cons entry rest ih =>
    have absent : entry.1 ≠ query := missing entry (by simp)
    have tail : ∀ pair ∈ rest, pair.1 ≠ query := fun pair member => missing pair (by simp [member])
    simpa [lookup, absent] using ih tail

theorem unknown_not_negative : tNot .unknown = .unknown := rfl

#print axioms evaluation_denotes
#print axioms activation_exact
#print axioms atom_exact_key
#print axioms missing_unknown
#print axioms unknown_not_negative
end RelationalExtensions.Expression
