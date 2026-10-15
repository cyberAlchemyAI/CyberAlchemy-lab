import NumberGrammarComplete
import BindingAstCombinators
set_option autoImplicit false
namespace RelationalSuccessor.CandidateNumberParser
open RelationalSuccessor.CandidateDecimal

-- Independent token meaning: complete lexical representation and the already
-- specified exact nonnegative rational-value equation; neither proposition calls
-- parseToken or the arithmetic evaluator.
def TokenEpochMeaning (token : String) (epoch : Nat) : Prop :=
  ∃ parts, Representation token.toList parts ∧ EpochMeaning parts epoch

def decodeTokenEpoch (token : String) : Option Nat :=
  match parseToken token with
  | none => none
  | some parts => decodeParts parts

theorem token_epoch_exact (token : String) (epoch : Nat) :
    decodeTokenEpoch token = some epoch ↔ TokenEpochMeaning token epoch := by
  constructor
  · intro accepted
    cases parsed : parseToken token with
    | none => simp [decodeTokenEpoch,parsed] at accepted
    | some parts =>
      exact ⟨parts,(parse_token_exact token parts).mp parsed,
        (decode_parts_exact parts epoch).mp (by simpa [decodeTokenEpoch,parsed] using accepted)⟩
  · rintro ⟨parts,representation,value⟩
    simp [decodeTokenEpoch,(parse_token_exact token parts).mpr representation,(decode_parts_exact parts epoch).mpr value]

def AstEpochMeaning (value : Ast) (epoch : Nat) : Prop :=
  ∃ token, value = .number token ∧ TokenEpochMeaning token epoch

def decodeEpochAst : Ast → Option Nat
  | .number token => decodeTokenEpoch token
  | _ => none

theorem epoch_ast_exact (value : Ast) (epoch : Nat) : decodeEpochAst value = some epoch ↔ AstEpochMeaning value epoch := by
  cases value with
  | number token =>
    have representation : AstEpochMeaning (.number token) epoch ↔ TokenEpochMeaning token epoch := by
      constructor
      · rintro ⟨actual,same,meaning⟩; cases same; exact meaning
      · intro meaning; exact ⟨token,rfl,meaning⟩
    rw [representation]
    exact token_epoch_exact token epoch
  | null => simp [decodeEpochAst,AstEpochMeaning]
  | boolean b => simp [decodeEpochAst,AstEpochMeaning]
  | string s => simp [decodeEpochAst,AstEpochMeaning]
  | array vs => simp [decodeEpochAst,AstEpochMeaning]
  | object es => simp [decodeEpochAst,AstEpochMeaning]

def epochAdapter : RelationalSuccessor.CandidateBindingAst.Decoder Nat :=
  ⟨decodeEpochAst,AstEpochMeaning,epoch_ast_exact⟩

theorem token_epoch_unique (token : String) (a b : Nat) (ha : TokenEpochMeaning token a) (hb : TokenEpochMeaning token b) : a = b := by
  rcases ha with ⟨pa,ra,va⟩
  rcases hb with ⟨pb,rb,vb⟩
  have same := token_representation_unique token.toList pa pb ra rb
  subst pb
  exact epoch_value_unique pa a b va vb

theorem invalid_number_token_refuses (token : String) (invalid : ¬ NumberGrammar token.toList) : decodeTokenEpoch token = none := by
  cases result : decodeTokenEpoch token with
  | none => rfl
  | some epoch =>
    rcases (token_epoch_exact token epoch).mp result with ⟨parts,representation,_⟩
    have grammar := (parser_covers_exact_JSON_grammar token.toList).mp ⟨parts,parse_chars_complete token.toList parts representation⟩
    exact False.elim (invalid grammar)

theorem no_natural_epoch_refuses (token : String) (invalid : ∀ epoch, ¬ TokenEpochMeaning token epoch) : decodeTokenEpoch token = none := by
  cases result : decodeTokenEpoch token with
  | none => rfl
  | some epoch => exact False.elim (invalid epoch ((token_epoch_exact token epoch).mp result))

#print axioms token_epoch_exact
#print axioms epoch_ast_exact
#print axioms token_epoch_unique
#print axioms invalid_number_token_refuses
#print axioms no_natural_epoch_refuses
end RelationalSuccessor.CandidateNumberParser
