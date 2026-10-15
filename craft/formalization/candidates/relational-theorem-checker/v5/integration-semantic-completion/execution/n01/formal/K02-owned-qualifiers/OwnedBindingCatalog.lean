import FiniteSourceCatalog

set_option autoImplicit false
namespace RelationalSuccessor.CandidateOwnedBindings
open RelationalSuccessor
abbrev FArtifact (α : Type) := CandidateFiniteSourceCatalog.Artifact α
abbrev UniqueBy {τ κ : Type} (key : τ → κ) (values : List τ) := CandidateFiniteSourceCatalog.UniqueBy key values

structure Body (α : Type) where
  token : String
  target : α
  frame : Frame
  deriving DecidableEq, Repr
abbrev Entry (α : Type) := FArtifact (Body α)
structure Catalog (α : Type) where
  frame : Frame
  records : List (Entry α)
  roots : List (Entry α)
  deriving DecidableEq, Repr

def allEntries {α : Type} (catalog : Catalog α) : List (Entry α) := catalog.records ++ catalog.roots

def Functional {α : Type} (entries : List (Entry α)) : Prop :=
  ∀ a ∈ entries, ∀ b ∈ entries, a.body.token = b.body.token → a.body.target = b.body.target

def functionalCheck {α : Type} [DecidableEq α] (entries : List (Entry α)) : Bool :=
  entries.all (fun a => entries.all (fun b => decide (a.body.token = b.body.token → a.body.target = b.body.target)))

theorem functional_check_exact {α : Type} [DecidableEq α] (entries : List (Entry α)) :
    functionalCheck entries = true ↔ Functional entries := by
  simp only [functionalCheck, Functional, List.all_eq_true, decide_eq_true_eq]

structure EntryMeaning {α : Type} (catalog : Catalog α) (kind : String) (entry : Entry α) : Prop where
  kind : entry.sourceKind = kind
  nonempty : entry.body.token ≠ ""
  frame : entry.body.frame = catalog.frame

def entryCheck {α : Type} (catalog : Catalog α) (kind : String) (entry : Entry α) : Bool :=
  decide (entry.sourceKind = kind) && decide (entry.body.token ≠ "") && decide (entry.body.frame = catalog.frame)

theorem entry_check_exact {α : Type} (catalog : Catalog α) (kind : String) (entry : Entry α) :
    entryCheck catalog kind entry = true ↔ EntryMeaning catalog kind entry := by
  simp only [entryCheck, Bool.and_eq_true, decide_eq_true_eq]
  constructor
  · rintro ⟨⟨a,b⟩,c⟩; exact ⟨a,b,c⟩
  · intro h; exact ⟨⟨h.kind,h.nonempty⟩,h.frame⟩

structure CatalogMeaning {α : Type} (catalog : Catalog α) (kind : String) (targetKey : α → RevisionKey) : Prop where
  recordKeys : UniqueBy (fun entry => entry.ref.key) (allEntries catalog)
  tokens : Functional (allEntries catalog)
  targets : UniqueBy targetKey ((allEntries catalog).map (fun entry => entry.body.target))
  issued : ∀ entry ∈ catalog.records, entry ∈ catalog.roots
  entries : ∀ entry ∈ allEntries catalog, EntryMeaning catalog kind entry

def catalogCheck {α : Type} [DecidableEq α] (catalog : Catalog α) (kind : String)
    (targetKey : α → RevisionKey) : Bool :=
  CandidateFiniteSourceCatalog.uniqueCheck (fun entry => entry.ref.key) (allEntries catalog) &&
  functionalCheck (allEntries catalog) &&
  CandidateFiniteSourceCatalog.uniqueCheck targetKey ((allEntries catalog).map (fun entry => entry.body.target)) &&
  catalog.records.all (fun entry => decide (entry ∈ catalog.roots)) &&
  (allEntries catalog).all (entryCheck catalog kind)

theorem catalog_check_exact {α : Type} [DecidableEq α] (catalog : Catalog α) (kind : String)
    (targetKey : α → RevisionKey) : catalogCheck catalog kind targetKey = true ↔ CatalogMeaning catalog kind targetKey := by
  simp only [catalogCheck, Bool.and_eq_true, CandidateFiniteSourceCatalog.unique_check_exact,
    functional_check_exact, List.all_eq_true, decide_eq_true_eq, entry_check_exact]
  constructor
  · rintro ⟨⟨⟨⟨a,b⟩,c⟩,d⟩,e⟩; exact ⟨a,b,c,d,e⟩
  · intro h; exact ⟨⟨⟨⟨h.recordKeys,h.tokens⟩,h.targets⟩,h.issued⟩,h.entries⟩

def lookupTarget {α : Type} : List (Entry α) → String → Option α
  | [], _ => none
  | entry :: rest, token => if entry.body.token = token then some entry.body.target else lookupTarget rest token

theorem lookup_target_sound {α : Type} (entries : List (Entry α)) (token : String) (target : α)
    (found : lookupTarget entries token = some target) :
    ∃ entry ∈ entries, entry.body.token = token ∧ entry.body.target = target := by
  induction entries with
  | nil => simp [lookupTarget] at found
  | cons first rest ih =>
    unfold lookupTarget at found
    split at found
    · rename_i matching; cases found; exact ⟨first, by simp, matching, rfl⟩
    · rcases ih found with ⟨entry, member, matching, exactTarget⟩
      exact ⟨entry, by simp [member], matching, exactTarget⟩

theorem lookup_target_complete {α : Type} (entries : List (Entry α)) (token : String) (target : α)
    (functional : Functional entries)
    (member : ∃ entry ∈ entries, entry.body.token = token ∧ entry.body.target = target) :
    lookupTarget entries token = some target := by
  induction entries with
  | nil => rcases member with ⟨entry, owned, _, _⟩; simp at owned
  | cons first rest ih =>
    rcases member with ⟨entry, owned, matching, exactTarget⟩
    unfold lookupTarget
    split
    · rename_i firstMatch
      have same := functional first (by simp) entry owned (firstMatch.trans matching.symm)
      rw [same, exactTarget]
    · rename_i firstMissing
      simp only [List.mem_cons] at owned
      rcases owned with head | tail
      · subst entry; exact False.elim (firstMissing matching)
      · apply ih
        · intro a ha b hb equal; exact functional a (by simp [ha]) b (by simp [hb]) equal
        · exact ⟨entry, tail, matching, exactTarget⟩

structure Resolved {α : Type} (catalog : Catalog α) (kind : String) (targetKey : α → RevisionKey)
    (frame : Frame) (token : String) (target : α) : Prop where
  valid : CatalogMeaning catalog kind targetKey
  frame : catalog.frame = frame
  binding : ∃ entry ∈ catalog.records, entry.body.token = token ∧ entry.body.target = target

def resolve {α : Type} [DecidableEq α] (catalog : Catalog α) (kind : String)
    (targetKey : α → RevisionKey) (frame : Frame) (token : String) : Option α :=
  if catalogCheck catalog kind targetKey then
    if catalog.frame = frame then lookupTarget catalog.records token else none
  else none

theorem resolve_exact {α : Type} [DecidableEq α] (catalog : Catalog α) (kind : String)
    (targetKey : α → RevisionKey) (frame : Frame) (token : String) (target : α) :
    resolve catalog kind targetKey frame token = some target ↔ Resolved catalog kind targetKey frame token target := by
  constructor
  · intro accepted
    unfold resolve at accepted
    split at accepted
    · rename_i checked
      split at accepted
      · rename_i exactFrame
        exact ⟨(catalog_check_exact catalog kind targetKey).mp checked, exactFrame,
          lookup_target_sound catalog.records token target accepted⟩
      · simp at accepted
    · simp at accepted
  · intro represented
    have functional : Functional catalog.records := by
      intro a ha b hb equal
      exact represented.valid.tokens a (by simp [allEntries, ha]) b (by simp [allEntries, hb]) equal
    have found := lookup_target_complete catalog.records token target functional represented.binding
    simp [resolve, (catalog_check_exact catalog kind targetKey).mpr represented.valid, represented.frame, found]

theorem resolved_token_nonempty {α : Type} [DecidableEq α] (catalog : Catalog α) (kind : String)
    (targetKey : α → RevisionKey) (frame : Frame) (token : String) (target : α)
    (found : resolve catalog kind targetKey frame token = some target) : token ≠ "" := by
  have meaning := (resolve_exact catalog kind targetKey frame token target).mp found
  rcases meaning.binding with ⟨entry, owned, matching, _⟩
  have complete := meaning.valid.entries entry (by simp [allEntries, owned])
  simpa only [matching] using complete.nonempty

theorem invalid_catalog_refuses {α : Type} [DecidableEq α] (catalog : Catalog α) (kind : String)
    (targetKey : α → RevisionKey) (frame : Frame) (token : String)
    (invalid : ¬ CatalogMeaning catalog kind targetKey) : resolve catalog kind targetKey frame token = none := by
  cases result : resolve catalog kind targetKey frame token with
  | none => rfl
  | some target => exact False.elim (invalid ((resolve_exact catalog kind targetKey frame token target).mp result).valid)

theorem wrong_frame_refuses {α : Type} [DecidableEq α] (catalog : Catalog α) (kind : String)
    (targetKey : α → RevisionKey) (frame : Frame) (token : String) (wrong : catalog.frame ≠ frame) :
    resolve catalog kind targetKey frame token = none := by
  simp only [resolve, if_neg wrong]
  split <;> rfl

theorem aliases_preserve_complete_target {α : Type} [DecidableEq α] (catalog : Catalog α) (kind : String)
    (targetKey : α → RevisionKey) (frame : Frame) (tokenA tokenB : String) (a b : α)
    (ha : resolve catalog kind targetKey frame tokenA = some a)
    (hb : resolve catalog kind targetKey frame tokenB = some b) (same : targetKey a = targetKey b) : a = b := by
  have ma := (resolve_exact catalog kind targetKey frame tokenA a).mp ha
  have mb := (resolve_exact catalog kind targetKey frame tokenB b).mp hb
  rcases ma.binding with ⟨ea, ha, _, sameA⟩
  rcases mb.binding with ⟨eb, hb, _, sameB⟩
  apply ma.valid.targets a _ b _ same
  · exact List.mem_map.mpr ⟨ea, by simp [allEntries, ha], sameA⟩
  · exact List.mem_map.mpr ⟨eb, by simp [allEntries, hb], sameB⟩

#print axioms functional_check_exact
#print axioms entry_check_exact
#print axioms catalog_check_exact
#print axioms lookup_target_sound
#print axioms lookup_target_complete
#print axioms resolve_exact
#print axioms resolved_token_nonempty
#print axioms invalid_catalog_refuses
#print axioms wrong_frame_refuses
#print axioms aliases_preserve_complete_target
end RelationalSuccessor.CandidateOwnedBindings
