import SupportLineage
import RequirementControls
namespace Successor.Producer.Controls
open Inference
open Successor
open Successor.Controls
def conf : Key := ⟨"ConformsTo","v2","conformance"⟩
def kind : Key := ⟨"TargetKind","v2","kind"⟩
def unary : Key := ⟨"Conforms","v1","unary"⟩
def signal : Key := ⟨"Signal","v2","signal"⟩
def vocab : Vocabulary := ⟨conf,kind,unary⟩
def F := Observation.observed vocab graph
def signalRule : Rule := ⟨⟨"derive-signal","v2","rule"⟩,[],⟨signal,[]⟩,[⟨conf,[.constant (referenceValue subject),.constant (referenceValue targetA),.constant (.scope "scope-A")]⟩]⟩
def T : Theory := ⟨[referenceValue subject,referenceValue targetA,.scope "scope-A"],[],[signalRule],[],0⟩
def forgedRule (k : Key) : Rule := ⟨⟨"forge","v2","forged"⟩,[],⟨k,[]⟩,[]⟩
theorem derived_head_permitted : checkHeads T (Observation.keys vocab) = true := by decide
theorem constant_conformance_head_blocked : checkHeads {T with rules := [forgedRule conf]} (Observation.keys vocab) = false := by decide
theorem constant_kind_head_blocked : checkHeads {T with rules := [forgedRule kind]} (Observation.keys vocab) = false := by decide
theorem unary_alias_head_blocked : checkHeads {T with rules := [forgedRule unary]} (Observation.keys vocab) = false := by decide
theorem source_positive : conformanceAtom vocab observed ∈ F := by decide
theorem wrong_scope_absent : conformanceAtom vocab {observed with scope := "elsewhere"} ∉ F := by decide
theorem wrong_target_absent : conformanceAtom vocab {observed with target := targetB} ∉ F := by decide
theorem nonmember_source_absent : conformanceAtom vocab observed ∉ Observation.observed vocab noMember := by decide
theorem exact_kind_positive : kindAtom vocab targetA .contract ∈ F := by decide
theorem wrong_kind_absent : kindAtom vocab targetA .governedModel ∉ F := by decide
theorem vocabulary_distinct : Support.VocabularyDistinct vocab := by decide
theorem seed_coverage : Observation.SeedCoverage vocab graph F := by
  intro a _
  exact Observation.observation_exact vocab graph a
theorem protected_observation_not_fabricated :
    Derivable T F (conformanceAtom vocab {observed with scope := "elsewhere"}) → False := by
  intro derived
  have sealed : Sealed (Observation.keys vocab) (conformanceAtom vocab {observed with scope := "elsewhere"}) := by decide
  exact wrong_scope_absent ((observation_derivation_exact T F (Observation.keys vocab) _ (checked_heads_sealed derived_head_permitted) sealed).mp derived)
theorem positive_has_support : ∃ support, Projection.Supports graph observed support := by
  exact Support.sealed_conformance_support (checked_heads_sealed derived_head_permitted) seed_coverage vocabulary_distinct (Derivable.base source_positive)
def signalInstance : GroundInstance := ⟨signalRule.key,[],⟨signal,[]⟩,[conformanceAtom vocab observed]⟩
theorem signal_reads_observation : Derivable T F ⟨signal,[]⟩ := by
  apply Derivable.apply signalInstance (by decide)
  intro a ha
  have eq : a = conformanceAtom vocab observed := by simpa [signalInstance] using ha
  subst a
  exact Derivable.base source_positive
-- Root role is orthogonal to producer class. The permitted signal is ordinary
-- and cannot serve as a CheckedRoot declaration.
theorem signal_distinct_from_checked_root : signal.id ≠ "CheckedRoot" := by decide
#print axioms protected_observation_not_fabricated
#print axioms positive_has_support
#print axioms signal_reads_observation
end Successor.Producer.Controls
