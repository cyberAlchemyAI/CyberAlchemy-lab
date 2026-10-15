# Complete recursive parser soundness: implementation review

The soundness gap is now proved for the implemented recursive parser. For every
fuel and finite input, a successful value, array-body or object-body result has
the existing independent grammar meaning and exact original suffix. Successful
whole documents have `DocumentMeaning`; successful UTF-8 byte documents have
`ByteDocumentMeaning`.

This is one direction of refinement: accepted input is grammatical. The opposite
direction—every grammatical input is accepted—and sufficiency of the wrapper's
fuel budget remain unproved. Soundness alone allows false refusals, so it cannot
support a complete-parser claim or a new bounded-use recommendation.

| Result | What the theorem establishes |
|---|---|
| Whitespace reconstruction | The original input is exactly consumed whitespace followed by the remaining input; consumed codes meet the independent whitespace meaning |
| Array/member reconstruction | Parsed source spans reconstruct original commas, colons, keys, values and closing delimiters under existing `ItemsMeaning`/`MembersMeaning` |
| Mutual mode soundness | Value, array-body and object-body implications hold simultaneously for every Nat fuel; no recursive hypothesis is assumed without induction |
| Post-comma nonempty output | Array/object body calls with `allowEmpty=false` cannot successfully produce an empty list, which rules out trailing-comma acceptance |
| Wrapped value soundness | The actual `parseValue` wrapper result meets `BoundedValuePrefixMeaning`; the particular budget need not be assumed sufficient to prove this implication |
| Complete document soundness | Leading/trailing whitespace and exact root consumption reconstruct `DocumentMeaning` for the original input |
| UTF-8 document soundness | The proved UTF-8 composition and document theorem establish actual `ByteDocumentMeaning`, rather than only a relationship to parser success |
| Invalid-grammar refusal | If the independent meaning has no value for an input, parsing must return `none` |
| Value progress | Every successful value parse consumes a nonempty grammar word and strictly shortens the remaining input |

The proof reuses the already registered parser unchanged. Grammar meanings are
not rewritten as equations with its output. Seven reconstruction lemmas combine
independent value/string/member meanings with exact consumed spans; three step
proofs then form a simultaneous induction on fuel. Induction makes soundness
available only for smaller recursive calls. Document and byte wrappers derive
from this result without assuming completeness, authenticated source facts or
public profile decisions.

The object reconstruction preserves ordered key/value entries, including
duplicate decoded keys and raw UTF-16 units. Number spellings remain exact.
Soundness confirms those raw results belong to the independent grammar; it does
not qualify them against a binding schema, convert unsupported UTF-16 units to
scalar strings or authenticate any revision/digest/review root.

Preparation review caught a list-associativity issue when reconstructing empty
container bodies and normalized both sides before completing the proof. Failed
preparation logs are retained separately. Final sources contain no admitted
proof, native proof shortcut or custom axiom. Fresh replay uses the same pinned
Lean kernel and is not the mandatory independent closure checker.

Remaining work, starting with formalization:

1. State and prove independent starting-character/nonempty and whitespace-stop
   lemmas for all grammar constructors. They must cover primitive and recursively
   nested values, item lists and member lists.
2. State completeness with a consumed-word length measure for all three modes,
   then prove it by independent grammar derivation. Prove the wrapper budget
   `2*input.length+1` is sufficient, or revise the implementation with an equally
   explicit independently proved sufficient bound. Preserve the full grammar.
3. Derive value/document/UTF-8 exactness and unique raw meanings from both
   directions. Prove legal root whitespace and complete input consumption;
   finite controls do not replace these statements.
4. Formalize and implement scalar-AST conversion with explicit surrogate pairing
   or unsupported representation. Retain number spellings, member order and
   duplicates before binding-schema qualification.
5. Prove actual capture-byte-to-binding-record/catalog correspondence and realize
   digest computation, owned profiles, Schema semantics, authentic review providers
   and all nineteen K02 source policies.
6. Finish original relation/effect/theory closure and exact inherited-ID audit,
   mandatory independent checking, useful public diagnostics and measured runtime
   limits. Integrate all seven extensions and obtain the final actual new use
   assessment through the unchanged twenty-task DAG.

All 263 inherited IDs remain pending, and all 90 original discharges retain scope.
K00–K03 meanings retain their actual scoped acceptance. K04 and D01–D08 remain
pending. N01 is in progress; N02/N03 are unstarted and only N00 is accepted.
This proof package closes recursive parser soundness, not the full
41-kind/550-pair/seven-extension plan or original source semantics.

Fresh verification passes all 23 new general results through 48 compile/replay
invocations, 350 dependency-inclusive axiom inspections and 48 matching-phase
import audits. Only allowed standard axioms occur. Compilation/elaboration took
36.374 seconds total, with a 1.926-second maximum module.
Those timings are not runtime limits. No new finite controls were substituted
for the quantified proofs. Same-kernel replay is not independent proof checking.
Grammar completeness, budget sufficiency and all inherited discharges remain open.
