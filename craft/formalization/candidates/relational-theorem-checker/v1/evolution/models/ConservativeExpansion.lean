import RegistryChecker

namespace Registry.Models

def expandedTheory (base : Theory) (added : List Kind) : Theory :=
  { nodeKinds := base.nodeKinds, kinds := base.kinds ++ added }
def oldReduct (base : Theory) (model : Graph) : Graph :=
  { nodes := model.nodes, assertions := model.assertions.filter (fun e => decide (e.kindId ∈ base.kinds.map Kind.id)) }

theorem preserves_base_instances (base : Theory) (added : List Kind) (model : Graph)
    (edge : Assertion) (valid : InstanceValid base model edge) :
    InstanceValid (expandedTheory base added) model edge := by
  rcases valid with ⟨id, source, hs, target, ht, sr, tr, d, hd, kid, ver, pair, qualifiers⟩
  have extended : d ∈ (expandedTheory base added).kinds := List.mem_append.mpr (Or.inl hd)
  exact ⟨id, source, hs, target, ht, sr, tr, d, extended, kid, ver, pair, qualifiers⟩

theorem existing_model_expands (base : Theory) (added : List Kind)
    (theoryValid : TheoryValid (expandedTheory base added)) (model : Graph)
    (valid : Inv base model) : Inv (expandedTheory base added) model := by
  rcases valid with ⟨_, keys, nodes, ids, edges⟩
  refine ⟨theoryValid, keys, nodes, ids, ?_⟩
  intro edge he
  exact preserves_base_instances base added model edge (edges edge he)

theorem base_model_reduct_unchanged (base : Theory) (model : Graph) (valid : Inv base model) :
    oldReduct base model = model := by
  have filtered : model.assertions.filter (fun e => decide (e.kindId ∈ base.kinds.map Kind.id)) = model.assertions := by
    apply List.filter_eq_self.mpr
    intro edge he
    rcases valid.2.2.2.2 edge he with ⟨_, _, _, _, _, _, _, d, hd, kid, _, _, _⟩
    have known : edge.kindId ∈ base.kinds.map Kind.id := List.mem_map.mpr ⟨d, hd, kid⟩
    simpa using known
  cases model
  simp only [oldReduct, filtered]

-- Every base model has an expansion: the new relation interpretations are empty.
theorem expands_every_base_model (base : Theory) (added : List Kind)
    (theoryValid : TheoryValid (expandedTheory base added)) (model : Graph) (valid : Inv base model) :
    ∃ expansion, Inv (expandedTheory base added) expansion ∧ oldReduct base expansion = model :=
  ⟨model, existing_model_expands base added theoryValid model valid, base_model_reduct_unchanged base model valid⟩

def RequiredConservativity : Prop := ∀ (base : Theory) (added : List Kind),
  TheoryValid (expandedTheory base added) → ∀ model, Inv base model →
    ∃ expansion, Inv (expandedTheory base added) expansion ∧ oldReduct base expansion = model
theorem audited_conservativity : RequiredConservativity := expands_every_base_model

def InhabitedUse (theory : Theory) (model : Graph) : Prop :=
  Inv theory model ∧ model.nodes ≠ [] ∧ model.assertions ≠ []
def HasKind (model : Graph) (kindId : String) : Prop := ∃ edge ∈ model.assertions, edge.kindId = kindId
instance (model : Graph) (kindId : String) : Decidable (HasKind model kindId) := by
  unfold HasKind
  infer_instance

#print axioms preserves_base_instances
#print axioms existing_model_expands
#print axioms base_model_reduct_unchanged
#print axioms expands_every_base_model
#print axioms audited_conservativity
end Registry.Models
