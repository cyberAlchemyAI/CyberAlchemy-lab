# Native outputs into owned workflow journals

Keep the original strict workflow kernel/profile frozen. Add an explicitly
private, host-selected `owned-produced-current` variant. It coordinates exact
local fixture outputs; it grants no repository admission, Work satisfaction,
runtime capability, real owner outcome or permission inherited from old Sessions.

## Exact original workflow requirements

| Original transition | States | Required output carriers |
| --- | --- | --- |
| `agent-context:context-ready` | requested → context-ready | ContextView/v1, OntologyView/v1 |
| `agent-context:session-ready` | context-ready → session-ready | AgentSession/v1 |
| `challenge-handling:eligible` | submitted → eligible | ChallengeEvent/v1 |
| `challenge-handling:responded` | eligible → responded | ChallengeEvent/v1 |
| `challenge-handling:resolved` | responded → resolved | Decision/v2, ChallengeEvent/v1 |

AgentInstance/v1 is useful native evidence, but is not required by this original
agent-context transition and is not in the 33-output-carrier catalog. Do not add
it to the transition's exact required output set or rename the original states
to prepared/active.

## Actual body inventory and capture

1. `current_legacy_context_sessions.ContextSessions.view_get` stores all generated
   originals in its actual Vault and puts ContextView/OntologyView ArtifactRefs in
   the successful `context.get` reply. The existing `AuthorizedAPIProducer` in
   `workflow_api_outputs.py` can walk those refs and preserve their exact bytes.
2. `session.open` constructs actual `LiveReader.agent` and `.session`, but returns
   an AgentSessionResult with identifiers, not formal ArtifactRefs. The formal
   Session body has never been emitted as its own native Vault object. A trusted
   private first-emitter adapter must validate the actual live resource/result,
   source cut, grant, scope and UTC; serialize the exact constructed formal body
   before disposal; validate its original AgentSession schema; then commit its
   derived ArtifactRef through OutputJournal. Label first encoding accurately.
   Never read or persist `resource.memory`, notes or RAM snapshots. The existing
   OriginalCarriers AgentSession branch already permits the original formal
   `session_memory` reference arrays; it does not permit actual RAM memory.
3. Successful native `challenge.submit` returns a ChangeProposal whose target
   content points to the exact ChallengeEvent bytes in the producer Vault.
   Its response state is open. Actual executed eligibility plus that unchanged
   event can support the eligible step; do not rewrite it to pretend another
   native state. Preserve original request, result, claim and event hashes.
4. API64's signed response capsule is a genuine bounded fixture response, but it
   does not emit a standalone responded Event. Its final deferred Event is not
   that missing phase. Produce a distinct responded successor only after exact
   authenticated response/obligations checks against the committed eligible
   event. Existing `workflow_response_outputs.py` has a useful phase scaffold,
   but assumes a Source-current Principal challenger/RoleAssignment; its exact
   type assumptions need an explicit Agent-origin fixture variant.
5. API64's Decision/v1 capsule does not satisfy the resolved step's Decision/v2.
   A new schema-valid v2 producer must preserve the actual fixture defer outcome
   and its signed inputs, with `actual_owner_outcome=None`; do not relabel v1.

The API71 runner is retaining private existing Vault view originals and explicit
first encodings of the actual formal Session/Agent objects before close. Its
public receipt must say `WorkflowRun_committed=False` until the adapter/journal
steps below actually execute. These captures are inputs, not completed T31 proof.

## Smallest implementation delta

1. Add a disjoint owned-currentness kernel/profile. In the selected successor of
   `workflow-transition-v1/kernel.py`, retain all original template states,
   carrier sets, obligations, actor/scope/cut checks and no-completion flags. Add
   explicit proof categories `signed-source-current`, `owned-produced-current`
   and `owned-coordination-current`; never translate the latter two to admitted.
   Original Source semantic refs still use the original exact Source resolver.
2. Add `workflow_owned_currentness.py`: resolve derived inputs only through this
   owned journal's committed HEAD/transaction and producer invocation. Verify
   exact original bytes/schema/header, scope, Source cut, Actor, Work, Run,
   producer method/source binding, original API request/reply and receipt chain.
   Recheck grant/source/UTC and those bindings at claim and every commit boundary.
   A caller-supplied output header, orphan blob or unheaded transaction is never
   current. Session output currentness describes retained lifecycle evidence;
   it never reactivates the closed resource or grants action authority.
3. Add a private scoped coordination capsule for missing IntentResolution,
   Decision, Effect and exact declares-effect-on relation inputs. Final 4636 has
   zero current IntentResolution/Delegation/Effect/RoleAssignment instances.
   Bind capsule facts to the actual Source Intent/Work/Goal/Coordination refs,
   exact Run and host-selected fixture grant; validate original schemas and
   relation signatures. Mark these as owned coordination facts, with no owner
   admission. If needed, supply similarly scoped Delegation and ContextRequest
   inputs. Do not borrow historical first-episode view/Session witnesses.
4. Add the narrow current-legacy workflow auth branch in the next API `auth.py`:
   independently selected private policy, exact final family/cut and source
   period, scoped candidate-workflow effects, grant UTC/revocation and explicit
   fixture roles. No parent Session capability/lease is borrowed. Keep the
   existing strict source families/policies unchanged.
5. Add private first-emitter/later-read adapters alongside
   `workflow_api_outputs.py` and `workflow_output_factory.py`. Select exact
   callables/control bindings before invoking native effects. The existing
   factory demands all 28 routes; the new profile should permit an explicit
   complete route subset for the selected original workflow, not fabricate
   unrelated producer slots. `guard_original_producer` currently requires an
   exact ReaderChannel; native Agent challenge uses MachinePeer. Add a separately
   constrained selected MachinePeer adapter with exact live resource, signed
   one-use grant, Actor and Source checks; never general duck typing.
6. Use the repaired durable `output_store.OutputJournal` around the original
   output journal. Commit actual originals with the exact next original
   WorkflowRun; cold replay and a distinct consumer must reopen their unchanged
   byte hashes. The initial implementation unit should complete both original
   agent-context transitions using the actual native capture, then reuse the
   same proof/journal path for the three contest phases.

Acceptance negatives: foreign Actor/Run/Work/scope/cut; another journal's output;
tampered producer or input bytes; orphan/unheaded output; expired/revoked grant;
Session close/expiry during first emission; post-write guard failure; wrong
Decision version; invented responded phase; and retry producing a second native
effect. Each must leave no new completed workflow HEAD or false output claim.
