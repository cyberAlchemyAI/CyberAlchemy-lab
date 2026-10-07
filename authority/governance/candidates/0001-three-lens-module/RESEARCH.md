# Research and source map

## Local admitted authority

| Source | Finding applied here |
| --- | --- |
| [Definition registry](../../../definitions/registry.json) and the twelve exact Definition files in [sources.json](sources.json) | Authority is owner-qualified and scope-bounded; Provenance is a declared origin and transformation chain; evidence, decision, policy, and challenge have separate effects. The governance-axis invariant keeps seven facets independent. |
| [D72 Artifact Type registry](../../../admissions/project-state-bootstrap/v1/registries/artifact-type-registry.json) | The current admitted registry includes two Project history carriers added after D70. An admitted-current carrier contract does not automatically admit its instances. |
| [D70 Relation Kind registry](../../../admissions/definition-complete-lab-model/v1/relation-kind-registry.json) | Origin, derivation, authority scope, decision effect, lifecycle succession, and other relation axes are distinct and use closed endpoint pairs. There is no single `axis.provenance` that replaces them. |
| [D71 bundle](../../../admissions/cyberalchemy-lab-operational-foundation/v1/bundle.json), [artifact overlay](../../../admissions/cyberalchemy-lab-operational-foundation/v1/artifact-instance-admission.json), [relation overlay](../../../admissions/cyberalchemy-lab-operational-foundation/v1/typed-relation-admission.json) | Nine artifact instances and thirteen Typed Relation instances are admitted. Runtime activations are zero. Effective instance state comes from the overlay, while copied candidate status remains in source bytes. |
| [D71 histories](../../../admissions/cyberalchemy-lab-operational-foundation/v1/history-declarations.json) | Two logical Project histories are declared empty at cursor 0. They are not event instances or proof of present runtime state. |
| [D72 bundle](../../../admissions/project-state-bootstrap/v1/bundle.json), [artifact overlay](../../../admissions/project-state-bootstrap/v1/artifact-instance-admission.json), [Project semantic history](../../../admissions/project-state-bootstrap/v1/instances/artifacts/project-semantic-event-history.json), [Project governance history](../../../admissions/project-state-bootstrap/v1/instances/artifacts/project-governance-event-history.json), [successor Project State](../../../admissions/project-state-bootstrap/v1/instances/artifacts/project-state.json) | Decision 0072 admitted two Project history carriers and instances, one event in each stream, and the first immutable successor Project State. The predecessor became historical. Decision 0072 itself is not included in the successor. |
| [Integrated ontology model](../../../ontology-integration/candidates/0003-definition-complete-runtime-integration/integrated-model.json) | Project State is durable; Context and Ontology Views derive from it; an Agent is ephemeral. Definition, instance, Typed Relation, ontology edge, and event history remain different subjects. |

## External comparisons, not imported requirements

- [W3C PROV-O](https://www.w3.org/TR/prov-o/) models entities, activities, agents, and derivation/attribution separately. This supports a typed lineage trail, but the Lab's admitted relation and authority contracts remain controlling.
- [W3C PROV Constraints](https://www.w3.org/TR/prov-constraints/) treats valid provenance as constrained by identity, ordering, and impossibility rules. A chain of named sources alone is insufficient to establish a valid transformation history.
- [NIST SP 800-162](https://csrc.nist.gov/pubs/sp/800/162/upd2/final) describes access decisions in terms of subject, object, action, environment, and policy attributes. The module therefore marks action authorization `not-evaluated` instead of treating record admission or an owner field as permission.

## Design result

The three lenses are coherent as **questions over one subject**. The seven independent facets and closed Relation Kind axes remain the underlying semantic structure. The smallest executable slice is a read-only posture projection over D71–D72 admitted instances. Project history carriers and the first event pair now exist. A reusable live writer, access-control evaluator, runtime state observer, and next Project State successor require separate contracts and evidence.
