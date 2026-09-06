<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Product Thesis

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.product-thesis`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.product`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Product Thesis is the normalized definition identified by semantic.product-thesis, owned within scope.product, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D63 without silently merging it with another target.

Bound source-semantic basis:

A product thesis is an owner-held, durable proposition that explains which
product should exist, for whom, which problem it addresses, how it intends to
create value, which first-order principles constrain it, which outcomes it
seeks, which claims remain hypotheses, what evidence tests particular
realizations, and what evidence or counterevidence requires revision.

A Product Thesis must preserve the product identity, participants, problem,
value proposition, value mechanism, first-order principles, intended outcomes,
boundaries, hypotheses, evidence and counterevidence routes, revision criteria,
owner route, commitment state, revision history, and challenge route. Its
principles may be committed before a complete product realization exists, but
outcome, market, causal, and effectiveness claims remain bounded by evidence.

```text
```text
ProductThesis =
  (id, product_ref, participants, problem, value_proposition,
   value_mechanism, first_order_principles, intended_outcomes,
   boundaries, hypotheses, evidence_routes, counterevidence_routes,
   revision_criteria, owner_route, commitment_state,
   revision_history, challenge_route)

commitment_state in { draft, committed, revised, retired, superseded }

committed(ProductThesis) =/=> realized(Product)
evidence_for_one_realization =/=> proves(ProductThesis)
```
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.product-thesis | Stable normalized identity for Product Thesis. |
| CAV2-D63 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- A Product Thesis is not the product, product vision, strategy, roadmap,
business plan, Goal (`CAV2-D59`), Project (`CAV2-D60`), premise (`CAV2-D55`),
hypothesis, specification, evidence, market claim, or implementation. It can
contain hypotheses and guide specifications without becoming either one. A
committed thesis does not prove that the product exists, works, creates value,
has customers, or has product-market fit.

Promoting this term creates Definition authority for the meaning of `product
thesis`. It does not promote the CyberAlchemy thesis artifact, approve a product
strategy, achieve a Goal, authorize an Experiment, or validate product value.

### Testable conditions

- The candidate identity remains cal.definition.product-thesis.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

A product thesis says why a product should exist, what we believe it must do and
protect, how it should create value, and what evidence could make us change our
mind.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Product Thesis is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2, the Product Thesis commits to an ergonomic, governed
human-machine work loop that preserves human agency, shared meaning, evidence,
ownership, bounded authority, and honest incompleteness. The PythonConstraint
Project tests one bounded realization of that thesis. It cannot prove the whole
thesis or redefine it from one experiment.

### Examples

- Resolve semantic.product-thesis by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Product Thesis.

## Applicability

Use a Product Thesis to keep product direction stable while Projects, Goals,
Research, Experiments, designs, interfaces, and implementations change. Trace
each Project and Goal to the part of the thesis it is trying to realize or test.
Use evidence to judge realizations and bounded outcome claims, and use the
declared revision criteria when evidence challenges the thesis itself.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- A Product Thesis is not the product, product vision, strategy, roadmap,
business plan, Goal (`CAV2-D59`), Project (`CAV2-D60`), premise (`CAV2-D55`),
hypothesis, specification, evidence, market claim, or implementation. It can
contain hypotheses and guide specifications without becoming either one. A
committed thesis does not prove that the product exists, works, creates value,
has customers, or has product-market fit.

Promoting this term creates Definition authority for the meaning of `product
thesis`. It does not promote the CyberAlchemy thesis artifact, approve a product
strategy, achieve a Goal, authorize an Experiment, or validate product value.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D63 | ## CAV2-D63: Product Thesis | `590a70d5490d4652ba68af4ac7514eb35157364dd216b1bada901d1e4e640ef2` | `candidate-unadmitted` |

## Primary consumers

None declared.

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.product-thesis@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.product-thesis | cyberalchemy-v2:CAV2-D63 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-product-thesis/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
