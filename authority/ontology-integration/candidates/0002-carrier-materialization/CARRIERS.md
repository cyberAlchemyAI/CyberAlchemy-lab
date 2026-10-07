<!-- GENERATED FILE: canonical data is carrier-postimages.json and package schemas. -->

# Step 7 ontology carrier materialization

- Carrier postimages: `7`
- Candidate successor: `1`
- New carriers: `6`
- Authority effect: `none`

## Carriers

### `cal.artifact-type.ontology-node/v2`

One immutable governed representation of one exact subject revision in one Ontology, with semantic and governance facets kept separate and bound to exact event epochs; it is neither its subject nor a replay source.

Realistic example: `authority/artifact-types/ontology-node/v2/fixtures/valid/record.json`

### `cal.artifact-type.ontology-edge/v1`

One independently identified Ontology-scoped connection between exact Ontology Nodes, either a digest-bound projection of a global Typed Relation or an explicitly local interpretation.

Realistic example: `authority/artifact-types/ontology-edge/v1/fixtures/valid/record.json`

### `cal.artifact-type.ontology-manifest/v1`

The stable identity and configuration record for one Ontology, distinct from its subjects, histories, cuts, views, packages, and runtime process.

Realistic example: `authority/artifact-types/ontology-manifest/v1/fixtures/valid/record.json`

### `cal.artifact-type.ontology-cut/v1`

One rebuildable consistent Ontology state at an exact semantic cursor and governance join policy, after endpoint-integrity validation.

Realistic example: `authority/artifact-types/ontology-cut/v1/fixtures/valid/record.json`

### `cal.artifact-type.ontology-view/v1`

One immutable purpose-bounded projection of an exact Ontology Cut for a named consumer, with source digest, freshness, expiry, exclusions, and no replay authority.

Realistic example: `authority/artifact-types/ontology-view/v1/fixtures/valid/record.json`

### `cal.artifact-type.semantic-event-history/v1`

The canonical append-only replay history index for complete semantic states of one Ontology Node or Edge; the referenced event records are replay sources.

Realistic example: `authority/artifact-types/semantic-event-history/v1/fixtures/valid/record.json`

### `cal.artifact-type.governance-event-history/v1`

The canonical append-only governance history index joined to exact semantic event epochs and upstream Governance evidence, without semantic patch authority.

Realistic example: `authority/artifact-types/governance-event-history/v1/fixtures/valid/record.json`

## Claim ceiling

This manifest binds seven candidate carrier postimages. It does not add them to Decision 0069, admit them, admit instances or relations, migrate an ontology, or activate a runtime.
