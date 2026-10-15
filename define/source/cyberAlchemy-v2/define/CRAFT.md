# CyberAlchemy v2 Define Craft

Human-readable view of [`.craft/ledger.yml`](.craft/ledger.yml), the package-local machine source of truth. This view is non-canonical and grants no authority.

## Current structure

| Context | Owned scope | Validation |
| --- | --- | --- |
| `CTX-CAV2-DEFINE-ROOT` | Parent business-system bridge: 1 bridge node, 10 cross-package relations, 9 residue records | `BLOCK`: 19 structural checks pass; exact source currency blocks |
| `CTX-CAV2-DEFINE-BUSINESS-ONTOLOGY` | `cav2.define.business-domain.v1`: 9 product-meaning nodes, 8 relations | `PASS`: 13/13 |
| `CTX-CAV2-DEFINE-SYSTEM-ONTOLOGY` | `cav2.define.system-runtime.v1`: 65 DomainSpec nodes, 131 relations, six views, discovery Design | `FLAG`: 55 PASS, compilation `NOT_EVALUABLE`, 0 BLOCK |

The parent declares both child roots as independently owned nested packages. It validates each child profile, deterministic validator output, current append-only receipt, and every qualified bridge endpoint. Child material bytes and Craft collaboration files are excluded from the parent material digest by explicit contract.

## Active parent blocker

### `BLK-CAV2-DEFINE-SOURCE-CURRENCY-001`

Three pre-existing exact source bindings have SHA-256 or size drift:

- `SRC-CAV2-DEFINITIONS`
- `SRC-CAV2-DEFINITIONS-INDEX`
- `SRC-CAV2-AUTHORITY-MODEL`

The validator detects the changed bytes but cannot decide whether they remain applicable. The relevant source owners and the Define package owner must review them before any binding refresh or parent PASS claim.

The former `BLK-CAV2-DEFINE-CRAFT-INVENTORY-001` is retained in the ledger as resolved history. The current parent validator passes its nested-package and collaboration-file boundary check.

## Business ontology child

- Package: [`business-ontology/`](business-ontology/)
- Profile: [`business-ontology/PROFILE.json`](business-ontology/PROFILE.json)
- Nodes: [`business-ontology/NODES.json`](business-ontology/NODES.json)
- Relations: [`business-ontology/RELATIONS.json`](business-ontology/RELATIONS.json)
- Current receipt: [`business-ontology/receipts/validation-c86f855654ba1f7d.json`](business-ontology/receipts/validation-c86f855654ba1f7d.json)
- Output SHA-256: `783ff894cc4491a48bd16e8f3be96f87e0c02edbe0f750eae744553c24f29c62`

This child contains the original business branch plus the committed progressive context-sufficiency rule: explicit context and references first, then provenance-marked current-window and saved-session candidates, then a visible request when context remains insufficient or indeterminate. This is product meaning, not implemented behavior or product proof.

## System ontology child

- Package: [`system-ontology/`](system-ontology/)
- Profile: [`system-ontology/PROFILE.json`](system-ontology/PROFILE.json)
- DomainSpec source: [`system-ontology/domainspec-project/project.json`](system-ontology/domainspec-project/project.json)
- Current receipt: [`system-ontology/receipts/validation-5abb710c7e8930e0.json`](system-ontology/receipts/validation-5abb710c7e8930e0.json)
- Output SHA-256: `68a32c8cd91676bc7b53e13a2b3317049cf33a88e45f51682e27460c9af84903`
- Discovery Design: [`system-ontology/design/`](system-ontology/design/)

The graph has expanded to 65 nodes and 131 relations with technology-neutral revision,
persistence, transport, access/privacy, retention, telemetry, proportional
governance, accessibility, SLO, private Arcanum-boundary, progressive context
resolution, three-valued sufficiency, and private semantic-evaluator contracts.
The Design subpackage has 42 typed records, 38 relations, six views, ten
owner-routed gaps, and twelve unexecuted witness contracts. Canonical Invoke
Design W1-W3 was not run. `RES-CAV2-DEFINE-SYS-001` remains resolved and guarded
against the exact parent binding. The only child-validator non-PASS check is
full DomainSpec v2 compilation, which remains `NOT_EVALUABLE`.

## Parent bridge

The parent no longer duplicates business or system ontology nodes. Its ten current cross-package edges map:

- bridge membership to the business capability and system workflow;
- product capability to the proposed system workflow;
- system Definition Pack to the product Definition Pack;
- exact disposition rule to concept coverage;
- Define Session to work continuity;
- human control to answer recording; and
- bounded authority to the runtime authority envelope.
- progressive context sufficiency to the ordered resolution policy; and
- the proposed sufficiency operation back to the business rule it supports.

Two former bridge claims now have candidate system endpoints, but remain owner
gates rather than forced edges:

- `RES-DEFINE-008`: `ProportionateGovernancePolicy` exists, but the exact bridge relation and evidence are not owner-reviewed;
- `RES-DEFINE-009`: `ArcanumSubstrateInterface` exists as a private boundary, but the exact bridge relation and any public migration remain unreviewed.

Both remain explicit bridge evidence gaps until their owners provide stronger evidence or decide to keep them only as provenance.

## Other active gaps

| Gap | Scope | Current limit |
| --- | --- | --- |
| `GAP-CAV2-DEFINE-RES-001` | Parent | Three local definition candidates are not promoted. |
| `GAP-CAV2-DEFINE-RES-002` | System | Runtime behavior remains proposed, not implemented. |
| `GAP-CAV2-DEFINE-RES-003` | Business | Wider product ontology rebinding requires owner review. |
| `GAP-CAV2-DEFINE-RES-004` | Parent | Public Invoke migration is not decided or authorized. |
| `GAP-CAV2-DEFINE-RES-005` | System | Required ports/policies now exist; backend, protocol, topology, identity provider, retention values, SLOs, and deployment remain unselected. |
| `GAP-CAV2-DEFINE-RES-006` | Business | Measured product outcomes are not established. |
| `GAP-CAV2-DEFINE-RES-007` | Parent | Perennial documents are not admitted canonical artifacts. |
| `GAP-CAV2-DEFINE-SYSTEM-ONTOLOGY-CONFORMANCE-001` | System | Compiler conformance and release admission are absent. |
| `GAP-CAV2-DEFINE-BRIDGE-EVIDENCE-008` | Bridge | Candidate governance endpoint exists; exact bridge edge still needs owner review. |
| `GAP-CAV2-DEFINE-BRIDGE-EVIDENCE-009` | Bridge | Candidate private Arcanum endpoint exists; exact bridge edge and migration remain owner-gated. |

## Claim ceiling

The refactor establishes explicit package ownership, structural closure, deterministic child validation, current child receipts, and cross-package endpoint closure. It does not clear the parent source-drift blocker, prove product outcomes or runtime implementation, establish DomainSpec compiler conformance, admit canonical artifacts, promote definitions, authorize Invoke migration, execute, publish, release, deploy, or create any external effect.

## Next move

Route the three exact drifted parent source identities to their source owners and
the Define package owner. For the system child, resolve the ten discovery
Design gaps, obtain an exact Design input boundary and admitted Define result
before canonical Invoke Design, and obtain the DomainSpec compiler/profile
conformance path. Preserve authority effect none throughout.
