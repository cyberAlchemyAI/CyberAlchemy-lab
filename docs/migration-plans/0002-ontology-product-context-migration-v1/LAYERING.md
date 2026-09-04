<!-- Generated from plan.json. Do not edit this projection. -->

# Implementation layering

Each layer exists because it unlocks a distinct decision and reduces a different risk.

## `L0-SOURCE-SEMANTIC-CLOSURE`

**After this layer, we know:** Whether current source meanings support one exact Ontology Product migration epoch.

- State: `runnable-planning-work`
- Smallest working unit: `SWU-CML11-101-SOURCE-CLOSURE`
- Included:

  - Recompute and compare the three drifted source selectors.
  - Classify each change as compatible, meaning-changing, or owner-decision-required.
  - Produce one immutable source-closure candidate and validation receipt in CyberAlchemy Lab.

- Deferred:

  - Product identity authoring
  - Context binding
  - Package copying
  - Approval

- Exit evidence:

  - All eight source records resolve to current immutable digests
  - The source-closure validator returns PASS
  - Meaning-changing residue has an explicit owner route

## `L1-PRODUCT-IDENTITY-CARRIER`

**After this layer, we know:** Whether CyberAlchemy Lab can represent the same bounded subproduct without importing stale authority.

- State: `blocked-by-L0`
- Smallest working unit: `SWU-CML11-102-PRODUCT-IDENTITY`
- Included:

  - Canonical product.json
  - Generated PRODUCT.md
  - Parent Product relation
  - Semantic definition references
  - Lineage and source-closure references

- Deferred:

  - Bounded Context ownership inference
  - Runtime migration
  - Product approval

- Exit evidence:

  - Product-identity schema PASS
  - Generated projection equality
  - Same-Product and parent relation checks PASS

## `L2-PRODUCT-CONTEXT-COORDINATION`

**After this layer, we know:** Whether one explicit coordination surface can connect the Product to the Governance and Ontology Lifecycle contexts while leaving Context Map ownership intact.

- State: `blocked-by-L1`
- Smallest working unit: `SWU-CML11-103-COORDINATION-CONTEXT`
- Included:

  - One Coordination Context instance
  - Explicit Product ref
  - Explicit v3 Bounded Context refs
  - Craft consumer ref
  - Context Map compatibility check

- Deferred:

  - Context admission
  - Context Map admission
  - Runtime adapter
  - Approval

- Exit evidence:

  - Coordination Context schema PASS
  - Product and Context non-collapse checks PASS
  - No endpoint relation duplicated outside the Context Map

## `L3-SOURCE-PRESERVING-PACKAGE-MIGRATION`

**After this layer, we know:** Whether the source-bound product ontology can operate as a Lab candidate without rewriting its meaning.

- State: `blocked-by-L0-L2`
- Smallest working unit: `SWU-CML11-104-ONTOLOGY-PACKAGE`
- Included:

  - Exact allowlisted source copy
  - Lab path translation only where required
  - Schema and validator integration
  - Source and rollback manifest

- Deferred:

  - Lean compiler capability
  - Python runtime authority
  - Publication
  - Deployment

- Exit evidence:

  - All copied bytes match the migration manifest or documented translations
  - Package validator PASS
  - Rollback manifest PASS

## `L4-INTEGRATED-PRODUCT-CANDIDATE`

**After this layer, we know:** Whether the complete migrated Product candidate is coherent and ready for one human product-approval decision.

- State: `blocked-by-L1-L3`
- Smallest working unit: `SWU-CML11-105-INTEGRATED-CANDIDATE`
- Included:

  - Identity tests
  - Context coordination tests
  - Source closure tests
  - Package tests
  - Drift and rollback tests
  - Operator-readable evidence summary

- Deferred:

  - Admission
  - Activation
  - Cutover
  - Publication
  - Release
  - Deployment

- Exit evidence:

  - Collect-all product-test receipt
  - No unresolved causal blocker
  - Immutable candidate manifest ready for the single approval boundary
