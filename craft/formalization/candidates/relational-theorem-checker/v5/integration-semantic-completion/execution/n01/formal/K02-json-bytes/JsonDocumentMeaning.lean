import Utf8Stream
import NumberGrammarComplete
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonBytes

-- Raw syntax retains UTF-16 string units, including unpaired escaped surrogates.
-- Conversion to the existing scalar-string AST is a separate profile obligation.
inductive RawValue where
  | null
  | boolean (value : Bool)
  | number (token : String)
  | string (units : List Nat)
  | array (values : List RawValue)
  | object (entries : List (List Nat × RawValue))
  deriving Repr

def WhiteSpace (text : List Nat) : Prop := ∀ code ∈ text, code = 32 ∨ code = 9 ∨ code = 10 ∨ code = 13

def scalarUnits (value : Nat) : List Nat :=
  if value < 65536 then [value] else [55296 + (value-65536)/1024,56320 + (value-65536)%1024]

inductive HexMeaning : Nat → Nat → Prop
  | digit (value : Nat) (bound : value < 10) : HexMeaning (48+value) value
  | lower (value : Nat) (bound : value < 6) : HexMeaning (97+value) (10+value)
  | upper (value : Nat) (bound : value < 6) : HexMeaning (65+value) (10+value)

inductive SimpleEscape : Nat → Nat → Prop
  | quotation : SimpleEscape 34 34
  | reverseSolidus : SimpleEscape 92 92
  | solidus : SimpleEscape 47 47
  | backspace : SimpleEscape 98 8
  | formfeed : SimpleEscape 102 12
  | newline : SimpleEscape 110 10
  | carriageReturn : SimpleEscape 114 13
  | tab : SimpleEscape 116 9

inductive StringUnitMeaning : List Nat → List Nat → Prop
  | raw (value : Nat) (scalar : Scalar value) (printable : 32 ≤ value)
      (notQuote : value ≠ 34) (notSlash : value ≠ 92) : StringUnitMeaning [value] (scalarUnits value)
  | simple (encoded decoded : Nat) (escape : SimpleEscape encoded decoded) :
      StringUnitMeaning [92,encoded] [decoded]
  | hexadecimal (a b c d va vb vc vd : Nat)
      (ha : HexMeaning a va) (hb : HexMeaning b vb) (hc : HexMeaning c vc) (hd : HexMeaning d vd) :
      StringUnitMeaning [92,117,a,b,c,d] [va*4096+vb*256+vc*16+vd]

inductive StringContentMeaning : List Nat → List Nat → Prop
  | nil : StringContentMeaning [] []
  | cons (word text units restUnits : List Nat) (head : StringUnitMeaning word units)
      (tail : StringContentMeaning text restUnits) :
      StringContentMeaning (word ++ text) (units ++ restUnits)

def StringMeaning (text units : List Nat) : Prop :=
  ∃ content, text = [34] ++ content ++ [34] ∧ StringContentMeaning content units

mutual
  inductive ValueMeaning : List Nat → RawValue → Prop
    | null : ValueMeaning [110,117,108,108] .null
    | false : ValueMeaning [102,97,108,115,101] (.boolean false)
    | true : ValueMeaning [116,114,117,101] (.boolean true)
    | number (token : String) (grammar : RelationalSuccessor.CandidateDecimal.NumberGrammar token.toList) :
        ValueMeaning (token.toList.map Char.toNat) (.number token)
    | string (text units : List Nat) (meaning : StringMeaning text units) : ValueMeaning text (.string units)
    | emptyArray (space : List Nat) (ws : WhiteSpace space) : ValueMeaning ([91] ++ space ++ [93]) (.array [])
    | array (left text right : List Nat) (values : List RawValue)
        (wl : WhiteSpace left) (members : ItemsMeaning text values) (wr : WhiteSpace right) :
        ValueMeaning ([91] ++ left ++ text ++ right ++ [93]) (.array values)
    | emptyObject (space : List Nat) (ws : WhiteSpace space) : ValueMeaning ([123] ++ space ++ [125]) (.object [])
    | object (left text right : List Nat) (entries : List (List Nat × RawValue))
        (wl : WhiteSpace left) (members : MembersMeaning text entries) (wr : WhiteSpace right) :
        ValueMeaning ([123] ++ left ++ text ++ right ++ [125]) (.object entries)

  inductive ItemsMeaning : List Nat → List RawValue → Prop
    | one (text : List Nat) (value : RawValue) (meaning : ValueMeaning text value) : ItemsMeaning text [value]
    | cons (text left right remaining : List Nat) (value : RawValue) (values : List RawValue)
        (head : ValueMeaning text value) (wl : WhiteSpace left) (wr : WhiteSpace right)
        (tail : ItemsMeaning remaining values) :
        ItemsMeaning (text ++ left ++ [44] ++ right ++ remaining) (value::values)

  inductive MembersMeaning : List Nat → List (List Nat × RawValue) → Prop
    | one (key left right text units : List Nat) (value : RawValue)
        (name : StringMeaning key units) (wl : WhiteSpace left) (wr : WhiteSpace right)
        (meaning : ValueMeaning text value) :
        MembersMeaning (key ++ left ++ [58] ++ right ++ text) [(units,value)]
    | cons (key left right text before after remaining units : List Nat) (value : RawValue)
        (entries : List (List Nat × RawValue)) (name : StringMeaning key units)
        (wl : WhiteSpace left) (wr : WhiteSpace right) (meaning : ValueMeaning text value)
        (wb : WhiteSpace before) (wa : WhiteSpace after) (tail : MembersMeaning remaining entries) :
        MembersMeaning (key ++ left ++ [58] ++ right ++ text ++ before ++ [44] ++ after ++ remaining)
          ((units,value)::entries)
end

def DocumentMeaning (text : List Nat) (value : RawValue) : Prop :=
  ∃ left word right, WhiteSpace left ∧ ValueMeaning word value ∧ WhiteSpace right ∧ text = left ++ word ++ right

def ByteDocumentMeaning (bytes : Bytes) (value : RawValue) : Prop :=
  ∃ text, StreamMeaning bytes text ∧ DocumentMeaning text value

theorem hex_value_bound (encoded value : Nat) (meaning : HexMeaning encoded value) : value < 16 := by
  cases meaning <;> omega

theorem raw_scalar_units_bounded (value : Nat) (scalar : Scalar value) :
    ∀ unit ∈ scalarUnits value, unit < 65536 := by
  intro unit member
  unfold scalarUnits at member
  split at member
  · simp only [List.mem_singleton] at member; subst unit; assumption
  · simp at member
    unfold Scalar at scalar
    rcases member with same | same <;> subst unit <;> omega

theorem string_units_bounded (text units : List Nat) (meaning : StringUnitMeaning text units) :
    ∀ unit ∈ units, unit < 65536 := by
  cases meaning with
  | raw value scalar printable nq ns => exact raw_scalar_units_bounded value scalar
  | simple encoded decoded escape => cases escape <;> simp
  | hexadecimal a b c d va vb vc vd ha hb hc hd =>
    have ba := hex_value_bound a va ha
    have bb := hex_value_bound b vb hb
    have bc := hex_value_bound c vc hc
    have bd := hex_value_bound d vd hd
    intro unit member
    simp only [List.mem_singleton] at member
    subst unit
    omega

theorem string_content_units_bounded (text units : List Nat) (meaning : StringContentMeaning text units) :
    ∀ unit ∈ units, unit < 65536 := by
  induction meaning with
  | nil => intro unit member; simp at member
  | cons word text units restUnits head tail ih =>
    intro unit member
    simp only [List.mem_append] at member
    rcases member with first | remaining
    · exact string_units_bounded word units head unit first
    · exact ih unit remaining

theorem byte_document_encoding_bridge (bytes : Bytes) (value : RawValue) :
    ByteDocumentMeaning bytes value ↔ ∃ text, decodeUtf8 bytes = some text ∧ DocumentMeaning text value := by
  constructor
  · rintro ⟨text,utf8,meaning⟩; exact ⟨text,(decode_utf8_exact bytes text).mpr utf8,meaning⟩
  · rintro ⟨text,utf8,meaning⟩; exact ⟨text,(decode_utf8_exact bytes text).mp utf8,meaning⟩

#print axioms hex_value_bound
#print axioms raw_scalar_units_bounded
#print axioms string_units_bounded
#print axioms string_content_units_bounded
#print axioms byte_document_encoding_bridge
end RelationalSuccessor.CandidateJsonBytes
