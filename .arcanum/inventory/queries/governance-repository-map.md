# Governance repository map

The [Governance module candidate](../../../authority/governance/candidates/0001-three-lens-module/REPOSITORY-MAP.md) maps every path in the [repository inventory](../inventory.json) to a governance zone and status lookup route. Its [machine-readable zone map](../../../authority/governance/candidates/0001-three-lens-module/repository-map.json) is a navigation projection with no authority effect.

Use [map_repository.py](../../../authority/governance/candidates/0001-three-lens-module/map_repository.py) to inspect one path, page through a zone, obtain area counts, or check total path coverage. The [governance posture projector](../../../authority/governance/candidates/0001-three-lens-module/project.py) gives the full Authority, Provenance, and Lifecycle read view for the twelve artifact instances admitted by Decisions 0071–0072.

**Status rule:** physical inclusion in the repository does not imply governance admission. Resolve current Definition state in the [live Definition registry](../../../authority/definitions/registry.json), Artifact Type state in the [D72 effective registry](../../../authority/admissions/project-state-bootstrap/v1/registries/artifact-type-registry.json), Relation Kind closure in the [D70 registry](../../../authority/admissions/definition-complete-lab-model/v1/relation-kind-registry.json), instance status through exact admission overlays, and operation authority through the matching decision and authorization. Candidate source and evidence remain traceable without inheriting those effects.

This page and the map are non-authority navigation records. They do not create Ontology nodes, Typed Relations, Agent memory, runtime activation, or migration completion.
