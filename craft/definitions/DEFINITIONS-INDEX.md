<!-- MINT-BASELINE BACKFILL (2026-07-01) for domainspec-v2 — cast from templates/definitions-index.md
     (Tier-1 addition #8, SWU-5), which post-dates v2's 2026-06-29 first mint. INTERNAL/private.
     INHERITS the definition-index FORMAT; LOCALIZES the rows (one per DEFINITIONS.md card). -->

# DomainSpec v2 Definitions Index

Status: active
Owner: definitions-governance (domain-local)
Reconciled by: [DEFINITION-DRIFT-AUDIT.md](./DEFINITION-DRIFT-AUDIT.md)

The canonical registry of every DomainSpec v2 definition card. A **load-bearing term** (the constitution's
Load-Bearing Term Tracking rule, `C(meta-4)`) is "tracked" iff it has a row here that resolves to a card in
[DEFINITIONS.md](./DEFINITIONS.md). A load-bearing term cited with no row here is a **drift defect** the
[drift audit](./DEFINITION-DRIFT-AUDIT.md) must flag.

| Definition ID | Term | Status | Source kind | Card |
| --- | --- | --- | --- | --- |
| `domainspec-v2-D1` | Drift | active | operator-reading; local-inference | [DEFINITIONS.md#domainspec-v2-d1](./DEFINITIONS.md) |
| `domainspec-v2-D2` | Validation governance | active | local-inference (domain-originated; RATIFIED kind) | [DEFINITIONS.md#domainspec-v2-d2](./DEFINITIONS.md) |
| `domainspec-v2-D3` | Edge-Law Admissibility | active | local-inference (build-from-owned: CAV2-D22/D29/D16) | [DEFINITIONS.md#domainspec-v2-d3](./DEFINITIONS.md) |
| `domainspec-v2-D4` | Executable Typed Graph | active | local-inference; synthesis | [DEFINITIONS.md#domainspec-v2-d4](./DEFINITIONS.md) |
| `domainspec-v2-D5` | Two-Plane Boundary | active | local-inference | [DEFINITIONS.md#domainspec-v2-d5](./DEFINITIONS.md) |
| `domainspec-v2-D6` | meta-type | candidate | method-vocabulary | [DEFINITIONS.md#domainspec-v2-d6](./DEFINITIONS.md) |
| `domainspec-v2-D7` | category | candidate | method-vocabulary | [DEFINITIONS.md#domainspec-v2-d7](./DEFINITIONS.md) |
| `domainspec-v2-D8` | formal criterion | candidate | method-vocabulary | [DEFINITIONS.md#domainspec-v2-d8](./DEFINITIONS.md) |
| `domainspec-v2-D9` | edge-participation signature | active | method-vocabulary (cites DS-D8) | [DEFINITIONS.md#domainspec-v2-d9](./DEFINITIONS.md) |
| `domainspec-v2-D10` | content validator | candidate | method-vocabulary | [DEFINITIONS.md#domainspec-v2-d10](./DEFINITIONS.md) |
| `domainspec-v2-D11` | instance | candidate | method-vocabulary | [DEFINITIONS.md#domainspec-v2-d11](./DEFINITIONS.md) |
| `domainspec-v2-D12` | instance validator | candidate | method-vocabulary | [DEFINITIONS.md#domainspec-v2-d12](./DEFINITIONS.md) |
| `domainspec-v2-D13` | aspect file | candidate | method-vocabulary | [DEFINITIONS.md#domainspec-v2-d13](./DEFINITIONS.md) |
| `domainspec-v2-D14` | Concept Registry | candidate | method-vocabulary | [DEFINITIONS.md#domainspec-v2-d14](./DEFINITIONS.md) |
| `domainspec-v2-D15` | declared-attributes convention | candidate | method-vocabulary | [DEFINITIONS.md#domainspec-v2-d15](./DEFINITIONS.md) |
| `domainspec-v2-D16` | Layering governance | active | local-inference (domain-originated; RATIFIED kind) | [DEFINITIONS.md#domainspec-v2-d16](./DEFINITIONS.md) |
| `domainspec-v2-D17` | Drift governance | active | local-inference (domain-originated; RATIFIED kind) | [DEFINITIONS.md#domainspec-v2-d17](./DEFINITIONS.md) |
| `domainspec-v2-D18` | relationship non-collapse test | active | method-vocabulary (build-from-owned via D3) | [DEFINITIONS.md#domainspec-v2-d18](./DEFINITIONS.md) |
| `domainspec-v2-D19` | typed composable graph fragment | active | method-vocabulary | [DEFINITIONS.md#domainspec-v2-d19](./DEFINITIONS.md) |
| `domainspec-v2-D20` | reject/allow decision | active | method-vocabulary; D18 property | [DEFINITIONS.md#domainspec-v2-d20](./DEFINITIONS.md) |
| `domainspec-v2-D21` | derivation consequence | active | method-vocabulary; D18 property | [DEFINITIONS.md#domainspec-v2-d21](./DEFINITIONS.md) |
| `domainspec-v2-D22` | projection consequence | active | method-vocabulary; D18 property | [DEFINITIONS.md#domainspec-v2-d22](./DEFINITIONS.md) |
| `domainspec-v2-D23` | composition path consequence | active | method-vocabulary; D18 property | [DEFINITIONS.md#domainspec-v2-d23](./DEFINITIONS.md) |
| `domainspec-v2-D24` | owner route consequence | active | method-vocabulary; D18 property | [DEFINITIONS.md#domainspec-v2-d24](./DEFINITIONS.md) |
| `domainspec-v2-D25` | generated artifact consequence | active | method-vocabulary; D18 property | [DEFINITIONS.md#domainspec-v2-d25](./DEFINITIONS.md) |
| `domainspec-v2-D26` | relationship source-effect binding | superseded | historical method-vocabulary; superseded by D27 | [DEFINITIONS.md#domainspec-v2-d26](./DEFINITIONS.md) |
| `domainspec-v2-D27` | Canonical Single Responsibility Principle | active | method-vocabulary (build-from-owned: SRP + CAV2-D16/D22/D29) | [DEFINITIONS.md#domainspec-v2-d27](./DEFINITIONS.md) |
| `domainspec-v2-D28` | DomainSpec obligation lifecycle | active | local-inference; owner-ratified lifecycle vocabulary | [DEFINITIONS.md#domainspec-v2-d28](./DEFINITIONS.md) |
| `domainspec-v2-D29` | Ownership Dimension Registry | active | domain-vocabulary; D06 P01 owner-selected registry | [DEFINITIONS.md#domainspec-v2-d29](./DEFINITIONS.md) · [registry](./ownership-dimensions/ownership-dimensions.json) |
| `domainspec-v2-D30` | Membership Kind Registry | active | domain-vocabulary; D07 P01 contents owner-selected registry | [DEFINITIONS.md#domainspec-v2-d30](./DEFINITIONS.md) · [registry](./membership-kinds/membership-kinds.json) |
| `domainspec-v2-D31` | meta-type realization | active | method-vocabulary; owner-admitted implementation binding | [DEFINITIONS.md#domainspec-v2-d31](./DEFINITIONS.md) |
| `domainspec-v2-D32` | canonical implemented meta-type baseline | active | project-local implementation authority | [DEFINITIONS.md#domainspec-v2-d32](./DEFINITIONS.md) · [current state](./meta-types/current-implementation.md) |
| `domainspec-v2-D33` | meta-type instantiation | active | method-vocabulary; deterministic generation contract | [DEFINITIONS.md#domainspec-v2-d33](./DEFINITIONS.md) |
| `domainspec-v2-D34` | target implementation conformance | active | method-vocabulary; observed-vs-selected predicate | [DEFINITIONS.md#domainspec-v2-d34](./DEFINITIONS.md) |
| `domainspec-v2-D35` | baseline-bound instantiation receipt | active | evidence-vocabulary; deterministic generation receipt | [DEFINITIONS.md#domainspec-v2-d35](./DEFINITIONS.md) |
| `domainspec-v2-D36` | Workflow Compensation | active | method-vocabulary; owner-admitted forward-recovery model | [DEFINITIONS.md#domainspec-v2-d36](./DEFINITIONS.md) |
| `domainspec-v2-D37` | Recovery Intent | active | method-vocabulary; durable-recovery identity | [DEFINITIONS.md#domainspec-v2-d37](./DEFINITIONS.md) |
| `domainspec-v2-D38` | Durable Compensation Dispatch | active | method-vocabulary; durable coordination aggregate | [DEFINITIONS.md#domainspec-v2-d38](./DEFINITIONS.md) |
| `domainspec-v2-D39` | Compensation Execution Attempt | active | method-vocabulary; execution-episode identity | [DEFINITIONS.md#domainspec-v2-d39](./DEFINITIONS.md) |
| `domainspec-v2-D40` | Compensation Invocation Identity | active | method-vocabulary; replay-protection identity | [DEFINITIONS.md#domainspec-v2-d40](./DEFINITIONS.md) |
| `domainspec-v2-D41` | Compensation Claim | active | method-vocabulary; exclusive advancement authority | [DEFINITIONS.md#domainspec-v2-d41](./DEFINITIONS.md) |
| `domainspec-v2-D42` | Compensation Claim Lease | active | method-vocabulary; bounded claim validity | [DEFINITIONS.md#domainspec-v2-d42](./DEFINITIONS.md) |
| `domainspec-v2-D43` | Compensation Retry | active | method-vocabulary; successor-attempt scheduling | [DEFINITIONS.md#domainspec-v2-d43](./DEFINITIONS.md) |
| `domainspec-v2-D44` | Compensation Terminal Disposition | active | method-vocabulary; terminal recovery result | [DEFINITIONS.md#domainspec-v2-d44](./DEFINITIONS.md) |
| `domainspec-v2-D45` | Concern-Specific Dependency Contract | active | method-vocabulary; responsibility-specific code seam | [DEFINITIONS.md#domainspec-v2-d45](./DEFINITIONS.md) |
| `domainspec-v2-D46` | Persistence Binding | active | method-vocabulary; logical-to-physical persistence realization | [DEFINITIONS.md#domainspec-v2-d46](./DEFINITIONS.md) |
| `domainspec-v2-D47` | Transaction Guarantee Binding | active | method-vocabulary; exact local transaction boundary | [DEFINITIONS.md#domainspec-v2-d47](./DEFINITIONS.md) |
| `domainspec-v2-D48` | Failure Outcome Binding | active | method-vocabulary; typed integration failure classification | [DEFINITIONS.md#domainspec-v2-d48](./DEFINITIONS.md) |
| `domainspec-v2-D49` | Durable Workflow Runtime Binding | active | method-vocabulary; durable-profile composition binding | [DEFINITIONS.md#domainspec-v2-d49](./DEFINITIONS.md) |
| `DS-D1` | Meta-Type System (24 staged labels) | active | domain-vocabulary | [meta-types/meta-types.md](./meta-types/meta-types.md) · [.yml](./meta-types/meta-types.yml) |
| `DS-D1.1` | Entity | active | domain-vocabulary; formalized | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.2` | Value Object | active | domain-vocabulary; formalized | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.3` | Enum | active | domain-vocabulary; formalized | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.4` | Operation | active | domain-vocabulary; formalized | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.5` | Query | active | domain-vocabulary; formalized | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.6` | Calculation | active | domain-vocabulary; formalized | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.7` | Rule | active | domain-vocabulary; formalized | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.8` | Policy | active | domain-vocabulary; formalized | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.9` | Workflow | active | domain-vocabulary; formalized | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.10` | Saga | superseded | domain-vocabulary; stable retired ID | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.11` | Interface | active | domain-vocabulary; formalized | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.12` | Event | active | domain-vocabulary; formalized | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.13` | Mapping | active | domain-vocabulary; formalized | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.14` | State Machine | active | domain-vocabulary; formalized | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.15` | Page | candidate | domain-vocabulary; candidate shape evidence | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.16` | Layout | candidate | domain-vocabulary; candidate shape evidence | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.17` | Component | candidate | domain-vocabulary; candidate shape evidence | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.18` | View Model | candidate | domain-vocabulary; candidate shape evidence | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.19` | Hook | candidate | domain-vocabulary; candidate shape evidence | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.20` | Form | candidate | domain-vocabulary; candidate shape evidence | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.21` | Action | candidate | domain-vocabulary; candidate shape evidence | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.22` | Guard | candidate | domain-vocabulary; candidate shape evidence | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.23` | Binding | candidate | domain-vocabulary; candidate shape evidence | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.24` | Adapter | deferred/merge-candidate | domain-vocabulary; collapse observed | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D1.25` | State Indicator | deferred/split-candidate | domain-vocabulary; unresolved split | [meta-types.md](./meta-types/meta-types.md) |
| `DS-D2` | Relationship Verb Set | active | domain-vocabulary; R3A root authority | [DEFINITIONS.md#ds-d2](./DEFINITIONS.md) · [relationships.yml](./relationships/relationships.yml) |
| `DS-D8` | Relationship Signature Authority | active | domain-vocabulary; R3A root authority | [DEFINITIONS.md#ds-d8](./DEFINITIONS.md) · [relationships.yml](./relationships/relationships.yml) |

## Status vocabulary
- `candidate` — first-cited, carries an `Open / to-ground:` field; not yet validation.
- `active` — a full three-voice card exists and its load-bearing terms resolve.
- `deferred/*` — retained for a named correction route but not admitted as active authority.
- `superseded` — retired stable ID retained for history and forbidden from reuse.
- `deprecated` — superseded; keep the row with its supersedes/superseded-by link (never delete).

<!-- The domain owner maintains this index through the definitions lifecycle. Every row must resolve to a
     card; the drift audit flags any load-bearing term missing a row. The governance-kind cards
     layering-governance and drift-governance resolve as domainspec-v2-D16/D17. -->
