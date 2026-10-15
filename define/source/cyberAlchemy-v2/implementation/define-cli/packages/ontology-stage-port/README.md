# Define Ontology Stage Port

This candidate package lets Define consume statically configured ontology
authoring adapters through ARE's existing Module Port without giving ARE the
workflow or putting ontology-specific questions into Define core.

An empty stage registry is valid. A configured stage has one exact descriptor,
module identity, capability set, prerequisite list, and Alch entry-point list.
There is no discovery, fallback, provider priority, installation, or hot reload.

`runOntologyStage` is the L0 proof coordinator. It uses compiled Alch decisions
for dependency, response, readiness, and handoff laws; uses the typed port for
ontology-specific describe/question/evaluate/materialize/validate operations;
and emits a digest-bound candidate handoff receipt only after exact user
confirmation. Its results have `authority_effect: none`.

The synthetic adapter is test evidence, not a Product Ontology definition or an
admitted module.

## Open Questions

The Product adapter, durable Define Client API, Business dependency, and Plan
consumer remain owned by the later layers in
[`planning/integration-api/IMPLEMENTATION-LAYERING.md`](../../planning/integration-api/IMPLEMENTATION-LAYERING.md).

