import ClosedJsonObject

set_option autoImplicit false
namespace RelationalSuccessor.CandidateIntentSourceContract.Qualifiers
open RelationalSuccessor.CandidateJsonSource

structure Raw where
  intent_resolution_ref : String
  addressing_role : String
  deriving DecidableEq, Repr

def keys : List String := ["intent_resolution_ref", "addressing_role"]
def values (raw : Raw) : List Value :=
  [.string raw.intent_resolution_ref, .string raw.addressing_role]

-- This predicate retains object entries, so duplicate keys are not erased.
-- Raw decoding does not resolve references or establish a role's authority.
def Meaning (ast : Value) (raw : Raw) : Prop := ObjectValueMeaning keys ast (values raw)

def decodeFields : List Value → Option Raw
  | [.string resolution, .string role] => some ⟨resolution, role⟩
  | _ => none

theorem fields_exact (fields : List Value) (raw : Raw) :
    decodeFields fields = some raw ↔ fields = values raw := by
  constructor
  · intro decoded
    unfold decodeFields at decoded
    split at decoded
    · cases decoded; rfl
    · cases decoded
  · intro same; rw [same]; rfl

def decode (ast : Value) : Option Raw :=
  match decodeObject keys ast with
  | none => none
  | some fields => decodeFields fields

theorem decode_exact (ast : Value) (raw : Raw) :
    decode ast = some raw ↔ Meaning ast raw := by
  rw [Meaning, ← decode_object_exact]
  cases found : decodeObject keys ast with
  | none => simp [decode, found]
  | some fields => simp [decode, found, fields_exact]

def encode (raw : Raw) : Value := .object
  [("intent_resolution_ref", .string raw.intent_resolution_ref),
   ("addressing_role", .string raw.addressing_role)]

theorem encoding_exact (raw : Raw) : decode (encode raw) = some raw := by rfl

#print axioms fields_exact
#print axioms decode_exact
#print axioms encoding_exact
end RelationalSuccessor.CandidateIntentSourceContract.Qualifiers
