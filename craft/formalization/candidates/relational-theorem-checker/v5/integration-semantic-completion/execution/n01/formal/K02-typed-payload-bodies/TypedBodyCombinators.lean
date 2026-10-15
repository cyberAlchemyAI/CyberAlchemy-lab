import CompleteCatalogAst
set_option autoImplicit false
namespace RelationalSuccessor.CandidateTypedBodies
open CandidateBindingAst (Decoder J)

def ConstrainedMeaning {α : Type} (base : Decoder α) (condition : α → Prop)
    (value : J) (output : α) : Prop := base.Meaning value output ∧ condition output

def constrainedDecode {α : Type} (base : Decoder α) (condition : α → Prop)
    [DecidablePred condition] (value : J) : Option α :=
  match base.decode value with
  | none => none
  | some output => if condition output then some output else none

theorem constrained_exact {α : Type} (base : Decoder α) (condition : α → Prop)
    [DecidablePred condition] (value : J) (output : α) :
    constrainedDecode base condition value = some output ↔ ConstrainedMeaning base condition value output := by
  cases found : base.decode value with
  | none => simp [constrainedDecode,ConstrainedMeaning,←base.exact,found]
  | some actual =>
    by_cases same : actual = output
    · subst output
      simp [constrainedDecode,ConstrainedMeaning,←base.exact,found]
    · by_cases holds : condition actual <;>
        simp [constrainedDecode,ConstrainedMeaning,←base.exact,found,holds,same]

def constrained {α : Type} (base : Decoder α) (condition : α → Prop)
    [DecidablePred condition] : Decoder α :=
  ⟨constrainedDecode base condition,ConstrainedMeaning base condition,constrained_exact base condition⟩

def MappedMeaning {α β : Type} (base : Decoder α) (transform : α → β)
    (value : J) (output : β) : Prop :=
  ∃ input,base.Meaning value input ∧ transform input = output

theorem mapped_exact {α β : Type} (base : Decoder α) (transform : α → β)
    (value : J) (output : β) :
    (base.decode value).map transform = some output ↔ MappedMeaning base transform value output := by
  constructor
  · intro accepted
    cases found : base.decode value with
    | none => simp [found] at accepted
    | some input => exact ⟨input,(base.exact value input).mp found,by simpa [found] using accepted⟩
  · rintro ⟨input,meaning,same⟩
    simp [(base.exact value input).mpr meaning,same]

def mapped {α β : Type} (base : Decoder α) (transform : α → β) : Decoder β :=
  ⟨fun value => (base.decode value).map transform,MappedMeaning base transform,mapped_exact base transform⟩

def ArrayMeaning {α : Type} (element : Decoder α) (value : J) (outputs : List α) : Prop :=
  ∃ values,value = .array values ∧ CandidateJsonSource.ElementsMeaning element.Meaning values outputs

def arrayDecode {α : Type} (element : Decoder α) : J → Option (List α)
  | .array values => CandidateJsonSource.decodeElements element.decode values
  | _ => none

theorem array_exact {α : Type} (element : Decoder α) (value : J) (outputs : List α) :
    arrayDecode element value = some outputs ↔ ArrayMeaning element value outputs := by
  cases value with
  | array values =>
    simp only [arrayDecode]
    rw [CandidateJsonSource.decode_elements_exact element.decode element.Meaning element.exact]
    constructor
    · intro represented;exact ⟨values,rfl,represented⟩
    · rintro ⟨actual,same,represented⟩;cases same;exact represented
  | null => simp [arrayDecode,ArrayMeaning]
  | boolean value => simp [arrayDecode,ArrayMeaning]
  | number token => simp [arrayDecode,ArrayMeaning]
  | string value => simp [arrayDecode,ArrayMeaning]
  | object entries => simp [arrayDecode,ArrayMeaning]

def array {α : Type} (element : Decoder α) : Decoder (List α) :=
  ⟨arrayDecode element,ArrayMeaning element,array_exact element⟩

def NullableMeaning {α : Type} (base : Decoder α) (value : J) (output : Option α) : Prop :=
  (value = .null ∧ output = none) ∨
    ∃ input,value ≠ .null ∧ base.Meaning value input ∧ output = some input

def nullableDecode {α : Type} (base : Decoder α) : J → Option (Option α)
  | .null => some none
  | value => (base.decode value).map some

theorem nullable_exact {α : Type} (base : Decoder α) (value : J) (output : Option α) :
    nullableDecode base value = some output ↔ NullableMeaning base value output := by
  cases value with
  | null => simp [nullableDecode,NullableMeaning,eq_comm]
  | boolean flag =>
    cases found : base.decode (.boolean flag) <;> simp [nullableDecode,NullableMeaning,←base.exact,found,eq_comm]
  | number token =>
    cases found : base.decode (.number token) <;> simp [nullableDecode,NullableMeaning,←base.exact,found,eq_comm]
  | string text =>
    cases found : base.decode (.string text) <;> simp [nullableDecode,NullableMeaning,←base.exact,found,eq_comm]
  | array values =>
    cases found : base.decode (.array values) <;> simp [nullableDecode,NullableMeaning,←base.exact,found,eq_comm]
  | object entries =>
    cases found : base.decode (.object entries) <;> simp [nullableDecode,NullableMeaning,←base.exact,found,eq_comm]

def nullable {α : Type} (base : Decoder α) : Decoder (Option α) :=
  ⟨nullableDecode base,NullableMeaning base,nullable_exact base⟩

def ArrayConstraints {α : Type} (minimum : Nat) (maximum : Option Nat) (unique : Bool)
    (outputs : List α) : Prop :=
  minimum ≤ outputs.length ∧ (∀ bound ∈ maximum.toList,outputs.length ≤ bound) ∧
    (unique = true → outputs.Nodup)

instance {α : Type} [DecidableEq α] (minimum : Nat) (maximum : Option Nat) (unique : Bool) :
    DecidablePred (ArrayConstraints (α := α) minimum maximum unique) :=
  fun outputs => inferInstanceAs (Decidable (minimum ≤ outputs.length ∧
    (∀ bound ∈ maximum.toList,outputs.length ≤ bound) ∧ (unique = true → outputs.Nodup)))

def boundedArray {α : Type} [DecidableEq α] (element : Decoder α)
    (minimum : Nat) (maximum : Option Nat) (unique : Bool) : Decoder (List α) :=
  constrained (array element) (ArrayConstraints minimum maximum unique)

#print axioms constrained_exact
#print axioms mapped_exact
#print axioms array_exact
#print axioms nullable_exact
end RelationalSuccessor.CandidateTypedBodies
