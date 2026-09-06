<!-- GENERATED FILE: edit scaffold.json and run build.py. -->

# Craft Agent-Facing Ontology Scaffold — Epoch 001

> Prototype navigation only. This scaffold is not semantic or operational authority.

- Scaffold: `CAL-CML08-P1-CRAFT-AGENT-ONTOLOGY-SCAFFOLD-EPOCH-001`
- Stage: `CML08-P1-AUTHOR-AGENT-ONTOLOGY-SCAFFOLD`
- Lifecycle: `prototype-scaffold`
- Canonicality: `non-authoritative`
- Authority effect: `none`

## Definition nodes

| Prototype definition | Term | Canonical object digest | Posture |
| --- | --- | --- | --- |
| `cal.prototype.definition.definition-prototype` | Definition Prototype | `ad6ecc231e86c791a3046ea29c14968f47d024e32c3a79feb3333da319f1233d` | `prototype-node` |
| `cal.prototype.definition.agent-ontology-scaffold` | Agent-Facing Ontology Scaffold | `10f6b506c3ffa6c1750798570d27ffcacc6b8e3043795e9cdd624876266bde01` | `prototype-node` |
| `cal.prototype.definition.product-capability-prototype` | Product Capability Prototype | `34640669d064305e41e6c5f6818c0bad678df69f749307f8cfe966fe96711508` | `prototype-node` |
| `cal.prototype.definition.business-ontology-prototype` | Capability-Local Business Ontology Prototype | `9069b8149acdc7341b6eff21b353ae61b093ed9e960b7d5424f4f6426511a9ec` | `prototype-node` |
| `cal.prototype.definition.domainspec-source-prototype` | Authored DomainSpec Source Prototype | `e637fb56a32a7ec13bf94fce1fdb90f9962c988cce95cd7600ee02f94f8e1bb6` | `prototype-node` |
| `cal.prototype.definition.compiled-graph-prototype` | Compiled Graph Prototype | `613d51b38fea185774d0c96749ab591c937ff413b9548ed78ae702e153db97ae` | `prototype-node` |
| `cal.prototype.definition.system-ontology-prototype` | System Ontology Prototype | `a9f1f857702ccb9b6404965393f9b5f04c45398c3aaca2e31cfe55ee0bee6458` | `prototype-node` |
| `cal.prototype.definition.implementation-prototype` | Implementation Prototype | `345d0d17643ce7f177243632ccf31104f5641740b9e0d3873d070d1034b58b78` | `prototype-node` |
| `cal.prototype.definition.testable-product-candidate` | Testable Product Candidate | `19f6360ef1d525c92720eb5b9385486958112390a93b523aff5e1cee2c919383` | `prototype-node` |
| `cal.prototype.definition.product-test-evidence` | Product-Test Evidence | `e2725b9e5ef3bb26843a65d137737aa667ee899e8574f9268745819c067a5c13` | `prototype-node` |
| `cal.prototype.definition.product-approval` | Product Approval | `15f96cf6b2478d0442fd4cb8ac4a8be7f0c6e472469b8c6689955901df754884` | `prototype-node` |
| `cal.prototype.definition.post-approval-authority-decision` | Post-Approval Authority Decision | `bdcb0a34d3796f1baa7ab9d3d911e40584af6cfd40119b0d549a406776b7644c` | `prototype-node` |

## Relation hints

| Source | Hint | Target | Posture |
| --- | --- | --- | --- |
| `cal.prototype.definition.definition-prototype` | `provides_provisional_meaning_for` | `cal.prototype.definition.agent-ontology-scaffold` | `prototype-hint` |
| `cal.prototype.definition.agent-ontology-scaffold` | `helps_agents_navigate` | `cal.prototype.definition.product-capability-prototype` | `prototype-hint` |
| `cal.prototype.definition.product-capability-prototype` | `requires_local_meaning_from` | `cal.prototype.definition.business-ontology-prototype` | `prototype-hint` |
| `cal.prototype.definition.business-ontology-prototype` | `informs_authored_intent_in` | `cal.prototype.definition.domainspec-source-prototype` | `prototype-hint` |
| `cal.prototype.definition.domainspec-source-prototype` | `compiles_to` | `cal.prototype.definition.compiled-graph-prototype` | `prototype-hint` |
| `cal.prototype.definition.compiled-graph-prototype` | `projects_to` | `cal.prototype.definition.system-ontology-prototype` | `prototype-hint` |
| `cal.prototype.definition.system-ontology-prototype` | `constrains` | `cal.prototype.definition.implementation-prototype` | `prototype-hint` |
| `cal.prototype.definition.implementation-prototype` | `is_frozen_within` | `cal.prototype.definition.testable-product-candidate` | `prototype-hint` |
| `cal.prototype.definition.testable-product-candidate` | `is_evaluated_by` | `cal.prototype.definition.product-test-evidence` | `prototype-hint` |
| `cal.prototype.definition.product-test-evidence` | `may_make_eligible` | `cal.prototype.definition.product-approval` | `prototype-hint` |
| `cal.prototype.definition.product-approval` | `must_precede_request_for` | `cal.prototype.definition.post-approval-authority-decision` | `prototype-hint` |

## Selected sources

| Dependency | Selector | Relevance | Drift effect | Digest |
| --- | --- | --- | --- | --- |
| `CAL-CML08-P0-DEFINITION-REGISTRY` | `whole-file` | exact prototype meanings projected as scaffold nodes | `block-selected-dependency` | `9d8fd83b51ef157cc9e199674680dffe9fd42c2db79b113e1642a3aed4dfeff6` |
| `CAL-CML08-P0-VALIDATION` | `whole-file` | current TESTED_PROTOTYPE evidence for the selected meanings | `block-selected-dependency` | `a04060c35fb3149c256676fc2f72883f3dd33fd52b85404d525a86cf1a36b621` |
| `CAL-CML08-P1-STAGE-CONTRACT` | `stage:CML08-P1-AUTHOR-AGENT-ONTOLOGY-SCAFFOLD` | P1 outputs, exit evidence, and effect ceiling | `block-selected-dependency` | `6ce5972ca93b541ca6fce8b8160539812160685293ea5ac290239018a88dd149` |
| `GOV-D65-R2-SCAFFOLD-001` | `scaffold_id:GOV-D65-R2-SCAFFOLD-001` | tested navigation-scaffold precedent and non-authority boundary | `block-selected-dependency` | `82122c2025043e31244467eedef37fa918292317f4ab337555ec3682dfc3284c` |
| `GOV-D65-R2-PROTOTYPE-CONSTRUCTION-001` | `construction_id:GOV-D65-R2-PROTOTYPE-CONSTRUCTION-001` | tested D65 prototype construction order and product boundary | `block-selected-dependency` | `7b8166b26834c2c8121cdc7aab1efb0cee560855b6c4df7a4f61cca2677744d0` |
| `CAL-LIVE-DEFINITION-REGISTRY` | `whole-file` | prove the scaffold did not mutate or collide with admitted Definition authority | `block-selected-dependency` | `59c9fc6b5e76f828e655ee72c065a6c2ffb524ba592ec4f0f225a889ab4cfd45` |

## Challenge routes

### CAL-P1-CHALLENGE-DEFINITION-DIGEST

- Condition: a selected prototype Definition is missing or has a different canonical object digest
- Route: `role:prototype-definition-contributor`
- Outcome: stop P2 and produce a new P0 evidence epoch before rebuilding the scaffold

### CAL-P1-CHALLENGE-SELECTED-SOURCE-DRIFT

- Condition: a source in source_selector_index is missing or differs from its bound digest
- Route: `role:craft-project-owner`
- Outcome: stop P2 until the selected source is restored or explicitly rebound in a successor scaffold

### CAL-P1-CHALLENGE-AUTHORITY-COLLAPSE

- Condition: the scaffold, a node, or a relation hint claims canonical, admitted, enforcement, or operational authority
- Route: `CA2-ROUTE-IMPLEMENT`
- Outcome: reject the scaffold candidate and restore prototype-only posture

### CAL-P1-CHALLENGE-AMBIENT-DRIFT

- Condition: ontology material outside source_selector_index changes
- Route: `CA2-ROUTE-VALIDATE`
- Outcome: record diagnostic evidence only; do not block P2 unless dependency relevance is established

### CAL-P1-CHALLENGE-P2-SELECTIONS

- Condition: P2 lacks a provisional Product Capability identity, explicit context posture, or dependency-closed import selectors
- Route: `role:craft-project-owner`
- Outcome: resolve the missing P2 construction choice before importing or implementing source content

## Dependency drift boundary

- Selected dependency drift: `block`
- Unselected ambient drift: `diagnostic-only`
- Implicit dependency expansion: `forbidden`
- Mandatory ontology runtime gate: `false`

## Stage transition evidence

- Tested state: `TESTED_PROTOTYPE`
- Next stage: `CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE`
- Next frontier candidate: `product_business_domainspec_compiled_system_implementation_prototypes`
- Effect: evidence-only; no Product Capability identity, context placement, source import, or operational authority is selected

## Claim ceiling

This machine-canonical P1 scaffold helps agents navigate exact P0 prototype Definitions, relation hints, selected sources, challenges, and D65 construction order. It does not canonize or admit meaning, activate ontology enforcement, select the P2 Product Capability or Bounded Context, import legacy source, implement a product, approve a product, or grant migration, publication, release, deployment, or external-effect authority.
