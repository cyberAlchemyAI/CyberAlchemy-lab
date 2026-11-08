---
title: Define Integration API And Ontology Authoring Adapter Design
status: candidate
updatedAt: 2026-09-08
owner: CyberAlchemy v2 Define runtime owner
authority_effect: none
---

# Define Integration API And Ontology Authoring Adapter Design

## Design Outcome

Define will expose one stable client API to its consumers and consume ontology
authoring extensions through a separate typed adapter protocol. These are two
different boundaries:

1. **Define Client API** — ARE, CLI, chat, Plan, and other products use it to
   start or resume Define work, obtain the next question, record a user answer,
   inspect readiness, confirm an artifact, and export a candidate plus receipt.
2. **Ontology Authoring Adapter Protocol** — statically configured ontology
   packages implement it to describe one ontology stage, declare prerequisites,
   provide question contracts, evaluate readiness, materialize a candidate,
   validate that candidate, and emit a handoff receipt.

Adding an ontology must add a reviewed adapter and one explicit stage-registry
record at the composition root. It must not add an ontology name, question set,
or readiness branch to Define core.

## Current Evidence And Problem

- [The current Define runtime](../../src/conversation-runtime.mjs) owns the full
  Definition Pack conversation directly.
- [The current durable runtime](../../src/durable-session-runtime.mjs) owns
  revisioned commands, persistence boundaries, and resumable state.
- [The current Alch assembly](../../alch/define-runtime.alch) correctly keeps
  semantic and workflow decisions in distinct compiled entry points.
- [The current ontology selection](../../alch/define-runtime.ontology-selection.json)
  binds specific business and system records directly.
- [The Define profile](../../../../define/profile.json) names the current
  business and system child packages.
- [ARE's Module Port](../../../agent-reasoning-engine/packages/module-port/README.md)
  already supplies the required no-discovery, exact-provider, digest-bound
  extension mechanics.

Those surfaces prove the current fixed workflow, but they do not provide a
contract by which a future Product, Business, Security, Compliance, or other
ontology can participate without Define-core edits.

## Responsibility Boundary

| Owner | Owns | Must Not Own |
| --- | --- | --- |
| Define core | interaction lifecycle, stage state, provenance, correction/deferral, user confirmation, export coordination | ontology-specific questions, ontology meaning, route selection, admission |
| Define Client API | stable consumer operations and typed results | transport UI, ontology internals, fallback policy |
| Ontology adapter | ontology-specific prerequisites, question contracts, readiness facts, candidate materialization and validation | session persistence, user confirmation, canonical admission, route creation |
| Static stage registry | exact stage IDs, dependency edges, capability IDs, versions and manifest digests | filesystem discovery, provider priority, semantic decisions |
| ARE | select `CA2-ROUTE-DEFINE` when that registered route is available | invoke Define stages, require an ontology globally, own the workflow |
| Plan | consume an exact candidate handoff receipt for its declared input | reinterpret or promote ontology meaning |
| User/domain owner | confirm or correct meaning and make owner-controlled decisions | implicit confirmation by silence or generated evidence |

## Topology

```text
ARE route selection
       |
       v
CLI / chat / Plan / another product
       |
       v
Define Client API
       |
       +----> Define core: session + provenance + confirmation
       |
       v
Ontology Stage Facade
       |
       v
ARE Module Port (exact injected adapters, immutable module-set)
       |
       +----> Product Ontology adapter
       +----> Business Ontology adapter
       +----> System Ontology adapter
       +----> future ontology adapter

Static stage registry: dependencies + exact capability bindings
```

The workflow is a dependency graph, not a hard-coded list. The initial graph is:

```text
Definition Pack -> Product Ontology -> Business Ontology -> System Ontology
                                      +-> future Security/Compliance branches
```

The registry may expose multiple valid entry points. A consumer selects an
entry stage explicitly; Define computes only that stage's prerequisite closure.
The L4 candidate composition exposes Definition Pack, Product, Business, and
System stages, with System remaining optional at composition time.

## Define Client API

The v1 facade is transport-neutral and synchronous over the current local
runtime. Each operation accepts a closed request and returns a closed result
with `authority_effect: none`.

| Operation | Purpose | Important output |
| --- | --- | --- |
| `startWork` | Create one Define work record for an exact entry stage | work ID, revision, stage graph digest |
| `resumeWork` | Read one confirmed revision | snapshot and current stage |
| `listStages` | Show configured stages and dependency posture | ordered stage summaries |
| `nextQuestion` | Ask the active adapter for one question contract | question, purpose, expected answer shape, owner |
| `submitResponse` | Record answer, correction, refusal, or deferral | confirmed revision and provenance |
| `inspectReadiness` | Separate interaction, semantic, dependency, and artifact readiness | typed readiness dimensions and repair focus |
| `confirmArtifact` | Record the user's confirmation against exact bytes | confirmation receipt or explicit block |
| `exportArtifact` | Return candidate artifact and handoff receipt | artifact digest, adapter receipt, dependency receipt set |

The facade does not expose a universal `invoke(name, any)` function. Consumers
cannot call raw adapters or bypass confirmation.

## Ontology Stage Descriptor

Each registry record is closed and exact:

```json
{
  "schema_version": "cav2.define-ontology-stage/v1",
  "stage_id": "product-ontology",
  "ontology_type": "product",
  "module_id": "cav2.define.product-ontology-authoring",
  "module_version": "1-candidate",
  "manifest_digest": "<sha256>",
  "prerequisite_stage_ids": ["definition-pack"],
  "capabilities": {
    "describe": "define.ontology.product.describe/v1",
    "next_question": "define.ontology.product.next-question/v1",
    "evaluate": "define.ontology.product.evaluate/v1",
    "materialize": "define.ontology.product.materialize/v1",
    "validate": "define.ontology.product.validate/v1"
  },
  "alch_entrypoints": [
    "ProductOntologyQuestion",
    "ProductOntologyReadiness",
    "ProductOntologyMaterializationReadiness"
  ],
  "authority_effect": "none"
}
```

Capability IDs include the ontology type because the Module Port permits one
exact provider per capability and intentionally has no provider priority.
Duplicate stage IDs, duplicate ontology types, missing exact dependencies,
cycles, manifest drift, or capability/protocol mismatch block stage-registry
construction.

## Adapter Protocol

The typed facade maps each descriptor to five operations:

- `describe` returns label, purpose, output artifact kind, owners, and declared
  prerequisite artifact kinds.
- `nextQuestion` consumes frozen stage state and returns zero or one typed
  question; it cannot write the session.
- `evaluate` returns independent readiness dimensions, reason codes, and repair
  focus; `unavailable` is never interpreted as `not ready` or `false`.
- `materialize` consumes confirmed answers and exact prerequisite receipts and
  returns candidate bytes plus their digest.
- `validate` checks the candidate against the adapter's declared contract and
  returns no-effect evidence. Validation does not confirm or admit the artifact.

Define core wraps adapter receipts with the work ID, stage-registry digest,
prerequisite receipt-set digest, confirmation digest, and candidate digest.

## Alch Language Layer

Generic semantic decisions belong in a new multi-entry Alch assembly. This is
an illustrative contract shape, not executable source in this planning turn:

```alch
domain define-integration "Define ontology authoring integration"
profile service-v1
owner cyberalchemy-define-runtime-owner

import StageDependencyFunction from "./stage-dependency.alch"
import StageResponseFunction from "./stage-response.alch"
import StageReadinessFunction from "./stage-readiness.alch"
import StageHandoffFunction from "./stage-handoff.alch"

service DefineIntegrationRuntime:
  ontology "ALCH-DEFINE-INTEGRATION-RUNTIME"
  meaning "Evaluate generic ontology-stage transitions without owning ontology meaning."

entry StageDependency:
  function StageDependencyFunction
  ontology "ALCH-DEFINE-STAGE-DEPENDENCY-ENTRY"
  meaning "Decide whether exact prerequisite receipts are complete."

entry StageResponse:
  function StageResponseFunction
  ontology "ALCH-DEFINE-STAGE-RESPONSE-ENTRY"
  meaning "Classify answer, correction, refusal, and deferral postures."

entry StageReadiness:
  function StageReadinessFunction
  ontology "ALCH-DEFINE-STAGE-READINESS-ENTRY"
  meaning "Keep interaction, semantic, dependency, and artifact readiness distinct."

entry StageHandoff:
  function StageHandoffFunction
  ontology "ALCH-DEFINE-STAGE-HANDOFF-ENTRY"
  meaning "Require exact candidate, confirmation, validation, and dependency receipts."
```

Ontology-specific adapters own separate `.alch` assemblies and may expose more
entry points. The generic layer compiles through source ontology, Craft,
DomainSpec, and executable projection before host code consumes it. Host code
continues to own transport, state mutation, hashing, filesystem I/O, and audit.

### Law, invariant, and Constitution placement

- A generic Alch entry is a candidate executable **law of decision**: given
  declared facts, it returns one deterministic stage judgment.
- An invariant states a property every adapter and later layer must preserve,
  such as `authority_effect: none`, exact prerequisites, or confirmation before
  export.
- A Constitution groups scoped invariants and their evidence/adoption rules. It
  is the later governance vehicle if owners choose enforceability.

Compilation proves that the candidate law is representable and executable for
tested inputs. It does not adopt the invariant set, activate a Constitution, or
make an ontology canonical.

## Readiness And Authority Non-Collapse

The API must keep these states separate:

1. interaction completeness — required questions have dispositions;
2. semantic quality — grounding, non-collapse, and orthogonality pass for the
   relevant language;
3. dependency readiness — exact prerequisite candidate receipts are present;
4. artifact validity — the adapter validator accepts the candidate shape;
5. user confirmation — a user/domain owner confirmed exact candidate bytes;
6. admission/activation — outside Define and never inferred from 1–5.

A stage can be complete with an explicit deferral and remain handoff-blocked.
A validator PASS remains candidate evidence. An adapter cannot turn readiness
into authority.

## Failure And Degraded Behavior

- Zero ontology adapters is a valid Define startup; the built-in Definition
  Pack path remains available.
- An unknown entry stage is `unavailable`, not silently replaced.
- A configured missing adapter blocks only that stage and its dependents.
- A blocked adapter remains blocked; no handwritten semantic fallback runs.
- An unavailable optional branch does not block an independent selected branch.
- Adapter exceptions reduce to stable public reason codes; local diagnostics do
  not enter portable receipts.
- Registry or module-set changes create a successor digest and cannot mutate an
  existing work record in place.

## Required Validation

- empty registry and one-adapter registry are deterministic;
- descriptor permutation yields the same graph digest;
- duplicate stage/type/capability, missing dependency, and cycle block;
- invalid input/output and authority-bearing result block;
- missing adapter stays distinct from negative readiness;
- Definition Pack behavior is unchanged with zero ontology adapters;
- Product stage works through one exact adapter;
- Business stage requires the exact Product handoff receipt;
- a third fixture ontology is added without editing Define core;
- user correction and deferral remain replayable across client interfaces;
- semantic grounding, non-collapse, and orthogonality are evaluated independently;
- identical state, registry, and adapter set reproduce identical artifacts and receipts; and
- ARE selects only an available registered route and never invokes a stage.

## Frame Expiry

Reopen this design if adapters require untrusted code, runtime installation,
hot reload, remote transport, effects, credentials, incompatible simultaneous
protocol majors, or independent deployment. Those needs require an isolated
process/service architecture rather than widening the in-process port.

## Open Questions

- Does the existing Definition Pack become an explicit built-in stage record in
  L1, or remain the core prerequisite producer until the Product adapter passes?
- Should a later stage be allowed to request a repair in a prerequisite stage,
  or only report a typed dependency gap in v1?

Resolved for this candidate: the exact Product source is the Alch Product
Ontology package, the third ontology is `define/system-ontology`, and the Plan
boundary consumes `cav2.plan-ontology-handoff-input/v1`. These selections are
candidate integration bindings, not canonical admission decisions.
