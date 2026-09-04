<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Capability Instance

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.capability-instance`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-capability-recursion`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Capability Instance is an owner-local, version-exact realization or specialization of one Product Capability inside explicitly declared coordination and semantic contexts. It binds separate parent and instance authority lanes, inherited contract, extension scope, adoption decision, D65 construction stages, conformance evidence, lifecycle, drift and recomposition routes, recursion budget or stop, and terminal handoff.

```text
CapabilityInstance = (id, capability_version_ref, coordination_context_ref, bounded_context_refs, parent_authority_claim, instance_authority_claim, inherited_contract_ref, extension_scope, adoption_decision_ref, construction_binding_ref, conformance_refs, lifecycle, drift_route, recomposition_route, recursion_stop, terminal_handoff); Instance != Parent; Conformance does not imply Authority.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| Instance != Parent | Local realization identity and authority remain distinct from the reusable capability. |

### Boundary conditions

- Exactly one parent capability version is explicit.
- Recursion includes a budget or stop and a recomposition route.
- Parent and instance authority claims remain separate.

### Testable conditions

- Parent version, local owner, contexts, construction binding, recursion stop, recomposition, and handoff are present.
- Conformance is never interpreted as authority.

## Plain-language voice

A locally owned realization of a reusable capability, connected to its blueprint without becoming the blueprint.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

The existing ontology-lifecycle vertical can become a capability instance only after its exact parent capability and complete recursive and construction bindings are selected.

### Examples

- An Ontology Lifecycle runtime instance can live inside its context while referencing a separately owned product capability.

## Applicability

Owner-local realizations or specializations of exact Product Capability versions.

### Exclusions

- Product Capability meaning itself.
- Directories, implementation components, deployments, and conformance results.

## Boundaries

- A Capability Instance is not the Product Capability, Bounded Context, Coordination Context, Project, Goal, directory, component, deployment, conformance result, or authority grant.
- Copied folder structure does not establish recursion.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| CAL-SOURCE-ADMISSION-CTX00-CAV2-D64 | CAV2-D64 | `891c6b66c578bc0b8f763ad15e250fea255aed36274b9799436f6ab9544dd080` | `admitted` |
| CAL-SOURCE-ADMISSION-CTX00-CAV2-D67 | CAV2-D67 | `bf8f3cb9b7d22aaa3c54b7c1eb177b85100be9bc421142bb3ead7e2456431d13` | `admitted` |

## Primary consumers

- contexts/*/instances
- product/capabilities
- ontology-lifecycle

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `cal.definition.capability-instance`
- Drift owner: `role:definition-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.capability-instance@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |

## Evidence

- CAL-DECISION-0017-CTX00-SOURCE-ADMISSION

## Residue

- capability-instance-artifact-type-required
- parent-product-capability-required

## Claim ceiling

This candidate defines Capability Instance meaning only; it does not instantiate, adopt, bind, or conform any Product Capability.
