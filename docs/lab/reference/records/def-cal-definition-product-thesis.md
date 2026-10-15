[Documentation home](../../README.md)

# Product Thesis

<a id="def-cal-definition-product-thesis"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Product Thesis

# Product Thesis

States who the product serves, the expected value, important constraints and evidence that could change those propositions.

**When it applies**

Use a Product Thesis to keep product direction stable while Projects, Goals, Research, Experiments, designs, interfaces, and implementations change. Trace each Project and Goal to the part of the thesis it is trying to realize or test. Use evidence to judge realizations and bounded outcome claims, and use the declared revision criteria when evidence challenges the thesis itself.

**Record formats**

[Product thesis · v1](type-cal-artifact-type-product-thesis-v1.md#type-cal-artifact-type-product-thesis-v1)

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-product-thesis-section-2"></a>

## Source explanatory wording

A product thesis says why a product should exist, what we believe it must do and protect, how it should create value, and what evidence could make us change our mind.

<a id="def-cal-definition-product-thesis-section-3"></a>

## Exact governing statement

Product Thesis is the normalized definition identified by semantic.product-thesis, owned within scope.product, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D63 without silently merging it with another target.

Bound source-semantic basis:

A product thesis is an owner-held, durable proposition that explains which product should exist, for whom, which problem it addresses, how it intends to create value, which first-order principles constrain it, which outcomes it seeks, which claims remain hypotheses, what evidence tests particular realizations, and what evidence or counterevidence requires revision.

A Product Thesis must preserve the product identity, participants, problem, value proposition, value mechanism, first-order principles, intended outcomes, boundaries, hypotheses, evidence and counterevidence routes, revision criteria, owner route, commitment state, revision history, and challenge route. Its principles may be committed before a complete product realization exists, but outcome, market, causal, and effectiveness claims remain bounded by evidence.

````
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
````

- A Product Thesis is not the product, product vision, strategy, roadmap, business plan, Goal (`CAV2-D59`), Project (`CAV2-D60`), premise (`CAV2-D55`), hypothesis, specification, evidence, market claim, or implementation. It can contain hypotheses and guide specifications without becoming either one. A committed thesis does not prove that the product exists, works, creates value, has customers, or has product-market fit. Promoting this term creates Definition authority for the meaning of `product thesis`. It does not promote the CyberAlchemy thesis artifact, approve a product strategy, achieve a Goal, authorize an Experiment, or validate product value.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/product-thesis/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.product-thesis@1.0.0-candidate.1

**Content fingerprint · SHA-256**

e323ddd93cfe4c42d4e4dac422b22cb77e3871a9a500de57fa29131eed92c0d4

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use a Product Thesis to keep product direction stable while Projects, Goals,\nResearch, Experiments, designs, interfaces, and implementations change. Trace\neach Project and Goal to the part of the thesis it is trying to realize or test.\nUse evidence to judge realizations and bounded outcome claims, and use the\ndeclared revision criteria when evidence challenges the thesis itself.",
  "authority_scope_ref": "scope.product",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
