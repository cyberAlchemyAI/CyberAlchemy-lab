# E03 independent evidence verification: candidate review

E03 adds an independent finite-model witness checker and independently reconstructs the obligation denominator before it inspects submitted results. It follows the definitions-first plan: exact definition identity, types, selected meaning, logical conditions and evidence strength precede a readiness decision. This unit establishes a bounded candidate checking capability. It does not finish the formalization of the 183 current Lab definitions.

## 1. What defines the required work

The submitted results do not choose which obligations exist. A separately selected, byte-bound input envelope identifies the theory, relation requests, population policies and source-qualified endpoint bindings. A06 generates the required set from those inputs. E01/E02 then compare the captured bundle with that independently generated set, including logical statements, source references, assumption context, minimum strength and administrative or semantic gates.

Deleting a result, deleting a gate, or replacing an alias requirement with a disjointness requirement cannot become success by shortening the submitted denominator. Controlled forged packages exercise this boundary even when their outer hashes and content-addressed directory identities are internally consistent.

## 2. Definition identity and source applicability

The identity remains the exact definition ID, version, source path and source digest. The snapshot captures registry, source and admission-provenance bytes. E02 reconstructs the snapshot and checks that the selected sources belong to that snapshot's current selection. This is an exact historical selection when a live source root is absent. Passing a live root additionally checks current repository bytes.

A source change therefore leaves an old captured package available for historical inspection while preventing the old bytes from being treated as current. Source provenance is not proof that a definition's translation is faithful or that its propositions describe the world.

## 3. Closed independent input capture

The independent selection has a closed shape and explicit digest-bound references. It includes the selected dependency artifact, assumption artifact, carrier coupling records, finite query inputs, contract build and provider build record. Nested finite inputs identify their typed subject and composition inputs explicitly. Those bytes are checked even when the corresponding native result is missing; missing evidence cannot excuse skipping the selected input closure.

Reads use the existing descriptor-relative resolver, which rejects path traversal and symlink components. The verifier limits each file through that resolver and caps its independent input capture at 32 MB. Every loaded input is reread before success. These checks establish the selected byte closure, not a hermetic operating system or an authenticated external data source.

## 4. Nominal types and local-to-canonical translation

A06 obligations use local symbols in a selected theory. C01 subjects use canonical identities derived from definition ID, version, scope and local symbol. The verifier requires an explicit mapping between them. It checks the mapping against the original source-qualified IR origins, the selected shared-sort unions and the complete translated signature.

Predicates retain their owner definition. An explicit carrier alignment can share a sort without merging its predicates. Attributing Q to P's source, introducing a second meaning for a local name, omitting a declaration, or changing an argument or result sort fails this check. Equal visible labels do not supply a mapping. This type-level correspondence is still distinct from natural-language source fidelity.

## 5. Theory, assumptions, populations and query

The selected theory formulas and selected assumption formulas form T. The assumption context ID must match the independently selected theory context. Population obligations form a separate I. The consistency query uses no population assumptions; subsequent population and relation checks require the selected population conditions in the same structure.

Q is regenerated from the required obligation and translated through the explicit nominal map. The submitted provider query never defines Q. Exact provider input bindings must match the regenerated T, I and Q, the subject digest, cardinality vector, composition inputs and selected alignments. A provider cannot establish a target by silently inserting that target into T or by changing the population context.

The selected assumptions remain conditional premises. Neither their selection nor a model of them turns them into owner-admitted facts.

## 6. Structure before satisfaction

The new `Denotation` implementation independently validates a complete finite structure. Every declared sort has a nonempty domain of distinct named atoms. Every constant denotes a member of its declared sort. Each total function supplies one correctly sorted value for every tuple in its declared domain product; the verifier enumerates that product independently. Each predicate supplies a correctly sorted extension, which may be empty.

Missing interpretations, empty sort domains, extra symbols, duplicate tuples, out-of-sort values and partial total functions fail before evaluation. A declared empty predicate is a valid mathematical interpretation. Missing source information is not automatically converted into an empty predicate. String atoms represent model elements; they do not authenticate people, grants, events or records.

## 7. Independent satisfaction implementation

The evaluator follows the mathematical denotation specified in C02/DENOTATION.md. Terms denote environment assignments, constants or function applications. Predicate satisfaction is tuple membership; equality compares terms of an explicitly common sort. Negation, conjunction, disjunction, implication and equivalence use their stated truth conditions. Empty conjunction is true and empty disjunction is false. Quantifiers inspect the selected sort domain, and nested variable bindings shadow only their own body.

This implementation does not call the provider's evaluator or its witness replay routine. A control disables the provider evaluator during checking. Static AST typing and canonical identity regeneration still reuse C01, and byte resolution and envelope validation reuse earlier candidate components. Independence of witness evaluation is therefore specific and documented; the whole checking stack is not an independently proved system.

## 8. Checking a witness and a countermodel

For a witness, the exact supplied model must satisfy T and I and make Q true. For a countermodel, it must satisfy T and I and make Q false. Rehashing a changed model is insufficient: the evaluator recomputes those conditions. A joint-population witness with an emptied required predicate is rejected even when its new bytes are captured by an otherwise well-formed publisher.

A checked witness gives model-witness strength. A checked countermodel can refute the selected universal claim under its selected premises; it does not satisfy that claim's positive obligation. The result records whether the required positive strength is met separately from whether the model was checked.

## 9. Provider, profile and build bindings

Witness verification checks the selected policy digest, complete provider implementation/runtime binding list, actual profile bytes and toolchain record. The current runtime inventory is rechecked at both verification boundaries. E02 contract bindings are separately selected and checked against the active contract. The verifier also detects changes to its file, the obligation generator and obligation rules while it runs.

These are local build/currentness checks. They do not prove generic evaluator correctness, attest the machine or bind every system library and operating-system component. Python, the type checker, parser and resolver remain in the checker trust base.

## 10. Explicit unverified states

Bounded-exhaustion reports remain unverified by this unit. A witness checker cannot certify that every interpretation was enumerated. Unsupported solver or proof-kernel evidence remains explicitly pending. Missing evidence retains its required row. Reported gate support remains pending independent administrative or semantic review, including source fidelity, population exemptions and semantic dependency closure.

The complete return value always retains `semantic_ready: false`, `authority_effect: none` and `mechanized_proof: false`. Successful byte accounting and a checked model do not erase any pending obligation or owner review. There is no aggregation rule that lets one witness substitute for a universal proof or for a complete translation.

## 11. Resource and execution boundaries

The independent evaluator limits its work to 100,000 steps, limits function domain products and predicate extensions, checks cancellation and has a 30-second evaluation deadline. Exact finite cardinalities are positive integers up to the selected three-element domain ceiling; booleans are rejected. Budget exhaustion, cancellation, malformed input and unavailable input/build state yield rejection or unresolved execution, with no inferred logical absence.

The evaluator deadline bounds satisfaction work. The enclosing verifier performs bounded byte reads and runtime hashing without claiming a hard process-wide wall-clock limit. Candidate checking is local and read-only; it does not publish, admit or remove source evidence.

## 12. Validation and retained examples

The selected test log records the final unit suite. Controls cover actual provider witnesses, a separate denotation evaluator, connective identities, quantifier shadowing, total functions, nullary predicates, incomplete or ill-sorted models, substituted queries and policies, provider drift, omitted result/gate rows, dependency and assumption substitution, wrong nominal ownership, currentness changes, input mutation, missing nested bytes and unsupported bounded reports.

The worked-case harness retains three isolated serialized captures: a complete denominator with missing evidence, a checked joint-population witness, and a rehashed false population witness. Replays rebuild each capture in a fresh temporary root and rerun the verifier. These synthetic IDs and admission bytes are not installed in canonical Lab authority. Their outcomes test this candidate verifier; they are not formalization evidence for the 183 actual Lab definitions.

## 13. Review disposition and next work

This is agent candidate review, with exact implementation and validation evidence bound in the receipt. E03 is suitable for the bounded independent checks described above. Full semantic closure, source-owner translation review, generic soundness/completeness proofs, solver and kernel checking, full-family translations and the final episode review remain open. The next integration work should use these explicit checking boundaries and preserve them when adding source-backed pilot evidence or new profiles.
