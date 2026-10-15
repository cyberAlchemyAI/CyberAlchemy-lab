import JsonElements

set_option autoImplicit false
namespace RelationalSuccessor.CandidateBindingAst
abbrev J := RelationalSuccessor.CandidateJsonSource.Value

-- Meanings in these carriers are propositions about retained AST entries and
-- typed values. They never call the corresponding executable decoders.
structure Decoder (α : Type) where
  decode : J → Option α
  Meaning : J → α → Prop
  exact : ∀ value output, decode value = some output ↔ Meaning value output

structure Fields (α : Type) where
  decode : List J → Option α
  Meaning : List J → α → Prop
  exact : ∀ values output, decode values = some output ↔ Meaning values output

def emptyDecode : List J → Option Unit
  | [] => some ()
  | _ => none

def EmptyMeaning (values : List J) (_output : Unit) : Prop := values = []

theorem empty_exact (values : List J) (output : Unit) :
    emptyDecode values = some output ↔ EmptyMeaning values output := by
  cases output
  cases values <;> simp [emptyDecode, EmptyMeaning]

def empty : Fields Unit := ⟨emptyDecode, EmptyMeaning, empty_exact⟩

def consDecode {α β : Type} (head : Decoder α) (tail : Fields β) : List J → Option (α × β)
  | value :: rest =>
      match head.decode value, tail.decode rest with
      | some a, some b => some (a,b)
      | _, _ => none
  | [] => none

def ConsMeaning {α β : Type} (head : Decoder α) (tail : Fields β)
    (values : List J) (output : α × β) : Prop :=
  ∃ value rest, values = value :: rest ∧ head.Meaning value output.1 ∧ tail.Meaning rest output.2

theorem cons_exact {α β : Type} (head : Decoder α) (tail : Fields β)
    (values : List J) (output : α × β) :
    consDecode head tail values = some output ↔ ConsMeaning head tail values output := by
  cases values with
  | nil => simp [consDecode, ConsMeaning]
  | cons value rest =>
    rcases output with ⟨a,b⟩
    have represented : ConsMeaning head tail (value :: rest) (a,b) ↔
        head.Meaning value a ∧ tail.Meaning rest b := by
      constructor
      · rintro ⟨actual, remaining, same, hm, tm⟩
        cases same; exact ⟨hm,tm⟩
      · rintro ⟨hm,tm⟩; exact ⟨value,rest,rfl,hm,tm⟩
    rw [represented, ← head.exact, ← tail.exact]
    cases h : head.decode value <;> cases t : tail.decode rest <;>
      simp [consDecode, h, t]

def cons {α β : Type} (head : Decoder α) (tail : Fields β) : Fields (α × β) :=
  ⟨consDecode head tail, ConsMeaning head tail, cons_exact head tail⟩

def MapMeaning {α β : Type} (fields : Fields α) (transform : α → β)
    (values : List J) (output : β) : Prop :=
  ∃ input, fields.Meaning values input ∧ transform input = output

theorem map_fields_exact {α β : Type} (fields : Fields α) (transform : α → β)
    (values : List J) (output : β) :
    (fields.decode values).map transform = some output ↔ MapMeaning fields transform values output := by
  constructor
  · intro accepted
    cases found : fields.decode values with
    | none => simp [found] at accepted
    | some input =>
      exact ⟨input,(fields.exact values input).mp found,by simpa [found] using accepted⟩
  · rintro ⟨input,meaning,same⟩
    simp [(fields.exact values input).mpr meaning,same]

def mapFields {α β : Type} (fields : Fields α) (transform : α → β) : Fields β :=
  ⟨fun values => (fields.decode values).map transform,
    MapMeaning fields transform, map_fields_exact fields transform⟩

def ObjectMeaning {α : Type} (keys : List String) (fields : Fields α)
    (value : J) (output : α) : Prop :=
  ∃ values, CandidateJsonSource.ObjectValueMeaning keys value values ∧ fields.Meaning values output

def objectDecode {α : Type} (keys : List String) (fields : Fields α) (value : J) : Option α :=
  match CandidateJsonSource.decodeObject keys value with
  | some values => fields.decode values
  | none => none

theorem object_exact {α : Type} (keys : List String) (fields : Fields α)
    (value : J) (output : α) : objectDecode keys fields value = some output ↔ ObjectMeaning keys fields value output := by
  constructor
  · intro accepted
    cases found : CandidateJsonSource.decodeObject keys value with
    | none => simp [objectDecode,found] at accepted
    | some values =>
      exact ⟨values,(CandidateJsonSource.decode_object_exact keys value values).mp found,
        (fields.exact values output).mp (by simpa [objectDecode,found] using accepted)⟩
  · rintro ⟨values,represented,meaning⟩
    simp [objectDecode,(CandidateJsonSource.decode_object_exact keys value values).mpr represented,
      (fields.exact values output).mpr meaning]

def object {α : Type} (keys : List String) (fields : Fields α) : Decoder α :=
  ⟨objectDecode keys fields, ObjectMeaning keys fields, object_exact keys fields⟩

theorem duplicate_object_refuses {α : Type} (keys : List String) (fields : Fields α)
    (entries : CandidateJsonSource.Entries) (duplicates : ¬ (entries.map Prod.fst).Nodup) :
    (object keys fields).decode (.object entries) = none := by
  simp [object,objectDecode,CandidateJsonSource.duplicate_keys_refuse keys entries duplicates]

theorem extra_object_refuses {α : Type} (keys : List String) (fields : Fields α)
    (entries : CandidateJsonSource.Entries) (entry : String × J)
    (member : entry ∈ entries) (extra : entry.1 ∉ keys) :
    (object keys fields).decode (.object entries) = none := by
  simp [object,objectDecode,CandidateJsonSource.extra_key_refuses keys entries entry member extra]

#print axioms empty_exact
#print axioms cons_exact
#print axioms map_fields_exact
#print axioms object_exact
#print axioms duplicate_object_refuses
#print axioms extra_object_refuses
end RelationalSuccessor.CandidateBindingAst
