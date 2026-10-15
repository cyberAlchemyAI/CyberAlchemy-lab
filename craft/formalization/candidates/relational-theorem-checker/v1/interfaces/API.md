# API contract and flows

The proposed service exposes 16 operations. No endpoint is started by this package. Requests are untrusted; asynchronous 202 responses only acknowledge execution scheduling.

| Method | Path | Operation |
|---|---|---|
| POST | /v1/snapshots | captureSnapshot |
| POST | /v1/normalizations | normalizeGraph |
| POST | /v1/checks | checkAddition |
| POST | /v1/obligations | deriveObligations |
| POST | /v1/derivations/check | checkDerivation |
| POST | /v1/closures/check | checkClosure |
| POST | /v1/models/check | checkModel |
| POST | /v1/proofs/verify | verifyProof |
| POST | /v1/reviews | reviewBundle |
| POST | /v1/replays | replayBundle |
| POST | /v1/application-rechecks | recheckApplication |
| POST | /v1/artifacts | putArtifact |
| GET | /v1/artifacts/{sha256} | getArtifact |
| GET | /v1/jobs/{job_id} | getJob |
| POST | /v1/jobs/{job_id}/cancel | cancelJob |
| GET | /v1/capabilities | getCapabilities |

## Artifact transport

Upload exact original bytes to POST /v1/artifacts with X-Artifact-Schema and X-Artifact-Media-Type. Named envelope schemas require UTF-8 JSON and duplicate-key rejection. Use raw-artifact for proof source, required statements, raw provider output and pinned dependencies. A raw upload remains untrusted and cannot bypass the expected role/schema checks of its consuming operation. SHA-256 and byte size describe original bytes without reserialization.
A controlled source adapter may register captured immutable authority source bytes and aliases in the artifact store. Caller-submitted repo paths are not executed or fetched directly. Every read, including raw proof/dependency content and known digests, still requires principal-scoped authorization.
Idempotency-Key is required for asynchronous operations. Same principal/route/key with identical raw request bytes returns the original job; different bytes produce 409. Idempotency records and jobs must remain principal scoped.

## Add a relation

1. Capture and upload a selected source snapshot and reviewed semantic profile.
2. Upload the base graph, resulting graph and exact change proposal.
3. Normalize inputs and request complete obligations derived from the actual diff.
4. Request the checker and attach proof/model evidence for applicable obligations.
5. Submit the evidence bundle for independent review aggregation.
6. Poll the job; read its result documents and their scope/currentness dimensions.
7. Simulate application recheck against a fresh trusted baseline; actual admission is separate.

## Example check request

[Complete request](examples/check-request.json) binds the captured snapshot, draft profile, base graph and addition proposal. Its requested scope is structural. A supported-semantics request cannot become ready with this draft profile or without independent semantics and soundness evidence.

## Rule changes

Upload the positive finite rule profile, rules, base facts and derivation/closure certificates. Certificates carry exact rule versions and ground substitutions. Only an independently verified least fixed point or general theorem supports negative non-derivability claims. The checker must preserve protected root lineage across all intermediate rules.

## Errors and resource policy

Malformed data is 400; unknown or unsupported input schema/profile is 422; identity/idempotency/terminal-state conflicts are 409. Authentication and authorization use 401/403. Configured request size, graph size, rule-grounding, proof time and concurrency limits produce 413/429 or explicit timeout/unavailability job states. No throughput limit is invented here.
A syntactically valid job may finish with violated, unknown or unsupported semantic obligations. That is represented in the result, not converted into a transport success claim.

## Lifecycle

Queued -> running -> completed / timeout / unavailable / failed. Queued or running work can cancel. Completed jobs require operation-compatible result references; terminal artifacts are immutable. Cancellation never creates readiness.
