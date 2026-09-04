---
title: Craft Identity Implementation Layering
status: draft
updatedAt: 2026-09-03
owner: role:lab-architecture-owner
scope: system
---

# Craft Identity Implementation Layering

Layer 0 is the smallest semantic and authority closure. Later layers add carrier mechanics, materialization, and admission packaging without invalidating earlier guarantees.

## Context

- Target: CML-07 Craft Product/Project/Method/Goal identity graph
- Current state: admitted Definition foundation; identity carriers not authored
- Primary operator: CyberAlchemy Lab architecture and Product owners
- Primary constraint: migration without identity or authority collapse
- Source: `docs/identity-packs/0001-craft-identity-chain/chain.json`

## Layer Decision Table

| Layer | Decision question | Stages | Promotion |
| --- | --- | --- | --- |
| `L0` | After this layer, we know whether the identity graph has authoritative meanings and separately accountable owners. | `CML07-S0-ADMIT-SOURCES-AND-BIND-OWNERS`, `CML07-S1-AUTHOR-CANONICAL-DEFINITIONS` | Makes identity Artifact Type authoring evaluable only. |
| `L1` | After this layer, we know whether each orthogonal identity can be independently represented and validated. | `CML07-S2-AUTHOR-IDENTITY-ARTIFACT-TYPES` | Makes candidate identity instances evaluable only. |
| `L2` | After this layer, we know whether the renamed Product lineage and its coordination graph close at final Lab paths. | `CML07-S3-MATERIALIZE-CRAFT-IDENTITY-CARRIERS` | Makes one exact CML-07 admission request set eligible for review only. |
| `L3` | After this layer, we know whether one immutable CML-07 bundle is safe to present for admission. | `CML07-S4-VALIDATE-AND-AUTHOR-ADMISSION-BUNDLE` | Presents one digest-bound Decision Request Set; performs no admission. |

## Layer Boundary Heuristic

Layer value = decision unlocked + operator-visible outcome + migration risk reduced.

Layer cost = authoring time + verification time + owner coordination. A layer ends before the next distinct decision begins.

## Recommended next layer

Start `L0` with `CML07-W0-SOURCE-OWNER-DEFINITIONS`. It closes sources, owners, and canonical meanings before schemas or carriers exist.

## Explicitly deferred

- Product Capability selection and capability instance construction (CML-08)
- capability-local business ontology (CML-09)
- Craft authored specification and compiled graph
- runtime, implementation binding, conformance, publication, and stable release

## Non-regression guardrails

- Machine records remain canonical and every human view is generated.
- Product, Project, Method, Goal, Product Capability, capability instance, Bounded Context, module, package, and directory remain separate identities.
- Craft remains the same Product lineage renamed from DomainSpec v2.
- Stable CAV2 and DS source IDs are preserved where an actual source Definition exists.
- Craft Product does not imply a Craft root Bounded Context.
- Source repositories remain read-only and no bulk copy or global replacement occurs.
- Each stage validates before its successor becomes evaluable; validation never auto-admits the successor.
- Human approval occurs once, at the final digest-bound CML-07 bundle boundary.
