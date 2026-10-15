# Finite provider: search, witness evidence and bounded conclusions

P02 implements the generic finite provider needed by the full formalization plan. It consumes the supported typed signature rather than special-casing the original pilot identities. The selected input consists of exact typed IR, a premise theory T, required populations I, a query Q, one finite cardinality for every sort, and an explicit search mode. The provider preserves all 183 current definitions in the project scope; the controls in this unit are synthetic theories, not accepted current-source translations.

## What is being enumerated

Each sort receives a named carrier `a0 … a(n−1)` of its selected nonzero cardinality. A constant of result sort with n members has n possible interpretations. A total function with t argument tuples and a result carrier of n members has n^t interpretations. A predicate or relation with t possible argument tuples has 2^t possible extensions. A zero-argument symbol uses the single empty argument tuple: a zero-arity predicate has two interpretations, and a zero-arity total function selects one result member.

The whole interpretation space is the product of those choices. Sort and symbol identities remain the exact canonical C01 identities. Equal atom spellings in separate carriers do not authorize cross-sort equality or align meanings. Every generated function table is total; every generated predicate extension is explicitly complete, including an empty extension. Missing data is never filled in as false.

For example, a two-member carrier with one constant, one unary endofunction and one unary predicate has `2 × 2² × 2² = 32` interpretations. The census control constructs these 32 models independently with small explicit products, then compares their complete model digests with the provider enumeration. The provider visits every one exactly once in that control. This supports the concrete enumeration criteria; it is not a mechanized general enumeration theorem.

The static language has no built-in meaning for the implementation's atom names. Renaming a finite carrier while transporting all symbol interpretations gives the usual correspondence between its named representation and that abstract finite structure. Establishing a general preservation theorem for that representation and the evaluator remains separate proof work. A concrete model witness can still be checked directly by the independent denotation contract and C02's controlled evaluator.

## Streaming and exact large-space descriptions

The provider uses a vector of mixed-radix digits. A digit chooses a constant value, a complete function assignment or a predicate bitmask. Incrementing the vector advances to the next interpretation. The provider does not collect visited models, build a list of all predicate subsets, or use a product iterator that caches every interpretation of each predicate.

Function argument tuples are constructed by their index rather than stored in a separate Cartesian-product table. Predicate extensions enumerate set bits of the selected digit. At most the current model, its evaluation structure, the input signature/formulas and bounded counters are retained. Serialized model and result limits, tuple-space limits and input-node limits constrain those representations. Runtime file hashing reads 64 KiB chunks, so a large executable does not have to be loaded into memory at once.

When a dimension is much larger than the allowed visited prefix, the space record preserves its exact `base^exponent` factor without constructing the enormous integer. The enumeration radix is capped only above the maximum permitted prefix. Such a cap cannot be reached as full exhaustion within the permitted number of visits. Exhaustion explicitly requires all radices to be exact and the complete vector to overflow. This prevents a clipped search from appearing complete.

A nine-argument relation on three-member carriers has 19,683 possible tuples and 2^19683 extensions. The worked resource case visits 512 interpretations with no matching query and stops at its interpretation limit. Its status is resource-limit, its evidence strength is none, and its exhaustion flag is false. The recorded memory control verifies that this prefix does not retain a model history or powerset. It does not establish an operating-system memory limit or performance guarantee for every signature.

## Meaning of each outcome

| Outcome | Evidence supplied | Claim that remains unavailable |
| --- | --- | --- |
| `witness-found` | One complete structure satisfying T, every I, and Q | Source fidelity, an unrestricted universal property, or automatic readiness |
| `countermodel-found` | One complete structure satisfying T and I while Q is false | An assertion that every admissible model falsifies Q |
| `bounded-supported` | Full selected finite enumeration, at least one admissible model, no countermodel | Validity outside those selected cardinalities or a mechanized theorem |
| `bounded-no-witness` / `bounded-no-countermodel` | Exhaustive absence of the selected query witness in the exact finite scope | Unbounded absence or separation |
| `bounded-no-theory-model` | No structure satisfies T at the selected cardinalities | General inconsistency of T |
| `bounded-no-admissible-model` | Some T models exist, but none satisfies all required I in that scope | Non-vacuous support for Q |
| Timeout, cancellation, resource-limit, malformed, unsupported, provider error or unresolved binding | Execution/input diagnosis and retained counters where available | A logical absence conclusion or successful obligation result |

The provider never inserts Q into T. It checks all selected premises and populations in the same structure before evaluating Q. The global evaluation-step budget carries across interpretations; it does not reset for every model. Interpretation count, deadline, cancellation, tuple-space, domain-cardinality and output limits are checked. A deadline reached during final binding checks also prevents returning a witness.

Finite bounded validity remains distinct from the A05 mechanized-theorem requirement for universal properties. P02 cannot satisfy that minimum merely by reporting that every enumerated model passed. Its native records keep `unbounded_conclusion` null and `semantic_ready` false.

## Witness replay and provenance

A returned witness binds the complete model digest, typed subject, premise theory, required population list, exact query, cardinality vector and composition selections. Replay receives those inputs independently. It rejects substituted queries, scopes, composition inputs, mode changes, rehashed models that fail the required property, malformed records and forged readiness claims. It then checks the whole model using C02 satisfaction for T, I and Q. Replay is model checking; it does not treat the provider's own success flag as semantic evidence.

The provider records and rechecks its actual implementation, structural schema, selected policy and active Python/dependency runtime files. It also checks that the running interpreter, package origins and dependency versions match the selected inventory. This binds the new P02 implementation directly. The sealed P01 assessment remains the historical observation that the generic adapter was then pending; it is not rewritten to pretend the adapter already existed. Candidate workflow selection will need separately bound updated applicability evidence when it adopts this provider.

Source-currentness checks are optional explicit inputs to mathematical search. Without a selected snapshot they are reported as not checked. With a snapshot, exact current source refs are checked; with a live root, the source capture is reverified against the repository. Neither condition establishes meaning preservation. Source-fidelity and owner review remain separate obligations.

## Hand-derived theory controls

The first theory requires exactly one marked member. On a two-member carrier, both singleton marked interpretations leave an unmarked member. The provider finds and replays a witness and exhaustively confirms the selected bounded property. On a singleton carrier, the marked member leaves no unmarked member, so the witness query has scoped exhaustive absence. This illustrates why a result at one cardinality cannot stand for all cardinalities.

The second theory requires a total involution without fixed points. On a two-member carrier, the swap map is a witness: applying it twice returns the starting member, and each member moves. On a singleton carrier, every total endofunction fixes the only member, so no model exists in that scope. The two-member witness directly shows why singleton absence must not be reported as general inconsistency.

All 33 tests pass. Additional controls exercise countermodels under inhabitation guards, multiple sorts, binary and high-arity relations, zero-arity symbols, exact 32-model enumeration, bounded memory, global work budgets, cancellation during quantification, deadlines, output limits, replay claim boundaries and active-interpreter binding. These are candidate software/evidence controls with hand expectations. E03's independently selected required-set verification and P04's mechanized correctness/theorem work remain to be completed.

No current-source translation or source-owner acceptance is added by this unit. The next ready evidence-contract unit is E01, followed by immutable publication and independent evidence verification. The full episode still requires all-current interpretation/dependency coverage, joint theories, required proofs, source-fidelity dispositions and the final comprehensive review.
