<!-- GENERATED FILE: canonical data is implementation-layering.json. -->

# Artifact Reconstruction Pipeline Implementation Layering

## L0: D65 dependency-closed vertical

**Decision:** After this layer, we know whether existing Lab artifact mechanics can reconstruct one cross-family normalized slice without identity or authority collapse.

**Minimum working unit:** One D65 Definition, five Artifact Types, two evaluation profiles, reused relations, hostile fixtures, and exact source bindings.

**Exit evidence:** receipts/validation.json, manifest.json

## L1: Semantic-family repeatability

**Decision:** After this layer, we know whether candidate Definition reconstruction is repeatable across the remaining semantic targets.

**Minimum working unit:** Batch-independent Definition candidates with voice, source, index, and drift closure.

**Exit evidence:** family conformance receipt, drift audit

## L2: Cross-family reconstruction

**Decision:** After this layer, we know whether Artifact Types, profiles, relation kinds, and derived surfaces can be reconstructed without redundant canonical axes.

**Minimum working unit:** Family-specific schemas and dependency-ordered target batches.

**Exit evidence:** cross-family conformance receipt

## L3: Context reconstruction and recovery

**Decision:** After this layer, we know whether approved ontology routes can form bounded contexts that evolve and recover without losing source lineage.

**Minimum working unit:** One context vertical with map, bindings, evolution, rollback, and recovery tests.

**Exit evidence:** context product-test receipt

## Boundary

This implementation layering guides candidate construction only. It is not an execution registry, admission decision, activation plan, or migration authority.
