# What we already have, and what Open Ontologies could add

Focused source comparison, 2026-11-02. This covers the definition-assurance
candidate through its inspected I04 record, the relational checker's v2/v3
proofs and reviewed v3 extensions, and the pinned Open Ontologies checkout.
No formal suite was rerun and no provider was integrated.

## What the Lab already does

### Definition checking

The Lab has an implemented language for describing finite structures and asking
logical questions about them. It supports named types, predicates and relations,
functions, equality, Boolean expressions, and quantifiers. It can search for an
example or counterexample and check supplied examples independently.

The checks distinguish several questions:

- Can the selected definitions hold together?
- Can all required kinds of thing actually exist in the same example?
- Are two concepts aliases, subtypes, overlapping, disjoint, or independent in
  the precise way we declared?
- Did a source, assumption or dependency change, making old evidence stale?

There is also a working capture/check/verify/diff/report command interface,
dependency-based invalidation, and selected-theory regression. This is more than
an early design or the original three-definition pilot.

Sources: [evaluator](../../../../craft/formalization/candidates/definition-assurance-v1/semantics.py),
[independent model verification](../../../../craft/formalization/candidates/definition-assurance-v1/verifier.py),
[invalidation](../../../../craft/formalization/candidates/definition-assurance-v1/invalidation.py),
[I03 review](../../../plans/definition-formal-assurance/candidate/assurance-snapshots-v1/units/I03/REVIEW.md),
and [I04 review](../../../plans/definition-formal-assurance/candidate/assurance-snapshots-v1/units/I04/REVIEW.md).

The recorded I04 coverage remains partial: eight candidate definition drafts,
seven separate partial projections, zero owner-accepted whole-definition
translations and zero whole-definition proofs. Its selected baseline contains
183 current identities; 175 lack a per-definition draft. These are recorded
coverage results, not a freshly rebuilt audit of every source today.

The Python evaluator and independent replay are not backed by a general
mechanized correctness theorem. A checked example supports its exact encoded
theory. It does not show that the encoding preserves every source sentence.

### Relation proofs

The relational checker already has typed recursive inference: it calculates
consequences from selected facts and rules and can explain their support.
It has an exact saturation theorem and model-expansion/conservativity results
for its checked fresh-head extensions. Complete-profile absence is distinct
from an unsupported or unfinished query.

Those extension proofs have specific assumptions: a fixed domain, protected
roots and epoch, with new predicates and ordinary rule heads. They are not a
claim that every arbitrary ontology replacement preserves existing meaning.

The reviewed v3 extensions add conditions with explicit unknown values,
evidence support, bounded delegation chains that cannot widen permission,
criterion-based fulfillment, controlled lifecycle replacement, and preservation
of decoded typed values. There is also an actual independent nanoda checker
sample; it does not cover the whole checker.

Sources: [exact recursive closure](../../../../craft/formalization/candidates/relational-theorem-checker/v2/s03/RecursiveSaturation.lean),
[checked extension conservativity](../../../../craft/formalization/candidates/relational-theorem-checker/v2/s03/RecursiveConservativity.lean),
[query meanings](../../../../craft/formalization/candidates/relational-theorem-checker/v3/p04/QuerySemantics.lean),
[implemented extension review](../../../../craft/formalization/candidates/relational-theorem-checker/v3/execution/extensions-review.md),
and [recorded v3 completion](../../../../craft/formalization/candidates/relational-theorem-checker/v3/execution/PROGRESS.md).

These are scoped proofs and candidate operational profiles. They do not prove
all natural-language definitions or authenticate supplied real-world facts.

## The useful differences

| Concern | Already in the Lab | What Open Ontologies could add |
| --- | --- | --- |
| Logical evaluation | A typed finite language, model search and independent replay. | Additional model-search routes and Lean-checked model evidence for its supported fragment. |
| Inference and rule proofs | Typed recursive closure, exact explanations and scoped extension proofs. | A reusable RDF/Horn engine, standard ontology rules and corresponding derivation certificates. This overlaps existing capability. |
| Definition distinction and consistency | Joint theory and required-population checks, with declared relation obligations. | Checked countermodels and supported refutations as additional evidence providers. Translation still needs review. |
| Meaning-preserving changes | Dependency invalidation, regression, and preservation/conservativity obligations; stronger checked fresh-head results in the relation checker. | Concrete reports of new consequences over existing RDF terms. The two conservativity claims have different scopes. |
| Agent views | Exact versions and selected views; existing semantic preservation machinery. | A dedicated workflow checking which named conclusions survive in a retrieved RDF slice. |
| Independent checking | Separate model replay and a real but narrow independent-kernel sample. | Isabelle/Rocq Horn checking routes and other small checker formats for the matching fragments. They do not automatically check our existing Lean proofs. |

The clearest first transfers are the agent-view workflow and semantic-change
reports. Small verified checkers are a further candidate for strengthening
evidence from existing model-search work. Building a second general evaluator
or replacing the relation checker is not justified by this comparison.

## The formats do not line up automatically

The upstream finite first-order model checker has unary and binary predicates,
constants and one nonempty carrier. Our definition evaluator supports multiple
sorts, functions and general predicate arities. We must select a matching subset
or prove a suitable translation; lowering richer input silently would lose
meaning. Upstream [finite-model semantics](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/lean/Fol/Semantics.lean).

Likewise, positive RDF/Horn inference does not directly express our unknown
conditions, protected authority roots, source-qualified conformance, or full
normative meaning. OWL domain/range inference is different from rejecting a
forbidden endpoint-kind pair.

Upstream [claim-preservation analysis](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/projection_entailment.rs)
checks selected positive goals under a pinned rule table. Its
[consequence-change analysis](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/conservativity.rs)
does not replace the Lab's model-expansion theorem or complete definition-family
assurance.

## A practical starting point

Reuse an existing Provenance/Authority example. Its selected partial theory
permits an artifact with provenance but no authority, and another with both.
That example already tests the intended distinction.

Translate that bounded theory and one existing witness into the upstream model
format. Check the witness independently, then test a deliberately altered rule
that collapses provenance into authority. Bind the original source versions,
translation, assumptions, required populations and evidence throughout.

This would test whether an additional verified checker strengthens evidence for
our existing work. It would not settle the outstanding source-meaning reviews
or establish proof coverage for all definitions. The experiment has not run.
