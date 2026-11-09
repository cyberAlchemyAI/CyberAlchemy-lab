<!-- Generated from binding.json. Do not edit. -->

# Ontology Product lifecycle runtime binding

- Binding: `cal.binding.ontology-product-lifecycle`
- Version: `1.0.0-test-candidate.1`
- Status: `test-candidate`
- Authority effect: `none`
- Product: `CA2-PRODUCT-ONTOLOGY/v1`
- Coordination Context: `cal.coordination-context.ontology-product/v1`

## Product port

- Trait: `ProductEvolutionRuntime`
- Input: ordered digest-chained ProductChange events
- Output: normalized ProductObservation
- Canonical source: ProductChange event history
- Projection policy: runtime observations and checkpoints are derived and never canonical replay sources

## Semantic contexts

- `cal.context.governance/v2` — `external-semantic-owner`
- `cal.context.ontology-lifecycle/v2` — `external-semantic-owner`

## Runtime implementations

| Runtime | Role | Replaceable | Adopted | Authority effect |
| --- | --- | --- | --- | --- |
| `cal.runtime.ontology-lifecycle-rust/v1` | `selected-existing-adapter` | `true` | `false` | `none` |
| `cal.runtime.reference-evolution/v1` | `independent-test-double` | `true` | `false` | `none` |

## Product tests

- evolution changes the observation without authority effect
- full replay and checkpoint plus tail recovery are byte-equivalent
- existing lifecycle runtime and reference runtime return equal Product observations
- context observation preserves exact endpoint and Context Map references
- malformed change chains fail closed in both implementations

## Residue

- `L3-BINDING-R1` — The binding carrier has not been admitted and the existing runtime has not been adopted. Treatment: Retain as a nonblocking construction candidate until the single final Product approval boundary and later separate lifecycle decisions.
- `L3-BINDING-R2` — The selected lifecycle runtime still exposes prototype profile names internally. Treatment: Keep behind the Product port; replacement or normalization is a later runtime-owner concern and does not alter Product semantics.

## Claim ceiling

This candidate binds one existing Rust lifecycle runtime and one independent reference adapter behind a Product-facing port for private tests. It does not adopt a runtime, transfer context or source meaning ownership, approve the Product, or authorize activation, cutover, publication, release, or deployment.
