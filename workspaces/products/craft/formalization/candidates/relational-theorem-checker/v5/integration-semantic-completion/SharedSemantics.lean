import ExpressionSemantics

namespace RelationalSuccessor

abbrev Truth := RelationalExtensions.Expression.Truth
open RelationalExtensions.Expression (tAnd tOr tNot rails and_table or_table not_table)

structure RevisionKey where
  owner : String
  artifact : String
  revision : String
  deriving DecidableEq, Repr

structure RevisionRef where
  key : RevisionKey
  digest : String
  deriving DecidableEq, Repr

structure Frame where
  profile : RevisionRef
  subject : RevisionRef
  target : RevisionRef
  context : RevisionRef
  scope : RevisionRef
  snapshot : RevisionRef
  epoch : Nat
  timeDomain : String
  deriving DecidableEq, Repr

inductive Expr where
  | atom (leaf : RevisionRef)
  | conj (left right : Expr)
  | disj (left right : Expr)
  | neg (operand : Expr)
  deriving DecidableEq, Repr

inductive Body where
  | condition (expr : Expr)
  | requirement (criteria : List RevisionRef)
  deriving DecidableEq, Repr

structure Definition where
  ref : RevisionRef
  body : Body
  -- Raw content is retained in addition to its opaque digest. The model does
  -- not prove hashing, byte decoding or authenticity of the owner's review.
  content : List UInt8
  ownerReview : RevisionRef
  deriving DecidableEq, Repr

abbrev Catalog := List Definition

-- This finite predicate describes exact non-equivocation, independently of
-- the lookup algorithm. Faithfully observed approvals are separate context.
def WellFormedCatalog (c : Catalog) : Prop :=
  ∀ a ∈ c, ∀ b ∈ c, a.ref.key = b.ref.key → a = b

def checkedCatalog (c : Catalog) : Bool :=
  c.all fun a => c.all fun b => decide (a.ref.key = b.ref.key → a = b)

theorem catalog_check_exact (c : Catalog) :
    checkedCatalog c = true ↔ WellFormedCatalog c := by
  simp only [checkedCatalog, WellFormedCatalog, List.all_eq_true, decide_eq_true_eq]

def lookup : Catalog → RevisionKey → Option Definition
  | [], _ => none
  | a :: rest, key => if a.ref.key = key then some a else lookup rest key

theorem lookup_sound (c : Catalog) (k : RevisionKey) (d : Definition)
    (h : lookup c k = some d) : d ∈ c ∧ d.ref.key = k := by
  induction c with
  | nil => simp [lookup] at h
  | cons a rest ih =>
    unfold lookup at h
    split at h
    · rename_i hk
      cases h
      exact ⟨by simp, hk⟩
    · have hr := ih h
      exact ⟨by simp [hr.1], hr.2⟩

theorem lookup_complete (c : Catalog) (k : RevisionKey) (d : Definition)
    (wf : WellFormedCatalog c) (hd : d ∈ c) (hk : d.ref.key = k) :
    lookup c k = some d := by
  induction c with
  | nil => simp at hd
  | cons a rest ih =>
    simp only [List.mem_cons] at hd
    unfold lookup
    split
    · rename_i ha
      have heq : a = d := wf a (by simp) d (by simp only [List.mem_cons]; exact hd) (ha.trans hk.symm)
      simp [heq]
    · rename_i ha
      rcases hd with heq | hr
      · subst d; exact False.elim (ha hk)
      · exact ih (by intro x hx y hy hxy; exact wf x (by simp [hx]) y (by simp [hy]) hxy) hr

-- Roots are trusted owner-approval records supplied by the verification
-- context, never populated from proposal approval booleans.
def resolve (roots : List Definition) (c : Catalog) (ref : RevisionRef) : Option Definition :=
  if checkedCatalog c then
    match lookup c ref.key with
    | none => none
    | some d => if d.ref = ref ∧ d ∈ roots then some d else none
  else none

def OwnedDefinition (roots : List Definition) (c : Catalog) (ref : RevisionRef) (d : Definition) : Prop :=
  WellFormedCatalog c ∧ d ∈ c ∧ d.ref = ref ∧ d ∈ roots

theorem resolve_exact (roots : List Definition) (c : Catalog) (ref : RevisionRef) (d : Definition) :
    resolve roots c ref = some d ↔ OwnedDefinition roots c ref d := by
  constructor
  · intro h
    unfold resolve at h
    split at h
    · rename_i hc
      cases hl : lookup c ref.key with
      | none => simp [hl] at h
      | some e =>
        simp only [hl] at h
        split at h
        · rename_i he; cases h
          exact ⟨(catalog_check_exact c).mp hc, (lookup_sound c ref.key d hl).1, he.1, he.2⟩
        · simp at h
    · simp at h
  · rintro ⟨wf, hd, href, root⟩
    have hl := lookup_complete c ref.key d wf hd (congrArg RevisionRef.key href)
    simp [resolve, (catalog_check_exact c).mpr wf, hl, href, root]

theorem resolution_unique (roots : List Definition) (c : Catalog) (ref : RevisionRef) (a b : Definition)
    (ha : resolve roots c ref = some a) (hb : resolve roots c ref = some b) : a = b := by
  have h := ha.symm.trans hb
  exact Option.some.inj h

theorem same_key_same_body (c : Catalog) (a b : Definition)
    (wf : WellFormedCatalog c) (ha : a ∈ c) (hb : b ∈ c) (hk : a.ref.key = b.ref.key) :
    a.body = b.body ∧ a.content = b.content ∧ a.ref.digest = b.ref.digest := by
  have h := wf a ha b hb hk
  subst b
  exact ⟨rfl, rfl, rfl⟩

def LegalCatalogExtension (old next : Catalog) : Prop :=
  WellFormedCatalog old ∧ WellFormedCatalog next ∧ ∀ d ∈ old, d ∈ next

theorem catalog_extension_preserves_binding (roots : List Definition) (old next : Catalog)
    (ref : RevisionRef) (d : Definition) (he : LegalCatalogExtension old next)
    (h : resolve roots old ref = some d) : resolve roots next ref = some d := by
  have hd := (resolve_exact roots old ref d).mp h
  exact (resolve_exact roots next ref d).mpr ⟨he.2.1, he.2.2 d hd.2.1, hd.2.2.1, hd.2.2.2⟩

theorem substitution_breaks_catalog_extension (old next : Catalog) (a b : Definition)
    (ha : a ∈ old) (hb : b ∈ next) (hk : a.ref.key = b.ref.key) (hne : a.body ≠ b.body) :
    ¬ LegalCatalogExtension old next := by
  intro h
  exact hne (congrArg Definition.body (h.2.1 a (h.2.2 a ha) b hb hk))

theorem unapproved_definition_cannot_resolve (roots : List Definition) (c : Catalog)
    (ref : RevisionRef) (d : Definition) (hr : d ∉ roots) : resolve roots c ref ≠ some d := by
  intro h
  exact hr ((resolve_exact roots c ref d).mp h).2.2.2

def expressionMeaning (env : RevisionRef → Truth) : Expr → Bool × Bool
  | .atom leaf => rails (env leaf)
  | .conj l r =>
      let a := expressionMeaning env l; let b := expressionMeaning env r
      (a.1 && b.1, a.2 || b.2)
  | .disj l r =>
      let a := expressionMeaning env l; let b := expressionMeaning env r
      (a.1 || b.1, a.2 && b.2)
  | .neg e => let a := expressionMeaning env e; (a.2, a.1)

def evaluate (env : RevisionRef → Truth) : Expr → Truth
  | .atom leaf => env leaf
  | .conj l r => tAnd (evaluate env l) (evaluate env r)
  | .disj l r => tOr (evaluate env l) (evaluate env r)
  | .neg e => tNot (evaluate env e)

theorem evaluation_denotes (env : RevisionRef → Truth) (e : Expr) :
    rails (evaluate env e) = expressionMeaning env e := by
  induction e with
  | atom leaf => rfl
  | conj l r hl hr => simpa [evaluate, expressionMeaning, hl, hr] using and_table (evaluate env l) (evaluate env r)
  | disj l r hl hr => simpa [evaluate, expressionMeaning, hl, hr] using or_table (evaluate env l) (evaluate env r)
  | neg e he => simpa [evaluate, expressionMeaning, he] using not_table (evaluate env e)

def ownedValue (roots : List Definition) (c : Catalog) (ref : RevisionRef)
    (f : Frame) (env : Frame → RevisionRef → Truth) : Truth :=
  match resolve roots c ref with
  | some d => match d.body with
      | .condition e => evaluate (env f) e
      | .requirement _ => .unknown
  | none => .unknown

def PositiveOwned (roots : List Definition) (c : Catalog) (ref : RevisionRef)
    (f : Frame) (env : Frame → RevisionRef → Truth) : Prop :=
  ∃ d e, OwnedDefinition roots c ref d ∧ d.body = .condition e ∧
    (expressionMeaning (env f) e).1 = true

theorem owned_positive_exact (roots : List Definition) (c : Catalog) (ref : RevisionRef)
    (f : Frame) (env : Frame → RevisionRef → Truth) :
    ownedValue roots c ref f env = .yes ↔ PositiveOwned roots c ref f env := by
  constructor
  · intro h
    unfold ownedValue at h
    cases hd : resolve roots c ref with
    | none => simp [hd] at h
    | some d =>
      cases hb : d.body with
      | requirement cs => simp [hd, hb] at h
      | condition e =>
        have he : evaluate (env f) e = .yes := by simpa [hd, hb] using h
        refine ⟨d, e, (resolve_exact roots c ref d).mp hd, hb, ?_⟩
        rw [← evaluation_denotes, he]
        rfl
  · rintro ⟨d, e, owned, hb, hp⟩
    have hv : evaluate (env f) e = .yes := by
      rw [← evaluation_denotes] at hp
      exact (RelationalExtensions.Expression.positive_iff_yes _).mp hp
    simp [ownedValue, (resolve_exact roots c ref d).mpr owned, hb, hv]

structure Origin where
  subject : RevisionRef
  contract : RevisionRef
  norm : RevisionRef
  inheritance : RevisionRef
  deriving DecidableEq, Repr

def activate (roots : List Definition) (c : Catalog) (ref : RevisionRef)
    (f : Frame) (env : Frame → RevisionRef → Truth) (potential : List Origin) : List Origin :=
  if ownedValue roots c ref f env = .yes then potential else []

theorem activation_exact (roots : List Definition) (c : Catalog) (ref : RevisionRef)
    (f : Frame) (env : Frame → RevisionRef → Truth) (potential : List Origin) (origin : Origin) :
    origin ∈ activate roots c ref f env potential ↔
      origin ∈ potential ∧ PositiveOwned roots c ref f env := by
  unfold activate
  split
  · rename_i h; simp [(owned_positive_exact roots c ref f env).mp h]
  · rename_i h
    have hn : ¬ PositiveOwned roots c ref f env := fun hp => h ((owned_positive_exact roots c ref f env).mpr hp)
    simp [hn]

theorem unknown_never_activates (roots : List Definition) (c : Catalog) (ref : RevisionRef)
    (f : Frame) (env : Frame → RevisionRef → Truth) (potential : List Origin)
    (h : ownedValue roots c ref f env = .unknown) : activate roots c ref f env potential = [] := by
  simp [activate, h]

def ownedCriteria (roots : List Definition) (c : Catalog) (ref : RevisionRef) : Option (List RevisionRef) :=
  match resolve roots c ref with
  | some d => match d.body with
      | .requirement criteria => if criteria ≠ [] ∧ criteria.Nodup then some criteria else none
      | .condition _ => none
  | none => none

def CriteriaMeaning (roots : List Definition) (c : Catalog) (ref : RevisionRef)
    (criteria : List RevisionRef) : Prop :=
  ∃ d, OwnedDefinition roots c ref d ∧ d.body = .requirement criteria ∧ criteria ≠ [] ∧ criteria.Nodup

theorem owned_criteria_exact (roots : List Definition) (c : Catalog) (ref : RevisionRef)
    (criteria : List RevisionRef) : ownedCriteria roots c ref = some criteria ↔ CriteriaMeaning roots c ref criteria := by
  constructor
  · intro h
    unfold ownedCriteria at h
    cases hd : resolve roots c ref with
    | none => simp [hd] at h
    | some d =>
      cases hb : d.body with
      | condition e => simp [hd, hb] at h
      | requirement cs =>
        simp only [hd, hb] at h
        split at h
        · rename_i hc; cases h
          exact ⟨d, (resolve_exact roots c ref d).mp hd, hb, hc.1, hc.2⟩
        · simp at h
  · rintro ⟨d, owned, hb, nonempty, nodup⟩
    simp [ownedCriteria, (resolve_exact roots c ref d).mpr owned, hb, nonempty, nodup]

structure Assessment where
  criterion : RevisionRef
  requirement : RevisionRef
  frame : Frame
  action : RevisionRef
  output : RevisionRef
  value : Truth
  deriving DecidableEq, Repr

-- Exact approved action/output provenance is a trusted-source premise here.
-- The implementation and provenance adapters are later plan units.
def ExactSupport (verified : List Assessment) (required : RevisionRef) (f : Frame)
    (criterion : RevisionRef) : Prop :=
  ∃ e ∈ verified, e.criterion = criterion ∧ e.requirement = required ∧ e.frame = f ∧ e.value = .yes

def supportCheck (verified : List Assessment) (required : RevisionRef) (f : Frame)
    (criterion : RevisionRef) : Bool :=
  verified.any fun e => decide (e.criterion = criterion ∧ e.requirement = required ∧ e.frame = f ∧ e.value = .yes)

theorem support_check_exact (verified : List Assessment) (required : RevisionRef) (f : Frame)
    (criterion : RevisionRef) : supportCheck verified required f criterion = true ↔ ExactSupport verified required f criterion := by
  simp [supportCheck, ExactSupport, List.any_eq_true]

def fulfilled (roots : List Definition) (c : Catalog) (required : RevisionRef) (f : Frame)
    (verified : List Assessment) (submittedCriteria : List RevisionRef) : Bool :=
  match ownedCriteria roots c required with
  | none => false
  | some criteria => decide (submittedCriteria = criteria) && criteria.all (supportCheck verified required f)

def FulfillmentMeaning (roots : List Definition) (c : Catalog) (required : RevisionRef) (f : Frame)
    (verified : List Assessment) (submittedCriteria : List RevisionRef) : Prop :=
  ∃ criteria, CriteriaMeaning roots c required criteria ∧ submittedCriteria = criteria ∧
    ∀ criterion ∈ criteria, ExactSupport verified required f criterion

theorem fulfillment_exact (roots : List Definition) (c : Catalog) (required : RevisionRef)
    (f : Frame) (verified : List Assessment) (submittedCriteria : List RevisionRef) :
    fulfilled roots c required f verified submittedCriteria = true ↔
      FulfillmentMeaning roots c required f verified submittedCriteria := by
  constructor
  · intro h
    unfold fulfilled at h
    cases hc : ownedCriteria roots c required with
    | none => simp [hc] at h
    | some criteria =>
      have hh : submittedCriteria = criteria ∧ ∀ x ∈ criteria, ExactSupport verified required f x := by
        simpa [hc, List.all_eq_true, support_check_exact] using h
      exact ⟨criteria, (owned_criteria_exact roots c required criteria).mp hc, hh.1, hh.2⟩
  · rintro ⟨criteria, meaning, same, all⟩
    simpa [fulfilled, (owned_criteria_exact roots c required criteria).mpr meaning, same, List.all_eq_true, support_check_exact] using all

theorem every_owner_criterion (roots : List Definition) (c : Catalog) (required : RevisionRef)
    (f : Frame) (verified : List Assessment) (submitted : List RevisionRef) (criteria : List RevisionRef)
    (hc : ownedCriteria roots c required = some criteria)
    (h : fulfilled roots c required f verified submitted = true) :
    ∀ criterion ∈ criteria, ExactSupport verified required f criterion := by
  rcases (fulfillment_exact roots c required f verified submitted).mp h with ⟨actual, meaning, hs, he⟩
  have ha := (owned_criteria_exact roots c required actual).mpr meaning
  have eq := Option.some.inj (hc.symm.trans ha)
  simpa [eq] using he

theorem removed_criterion_refuses (roots : List Definition) (c : Catalog) (required : RevisionRef)
    (f : Frame) (verified : List Assessment) (submitted criteria : List RevisionRef)
    (hc : ownedCriteria roots c required = some criteria) (hne : submitted ≠ criteria) :
    fulfilled roots c required f verified submitted = false := by
  simp [fulfilled, hc, hne]

inductive Fact where
  | review | ready
  deriving DecidableEq, Repr

inductive Derivable (seeds : List Fact) : Fact → Prop where
  | seed (fact : Fact) (h : fact ∈ seeds) : Derivable seeds fact
  | reviewToReady : Derivable seeds .review → Derivable seeds .ready
  | readyToReview : Derivable seeds .ready → Derivable seeds .review

theorem cyclic_rules_require_seed (fact : Fact) : ¬ Derivable [] fact := by
  intro h
  induction h with
  | seed fact h => simp at h
  | reviewToReady _ ih => exact ih
  | readyToReview _ ih => exact ih

#print axioms catalog_check_exact
#print axioms lookup_sound
#print axioms lookup_complete
#print axioms resolve_exact
#print axioms resolution_unique
#print axioms same_key_same_body
#print axioms catalog_extension_preserves_binding
#print axioms substitution_breaks_catalog_extension
#print axioms unapproved_definition_cannot_resolve
#print axioms evaluation_denotes
#print axioms owned_positive_exact
#print axioms activation_exact
#print axioms unknown_never_activates
#print axioms owned_criteria_exact
#print axioms support_check_exact
#print axioms fulfillment_exact
#print axioms every_owner_criterion
#print axioms removed_criterion_refuses
#print axioms cyclic_rules_require_seed

end RelationalSuccessor
