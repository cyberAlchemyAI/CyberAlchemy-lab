# Schema review 0001

Status: **candidate shapes revised; execution and admission remain pending**. This review covers all 80 revised protocol schemas, their domain/storage dependencies, all 34 service mappings and ten workflow templates. It is an author review, not an independent audit or semantic admission.

The [prior manifest](pre-review-manifest.json), [prior receipt](prior-authoring-receipt.json) and `before/` copies preserve the starting package digest and changed generator/schema inputs. The original package had 72 protocol schemas and 27 services. Review adds eight bootstrap/inspection message schemas and seven operations; it changes candidate messages only. No admitted domain contract, current authority registry or frozen runtime package is revised.

## Findings and repairs

| Finding | Repair | Evidence surface |
|---|---|---|
| Inspection required the body even when only metadata was requested | Nullable body envelope; explicit included sections; excluded body/contract/relations/provenance/evidence sections cannot carry content | artifact-inspect-result; API request/result correspondence |
| Discovery depended on a SQLite generation and lacked a freshness policy | Canonical or projected read basis, explicit freshness requirement, requested and applied cuts; canonical reads carry no projection generation | artifact-query and artifact-query-result |
| Blocked session creation required a created identity and timestamps | Blocked creation carries null instance/session/times; active creation requires them | agent-session-result |
| Blocked close implied a termination timestamp | Nullable termination timestamp, required only for closed receipt; memory disposal remains an observed fact | agent-session-close-receipt |
| Blocked context/ontology or building projection required missing views/generations | Nullable absent objects; ready/applied states require exact bindings | context-delivery; ontology-projection-receipt; projection-query-status |
| Rejected admission could carry a canonical commit | Rejected receipt forbids a commit binding and commit outputs; committed receipt requires binding and no canonical recovery | commit-receipt |
| Workflow block could imply an applied event and outputs | Blocked receipt carries no applied event/outputs; indeterminate requires recovery | workflow-transition-receipt |
| Published files could have no manifest or outputs | Published/staged generations require manifest and identity; publication requires outputs; uncertainty requires recovery | file-materialization-receipt |
| Recovered/rolled-back results lacked observed proof | Recovered requires observed bindings; rolled-back installation requires postimage and verification; uncertain recovery forbids retry | recovery-receipt; installation-receipt |
| Export/adoption could select nothing; extension could name any carrier | Nonempty export selection and realization references; extension binds Relation Kind and Artifact Type descriptor carriers | package-export-request; capability-adoption-request; typed-extension-request |
| Errors allowed blind retry after uncertainty and lacked API boundary failures | Reconcile-first for indeterminate/recovery-required; seven additional error codes | error-result |
| No bootstrap/catalog/session/operation inspection or explicit extension/adoption/release preparation routes | Eight message schemas and seven closed service operations | revised service-contracts.json |
| No exact API invocation/response/identity/retry contract | Subsequent local API package supplies correlated calls/replies, trusted context, error and effect policies | [API contracts](../../../0008-lab-api-contracts/PROPOSAL.md) |

## Unresolved semantic and runtime requirements

1. Declare reviewed carrier mappings for `project`, `product` and `method` endpoints. The dispatcher preserves declared pairs; it does not establish a semantic alias.
2. Bind actual domain lifecycle mappings, actor routes, checks and recovery dispositions for every selected workflow. The ten templates remain non-executable.
3. Verify prospective carrier closures, typed extension qualifier domains, noncollapse evidence and canonical writable authority before selected new effects become admissible.
4. Implement and evidence source/hash/reference validation, authority channels, scoped idempotency, concurrent publication/recovery, query freshness, file safety, memory disposal and operational acceptance. A schema cannot establish those facts.

## Review evidence and scope

The regenerated authoring receipt checks exact resources, examples, closed dispatch, declarations and source preservation. Review scenarios additionally check allowed metadata-only/blocked shapes and reject selected invalid success, carrier and retry combinations. These are static schema authoring checks, not implementation tests, authority verification or an operational pilot.

No interpretation changes to immutable domain source schemas are applied. The prior nine offline wrapper mappings remain explicit compatibility bindings. The new API does not treat `authority_effect: none` as a statement that an operation has no local side effects: that field means the message itself grants no authority; each API operation separately declares its effects.
