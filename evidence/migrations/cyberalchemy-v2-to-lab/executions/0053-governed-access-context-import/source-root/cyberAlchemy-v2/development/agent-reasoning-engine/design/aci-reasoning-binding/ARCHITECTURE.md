---
title: ACI Reasoning Binding Candidate Architecture
status: accepted-aci-subordinate-with-external-gates
invoke_mode: design
scope: private-cav2-development
authority_effect: none
implementation_authorized: false
---

# ACI reasoning binding candidate architecture

## Design intent

Bind the private reasoning engine to the orchestrator without creating a second
runtime authority. The semantic evaluator may own deterministic derivation and
its content artifact; integrated commands, accepted events, canonical
acceptance receipts, replay cursor, aggregate concurrency, and effect intents
belong to ACI.

`G-ARE-ACI-BINDING` selected option A. This is the accepted local
ACI-subordinate target architecture: local-only evidence may continue under an
explicit non-integration ceiling while external gates remain blocked. The
selection does not authorize an adapter, runtime mutation, or a successor SWU.

## Source contracts

- [`CONTEXT-PACK.md`](CONTEXT-PACK.md)
- [`../../spec/SPEC.md`](../../spec/SPEC.md)
- [`../ARCHITECTURE.md`](../ARCHITECTURE.md)
- [`../COMPONENT-CONTRACTS.md`](../COMPONENT-CONTRACTS.md)
- [`../../decisions/g-are-l0-promotion/PROMOTION-RECEIPT.json`](../../decisions/g-are-l0-promotion/PROMOTION-RECEIPT.json)
- ACI ADR-001 at the pinned external source state
- ACI Work Pack, Bus Contracts discovery and review, ACP discovery, and APT
  Work Pack at their declared maturity

## View 1 — context

```text
confirmed DispatchSpec (future executable topology authority)
                         |
                         v
               ACI command acceptance
        [canonical command + EventJournal transaction]
                         |
            actor events / publication facts
                         |
                         v
      private semantic-judgment evaluator@1
       [admit observations -> reduce -> outcome]
                         |
             ReasoningReceipt artifact
                         |
                         v
        separate exact-effect gate decision
                         |
                         v
        ACI effect intent (only after acceptance)
```

The reasoning engine answers a semantic question under frozen inputs. ACI
answers whether commands/events/effect intents are durably accepted and
replayable. The Work Bus, if promoted, transports work publications; APT, if
promoted, projects provenance. Neither becomes evaluator authority.

## View 2 — high-level structure

| Plane | Target owner | Binding rule |
|---|---|---|
| executable topology | confirmed `DispatchSpec` / ACI protocol owner | reasoning records reference the confirmed dispatch digest; discovery snapshots never replace it |
| command and event lifecycle | ACI `EventJournal` | one physical writer and one canonical acceptance transaction in integrated mode |
| semantic reduction | private reasoning evaluator | deterministic applicability, derivation, outcome, and residue stay evaluator-owned |
| work publication | candidate Work Bus | transport only; acceptance and semantic admission are separate gates |
| artifact content | artifact service/admission owner | finalized immutable content; journal stores refs/digests/lifecycle facts |
| effect lifecycle | exact-effect gate owner plus ACI effect intent | recommendation is non-authorizing; effect intent exists only after the distinct gate and command acceptance |
| provenance/read views | session/dispatch authorities plus candidate APT | projections are rebuildable and never mutate source lifecycle |

Integrated mode uses an anti-corruption adapter: it translates local semantic
records into ACI commands/payload references but cannot open a second journal,
invent ACI identifiers, or translate semantic positivity into permission.

## View 3 — low-level components

| Component | Consumes | Produces | Owner / prohibition |
|---|---|---|---|
| `ReasoningRunCommandMapper` | confirmed dispatch ref, entry gate, frozen run envelope | candidate ACI command projection | adapter only; ACI validates/canonicalizes/accepts |
| `ActorEventMapper` | ACI command/event refs | evaluator-facing immutable actor cut | read adapter; no direct journal writes |
| `ObservationPublicationMapper` | accepted Work Bus candidate/submission refs | proposed observation handles | Work Bus acceptance is not evaluator admission |
| evaluator `ObservationAdmitter` | proposed handles plus frozen manifest | admitted/rejected `ObservationSet` | evaluator-owned deterministic decision |
| semantic evaluator | frozen inputs and actor cut | typed outcome, derivation, residue | no ACI, provider, tool, or effect writes |
| `ReasoningReceiptAssembler` | exact reducer outputs and source refs | finalized semantic receipt artifact | cannot fabricate journal acceptance |
| `ReasoningReceiptReferenceMapper` | finalized artifact ref/digest | candidate ACI event/command payload reference | ACI owns outer receipt bytes and identity |
| `ExactEffectCommandMapper` | positive semantic receipt plus fresh exact-effect pass | candidate ACI effect command | zero output for every other path |
| `ReplayBridge` | verified ACI journal cut plus receipt artifact | reproduced semantic outcome | no provider/tool/effect calls |
| `ProvenanceProjectionMapper` | accepted session/dispatch/research/event refs | candidate APT read facts | projection-only; no lifecycle mutation |

Minimum cross-boundary envelope:

```yaml
binding_version: candidate@1
dispatch_ref:
  dispatch_id: string
  dispatch_digest: sha256
aci_command_ref:
  command_id: string
  command_digest: sha256
  journal_span: {first_offset: integer, last_offset: integer}
semantic_run_ref:
  run_id: string
  evaluator_id: semantic-judgment-evaluator@1
  input_digest: sha256
reasoning_receipt_ref:
  artifact_ref: string
  content_digest: sha256
effect_binding:
  exact_gate_decision_digest: sha256 | null
  fixed_effect_envelope_digest: sha256 | null
provenance_refs: []
```

This is a logical design shape, not a promoted schema.

## View 4 — workflow process

1. Resolve an exact confirmed `DispatchSpec` and entry decision.
2. Map the bounded run request to a candidate command without canonicalizing it
   locally.
3. ACI validates authority, canonicalizes, and atomically accepts the command,
   receipt identity, events/head changes, and any permitted new intents.
4. Actor execution facts are read through the journal boundary. Work Bus
   publications, when available, remain proposed observations.
5. The evaluator independently admits/rejects observations and reduces frozen
   inputs to one typed outcome.
6. Finalize the semantic `ReasoningReceipt` artifact, then submit only its
   stable ref/digest to the ACI acceptance boundary.
7. For every non-positive outcome, stop with zero effect-intent requests.
8. For `RecommendedUnderSnapshot`, obtain a new exact-effect gate over the
   identical fixed envelope.
9. Only a gate `pass` may be mapped to an ACI command that can create an effect
   intent; ACI still performs canonical acceptance and idempotency checks.
10. Historical replay folds verified ACI facts and deterministic semantic
    artifacts with zero external calls. Current revalidation creates a new
    run/command and never overwrites history.

## View 5 — decision flow

```text
Is the binding owner disposition recorded?
  no  -> keep BLK-ARE-ACI-BINDING-001; no affected mutation
  yes -> selected disposition
           |
           +-- ACI-subordinate target
           |     external gates pass? no -> local-only experiments, no compatibility
           |                          yes -> conformance design/plan may proceed
           |
           +-- local-only
           |     isolated namespaces + explicit non-integration ceiling
           |
           +-- incompatible/rerouted
                 retain evaluator library; stop journal/effect integration work
```

The four owner choices are:

| Option | Meaning | Downstream ceiling |
|---|---|---|
| A | Target ACI-subordinate integration; allow explicitly local-only evidence while external gates remain blocked. | No compatibility claim until cross-repository conformance passes. |
| B | Keep the reasoning runtime local-only with no current ACI integration commitment. | No ACI compatibility or integrated packaging claim. |
| C | Defer the binding decision. | Keep affected SWUs blocked. |
| D | Declare the seam incompatible and reroute to a standalone semantic library. | Stop actor-journal/effect integration work. |

## View 6 — dependency and interface boundaries

| Interface | Logical contract | Conformance evidence required before implementation |
|---|---|---|
| confirmed dispatch | exact ID, bytes/digest, protocol revision and authority snapshot | promoted ACP/ACI contract plus fixture vectors |
| command acceptance | scope/idempotency key, expected versions, canonical digest | ACI TASK-010 canonical/idempotency/CAS receipts |
| journal cut | event IDs, offsets, aggregate versions, payload refs/digests | ACI replay and crash-matrix receipts |
| Work Bus publication | candidate/submission/review IDs, receipt, generation and release fact | post-remediation Bus `PASS` and accepted mapping |
| semantic receipt ref | immutable artifact ref and content digest | local artifact-admission and cross-language canonical reference fixtures |
| exact effect | exact gate digest, identical envelope digest, idempotency key | local zero/one tests plus accepted ACI effect-intent conformance |
| provenance projection | session, dispatch, research and event refs | APT mutation gate and rebuild/as-of fixtures |

No external schema is copied into local authority. Unknown versions, missing
digests, maturity regression, or identifier substitution block the adapter.

## Design decisions

| ID | Candidate decision | Status |
|---|---|---|
| `ARE-BIND-D1` | Integrated journal facts and canonical acceptance identity are ACI-owned. | structurally required by accepted ADR-001 |
| `ARE-BIND-D2` | Semantic applicability, derivation, outcome, and receipt content are evaluator-owned. | preserves local L0 contract |
| `ARE-BIND-D3` | Semantic receipt bytes live as artifact content; ACI owns the outer acceptance receipt and journal reference. | candidate mapping |
| `ARE-BIND-D4` | Work Bus acceptance and evaluator observation admission are separate facts. | candidate mapping |
| `ARE-BIND-D5` | A semantic recommendation plus exact-effect pass is input to—not a substitute for—ACI command acceptance/effect intent. | candidate mapping |
| `ARE-BIND-D6` | APT consumes lineage projections and cannot own session, dispatch, research, journal, or receipt lifecycle. | candidate mapping |
| `ARE-BIND-D7` | Historical replay uses ACI facts plus deterministic semantic artifacts; revalidation is a new run. | candidate mapping |
| `ARE-BIND-D8` | Select option A: ACI-subordinate integration target with explicitly local-only interim evidence. | accepted by `G-ARE-ACI-BINDING`; external maturity remains open |

## Risks and residue

| ID | Risk | Fail-closed treatment |
|---|---|---|
| `R-BIND-01` | Local `RuntimeJournal` becomes a second integrated authority. | prohibit integrated writes outside ACI; local-only namespace must be explicit |
| `R-BIND-02` | Two meanings of receipt collapse. | distinguish semantic artifact from ACI acceptance receipt in names and fixtures |
| `R-BIND-03` | Work Bus acceptance is treated as evidence truth. | require evaluator admission with independent posture |
| `R-BIND-04` | Positive outcome creates effect intent directly. | require separate exact-effect gate and ACI acceptance |
| `R-BIND-05` | Draft/FIX contracts harden accidentally. | keep mappings conditional on owner receipts/digests |
| `R-BIND-06` | Cross-language canonicalization forks. | local adapter never claims canonical bytes; conformance vectors gate integration |

## Design result

- Six required views: complete.
- Architecture profile: DomainSpec six-view profile with `architecture`
  companion.
- Glossary consistency: `flag`; one upstream stale status is recorded in
  [`GLOSSARY-CONSISTENCY.md`](GLOSSARY-CONSISTENCY.md).
- Distill: `pass with target-lifecycle residue`; the owner disposition is
  selected, while external maturity still blocks integrated execution.
- Implementation layering: seed only; no mutation-ready units.
- Phase status: `pass` for the local architecture decision.
- Decision receipt:
  [`BINDING-RECEIPT.json`](../../decisions/aci-reasoning-binding/BINDING-RECEIPT.json).
- Next route: `invoke:plan ACI-subordinate conformance revision`; do not select
  an implementation SWU.

