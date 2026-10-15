import OwnedBindingCatalog

set_option autoImplicit false
namespace RelationalSuccessor.CandidateOwnedBindings.Joint
open RelationalSuccessor

def leftEntry {α β : Type} (entry : Entry α) : Entry (Sum α β) :=
  ⟨entry.ref, entry.sourceKind, ⟨entry.body.token, .inl entry.body.target, entry.body.frame⟩,
    entry.content, entry.ownerReview⟩
def rightEntry {α β : Type} (entry : Entry β) : Entry (Sum α β) :=
  ⟨entry.ref, entry.sourceKind, ⟨entry.body.token, .inr entry.body.target, entry.body.frame⟩,
    entry.content, entry.ownerReview⟩

def records {α β : Type} (left : Catalog α) (right : Catalog β) : List (Entry (Sum α β)) :=
  (allEntries left).map leftEntry ++ (allEntries right).map rightEntry

-- Canonical binding-record identity across both fixed record kinds. This does
-- not require their target semantic references to have different values.
def Meaning {α β : Type} (left : Catalog α) (right : Catalog β) : Prop :=
  UniqueBy (fun entry => entry.ref.key) (records left right)
def check {α β : Type} [DecidableEq α] [DecidableEq β] (left : Catalog α) (right : Catalog β) : Bool :=
  CandidateFiniteSourceCatalog.uniqueCheck (fun entry => entry.ref.key) (records left right)

theorem check_exact {α β : Type} [DecidableEq α] [DecidableEq β] (left : Catalog α) (right : Catalog β) :
    check left right = true ↔ Meaning left right :=
  CandidateFiniteSourceCatalog.unique_check_exact _ _

#print axioms check_exact
end RelationalSuccessor.CandidateOwnedBindings.Joint
