import Std
namespace RelationalExtensions.Chain
structure Ref where
  id : String
  version : String
  deriving DecidableEq, Repr
inductive Truth where
  | yes | no | unknown
  deriving DecidableEq, Repr
structure Query where
  principal : Ref
  agent : Ref
  scope : String
  action : String
  epoch : Nat
  deriving DecidableEq, Repr
structure Hop where
  id : Ref
  principal : Ref
  agent : Ref
  scopes : List String
  actions : List String
  start : Nat
  finish : Nat
  redelegate : Bool
  gate : Truth
  revocation : Truth
  deriving DecidableEq, Repr
-- Missing facts never enter this finite source. Facts and assessments have exact
-- source/frame identities checked by the transport, then retained in the witness.
def covers (q : Query) (h : Hop) : Bool :=
  h.scopes.contains q.scope && h.actions.contains q.action &&
  decide (h.start ≤ q.epoch ∧ q.epoch < h.finish)
def permits (q : Query) (h : Hop) : Prop :=
  q.scope ∈ h.scopes ∧ q.action ∈ h.actions ∧ h.start ≤ q.epoch ∧
  q.epoch < h.finish ∧ h.gate = .yes ∧ h.revocation = .no
instance (q : Query) (h : Hop) : Decidable (permits q h) := inferInstanceAs (Decidable (_ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _))
def narrows (p c : Hop) : Bool :=
  c.scopes.all p.scopes.contains && c.actions.all p.actions.contains &&
  decide (p.start ≤ c.start ∧ c.finish ≤ p.finish) && p.redelegate && decide (p.agent = c.principal)
def joined : List Hop → Bool
  | [] => true
  | [_] => true
  | p :: c :: rest => narrows p c && joined (c :: rest)
def simple (p : List Hop) : Bool :=
  decide ((p.map Hop.principal ++ (p.getLast?.map Hop.agent).toList).Nodup)
def shaped (q : Query) (p : List Hop) : Bool :=
  !p.isEmpty && decide (p.head?.map Hop.principal = some q.principal) &&
  decide (p.getLast?.map Hop.agent = some q.agent) && joined p && simple p
-- Independent quantified permission target; activation never bypasses an ancestor.
def Effective (q : Query) (p : List Hop) : Prop :=
  shaped q p = true ∧ ∀ h ∈ p, permits q h
def effective (q : Query) (p : List Hop) : Bool := shaped q p && p.all (fun h => decide (permits q h))
theorem effective_exact (q : Query) (p : List Hop) : effective q p = true ↔ Effective q p := by
  simp [effective, Effective, List.all_eq_true]
theorem non_amplification (q : Query) (p : List Hop) (he : Effective q p) :
    ∀ h ∈ p, q.scope ∈ h.scopes ∧ q.action ∈ h.actions ∧ h.start ≤ q.epoch ∧ q.epoch < h.finish := by
  intro h hh
  obtain ⟨hs, ha, ht, hf, _, _⟩ := he.2 h hh
  exact ⟨hs, ha, ht, hf⟩
def possible (q : Query) (p : List Hop) : Bool := shaped q p &&
  p.all (fun h => covers q h && decide (h.gate ≠ .no ∧ h.revocation ≠ .yes))
def words (edges : List Hop) : Nat → List (List Hop)
  | 0 => [[]]
  | n+1 => edges.flatMap (fun h => (words edges n).map (h :: ·))
theorem words_exact (edges : List Hop) (n : Nat) (p : List Hop) :
    p ∈ words edges n ↔ p.length = n ∧ ∀ h ∈ p, h ∈ edges := by
  induction n generalizing p with
  | zero =>
    constructor
    · intro hp
      have hnil : p = [] := by simpa [words] using hp
      subst p; simp
    · intro hp
      have hnil : p = [] := List.eq_nil_of_length_eq_zero hp.1
      subst p; simp [words]
  | succ n ih =>
    cases p with
    | nil => simp [words]
    | cons a rest =>
      simp only [words, List.mem_flatMap, List.mem_map]
      constructor
      · rintro ⟨h, hh, r, hr, heq⟩
        obtain ⟨haeq, hreq⟩ := List.cons.inj heq
        subst h
        subst r
        obtain ⟨hlen, hall⟩ := (ih rest).mp hr
        exact ⟨by simp [hlen], by intro x hx; simp only [List.mem_cons] at hx; rcases hx with rfl | hx; exact hh; exact hall x hx⟩
      · rintro ⟨hlen, hall⟩
        refine ⟨a, hall a (by simp), rest, (ih rest).mpr ?_, rfl⟩
        exact ⟨by simpa using hlen, by intro x hx; exact hall x (by simp [hx])⟩
def pathUniverse (edges : List Hop) (depth : Nat) : List (List Hop) :=
  (List.range depth).flatMap (fun n => words edges (n+1))
theorem universe_exact (edges : List Hop) (depth : Nat) (p : List Hop) :
    p ∈ pathUniverse edges depth ↔ 0 < p.length ∧ p.length ≤ depth ∧ ∀ h ∈ p, h ∈ edges := by
  simp only [pathUniverse, List.mem_flatMap, List.mem_range, words_exact]
  constructor
  · rintro ⟨n, hn, hp, hall⟩; exact ⟨by omega, by omega, hall⟩
  · rintro ⟨hp, hd, hall⟩
    refine ⟨p.length-1, by omega, by omega, hall⟩
def supported (q : Query) (edges : List Hop) (depth : Nat) :=
  (pathUniverse edges depth).filter (effective q)
def undecided (q : Query) (edges : List Hop) (depth : Nat) :=
  (pathUniverse edges depth).filter (fun p => possible q p && !effective q p)
def query (q : Query) (edges : List Hop) (depth : Nat) : Truth :=
  if !(supported q edges depth).isEmpty then .yes
  else if !(undecided q edges depth).isEmpty then .unknown else .no
theorem support_exact (q : Query) (edges : List Hop) (depth : Nat) (p : List Hop) :
    p ∈ supported q edges depth ↔ (0 < p.length ∧ p.length ≤ depth ∧ ∀ h ∈ p, h ∈ edges) ∧ Effective q p := by
  simp [supported, universe_exact, effective_exact]
theorem reported_path_non_amplification (q : Query) (edges : List Hop) (depth : Nat)
    (p : List Hop) (hp : p ∈ supported q edges depth) :
    ∀ h ∈ p, q.scope ∈ h.scopes ∧ q.action ∈ h.actions ∧ h.start ≤ q.epoch ∧ q.epoch < h.finish :=
  non_amplification q p ((support_exact q edges depth p).mp hp).2
#print axioms effective_exact
#print axioms non_amplification
#print axioms words_exact
#print axioms universe_exact
#print axioms reported_path_non_amplification
end RelationalExtensions.Chain
