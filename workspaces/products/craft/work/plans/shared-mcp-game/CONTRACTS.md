# Shared-control implementation contracts

Date: 2026-10-29. Status: closed contracts, host boundary, actor authorization and owned-operation semantics are implemented in the offline game; the official SDK adapter is tested without live attachment. Decisions R01–R18 are recorded in [distill/RECONCILIATION.md](/home/vlad_/projects/cyberAlchemy-v2/goals/plans/craft-game-shared-mcp-2026-10-29/distill/RECONCILIATION.md). Field-level schemas, executable fixtures and typed port are now in `release-candidates/craft-alchlang-current/public-source-repository/examples/engineering-game/lab/contracts/`; `API.json` mirrors the emitted closed contracts. Consumers must use semantic validation as well as shape checking. Open questions are owned by [DESIGN.md](DESIGN.md#completion-and-open-questions).

## One port, one world

`BrowserPort.request(method, payload, trustedContext)` returns the application result; `close(reason)` revokes the channel. Events are obtained through the bounded `game_events` method. Trusted context contains authenticated actor/binding/channel identity, never supplied inside the model's payload. A test binding exercises this port against the real kernel without opening a listener. A fake independent world is not actual-tab acceptance.

Every request is checked for byte bound, closed schema, actor binding and exact target. `game_snapshot` alone can resolve an omitted target from the sole binding. A second binding/attachment is refused. Before pairing exists, the future companion may report unavailable; it must never fabricate instance identity. Protocol framing/version errors belong to the selected MCP SDK; domain denials use the application envelope.

## Registry and action outputs

Registry entry: `id`, input schema, output schema, required scope, declared host effects, handler binding, generated/host provenance references, logical-job expansion, output bindings, read-set dependencies and allowed plan position. Compile UI availability, port validation and MCP schema emission from this entry. All site/control identifiers are allowlisted registry IDs; inputs never name an arbitrary handler or source path.

| Action | Explicit inputs | Output / semantics |
|---|---|---|
| collect | actionKey, component kind | Owned carry handle; no installed component yet |
| assemble | actionKey, kind, named site and rotation | Installed part handle; several stages inside one job |
| place | actionKey, explicit carry reference, site/rotation | Consumes owned carry, produces installed part handle |
| return_carried | actionKey, explicit carry reference | Releases only identified owned custody |
| connect | actionKey, exact typed endpoints | New wire incarnation handle |
| disconnect | actionKey, wire handle | Removes exactly that wire incarnation |
| move / rotate | actionKey, part handle, site/rotation | Preserves installed identity; temporary custody is recorded |
| return | actionKey, installed part handle | Removes part and declares attached-wire effects |
| set_speed | actionKey, part handle, desired setting | Desired state, no accidental increment/toggle |
| operate | actionKey, allowlisted control, conditional arguments | Desired-state/control-specific typed result |

There are eleven variants (move and rotate are separate). `createdBy` references only an earlier actionKey and a compatible output type. Carry references and installed part references have distinct schema definitions even when their surface shapes match. Reject duplicate action keys, forward/cyclic dependencies, already-consumed carry, mismatched output types and implicit use of another actor's gripper. Prior completed collect custody may transfer to a new operation only through an exact still-owned carry handle, atomically; revocation cleans up loose owned custody before the human edit. Cleanup of a lifted existing part uses its recorded return position/identity, not deletion of an installed human asset.

Every action lowers to one logical queue job; stages do not consume additional queue slots. Agent admission requires an empty queue, idle PIP, no foreign custody and stopped experiment. The whole plan reserves at most twelve jobs atomically. Within-plan projection is required; general queue-prefix planning is deferred.

`run`, `reset_trial`, `restore_assembly`, `next_contract` are standalone. Schedule/run/badge wrappers set a desired state. Mission changes bind the exact next mission ID calculated at preview; restore binds archive ID/revision/digest. The registry interpreter, not a late “latest item” lookup, supplies those resolved arguments to the effect handler.

## Result and observation shapes

All results include `ok`, nullable exact `target`, nullable `versions`, `freshness`, `data`, `error`. Success has non-null target/versions, typed data and null error. Failure has null data and a typed error; unavailable replies have null current versions, never fabricated zero versions. Optional last-known metadata is labelled stale. Contradictory combinations are rejected by emitted schemas.

M01 emits a distinct closed success DTO per tool from these required fields. Domain values reuse actual compiled/profile shapes rather than a second hand-invented model. Schema fixtures include one success, every applicable failure shape and negative examples for every discriminator.

| Tool | Required success DTO content |
|---|---|
| game_snapshot | `capture` (capturedAt, age, target, versions, build/source/profile identity, eventCursor); requested `facets`; typed world/queue/guide/presentation/catalog facets; generated findings tagged with capture |
| game_inspect | Discriminated subject and matching typed facts, source/provenance references, capture and nextCursor/null; part→handle, port→handle+port, control→controlId, model→declarationId, guide→current guide |
| game_options | Subject handle, available and blocked typed choices, explicit reasons, relevant capture and reservation/custody state |
| game_preview | previewId, normalized action digest, expiresInMs, executable flag, per-action predicted output/effects, read-set token, blockers and capture; unknown prerequisites are non-executable |
| game_propose | proposalId, revision, proposer provenance, normalized preview/digest, draft state and expiry; does not enqueue PIP |
| game_execute | operationId, lifecycle, admission receipt and queue references, initially accepted; never a fabricated completed result |
| game_operation | operationId, origin/actor, lifecycle, last controlSequence, committed effects, pending/failed remainder, domain findings and cause/capture; requestId lookup is actor-scoped |
| game_events | ordered bounded typed events, nextCursor, hasMore and snapshot/cursor recovery information |
| game_control | operationId, accepted/current controlSequence, resulting lifecycle and control generation; older sequence yields CONTROL_SUPERSEDED with current state in structured error details |

Snapshot and journal high-water cursor are captured together. Event recovery reads a new snapshot and continues after that cursor. Cap responses by both entry count and serialized bytes. Cursors bind target, epoch and page/query semantics; altered/stale cursors fail, they are not offsets into arbitrary resources.

`lifecycle` is accepted/running/paused/blocked/completed/rejected/cancelled/failed. Completed, rejected, cancelled and failed are terminal. Failed means an unrecoverable execution failure; blocked preserves a reason and can be resumed after current checks. Proposal states are draft/accepted/rejected/expired. Effect summary describes committed action/stage effects and remainder independently of lifecycle. Observation unavailable/unknown never changes an authoritative operation's lifecycle. A completed interlock test may have a false domain predicate; guide predicates and human acknowledgment are separate.

## Admission, control and storage

One browser turn performs accepted-request lookup, validation, ledger insertion, custody reservation and whole-plan enqueue with no await. Dedup key includes exact target/epoch, trusted actor, method and requestId; canonical digest includes the full immutable input, not only action bytes. An existing accepted key/digest returns its receipt before preview-expiry checks. Changed payload conflicts. Rejected pre-admission calls do not consume retained receipt rows and do not promise replay of a prior rejection. Re-previewing changes the payload and requires a new request ID; retrying an uncertain accepted request uses the original ID/payload.

The retained capacity applies to **externally retryable effects**, including proposal/acceptance identities. At capacity, refuse new such admissions without evicting accepted identities. Ordinary local human jobs/controls remain available using bounded active/history records without cross-call replay guarantees; capacity must not disable play. Human-sponsored proposal acceptance can fail at that cap; manually issuing an ordinary human task still works. Human stop and authenticated owner pause/cancel also remain available.

Controls do not allocate admission rows. Each retained operation keeps one high-water controlSequence, last canonical control digest and last result. Equal sequence/equal digest returns that result; equal/different conflicts; lower is CONTROL_SUPERSEDED; higher applies the desired state after authorization. Reads expose the high-water value for recovery. A completed/cancelled/failed operation cannot resume. Pause/cancel checks authenticated ownership even after Assist revocation; resume additionally checks current Assist grant/controlEpoch and all current preconditions. No blanket Assist check may pre-empt the safe-control branch. Invalid authentication never bypasses checks.

Human acceptance of a proposal uses a trusted `(proposalId, revision)` acceptance identity and fresh human-sponsored preview/admission. It preserves attribution without granting Assist. Edited or expired proposals revalidate; duplicate acceptance returns the known operation. Human acceptance while PIP is busy reports the blocker rather than cancelling human work implicitly.

| Bounded store | Count and bytes | Overflow / expiry |
|---|---|---|
| External accepted receipt index | 1,024 records, 32 MiB total, max compact record 32 KiB | Reserve upper-bound footprint before admission; refuse new external effects, retain identities |
| Previews per actor | 16 entries, 1 MiB, 30 seconds monotonic TTL | Eviction/expiry makes token EXPIRED_PREVIEW; no world/queue/custody revision changes |
| Proposal tray | 8 entries, 512 KiB | Refuse new drafts at capacity; retained acceptance identities stay separate |
| Events | 2,048 entries, 2 MiB | Drop oldest with cursor boundary; expired request returns RESYNC_REQUIRED |
| Logical active PIP jobs | 12 including active job | Reject whole agent admission, never append a partial plan |
| Payloads | Request 64 KiB; response 256 KiB; event page ≤100 | Reject oversized request; page responses by bytes, never silently truncate a committed outcome |

M01 defines compact receipt effect summaries so each admitted plan's reserved bound is sufficient; do not retain whole world snapshots per effect. Body/digest parsing and output byte enforcement must happen at the shared port as well as the bridge. Event loss does not erase operation outcomes. Resource reads are allowlisted declaration/page queries with no path traversal.

Operation ledger/control generation/handle allocator stay outside undo snapshots. Restored objects get fresh handles. A shared session selects a new save branch before its first save and never automatically merges back; branch selection applies to all saves after disconnect. Browser storage failure must be visible and exportable; no cross-crash operation-receipt guarantee is inferred from a successful ordinary save.

## Authority and adversarial text

Human edits revoke the assisted writer before applying the edit. All stages and worker commits check their operation cause, current control generation, lease and current resources; stale callbacks lose. A standalone run retains production ownership until actual goal/bound/blocked/stop. Pause/cancel revokes pending worker generation. Visibility/notebook pauses are distinct from takeover and must not auto-resume revoked work.

Render proposal reasons, model labels and imported source text with literal text nodes. Validate fact references against the captured allowlisted model/build. Agent text never changes scopes, supplies a trusted actor, invokes a handler or proves a predicate.

## Version assertions and proposal observations

`game_preview` compares the caller’s expected `graphRev`, `queueRev` and `controlEpoch` to the current capture. A new `game_execute` admission compares the same fields to its reviewed preview capture, then revalidates the preview’s relevant state. `worldRev` is diagnostic here: learning-only interactions can advance it without changing the planned inputs. Exact target/build, resource incarnations, custody and relevant business state remain checked. Accepted request replay happens before preview or version checks and returns the original acknowledgment.

The optional event fields `proposalId`, `proposalState`, `proposalRevision`, `proposalDigest` and `proposerActorId` identify proposal changes without conflating them with operation lifecycle. Operation observations also expose optional `proposalId`. Model resource queries accept only the documented `view`, `operation`, `declarationId`, `cursor` and `limit` fields; instance and epoch path components are URI-encoded.

## Open questions

See [DESIGN.md](DESIGN.md#completion-and-open-questions). DTO extraction, shared commits, actor policy, owned operations, observations, preview, proposal acceptance and nine handlers are implemented. Their consolidated functional record is [VALIDATION.json](/home/vlad_/projects/cyberAlchemy-v2/goals/plans/craft-game-shared-mcp-2026-10-29/VALIDATION.json). Actual-tab transport and intended-host interoperability belong to deferred D01–D03; offline checks do not establish that boundary.
