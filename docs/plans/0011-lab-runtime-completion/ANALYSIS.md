# Complete runtime implementation analysis

Research date:2026-10-13. This audit covers the ten Lab implementation areas, the selected API16 integration and its independent Action/Governance branches, native/host dependencies, installation/publisher/readiness code, original contracts and current retained qualification/pilot evidence. Three agents performed partitioned source audits; the coordinator reconciled their findings into the completion DAG.

The current snapshot is API16 source `8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7`, profile `8cc29da16d3881d8816cdc45c55358d9229fcaf226d1b9a757402ebc8675d18c`. It is frozen and unqualified. Admitted Operational Runtime v1/D74 and candidate v2/D75 remain distinct. All implementation conclusions below are source/retained-evidence findings, not new runtime execution results.

## Source audits

| Audit | Implementation coverage | Detailed deliverables |
| --- | --- | --- |
| Core, state, domains and workflows | lab-runtime, lab-context, lab-continuity, lab-work, lab-workflows, lab-ontology; selected Session/Machine/Lesson/workflow/native boundaries | [Core report](analysis/core-workflows.md), [typed findings](analysis/core-findings.json) |
| Composition, security and operations | lab-integration, lab-bootstrap, lab-provisioning, lab-review; base/Action/Governance/Machine transport, stdio, native packaging and Paperclip | [Integration report](analysis/integration-operations.md), [typed findings](analysis/integration-findings.json) |
| Qualification and final package | Regression/common-operation accounting, protected proofs/semantic graphs/environment, materializers/publisher, roles/privacy/human evidence and original application/release obligations | [Qualification report](analysis/qualification-release.md), [typed findings](analysis/qualification-findings.json) |

[Source inventory](analysis/source-inventory.json) hashes432 implementation source files across all ten areas; [baseline](SOURCE-BASELINE.json) additionally binds112 API16 Python files and the30 already dirty tracked files. [Coverage](coverage.json) maps all34 operation entrypoints to task/qualification surfaces. This is comprehensive coverage of the relevant implementation areas and paths; it is not a claim that every source line or all possible runtime states have been formally verified. No full suite, live server probe, credential inspection or private store mutation was performed in this authoring turn.

## What works, and what that proves

The repository contains real guarded replay, signed local transactions, durable owned journals, ephemeral Sessions, native semantic/governance queries, candidate engineering/research/learning code, typed API handlers, independently authenticated Action/Governance branches, packaging and release-readiness checks. Existing passing cases demonstrate bounded behavior of those selected implementations.

The current regression reports contain345 unique cases:342 PASS,2 FAIL,1 ERROR. Passing common operation units cover27/34; the full live context/session/lesson sequence is incomplete. Successful `release.prepare` conformance can return a blocked readiness domain result and therefore does not prove release approval. Historical publisher, installation, privacy and Paperclip runs have narrower versions/inputs than the final package. Every retained failure and proof scope is preserved.

## Findings and priorities

The [finding crosswalk](finding-crosswalk.json) maps all33 audit findings, including preserved invariants and explicitly inferred risks, to completion tasks. Findings are not all confirmed defects.

| Priority surface | Evidence-based conclusion | Completion route |
| --- | --- | --- |
| Current source and live resources | Expired immutable Source8 period cannot support fresh positives. Source24h, reader at most30min and Session at most900s are separate bounds; current independently signed selections are required. | T00/T02/T35; just-in-time T15 and lapse policy |
| Session performance and caller | Actual lesson.select crosses real expiry; Session open and guards are expensive. Caller then indexes a transport refusal as domain message. Exact internal cost attribution is still needed. | T03/T04/T35 |
| Machine and fixture origin | Worker9 context.get raw observation is integrity-failed; legacy versus custody class mismatch is mechanically visible but exact throwing guard is not causally traced. Two metadata-resurrection test variants and one old-period assertion need faithful successor selectors. | T01/T02/T05 |
| Operator composition | Maintained stdio entrypoint is base-only; full34 facade exists in programmatic/test assembly. Candidate-only temporary provisioning is not durable admitted setup. | T06/T07/T34 |
| Release implementation | Protected host/proof reading, semantic graph selectors and composite-to-R02 environment comparison need versioned compatibility. Local key-adapter publication responses cannot stand in for an actual human conversation. | T08/T09/T33 |
| Domain/recovery boundaries | Workflow transition rejects output-bearing steps. Native per-file batch persistence has an inferred kill/recovery risk requiring selected-call-chain and interruption testing. | T31/T32 |
| Semantic final package |29 model relationships,230 consumer/domain scopes and88 native events/owner cores remain unresolved. Unknown actual owner Decision bytes may prevent a fixed pre-review target under the original schema. | T10/T11/T13, D01 at T25 |
| Qualification and genuine use | Same-family complete regression/all34/security/install/privacy proofs, actual later Work influence and authentic human journeys are still needed. Paperclip only demonstrated historical reader integration. | T16–T25 |
| Authority and release | Real governing assignments, exact authentic outcomes, admission, separately scoped operation and original admitted milestone/release conditions remain separate. | T12/T26–T30 |

The retained Machine per-call receipt binds the same test namespace, profile, request, connection and time. Its worker report does not cryptographically enumerate that observation file; this lineage limitation is retained, and the future diagnostic must explicitly bind its raw reply to its report. Static type incompatibility is a strong diagnostic lead, not a fabricated exception trace.

## Preservation and design stops

[Original obligation crosswalk](obligation-crosswalk.json) retains all46 full task nodes and63 original phase units, including every original acceptance text and operational route. [Product acceptance](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/PRODUCT-ACCEPTANCE.md) still contains AC01–AC13 and all three human owner journeys. Candidate proof does not close C13/W09/O07 or A01–A04 admitted-operation criteria.

Final target semantic decisions and absent governing owners gate the package/application lane; they do not block unrelated Machine diagnostics or technical execution qualification. Immutable execution/source cores, target cores, exact rehearsal inputs, observed evidence, review envelope and real owner-response envelope are separate digest domains. If the original native schema requires unknown response bytes inside the semantic target, D01 needs an actual representation disposition; no placeholder owner approval or conditional future target can conceal it.

The default operator surface remains serialized on-demand local stdio. A persistent network daemon, public deployment and broad autonomous Paperclip task management are outside this completion scope. The human pilot uses the already agreed questions and actual journeys with bounded, demonstrated capability.

## Limits and next evidence

No new runtime PASS is claimed. Inferred concurrency, persistence and performance risks require causal probes in independently pinned owned candidate copies. The first runnable planning frontiers are T00, then independent Machine diagnosis/caller work and current source construction/profiling, alongside disjoint dependency/representation/owner-prerequisite research. Final admission and release require authentic current authority and observed operation. [Plan](PLAN.md), [DAG](DAG.md) and [independent review](REVIEW.md) define the next steps and their claim limits.
