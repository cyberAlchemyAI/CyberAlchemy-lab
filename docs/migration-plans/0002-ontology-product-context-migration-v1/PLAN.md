<!-- Generated from plan.json. Do not edit this projection. -->

# Ontology Product and context migration plan

## Outcome brief

The migration subject is the **CyberAlchemy Ontology Product**. Governance and Ontology Lifecycle remain independent Bounded Contexts. Craft receives and coordinates the work; it is not the migration subject.

- Plan: `CAL-MIGRATION-0002-ONTOLOGY-PRODUCT-CONTEXT-V1`
- State: `candidate-unadmitted`
- Current construction frontier: `SWU-CML11-101-SOURCE-CLOSURE`
- Current source validation: `BLOCK`
- Approval policy: `single-final-product-boundary`

## Boundary and next decision

No Product or Context bytes should be migrated yet. The next bounded action is to author the L0 source-closure candidate for the three drifted selectors. After L0 passes, the sequence continues without intermediate approval requests until the integrated L4 candidate is ready for one product-approval decision.

## Identity architecture

- Migrated Product: `CA2-PRODUCT-ONTOLOGY` → `product/products/ontology/v1/product.json`
- Work receiver: `CA2-PRODUCT-CRAFT/v1`
- Context Map: `cal.context-map.governance-ontology-lifecycle/v2`
- Planned coordination carrier: `coordination/contexts/ontology-product-migration/v1/coordination-context.json`
- Bounded Contexts:
  - `cal.context.governance/v3` — Own governance meaning and authority boundaries relevant to Ontology Product operation.
  - `cal.context.ontology-lifecycle/v3` — Own ontology lifecycle meaning, event history, replay, projections, and typed residue.

## Source blocker

- `SRC-CAV2-DEFINITIONS` — `7ce90add640413c11b9a43e48f7149351254fa7db9b76d09cfe05476ed86d225` → `94ece1b66668b0345b317f18b74dd81c42919028030bc3ef790f0dd6cf43e12e`; owner `definitions-governance`
- `SRC-CAV2-UMBRELLA-PRODUCT-THESIS` — `f9d91241160b37fba67c8e2043949a81ba7f88eba71440983adc085bbd0e5593` → `1350199cdf7dec61158316dc407b61b1a64a2d91eb2742a3f99b4dcf3238b806`; owner `CyberAlchemy v2 product owner`
- `SRC-CAV2-ONTOLOGY-PRODUCT-THESIS` — `19f65e2b0bdd3596749ba71402869ca0d5201fb1dbd91c5229beec45f2b6c175` → `025d8230a065f794945c13a579efc102222b0f454957230550d073e22cbb8869`; owner `CyberAlchemy v2 product owner`

## Migration layers

### `L0-SOURCE-SEMANTIC-CLOSURE` — Reconcile the selected source epoch

- State: `runnable-planning-work`
- Smallest unit: `SWU-CML11-101-SOURCE-CLOSURE`
- Decision unlocked: Whether current source meanings support one exact Ontology Product migration epoch.
- Exit: All eight source records resolve to current immutable digests; The source-closure validator returns PASS; Meaning-changing residue has an explicit owner route

### `L1-PRODUCT-IDENTITY-CARRIER` — Author the Ontology Product identity carrier

- State: `blocked-by-L0`
- Smallest unit: `SWU-CML11-102-PRODUCT-IDENTITY`
- Decision unlocked: Whether CyberAlchemy Lab can represent the same bounded subproduct without importing stale authority.
- Exit: Product-identity schema PASS; Generated projection equality; Same-Product and parent relation checks PASS

### `L2-PRODUCT-CONTEXT-COORDINATION` — Bind Product and existing contexts without collapse

- State: `blocked-by-L1`
- Smallest unit: `SWU-CML11-103-COORDINATION-CONTEXT`
- Decision unlocked: Whether one explicit coordination surface can connect the Product to the Governance and Ontology Lifecycle contexts while leaving Context Map ownership intact.
- Exit: Coordination Context schema PASS; Product and Context non-collapse checks PASS; No endpoint relation duplicated outside the Context Map

### `L3-SOURCE-PRESERVING-PACKAGE-MIGRATION` — Copy the exact Ontology Product package

- State: `blocked-by-L0-L2`
- Smallest unit: `SWU-CML11-104-ONTOLOGY-PACKAGE`
- Decision unlocked: Whether the source-bound product ontology can operate as a Lab candidate without rewriting its meaning.
- Exit: All copied bytes match the migration manifest or documented translations; Package validator PASS; Rollback manifest PASS

### `L4-INTEGRATED-PRODUCT-CANDIDATE` — Test the Product/Context migration candidate

- State: `blocked-by-L1-L3`
- Smallest unit: `SWU-CML11-105-INTEGRATED-CANDIDATE`
- Decision unlocked: Whether the complete migrated Product candidate is coherent and ready for one human product-approval decision.
- Exit: Collect-all product-test receipt; No unresolved causal blocker; Immutable candidate manifest ready for the single approval boundary

## Orthogonality

- A Product is not a Bounded Context; migrating Product identity never creates a context.
- A Bounded Context owns a model and ubiquitous language, not Product identity or Product value.
- A Context Map owns exact endpoint membership and directional relationships; endpoints carry no canonical backreferences.
- A Coordination Context binds exactly one Product and explicit context references without acquiring their semantic authority.
- Craft receives migration work but cannot silently become the migrated Product, context owner, or source meaning owner.
- Capabilities and runtimes remain children or realizations of the Ontology Product and are not promoted into Products during this migration.
- Machine records are canonical; every human view in this plan and every future migrated artifact is generated from its canonical record.

## Approval boundary

Approve or reject exactly one immutable Product/Context migration candidate digest.

This approval grants Product approval only; it does not grant admission, activation, cutover, publication, release, deployment, or source deletion.

## Claim ceiling

This candidate plans a corrected Ontology Product and Bounded Context migration and identifies the first runnable source-closure unit. It does not reconcile the drifted sources, mutate Craft, create or admit a Product or Context, copy source files, prove runtime conformance, approve a product, authorize implementation, admit, activate, cut over, publish, release, deploy, or retire CyberAlchemy-v2 material.
