import Init

namespace Inference

inductive ValueSort where
  | reference | effect | scope | epoch | text
  deriving DecidableEq, Repr
inductive Value where
  | reference (id version : String)
  | effect (name : String)
  | scope (name : String)
  | epoch (number : Nat)
  | text (content : String)
  deriving DecidableEq, Repr
def Value.sort : Value → ValueSort
  | .reference _ _ => .reference
  | .effect _ => .effect
  | .scope _ => .scope
  | .epoch _ => .epoch
  | .text _ => .text
def Value.Valid : Value → Prop
  | .reference id version => id ≠ "" ∧ version ≠ ""
  | .effect name | .scope name | .text name => name ≠ ""
  | .epoch _ => True
instance (v : Value) : Decidable v.Valid := by cases v <;> simp [Value.Valid] <;> infer_instance

structure Key where
  id : String
  version : String
  hash : String
  deriving DecidableEq, Repr
abbrev Key.Valid (k : Key) : Prop := k.id ≠ "" ∧ k.version ≠ "" ∧ k.hash ≠ ""
inductive Role where
  | ordinary | protectedConclusion | checkedRoot | rootCarrier
  deriving DecidableEq, Repr
structure Predicate where
  key : Key
  sorts : List ValueSort
  role : Role
  deriving DecidableEq, Repr
structure Atom where
  predicate : Key
  values : List Value
  deriving DecidableEq, Repr
inductive Term where
  | slot (index : Nat)
  | constant (value : Value)
  deriving DecidableEq, Repr
structure Pattern where
  predicate : Key
  terms : List Term
  deriving DecidableEq, Repr
structure Rule where
  key : Key
  variables : List ValueSort
  head : Pattern
  body : List Pattern
  deriving DecidableEq, Repr
structure Theory where
  domain : List Value
  predicates : List Predicate
  rules : List Rule
  roots : List (List Value)
  epoch : Nat
  deriving DecidableEq, Repr

def rootValueSorts : List ValueSort := [.reference, .effect, .scope, .epoch]
def rootedRole (role : Role) : Bool := role != .ordinary
abbrev AtomValid (T : Theory) (a : Atom) : Prop :=
  ∃ p ∈ T.predicates, p.key = a.predicate ∧ a.values.map Value.sort = p.sorts ∧
    ∀ v ∈ a.values, v ∈ T.domain
instance (T : Theory) (a : Atom) : Decidable (AtomValid T a) := by unfold AtomValid; infer_instance

abbrev TermValid (T : Theory) (variables : List ValueSort) (term : Term) (sort : ValueSort) : Prop :=
  match term with
  | .slot i => variables[i]? = some sort
  | .constant v => v ∈ T.domain ∧ v.sort = sort
instance (T : Theory) (variables : List ValueSort) (term : Term) (sort : ValueSort) :
    Decidable (TermValid T variables term sort) := by cases term <;> unfold TermValid <;> infer_instance
abbrev PatternValid (T : Theory) (variables : List ValueSort) (pattern : Pattern) : Prop :=
  ∃ p ∈ T.predicates, p.key = pattern.predicate ∧ pattern.terms.length = p.sorts.length ∧
    ∀ pair ∈ pattern.terms.zip p.sorts, TermValid T variables pair.1 pair.2
instance (T : Theory) (variables : List ValueSort) (pattern : Pattern) :
    Decidable (PatternValid T variables pattern) := by unfold PatternValid; infer_instance
def usedSlots (patterns : List Pattern) : List Nat :=
  patterns.flatMap fun p => p.terms.filterMap fun t => match t with
    | .slot i => some i
    | .constant _ => none
abbrev RuleValid (T : Theory) (r : Rule) : Prop :=
  r.key.Valid ∧ PatternValid T r.variables r.head ∧
  (∀ p ∈ r.body, PatternValid T r.variables p) ∧
  (∀ i ∈ List.range r.variables.length, i ∈ usedSlots r.body) ∧
  ∀ p ∈ T.predicates, p.key = r.head.predicate → p.role ≠ .checkedRoot
instance (T : Theory) (r : Rule) : Decidable (RuleValid T r) := by
  unfold RuleValid PatternValid Key.Valid
  infer_instance
abbrev PredicateValid (p : Predicate) : Prop :=
  p.key.Valid ∧ (rootedRole p.role = true → p.sorts = rootValueSorts) ∧
  (p.role = .protectedConclusion ↔ p.key.id = "Admitted") ∧
  (p.role = .checkedRoot ↔ p.key.id = "CheckedRoot")
instance (p : Predicate) : Decidable (PredicateValid p) := by unfold PredicateValid Key.Valid; infer_instance
abbrev TheoryValid (T : Theory) : Prop :=
  T.domain ≠ [] ∧ T.domain.Nodup ∧ (∀ v ∈ T.domain, v.Valid) ∧
  (T.predicates.map fun p => p.key.id).Nodup ∧
  (∀ p ∈ T.predicates, PredicateValid p) ∧
  (T.rules.map Rule.key).Nodup ∧ (∀ r ∈ T.rules, RuleValid T r) ∧
  ∀ root ∈ T.roots, root.map Value.sort = rootValueSorts ∧
    root[3]? = some (.epoch T.epoch) ∧ ∀ v ∈ root, v ∈ T.domain
instance (T : Theory) : Decidable (TheoryValid T) := by unfold TheoryValid; infer_instance
abbrev InitialValid (T : Theory) (F : List Atom) : Prop :=
  F.Nodup ∧ ∀ a ∈ F, AtomValid T a ∧
    ∀ p ∈ T.predicates, p.key = a.predicate → rootedRole p.role = true → a.values ∈ T.roots
instance (T : Theory) (F : List Atom) : Decidable (InitialValid T F) := by unfold InitialValid; infer_instance

def substitute (values : List Value) : Term → Option Value
  | .slot i => values[i]?
  | .constant v => some v
def instantiate (values : List Value) (pattern : Pattern) : Option Atom := do
  let args ← pattern.terms.mapM (substitute values)
  pure { predicate := pattern.predicate, values := args }
def instantiateBody (values : List Value) (patterns : List Pattern) : Option (List Atom) :=
  patterns.mapM (instantiate values)
abbrev SubstitutionValid (T : Theory) (r : Rule) (values : List Value) : Prop :=
  values.map Value.sort = r.variables ∧ ∀ v ∈ values, v ∈ T.domain
structure GroundInstance where
  rule : Key
  substitution : List Value
  head : Atom
  body : List Atom
  deriving DecidableEq, Repr
-- Membership in an enumeration is deliberately not the definition of validity.
-- I03 must prove enumeration complete for these independently defined instances.
abbrev ValidInstance (T : Theory) (i : GroundInstance) : Prop :=
  ∃ r ∈ T.rules, r.key = i.rule ∧ SubstitutionValid T r i.substitution ∧
    instantiate i.substitution r.head = some i.head ∧
    instantiateBody i.substitution r.body = some i.body
instance (T : Theory) (i : GroundInstance) : Decidable (ValidInstance T i) := by
  unfold ValidInstance SubstitutionValid
  infer_instance

inductive Derivable (T : Theory) (F : List Atom) : Atom → Prop
  | base {a} : a ∈ F → Derivable T F a
  | apply (i : GroundInstance) : ValidInstance T i →
      (∀ a ∈ i.body, Derivable T F a) → Derivable T F i.head

abbrev Closed (T : Theory) (F C : List Atom) : Prop :=
  (∀ a ∈ F, a ∈ C) ∧
  ∀ i : GroundInstance, ValidInstance T i → (∀ a ∈ i.body, a ∈ C) → i.head ∈ C

theorem derivable_in_every_closed_model {T F C a} (closed : Closed T F C)
    (derived : Derivable T F a) : a ∈ C := by
  induction derived with
  | base h => exact closed.1 _ h
  | apply i valid _ ih => exact closed.2 i valid ih

end Inference
