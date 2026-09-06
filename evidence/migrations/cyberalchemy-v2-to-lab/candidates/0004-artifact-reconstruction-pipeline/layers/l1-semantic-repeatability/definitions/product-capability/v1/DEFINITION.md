<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Product Capability

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.product-capability`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.product`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Product Capability is the normalized definition identified by semantic.product-capability, owned within scope.product, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D67 without silently merging it with another target.

Bound source-semantic basis:

A Product Capability is a stable, owner-qualified statement of an outcome that
one Product must enable for named participants or consumers while preserving
explicit scope, contracts, context policies, evidence routes, and authority
limits. It states what the Product must make possible and why that behavior
belongs to the Product. It does not select the agent, component, command,
interface, workflow, or implementation that realizes the outcome.

Every Product Capability belongs to exactly one Product. Its identity remains
stable while realizations, interfaces, evidence, and implementation technology
change, provided the outcome, Product anchor, scope, and owner boundary remain
the same. A material change to any of those anchors requires a successor
Product Capability rather than a silent rewrite.

```text
```text
ProductCapability =
  (id, product_ref, outcome, scope, exclusions, participant_refs,
   consumer_refs, input_contract_refs, output_contract_refs,
   context_policy_refs, owner_routes, lifecycle_posture,
   realization_refs, evidence_refs, revision_history,
   challenge_route, authority_effect)

|product_ref| = 1
|owner_routes| >= 1
|consumer_refs| >= 1

lifecycle_posture =
  (kind, status, status_vocabulary_ref, evidence, commitment,
   provenance, owner, residue_refs)

lifecycle_posture.kind = product-capability
status_vocabulary_ref != null

valid(c) only if
  stable(c.id)
  and bounded(c.outcome, c.scope, c.exclusions)
  and contracts_resolve(c.input_contract_refs, c.output_contract_refs)
  and context_policies_resolve(c.context_policy_refs)
  and c.authority_effect = none

material_change(product_ref, outcome, scope, owner_routes) =>
  successor_product_capability_required

adopted(c) =/=> realized(c)
realized(c) =/=> conformant(c)
conformant(c) =/=> valuable(c)
observed(c) =/=> adopted(c)
permission_for(c) =/=> product_capability(c)
```

`lifecycle_posture` applies the `CAV2-D23` axis split. `status` is meaningful
only with its owning `status_vocabulary_ref`; this definition does not impose
one lifecycle enum on every capability. Evidence, owner commitment,
provenance, and residue remain separate posture fields. Realization,
conformance, and operational availability are separate axes owned by their
respective artifacts and evidence. None may be inferred from another or
collapsed into one `status` field.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.product-capability | Stable normalized identity for Product Capability. |
| CAV2-D67 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- A Product Capability is not the Product, Product Thesis, Project (`CAV2-D60`),
Goal (`CAV2-D59`), Context (`CAV2-D66`), Agent Capability
(`DEF-ARC-CAPABILITY`), Bounded Context, business rule, implementation,
component, command, interface, workflow, service, permission, role, authority
grant, runtime process, test, metric, evidence receipt, or release state.

An adopted Product Capability is not proof of implementation. An implemented
realization is not proof of conformance. A passing conformance check is not
proof of customer value, product-market fit, authority transfer, publication,
release, deployment, or permission to execute.

### Testable conditions

- The candidate identity remains cal.definition.product-capability.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

A Product Capability says what useful thing the product must make possible. It
does not yet say which tool or implementation will do it.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Product Capability is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

Inside CyberAlchemy v2, Define Shared Meaning, Resolve Bounded Language
Context, Resolve Registry Context, Governed Work Loop, and Governance
Enforcement are Product Capability candidates or projections owned by their
respective product and module surfaces. Public Arcanum Agent Capabilities such
as Invoke Define may realize part of a Product Capability, but the public
agent contract and the private product meaning remain separate authorities.

### Examples

- Resolve semantic.product-capability by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Product Capability.

## Applicability

Define a Product Capability after the Product Thesis identifies an outcome the
Product must repeatedly enable. Name its consumers, scope, inputs, outputs,
context policies, owners, and exclusions before selecting a realization.
Later, bridge it to one or more Agent Capabilities or system realizations and
test that bridge with separate conformance and runtime evidence.

Keep capability instances with the module that owns their local meaning and
lifecycle. A central Capability Ontology may index or project those instances,
but it must not copy their authority or turn one registry into their owner.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- A Product Capability is not the Product, Product Thesis, Project (`CAV2-D60`),
Goal (`CAV2-D59`), Context (`CAV2-D66`), Agent Capability
(`DEF-ARC-CAPABILITY`), Bounded Context, business rule, implementation,
component, command, interface, workflow, service, permission, role, authority
grant, runtime process, test, metric, evidence receipt, or release state.

An adopted Product Capability is not proof of implementation. An implemented
realization is not proof of conformance. A passing conformance check is not
proof of customer value, product-market fit, authority transfer, publication,
release, deployment, or permission to execute.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D67 | ## CAV2-D67: Product Capability | `04d9844b4c6b0e50fd2981801d23bb3b54e8a1f099ce5a351e7da483c84b6661` | `candidate-unadmitted` |

## Primary consumers

None declared.

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.product-capability@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.product-capability | cyberalchemy-v2:CAV2-D67 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-product-capability/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
