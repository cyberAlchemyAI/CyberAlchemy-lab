<!-- Generated from source-closure.json. Do not edit. -->

# Prototype source closure

- Closure: `CAL-ONTOLOGY-PRODUCT-SOURCE-CLOSURE-TEST-CANDIDATE-1`
- Status: `prototype-dependency-closure`
- Authority effect: `none`

Only the exact sources below control this thin Product candidate. The legacy Product Ontology package validator remains diagnostic and blocked; this closure neither rewrites nor admits it.

## Exact dependencies

| Source | Root | Path | SHA-256 | Owner |
| --- | --- | --- | --- | --- |
| `CAL-SOURCE-ONTOLOGY-AS-PRODUCT-SEMANTIC-MODEL` | `lab` | `docs/migration-plans/0003-ontology-as-product-context-migration-v1/semantic-model.json` | `be5b0256ee1c3a2a508602569b093eadfeb70cad961843dc327e54cd1199f8ea` | `Lab architecture owner` |
| `CAL-SOURCE-PRODUCT-DEFINITION` | `lab` | `authority/definitions/candidates/0006-craft-identity/definitions/product/v1/definition.json` | `19c6b3bdb5e4c8515837d40c2b0a98b0fecb6edc3698aab359fa2a0d64d9a1cd` | `role:definition-owner` |
| `CAV2-SOURCE-DEFINITIONS` | `domainspec-core` | `cyberAlchemy-v2/authority/definitions/DEFINITIONS.md` | `94ece1b66668b0345b317f18b74dd81c42919028030bc3ef790f0dd6cf43e12e` | `definitions-governance` |
| `CAV2-SOURCE-ONTOLOGY-PRODUCT-THESIS` | `domainspec-core` | `cyberAlchemy-v2/product/ontology-product/PRODUCT-THESIS.md` | `025d8230a065f794945c13a579efc102222b0f454957230550d073e22cbb8869` | `CyberAlchemy v2 product owner` |
| `CAV2-SOURCE-ONTOLOGY-PRODUCT-IDENTITY` | `domainspec-core` | `cyberAlchemy-v2/product/ontology-product/IDENTITY-DECISION.json` | `5a4f64efd4f2d34129b90395f6ad4c784748316b8d90fcca38038c7c55ae6cac` | `CyberAlchemy v2 product owner` |
| `CAV2-SOURCE-ONTOLOGY-PRODUCT-NODES` | `domainspec-core` | `cyberAlchemy-v2/ontology/ontology-product/nodes.json` | `7c8502ccbd67f1fe5eb3b69b79dbb7394e51cd6e676a5da1ddf292269f1de47a` | `CyberAlchemy v2 ontology route` |
| `CAV2-SOURCE-ONTOLOGY-PRODUCT-RELATIONS` | `domainspec-core` | `cyberAlchemy-v2/ontology/ontology-product/relations.json` | `b9af6f4679187656080753e703669622db2801234063ccbcd318190ec3969771` | `CyberAlchemy v2 ontology route` |

## Diagnostic residue

- `CML11-B01-LEGACY-SOURCE-REGISTRY-DRIFT` — The legacy cav2.ontology-product source registry records older digests for three sources. Its validator remains BLOCK and must be reconciled before a source-preserving migration claim. Status: `open-nonintersecting-for-thin-prototype`.

## Claim ceiling

Exact dependency closure for one private thin prototype only. It does not admit sources, repair the legacy source registry, prove migration completion, or transfer source authority.
