# Protocol schemas

Status: candidate. All new JSON schemas use Draft 2020-12 and explicit `v1-candidate` resource identifiers. Cross-field semantic checks are assigned to [runtime obligations](RUNTIME-OBLIGATIONS.md). The [offline resolver](resources.py) loads pinned local resources without network access.

Existing bodies and selectors are retained in [domain bindings](domain-bindings.json). Their schemas are not rewritten into a universal body shape.

## Foundation

| Schema | Purpose | Example | Obligations |
|---|---|---|---|

| [common](schemas/common.schema.json) | Shared exact bindings, cuts, actors, budgets and gaps | Shared definitions | O-EXACT, O-AUTHORITY, O-CUT |

| [domain-artifact](schemas/domain-artifact.schema.json) | Validate unchanged heterogeneous bodies under all exact registered carriers | [Message](examples/domain-artifact.json) | O-EXACT, O-CARRIER, O-REFERENCE |

| [artifact-envelope](schemas/artifact-envelope.schema.json) | Transport exact original content plus a body validated by its selected carrier | [Message](examples/artifact-envelope.json) | O-EXACT, O-CARRIER, O-BYTES, O-AUTHORITY |

| [typed-connection](schemas/typed-connection.schema.json) | Close all current Relation Kind endpoint pairs and current qualifier shapes | [Message](examples/typed-connection.json) | O-EXACT, O-REFERENCE, O-RELATION, O-EXTENSION |

| [candidate-contract-binding](schemas/candidate-contract-binding.schema.json) | Bind prospective schemas/identity rules before their admission | [Message](examples/candidate-contract-binding.json) | O-EXACT, O-CANDIDATE-CARRIER, O-CARRIER, O-REFERENCE, O-EXTENSION |

| [candidate-artifact](schemas/candidate-artifact.schema.json) | Transport a future-carrier body requiring dynamic pinned-schema validation | [Message](examples/candidate-artifact.json) | O-EXACT, O-CANDIDATE-CARRIER, O-CARRIER, O-BYTES, O-REFERENCE |

| [carrier-endpoint-binding](schemas/carrier-endpoint-binding.schema.json) | Declare endpoint-kind mapping without inferring aliases or authority | [Message](examples/carrier-endpoint-binding.json) | O-EXACT, O-CARRIER, O-RELATION, O-EXTENSION |

| [domain-lifecycle-mapping](schemas/domain-lifecycle-mapping.schema.json) | Bind workflow transitions to exact domain status/evidence contracts | [Message](examples/domain-lifecycle-mapping.json) | O-EXACT, O-WORKFLOW, O-CARRIER, O-EVIDENCE, O-AUTHORITY |

| [error-result](schemas/error-result.schema.json) | Explicit failure, indeterminate result or missing obligation | [Message](examples/error-result.json) | O-EXACT, O-AUTHORITY, O-RECOVERY |

| [protocol-package-manifest](schemas/protocol-package-manifest.schema.json) | Bind exact schemas, models, examples and retained domain contracts | [Message](examples/protocol-package-manifest.json) | O-EXACT, O-HASH, O-CARRIER |

## Sources

| Schema | Purpose | Example | Obligations |
|---|---|---|---|

| [canonical-store-config](schemas/canonical-store-config.schema.json) | Bind a scoped canonical store to independent profile and trust roots | [Message](examples/canonical-store-config.json) | O-EXACT, O-PROFILE, O-AUTHORITY, O-COMMIT, O-PRIVACY |

| [commit-head](schemas/commit-head.schema.json) | Identify committed history visibility without owning admission authority | [Message](examples/commit-head.json) | O-EXACT, O-COMMIT, O-CUT, O-RECOVERY |

| [source-profile](schemas/source-profile.schema.json) | Independent exact source and executable compatibility selection | [Message](examples/source-profile.json) | O-EXACT, O-PROFILE, O-CUT, O-CARRIER |

| [profile-transition](schemas/profile-transition.schema.json) | Explicit successor branch without rewriting old history | [Message](examples/profile-transition.json) | O-EXACT, O-PROFILE, O-AUTHORITY, O-RECOVERY |

| [candidate-workspace](schemas/candidate-workspace.schema.json) | Isolate exact candidate closure and eligibility from admitted state | [Message](examples/candidate-workspace.json) | O-EXACT, O-CARRIER, O-REFERENCE, O-MEMORY, O-PRIVACY |

## Storage

| Schema | Purpose | Example | Obligations |
|---|---|---|---|

| [sqlite-projection-config](schemas/sqlite-projection-config.schema.json) | Declare disposable DB compatibility, custody and complete generation checks | [Message](examples/sqlite-projection-config.json) | O-EXACT, O-PROJECTION, O-CUT, O-PRIVACY |

| [projection-refresh-request](schemas/projection-refresh-request.schema.json) | Request disposable SQLite projection rebuild at an exact cut | [Message](examples/projection-refresh-request.json) | O-EXACT, O-PROJECTION, O-CUT |

| [projection-query-status](schemas/projection-query-status.schema.json) | Return projection cut and independent source verification | [Message](examples/projection-query-status.json) | O-EXACT, O-PROJECTION, O-CUT |

| [file-materialization-request](schemas/file-materialization-request.schema.json) | Select exact export content and pinned rendering scope | [Message](examples/file-materialization-request.json) | O-EXACT, O-FILE, O-BYTES, O-PRIVACY, O-MEMORY |

| [file-materialization-receipt](schemas/file-materialization-receipt.schema.json) | Acknowledge file generation separately from canonical commit | [Message](examples/file-materialization-receipt.json) | O-EXACT, O-FILE, O-RECOVERY |

| [package-export-request](schemas/package-export-request.schema.json) | Export selected complete portable content and dependencies | [Message](examples/package-export-request.json) | O-EXACT, O-BYTES, O-PRIVACY, O-MEMORY, O-REFERENCE |

| [package-import-request](schemas/package-import-request.schema.json) | Prepare independent exact import/adaptation effects | [Message](examples/package-import-request.json) | O-EXACT, O-MIGRATION, O-AUTHORITY, O-REFERENCE |

## Reads

| Schema | Purpose | Example | Obligations |
|---|---|---|---|

| [context-query](schemas/context-query.schema.json) | Request bounded relevant context for an exact assignment | [Message](examples/context-query.json) | O-EXACT, O-CUT, O-VIEW, O-AUTHORITY |

| [context-delivery](schemas/context-delivery.schema.json) | Deliver source-bound Context/Ontology Views without granting authority | [Message](examples/context-delivery.json) | O-EXACT, O-VIEW, O-CUT, O-MEMORY |

| [artifact-inspect-request](schemas/artifact-inspect-request.schema.json) | Inspect one exact permitted artifact revision | [Message](examples/artifact-inspect-request.json) | O-EXACT, O-VIEW, O-AUTHORITY, O-CUT |

| [artifact-inspect-result](schemas/artifact-inspect-result.schema.json) | Explain content and independent status facets | [Message](examples/artifact-inspect-result.json) | O-EXACT, O-VIEW, O-CUT, O-CARRIER |

| [artifact-query](schemas/artifact-query.schema.json) | Bound artifact discovery to selectors, scope and exact cut | [Message](examples/artifact-query.json) | O-EXACT, O-VIEW, O-CUT, O-AUTHORITY |

| [artifact-query-result](schemas/artifact-query-result.schema.json) | Return attributable discovery results with projection watermark | [Message](examples/artifact-query-result.json) | O-EXACT, O-CUT, O-VIEW, O-PROJECTION |

| [lab-status-request](schemas/lab-status-request.schema.json) | Discover selected store/profile compatibility and current watermarks | [Message](examples/lab-status-request.json) | O-EXACT, O-VIEW, O-CUT, O-PROFILE, O-AUTHORITY |

| [lab-status-result](schemas/lab-status-result.schema.json) | Report selected heads and declared versus implemented operation support | [Message](examples/lab-status-result.json) | O-EXACT, O-VIEW, O-CUT, O-PROFILE, O-EVIDENCE |

| [catalog-request](schemas/catalog-request.schema.json) | Read exact contract/catalog bindings before artifact discovery | [Message](examples/catalog-request.json) | O-EXACT, O-VIEW, O-CARRIER, O-CUT, O-AUTHORITY |

| [catalog-result](schemas/catalog-result.schema.json) | Return pinned current/historical contracts and declared relation signatures | [Message](examples/catalog-result.json) | O-EXACT, O-CARRIER, O-CUT, O-VIEW, O-RELATION |

## Actors

| Schema | Purpose | Example | Obligations |
|---|---|---|---|

| [authority-envelope](schemas/authority-envelope.schema.json) | Present references to actual authority for an assignment | [Message](examples/authority-envelope.json) | O-EXACT, O-AUTHORITY |

| [authority-evaluation](schemas/authority-evaluation.schema.json) | Evaluate exact action against live scope, period, revocation and gates | [Message](examples/authority-evaluation.json) | O-EXACT, O-AUTHORITY, O-CUT |

| [agent-session-open](schemas/agent-session-open.schema.json) | Create a bounded ephemeral machine Agent session | [Message](examples/agent-session-open.json) | O-EXACT, O-MEMORY, O-AUTHORITY, O-VIEW |

| [agent-session-result](schemas/agent-session-result.schema.json) | Describe a new ephemeral session and durable-knowledge source | [Message](examples/agent-session-result.json) | O-EXACT, O-MEMORY, O-AUTHORITY |

| [ephemeral-memory](schemas/ephemeral-memory.schema.json) | Session-only short memory; excluded from persistence/export | [Message](examples/ephemeral-memory.json) | O-EXACT, O-MEMORY, O-PRIVACY |

| [agent-session-close](schemas/agent-session-close.schema.json) | Request termination without claiming memory already destroyed | [Message](examples/agent-session-close.json) | O-EXACT, O-MEMORY, O-RECOVERY |

| [agent-session-close-receipt](schemas/agent-session-close-receipt.schema.json) | Record actual termination, memory expiry and unresolved action residue | [Message](examples/agent-session-close-receipt.json) | O-EXACT, O-MEMORY, O-RECOVERY |

| [session-inspect-request](schemas/session-inspect-request.schema.json) | Inspect session metadata and audit references without exposing short memory | [Message](examples/session-inspect-request.json) | O-EXACT, O-MEMORY, O-PRIVACY, O-AUTHORITY |

| [session-inspect-result](schemas/session-inspect-result.schema.json) | Observe active/closed/expired session metadata and pending action residue | [Message](examples/session-inspect-result.json) | O-EXACT, O-MEMORY, O-RECOVERY, O-AUTHORITY |

## Actions

| Schema | Purpose | Example | Obligations |
|---|---|---|---|

| [tool-adapter-contract](schemas/tool-adapter-contract.schema.json) | Bind tool input/output contracts and side-effect/retry scope | [Message](examples/tool-adapter-contract.json) | O-EXACT, O-ACTION, O-AUTHORITY, O-RECOVERY |

| [action-request](schemas/action-request.schema.json) | Ask dispatch of one exact bounded action | [Message](examples/action-request.json) | O-EXACT, O-AUTHORITY, O-ACTION, O-RECOVERY |

| [action-receipt](schemas/action-receipt.schema.json) | Attribute dispatch, outputs and uncertain completion | [Message](examples/action-receipt.json) | O-EXACT, O-ACTION, O-RECOVERY, O-EVIDENCE |

| [recovery-request](schemas/recovery-request.schema.json) | Reconcile uncertain action or known uncommitted residue | [Message](examples/recovery-request.json) | O-EXACT, O-RECOVERY, O-AUTHORITY |

| [recovery-receipt](schemas/recovery-receipt.schema.json) | Record verified recovery and preserved committed state | [Message](examples/recovery-receipt.json) | O-EXACT, O-RECOVERY, O-EVIDENCE |

| [operation-inspect-request](schemas/operation-inspect-request.schema.json) | Look up only the caller-authorized invocation or scoped idempotency record | [Message](examples/operation-inspect-request.json) | O-EXACT, O-RECOVERY, O-AUTHORITY, O-TRANSPORT |

| [operation-inspect-result](schemas/operation-inspect-result.schema.json) | Observe known operation result or uncertainty without dispatching it again | [Message](examples/operation-inspect-result.json) | O-EXACT, O-RECOVERY, O-EVIDENCE, O-AUTHORITY |

## Governance

| Schema | Purpose | Example | Obligations |
|---|---|---|---|

| [change-proposal](schemas/change-proposal.schema.json) | Prepare exact artifact effects without applying authority | [Message](examples/change-proposal.json) | O-EXACT, O-CARRIER, O-REFERENCE, O-AUTHORITY, O-RELATION, O-HASH |

| [validation-report](schemas/validation-report.schema.json) | Record scope-bounded structural/semantic/authority check evidence | [Message](examples/validation-report.json) | O-EXACT, O-EVIDENCE, O-CARRIER |

| [proposal-review](schemas/proposal-review.schema.json) | Show exact diff, consequences, examples and unresolved obligations | [Message](examples/proposal-review.json) | O-EXACT, O-HASH, O-AUTHORITY, O-PRIVACY, O-EVIDENCE |

| [decision-core](schemas/decision-core.schema.json) | Keep independently governed exact target/effect cores acyclic | [Message](examples/decision-core.json) | O-EXACT, O-HASH, O-AUTHORITY |

| [review-package](schemas/review-package.schema.json) | One complete final checkpoint with independent exact members | [Message](examples/review-package.json) | O-EXACT, O-AUTHORITY, O-HASH, O-EVIDENCE |

| [authorization-proof](schemas/authorization-proof.schema.json) | Bind actual authorization channel to exact stable reviewed inputs | [Message](examples/authorization-proof.json) | O-EXACT, O-AUTHORITY, O-HASH, O-CUT |

| [checkpoint-resolution](schemas/checkpoint-resolution.schema.json) | Record actual member outcomes without inventing owner signatures | [Message](examples/checkpoint-resolution.json) | O-EXACT, O-AUTHORITY, O-HASH |

| [commit-request](schemas/commit-request.schema.json) | Request exact canonical application under one selected authority scope | [Message](examples/commit-request.json) | O-EXACT, O-COMMIT, O-AUTHORITY, O-HASH, O-RECOVERY |

| [commit-record](schemas/commit-record.schema.json) | Persist distinct event changes, exact content and consequences | [Message](examples/commit-record.json) | O-EXACT, O-COMMIT, O-HASH, O-AUTHORITY, O-RECOVERY |

| [commit-receipt](schemas/commit-receipt.schema.json) | Acknowledge canonical commit independently of projections/exports | [Message](examples/commit-receipt.json) | O-EXACT, O-COMMIT, O-RECOVERY, O-PROJECTION |

## Workflows

| Schema | Purpose | Example | Obligations |
|---|---|---|---|

| [workflow-definition](schemas/workflow-definition.schema.json) | Declare transitions and obligations independently of admission posture | [Message](examples/workflow-definition.json) | O-EXACT, O-WORKFLOW, O-AUTHORITY, O-EVIDENCE |

| [workflow-run](schemas/workflow-run.schema.json) | Bind a workflow instance to exact Work, coordination and observations | [Message](examples/workflow-run.json) | O-EXACT, O-WORKFLOW, O-EVIDENCE, O-AUTHORITY |

| [workflow-transition](schemas/workflow-transition.schema.json) | Request one exact permitted workflow step | [Message](examples/workflow-transition.json) | O-EXACT, O-WORKFLOW, O-AUTHORITY, O-EVIDENCE |

| [workflow-transition-receipt](schemas/workflow-transition-receipt.schema.json) | Record observed workflow change without automatic artifact admission | [Message](examples/workflow-transition-receipt.json) | O-EXACT, O-WORKFLOW, O-EVIDENCE, O-RECOVERY |

## Learning

| Schema | Purpose | Example | Obligations |
|---|---|---|---|

| [classification-request](schemas/classification-request.schema.json) | Propose one axis-qualified classification assignment | [Message](examples/classification-request.json) | O-EXACT, O-CLASSIFICATION, O-EVIDENCE |

| [failure-assessment-request](schemas/failure-assessment-request.schema.json) | Propose assessment keeping occurrence/mode/cause/recovery separate | [Message](examples/failure-assessment-request.json) | O-EXACT, O-FAILURE, O-EVIDENCE |

| [challenge-request](schemas/challenge-request.schema.json) | Submit attributable challenge under the exact contestability contract | [Message](examples/challenge-request.json) | O-EXACT, O-CHALLENGE, O-AUTHORITY, O-EVIDENCE |

| [challenge-resolution](schemas/challenge-resolution.schema.json) | Bind resolution to actual Decision and preserve semantic/governance distinction | [Message](examples/challenge-resolution.json) | O-EXACT, O-CHALLENGE, O-AUTHORITY, O-ONTOLOGY |

| [lesson-selection](schemas/lesson-selection.schema.json) | Explain eligible lesson selection without implying application or benefit | [Message](examples/lesson-selection.json) | O-EXACT, O-LESSON, O-MEMORY, O-EVIDENCE |

| [lesson-application-request](schemas/lesson-application-request.schema.json) | Record an explicit proposed application of an exact lesson revision | [Message](examples/lesson-application-request.json) | O-EXACT, O-LESSON, O-AUTHORITY |

| [lesson-assessment-request](schemas/lesson-assessment-request.schema.json) | Assess predicted/observed outcomes and causal claim ceiling | [Message](examples/lesson-assessment-request.json) | O-EXACT, O-LESSON, O-EVIDENCE |

## Ontology

| Schema | Purpose | Example | Obligations |
|---|---|---|---|

| [typed-extension-request](schemas/typed-extension-request.schema.json) | Declare missing pair/qualifier semantics and noncollapse review obligations | [Message](examples/typed-extension-request.json) | O-EXACT, O-EXTENSION, O-RELATION, O-AUTHORITY |

| [ontology-mapping](schemas/ontology-mapping.schema.json) | Preserve exact represented subjects and distinct edge authorities | [Message](examples/ontology-mapping.json) | O-EXACT, O-ONTOLOGY, O-RELATION, O-CUT |

| [ontology-project-request](schemas/ontology-project-request.schema.json) | Map exact committed Lab inputs to selected ontology representations | [Message](examples/ontology-project-request.json) | O-EXACT, O-ONTOLOGY, O-AUTHORITY, O-CUT |

| [ontology-projection-receipt](schemas/ontology-projection-receipt.schema.json) | Expose independent ontology watermark, exact mappings and gaps | [Message](examples/ontology-projection-receipt.json) | O-EXACT, O-ONTOLOGY, O-CUT, O-EVIDENCE |

## Product

| Schema | Purpose | Example | Obligations |
|---|---|---|---|

| [migration-disposition](schemas/migration-disposition.schema.json) | Account for every selected legacy item without claiming broad cutover | [Message](examples/migration-disposition.json) | O-EXACT, O-MIGRATION, O-PRIVACY, O-AUTHORITY |

| [capability-adoption-request](schemas/capability-adoption-request.schema.json) | Separate realization/binding conformance and owner-local adoption | [Message](examples/capability-adoption-request.json) | O-EXACT, O-ADOPTION, O-AUTHORITY, O-EVIDENCE |

| [release-manifest](schemas/release-manifest.schema.json) | Bind exact release bytes, acceptance, pilot and selected effects | [Message](examples/release-manifest.json) | O-EXACT, O-RELEASE, O-EVIDENCE, O-PRIVACY, O-AUTHORITY |

| [install-request](schemas/install-request.schema.json) | Request scoped install/upgrade/rollback without inferred service activation | [Message](examples/install-request.json) | O-EXACT, O-INSTALL, O-AUTHORITY, O-RECOVERY, O-PRIVACY |

| [installation-receipt](schemas/installation-receipt.schema.json) | Record observed local installation and recovery residue | [Message](examples/installation-receipt.json) | O-EXACT, O-INSTALL, O-EVIDENCE, O-RECOVERY |

## Interface

| Schema | Purpose | Example | Obligations |
|---|---|---|---|

| [tool-service-request](schemas/tool-service-request.schema.json) | Closed operation-specific request dispatch without implicit permissions | [Message](examples/tool-service-request.json) | O-EXACT, O-AUTHORITY, O-TRANSPORT |

| [tool-service-result](schemas/tool-service-result.schema.json) | Closed operation-specific result dispatch without implicit permissions | [Message](examples/tool-service-result.json) | O-EXACT, O-AUTHORITY, O-TRANSPORT |

## Reused storage schemas

These four candidate schemas and the 12-table SQL DDL retain their exact source bindings. They are owned by [storage proposal 0006](../0006-lab-artifact-storage/SCHEMAS.md).

| Schema | Responsibility |
|---|---|
| [artifact-content-entry](../0006-lab-artifact-storage/schemas/artifact-content-entry.schema.json) | Original bytes, digest, byte count, media type and content identity |
| [artifact-package-manifest](../0006-lab-artifact-storage/schemas/artifact-package-manifest.schema.json) | Exact input source cut, immutable entries and dependencies |
| [projection-generation](../0006-lab-artifact-storage/schemas/projection-generation.schema.json) | Complete verified disposable projection inputs and watermarks |
| [file-generation](../0006-lab-artifact-storage/schemas/file-generation.schema.json) | Managed exact or rendered files and output digests |
| [SQLite read model](../0006-lab-artifact-storage/schemas/sqlite-read-model.sql) | Query indexes, revisions, typed relations, reference resolution, authority facts, ontology links and gaps |

## Domain and compatibility resources

[DOMAIN-CONTRACTS.md](DOMAIN-CONTRACTS.md) links every one of the 143 bound versions and marks the 121 current carriers. Read/write eligibility still requires runtime authority and compatibility checks. Six existing v2 local-runtime message schemas and the Session Memory schema are pinned in [schema-catalog.json](schema-catalog.json); they do not become general admission authority.

Nine historical wrapper references select two repository schema dependencies. [schema-dependencies.json](schema-dependencies.json) declares each exact compatibility mapping. The offline resolver substitutes those declared file resource references in memory, retaining the original files and their hashes. This explicit adapter must be reviewed for runtime use; no network URL is dereferenced.

## Services

[service-contracts.json](service-contracts.json) binds 34 candidate operations to exact request, success and error schemas. `tool-service-request` and `tool-service-result` close dispatch to those operations. Helpers such as carrier mappings, authority proofs, extension reviews and release manifests are inputs to those services; they are not additional public endpoints. A declared caller requirement is not authorization.
