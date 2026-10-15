import TypedBodyCombinators
set_option autoImplicit false
namespace RelationalSuccessor.CandidateTypedBodies
open CandidateBindingAst (Decoder)

inductive Pattern where
  | nonWhitespace
  | timestamp
  deriving DecidableEq, Repr

def whitespaceCodes : List Nat :=
  [9,10,11,12,13,32,160,5760,8192,8193,8194,8195,8196,8197,8198,8199,
    8200,8201,8202,8232,8233,8239,8287,12288,65279]
def NonWhitespace (text : String) : Prop :=
  ∃ char ∈ text.toList,char.toNat ∉ whitespaceCodes
instance (text : String) : Decidable (NonWhitespace text) :=
  inferInstanceAs (Decidable (∃ char ∈ text.toList,char.toNat ∉ whitespaceCodes))

def timestampCharacter (chars : List Char) (index : Nat) : Prop :=
  let char := (chars[index]?).getD (Char.ofNat 0)
  if index = 4 ∨ index = 7 then char = '-'
  else if index = 10 then char = 'T'
  else if index = 13 ∨ index = 16 then char = ':'
  else if index = 19 then char = 'Z'
  else char ∈ ['0','1','2','3','4','5','6','7','8','9']
instance (chars : List Char) (index : Nat) : Decidable (timestampCharacter chars index) := by
  unfold timestampCharacter
  infer_instance
def TimestampShape (text : String) : Prop :=
  text.toList.length = 20 ∧ ∀ index ∈ List.range 20,timestampCharacter text.toList index
instance (text : String) : Decidable (TimestampShape text) :=
  inferInstanceAs (Decidable (text.toList.length = 20 ∧
    ∀ index ∈ List.range 20,timestampCharacter text.toList index))

def PatternMeaning : Pattern → String → Prop
  | .nonWhitespace,text => NonWhitespace text
  | .timestamp,text => TimestampShape text
instance (pattern : Pattern) (text : String) : Decidable (PatternMeaning pattern text) := by
  cases pattern <;> unfold PatternMeaning <;> infer_instance

def StringConstraints (minimum : Nat) (fixed : Option String) (choices : Option (List String))
    (pattern : Option Pattern) (text : String) : Prop :=
  minimum ≤ text.toList.length ∧ (∀ constant ∈ fixed.toList,text = constant) ∧
    (∀ allowed ∈ choices.toList,text ∈ allowed) ∧
    (∀ shape ∈ pattern.toList,PatternMeaning shape text)
instance (minimum : Nat) (fixed : Option String) (choices : Option (List String)) (pattern : Option Pattern) :
    DecidablePred (StringConstraints minimum fixed choices pattern) :=
  fun text => inferInstanceAs (Decidable (minimum ≤ text.toList.length ∧
    (∀ constant ∈ fixed.toList,text = constant) ∧ (∀ allowed ∈ choices.toList,text ∈ allowed) ∧
    (∀ shape ∈ pattern.toList,PatternMeaning shape text)))

def stringProfile (minimum : Nat) (fixed : Option String) (choices : Option (List String))
    (pattern : Option Pattern) : Decoder String :=
  constrained CandidateCatalogSnapshots.string (StringConstraints minimum fixed choices pattern)

theorem string_profile_exact (minimum : Nat) (fixed : Option String) (choices : Option (List String))
    (pattern : Option Pattern) (value : CandidateBindingAst.J) (text : String) :
    (stringProfile minimum fixed choices pattern).decode value = some text ↔
      CandidateJsonSource.StringMeaning value text ∧ StringConstraints minimum fixed choices pattern text :=
  constrained_exact _ _ _ _

#print axioms string_profile_exact
end RelationalSuccessor.CandidateTypedBodies
