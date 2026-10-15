# Work pack: integrated Lab roadmap

Status: **proposed plan**, 2026-10-07. Authority effect: **none**.

## Control fields

| Field | Value |
| --- | --- |
| workPackGateStatus | pass for complete planning contracts; task-specific upstream/design/effect gates remain mandatory |
| complexity / outputMode | high / split |
| executionPackRef | [EXECUTION-PACK.md](EXECUTION-PACK.md) |
| layeringArtifactRef | [IMPLEMENTATION-LAYERING.md](IMPLEMENTATION-LAYERING.md) |
| activeLayerWindow | L1; next selected design unit: SWU-C01-01 |
| readinessProfile | local pilot through stable-release preparation; release is R08 |
| implementationExecutionAuthorizedByThisRequest | false; current request authorizes analysis and planning |

## Objective and delivery slices

Deliver the full [roadmap](../../ROADMAP.md): repeatable real operation, integrated work/learning, selected ontology/migration closure and usable stable Product. L0 is a scoped existing proof, not an unfinished rebuild task. Each layer has its exact decision question and join in the layering companion. [dag.json](dag.json) is the machine dependency/status source; [swu-manifest.json](swu-manifest.json) holds every smallest working unit.

## Task status board

| Task | Goal | Layer | Kind | Depends on | Status |
| --- | --- | --- | --- | --- | --- |
| [B00](work-pack/tasks/B00.md) | Scoped foundation proof | L0 | evidence | — | satisfied-scoped |
| [B01](work-pack/tasks/B01.md) | Whole-Lab source and contract analysis | L0 | planning | B00 | complete-planning |
| [C01](work-pack/tasks/C01.md) | Independent source-profile contract | L1 | design | B01 | not-started |
| [C02](work-pack/tasks/C02.md) | Contract and reference impact matrix | L1 | design | B01 | not-started |
| [C03](work-pack/tasks/C03.md) | Replay and context measurements | L1 | measurement | B01 | not-started |
| [C04](work-pack/tasks/C04.md) | Explicit profile selection and capture | L1 | implementation | C01, C02 | not-started |
| [C05](work-pack/tasks/C05.md) | Successor-branch transition | L1 | implementation | C04 | not-started |
| [C06](work-pack/tasks/C06.md) | Measured replay reuse with full verifier | L1 | implementation | C03, C04 | not-started |
| [C07](work-pack/tasks/C07.md) | Local-result promotion and repository publisher | L1 | implementation | C02, C04, C14 | not-started |
| [C08](work-pack/tasks/C08.md) | Exact context and generator provenance | L1 | implementation | C02, C04 | not-started |
| [C09](work-pack/tasks/C09.md) | Successor integration validation and example | L1 | verification | C05, C06, C07, C08, C14 | not-started |
| [C10](work-pack/tasks/C10.md) | Exact successor admission decision | L1 | owner-decision | C09 | not-started |
| [C11](work-pack/tasks/C11.md) | Explicit operational branch provisioning | L1 | provision | C10 | not-started |
| [C12](work-pack/tasks/C12.md) | First real Work with selected durable evidence | L1 | real-work | C11 | not-started |
| [C13](work-pack/tasks/C13.md) | Repeatable-operation milestone closure | L1 | closure | C12 | not-started |
| [C14](work-pack/tasks/C14.md) | Complete typed extension admissibility | L1 | implementation | C02, C04 | not-started |
| [W01](work-pack/tasks/W01.md) | Integrated workflow transition contracts | L2 | design | C02 | not-started |
| [W02](work-pack/tasks/W02.md) | Bounded actor authority and tool dispatch | L2 | implementation | W01, C13 | not-started |
| [W03](work-pack/tasks/W03.md) | Engineering workflow implementation | L2 | implementation | W01, W02 | not-started |
| [W04](work-pack/tasks/W04.md) | Research and experiment workflow implementation | L2 | implementation | W01, W02 | not-started |
| [W05](work-pack/tasks/W05.md) | Evidence, classification, failure and challenge | L2 | implementation | W01, W02 | not-started |
| [W06](work-pack/tasks/W06.md) | Operational lesson selection and application | L2 | implementation | W05, C08 | not-started |
| [W07](work-pack/tasks/W07.md) | Integrated workflow validation | L2 | verification | W03, W04, W06 | not-started |
| [W08](work-pack/tasks/W08.md) | Exact integrated workflow review | L2 | owner-decision | W07 | not-started |
| [W09](work-pack/tasks/W09.md) | Real integrated work and learning closure | L2 | closure | W08, C13 | not-started |
| [O01](work-pack/tasks/O01.md) | Lab ontology mapping and coverage contract | L3 | design | B01, C02 | not-started |
| [O02](work-pack/tasks/O02.md) | Lab ontology lifecycle adapter | L3 | implementation | O01, C13, W05 | not-started |
| [O03](work-pack/tasks/O03.md) | Three-lens queries, freshness and coverage | L3 | implementation | O01, C08 | not-started |
| [O04](work-pack/tasks/O04.md) | Selected source migration inventory and disposition | L3 | design | O01, C07 | not-started |
| [O05](work-pack/tasks/O05.md) | Selected import and adaptation construction | L3 | implementation | O04, O02 | not-started |
| [O06](work-pack/tasks/O06.md) | Exact ontology and selected migration review | L3 | owner-decision | O05, O03, W09 | not-started |
| [O07](work-pack/tasks/O07.md) | Selected ontology and migration coherence closure | L3 | closure | O06, W09 | not-started |
| [R01](work-pack/tasks/R01.md) | Lab Product acceptance and release scope | L4 | design | B01 | not-started |
| [R02](work-pack/tasks/R02.md) | Install, upgrade, export and recovery packaging | L4 | implementation | R01, C13 | not-started |
| [R03](work-pack/tasks/R03.md) | Coherent operator inspection and review surface | L4 | implementation | R01, C13, W01 | not-started |
| [R04](work-pack/tasks/R04.md) | Capability realization, adoption and conformance | L4 | assessment | R01, W09, O07 | not-started |
| [R05](work-pack/tasks/R05.md) | Bounded real Product pilot | L4 | real-work | R02, R03, R04, O07 | not-started |
| [R06](work-pack/tasks/R06.md) | Exact private/public boundary review | L4 | review | R01, R02, O04 | not-started |
| [R07](work-pack/tasks/R07.md) | Stable candidate validation and final audits | L4 | verification | R05, R06 | not-started |
| [R08](work-pack/tasks/R08.md) | Exact stable v1.0.0 release decision | L4 | owner-decision | R07 | not-started |

## Smallest Working Units

Each SWU has one parent, exact sources/context hints, declared dependencies, planned write scope, done criteria, acceptance evidence and a reviewable validation check in its linked task and the machine manifest. These are construction contracts, not fabricated future outcomes. Multi-unit tasks execute one selected unit at a time. Shared runtime/schema paths require serialized integration.

| SWU | Parent contract | Objective | Dependencies | Owner |
| --- | --- | --- | --- | --- |
| SWU-B01-01 | [B01](work-pack/tasks/B01.md) | Whole-Lab source and contract analysis | B00 | local-collaborator |
| SWU-C01-01 | [C01](work-pack/tasks/C01.md) | Specify closed profile inputs, review binding and compatibility rules | B01 | local-collaborator |
| SWU-C02-01 | [C02](work-pack/tasks/C02.md) | Resolve the selected carrier, reference and typed endpoint closure | B01 | local-collaborator |
| SWU-C03-01 | [C03](work-pack/tasks/C03.md) | Specify and execute bounded per-operation measurements | B01 | local-collaborator |
| SWU-C04-01 | [C04](work-pack/tasks/C04.md) | Implement closed explicit profile loader and compatibility | C01, C02 | local-collaborator |
| SWU-C04-02 | [C04](work-pack/tasks/C04.md) | Integrate pinned capture, review binding and CLI selection | SWU-C04-01 | local-collaborator |
| SWU-C05-01 | [C05](work-pack/tasks/C05.md) | Implement transition classification and exact proposal | C04 | local-collaborator |
| SWU-C05-02 | [C05](work-pack/tasks/C05.md) | Integrate separately identified successor branch and recovery | SWU-C05-01 | local-collaborator |
| SWU-C06-01 | [C06](work-pack/tasks/C06.md) | Implement measured verified reuse or record justified no-op | C03, C04 | local-collaborator |
| SWU-C06-02 | [C06](work-pack/tasks/C06.md) | Integrate invalidation and independent full-replay parity | SWU-C06-01 | local-collaborator |
| SWU-C07-01 | [C07](work-pack/tasks/C07.md) | Implement exact committed-target export and repository dry review | C02, C04, C14 | local-collaborator |
| SWU-C07-02 | [C07](work-pack/tasks/C07.md) | Implement atomic repository publisher and mirror recovery | SWU-C07-01 | local-collaborator |
| SWU-C08-01 | [C08](work-pack/tasks/C08.md) | Bind exact context references and generator provenance | C02, C04 | local-collaborator |
| SWU-C08-02 | [C08](work-pack/tasks/C08.md) | Integrate fresh-context invalidation and ephemeral closure | SWU-C08-01 | local-collaborator |
| SWU-C09-01 | [C09](work-pack/tasks/C09.md) | Freeze and validate successor package and complete evidence | C05, C06, C07, C08, C14 | local-collaborator |
| SWU-C09-02 | [C09](work-pack/tasks/C09.md) | Prepare exact target and realistic example before owner decision | SWU-C09-01 | local-collaborator |
| SWU-C10-01 | [C10](work-pack/tasks/C10.md) | Record actual owner disposition of the exact successor envelope | C09 | owner |
| SWU-C11-01 | [C11](work-pack/tasks/C11.md) | Provision the explicitly selected operator boundary and local branch | C10 | manual-operator |
| SWU-C12-01 | [C12](work-pack/tasks/C12.md) | Perform and review one actual Work cycle with supported durable results | C11 | local-collaborator |
| SWU-C13-01 | [C13](work-pack/tasks/C13.md) | Verify L1 real-work continuity, alignment and layer boundaries | C12 | local-collaborator |
| SWU-C14-01 | [C14](work-pack/tasks/C14.md) | Implement exact typed extension admissibility and schema-fit rules | C02, C04 | local-collaborator |
| SWU-C14-02 | [C14](work-pack/tasks/C14.md) | Integrate no-collapse review evidence and single-authority projection checks | SWU-C14-01 | local-collaborator |
| SWU-W01-01 | [W01](work-pack/tasks/W01.md) | Specify complete engineering, research and learning transitions | C02 | local-collaborator |
| SWU-W02-01 | [W02](work-pack/tasks/W02.md) | Implement exact bounded authority evaluation | W01, C13 | local-collaborator |
| SWU-W02-02 | [W02](work-pack/tasks/W02.md) | Integrate local tool dispatch, receipts and interruption reconciliation | SWU-W02-01 | local-collaborator |
| SWU-W03-01 | [W03](work-pack/tasks/W03.md) | Implement engineering state transitions and typed closure | W01, W02 | local-collaborator |
| SWU-W03-02 | [W03](work-pack/tasks/W03.md) | Integrate bounded implementation and satisfaction assessment case | SWU-W03-01 | local-collaborator |
| SWU-W04-01 | [W04](work-pack/tasks/W04.md) | Implement inquiry, method and experiment/run transitions | W01, W02 | local-collaborator |
| SWU-W04-02 | [W04](work-pack/tasks/W04.md) | Integrate measurement provenance and bounded research assessment | SWU-W04-01 | local-collaborator |
| SWU-W05-01 | [W05](work-pack/tasks/W05.md) | Implement attributable evidence and independent classification/failure assessment | W01, W02 | local-collaborator |
| SWU-W05-02 | [W05](work-pack/tasks/W05.md) | Integrate exact challenge obligations and resolution | SWU-W05-01 | local-collaborator |
| SWU-W06-01 | [W06](work-pack/tasks/W06.md) | Implement scoped lesson drafting and explainable selection | W05, C08 | local-collaborator |
| SWU-W06-02 | [W06](work-pack/tasks/W06.md) | Integrate later application/outcome and improvement proposals | SWU-W06-01 | local-collaborator |
| SWU-W07-01 | [W07](work-pack/tasks/W07.md) | Validate full engineering/research/failure/lesson integration | W03, W04, W06 | local-collaborator |
| SWU-W08-01 | [W08](work-pack/tasks/W08.md) | Record actual disposition of the complete workflow envelope | W07 | owner |
| SWU-W09-01 | [W09](work-pack/tasks/W09.md) | Execute and assess real integrated cases and close L2 | W08, C13 | local-collaborator |
| SWU-O01-01 | [O01](work-pack/tasks/O01.md) | Specify exact ontology mapping, joins, namespaces and coverage | B01, C02 | local-collaborator |
| SWU-O02-01 | [O02](work-pack/tasks/O02.md) | Implement exact Lab-to-ontology representation adapter | O01, C13, W05 | local-collaborator |
| SWU-O02-02 | [O02](work-pack/tasks/O02.md) | Integrate independent lifecycle/challenge joins and parity | SWU-O02-01 | local-collaborator |
| SWU-O03-01 | [O03](work-pack/tasks/O03.md) | Implement exact lens query/evidence bridges | O01, C08 | local-collaborator |
| SWU-O03-02 | [O03](work-pack/tasks/O03.md) | Integrate deterministic refresh, coverage and stale reporting | SWU-O03-01 | local-collaborator |
| SWU-O04-01 | [O04](work-pack/tasks/O04.md) | Inventory and disposition one selected migration domain | O01, C07 | local-collaborator |
| SWU-O05-01 | [O05](work-pack/tasks/O05.md) | Implement selected source-qualified import adapters | O04, O02 | local-collaborator |
| SWU-O05-02 | [O05](work-pack/tasks/O05.md) | Build exact schema-valid import package and deterministic evidence | SWU-O05-01 | local-collaborator |
| SWU-O06-01 | [O06](work-pack/tasks/O06.md) | Record actual disposition of selected ontology/import envelope | O05, O03, W09 | owner |
| SWU-O07-01 | [O07](work-pack/tasks/O07.md) | Verify selected domain coherence, coverage and migration closure | O06, W09 | local-collaborator |
| SWU-R01-01 | [R01](work-pack/tasks/R01.md) | Specify Product users, acceptance measures and bounded release scope | B01 | local-collaborator |
| SWU-R02-01 | [R02](work-pack/tasks/R02.md) | Implement bounded installation and compatibility-aware upgrade | R01, C13 | local-collaborator |
| SWU-R02-02 | [R02](work-pack/tasks/R02.md) | Integrate scoped export, interrupted setup recovery and rollback | SWU-R02-01 | local-collaborator |
| SWU-R03-01 | [R03](work-pack/tasks/R03.md) | Implement selected inspection/currentness journey | R01, C13, W01 | local-collaborator |
| SWU-R03-02 | [R03](work-pack/tasks/R03.md) | Integrate exact proposal review, decision and receipt explanations | SWU-R03-01 | local-collaborator |
| SWU-R04-01 | [R04](work-pack/tasks/R04.md) | Construct exact capability realization and conformance proposals | R01, W09, O07 | local-collaborator |
| SWU-R05-01 | [R05](work-pack/tasks/R05.md) | Authorize selected pilot effects and execute assessed real Product journeys | R02, R03, R04, O07 | local-collaborator |
| SWU-R06-01 | [R06](work-pack/tasks/R06.md) | Review exact release privacy/source boundaries and dispositions | R01, R02, O04 | local-collaborator |
| SWU-R07-01 | [R07](work-pack/tasks/R07.md) | Validate exact release and preserved operational guarantees | R05, R06 | local-collaborator |
| SWU-R07-02 | [R07](work-pack/tasks/R07.md) | Complete alignment/layering audits and owner review target | SWU-R07-01 | local-collaborator |
| SWU-R08-01 | [R08](work-pack/tasks/R08.md) | Record actual owner disposition and apply only selected release effects | R07 | owner |

## Shared handoff context

- [Source context](work-pack/shared/context.md)
- [Gaps](work-pack/shared/cross-task-gaps.md)
- [Design decisions](work-pack/shared/cross-task-decisions.md)
- [Traceability](work-pack/shared/traceability.md)
- [All-current contract coverage](CONTRACT-COVERAGE.md)

Execution-time context packs select obligation-linked exact sources; this authoring package does not preload whole-session memory. Update DAG/task/wave/SWU evidence consistently; no node advances from a label or a planned receipt.

## Validation strategy and effect gates

Every task lists positive/negative acceptance evidence. C09 validates the successor, W07 the workflows, O07 selected ontology/migration coherence, R07 the release. C13/W09/O07/R07 also audit exact contract alignment and layer boundaries. Test/benchmark commands are selected after implementation interfaces and user authorization are established; no suite was run for this planning request.

Owner nodes C10/W08/O06/R08 require actual exact dispositions. Provisioning C11 and pilot R05 need explicit selected operational effects. One envelope can resolve multiple independent cores; deterministic consequences do not require additional owner responses. Data admission does not confer action authority.

No plan approval ceremony is added. The user can review these concrete artifacts; future candidate construction and owner decisions follow their stated scopes.
