# Minted Project Contract Index

Generated from `contract-manifest.json` and
`definitions/minted-project/supported-profiles.yml`. The contract test rejects
manual drift between this human view and those machine sources.

## Authority

- Profile admission: `definitions/minted-project/supported-profiles.yml`.
- Source and generated record form: this directory's JSON Schemas.
- Concrete domain meaning: the minted consumer project's source records.
- Graph, provenance, Markdown, and receipts: generated read models only.

## Experimental Profile

| Profile | Version | Status | Layout | Kinds | Relationships |
| --- | --- | --- | --- | --- | --- |
| `feature-with-independent-node-files` | `1` | `experimental` | `per-node-connections` | `Entity`, `Event`, `Operation`, `Rule` | `enforces` (Rule→Operation), `performs` (Entity→Operation), `produces` (Operation→Event) |

Formation schemas: `Entity` → `formations/entity-body.schema.json`, `Event` →
`formations/event-body.schema.json`, `Operation` →
`formations/operation-body.schema.json`, `Rule` →
`formations/rule-body.schema.json`.

Registry bindings use SHA-256 over the exact current bytes of
`definitions/meta-types/meta-types.yml` and
`definitions/relationships/relationships.yml`. The project and build receipt
also bind the exact supported-profile registry digest.

## Contract Family

| File | Schema ID | Record | Role | Authority | Version |
| --- | --- | --- | --- | --- | --- |
| `project.schema.json` | `https://domainspec.dev/schemas/minted-project/project/v1` | `project` | `source` | `consumer-project-source` | `minted-project/v1` |
| `feature.schema.json` | `https://domainspec.dev/schemas/minted-project/feature/v1` | `feature` | `source` | `consumer-project-source` | `minted-feature/v1` |
| `connection.schema.json` | `https://domainspec.dev/schemas/minted-project/connection/v1` | `connection` | `source` | `source-node-owned` | `minted-connection/v1` |
| `node.schema.json` | `https://domainspec.dev/schemas/minted-project/node/v1` | `node` | `source` | `consumer-project-source` | `minted-node/v1` |
| `formations/entity-body.schema.json` | `https://domainspec.dev/schemas/minted-project/formations/entity-body/v1` | `entity-body` | `source` | `consumer-project-source` | `minted-entity-body/v1` |
| `formations/event-body.schema.json` | `https://domainspec.dev/schemas/minted-project/formations/event-body/v1` | `event-body` | `source` | `consumer-project-source` | `minted-event-body/v1` |
| `formations/operation-body.schema.json` | `https://domainspec.dev/schemas/minted-project/formations/operation-body/v1` | `operation-body` | `source` | `consumer-project-source` | `minted-operation-body/v1` |
| `formations/rule-body.schema.json` | `https://domainspec.dev/schemas/minted-project/formations/rule-body/v1` | `rule-body` | `source` | `consumer-project-source` | `minted-rule-body/v1` |
| `graph.schema.json` | `https://domainspec.dev/schemas/minted-project/graph/v1` | `graph` | `generated` | `generated-semantic-read-model` | `minted-graph/v1` |
| `source-manifest.schema.json` | `https://domainspec.dev/schemas/minted-project/source-manifest/v1` | `source-manifest` | `generated` | `generated-provenance-read-model` | `minted-source-manifest/v1` |
| `markdown-view.schema.json` | `https://domainspec.dev/schemas/minted-project/markdown-view/v1` | `markdown-view` | `generated` | `generated-human-read-model` | `minted-markdown-view/v1` |
| `build-receipt.schema.json` | `https://domainspec.dev/schemas/minted-project/build-receipt/v1` | `build-receipt` | `generated` | `generated-verification-evidence` | `minted-build-receipt/v1` |

## Boundary Rules

1. A source connection owns `edge_id`, `type`, and `to`; its containing node
   supplies `from` during normalization.
2. Profile membership is separate from kind existence and relationship status.
3. Every project path is relative and must remain below the consumer root.
4. Generated artifacts carry explicit generated authority posture and are never
   repaired by hand.
5. Digests are lowercase SHA-256. A source-set digest hashes canonical JSON for
   the sorted `{path,digest}` input records with a final newline.
