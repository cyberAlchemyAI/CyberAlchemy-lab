# Integration, operator and security plan review

Disposition: changes requested. No P0 finding; three P1 and three P2 findings below. This is an independent read-only implementation/plan review followed by writing this review file only. No runtime checks, live service probes, private credential reads, admission or frozen source edits were performed.

Reviewed draft: `PLAN.md` SHA256 `8cbe846a626ba97db6e5643360dc3922743280c4902f3c5242004ffde67bd54b`; `dag.json` SHA256 `e90b697b6f67f2f1b7615ab2fc6acc88eaea9c0464410da795d8c3ece8ac1647`. These identify the reviewed draft, not any subsequent reconciled version. The detailed code/evidence map is [integration-operations.md](../analysis/integration-operations.md) and [integration-findings.json](../analysis/integration-findings.json).

## P1 — R1: The planned positive Source8 lifetime uses an already expired original fixture

Affected tasks: T02, T03, T05, T15, T17, T22. [T03.md:13](../work-pack/tasks/T03.md) selects the actual Source8 Context and lease, and line42 requires completion inside its original applicable lease. T02 presently addresses constructor identity and period selection but declares no new signed Source8 Lesson/applicability/review fixture family. The selected immutable `source8-lesson-fixture-source-v4-action-0148/episode-contract.json:7` and `packages/0001/fixture-applicability.json:4` expire at **2026-10-13T06:58:55.567340+00:00**. The earlier derived original Lesson also has its own earlier expiry. Correct clocks now make positive use of these expired bytes impossible. An optimization cannot cure the missing current authorization.

Fix: extend T02, or introduce an explicitly dependent fixture task, to construct and qualify a **new distinct signed source, reader, mapping, Context and Lesson/review/applicability family** with an independently selected current finite period and exact source/schema/native proof. Preserve all original bytes, keys, periods and expired/inapplicable refusals as historical negative inputs. Record explicit derived-target/identifier correspondence instead of calling the new fixture the original Source8 or relabeling its Lesson. T03/T05/T17 select this new current family by exact bindings; preserve the original duration and callback semantics and measure the full real lifetime. Genuine T22 learning still requires actual new failure and later Work evidence, not this controlled fixture. T15 must freeze the new dependency/origin closure before qualification.

Acceptance: causal positive on the distinct current family plus original-expiry negative; no clock patch, old permission renewal, invented review/human outcome or qualification transfer.

## P1 — R2: Composite configuration does not implement the missing durable operator provisioner

Affected tasks: T06, T07, T19, T23, T28. T06.md:21-25 describes three-branch startup from existing independent grants; its prospective outputs at35-36 are a launcher and configuration contract. T07 focuses on dependency discovery. T28.md:19-20 eventually executes authorized provisioning, but no pre-freeze task implements and qualifies that actual operator provisioning path.

This is a factual implementation gap: `implementation/lab-provisioning/candidates/v1/provision.py:46-51` accepts only candidate role/category/effect scope; lines54-79 own a disposable TemporaryDirectory/key and replay the legacy v2 engine. It cannot be promoted to real persistent operator setup by configuration. API16 `auth.py:43-46` independently requires an owned0600 policy **under /tmp**, outside the repository, and an exact raw-byte hash. The approved Paperclip technical wrapper used separately retained private custody and fresh per-invocation staging; it is not a general three-channel provisioning implementation.

Fix: add a versioned provisioner/custody/staging contract and implementation scope to T06 or a separate predecessor of T15/T19. Explicitly select actual independently authorized operator/principal/store/Project scope, persistent private ownership0700/0600, key outside native store, public key binding and rollback custody. Decide whether a new selected policy contract accepts durable private custody directly or preserves /tmp via fresh exact staging with original-custody revocation watch. Do not rewrite private policy fields merely to satisfy a path guard. Define all three independent channel grants and workspace/store selections, read-only versus effect scopes, reopen/cold native verification, expiry, revocation, cleanup and interrupted setup. The candidate fixture provisioner remains separate. Implementation can be tested with isolated technical credentials; actual persistent setup still requires the exact represented effect authorization at T28.

Acceptance: fresh installation can provision and launch the selected full34 composition through this versioned path, preserving source/policy currentness on restart, refusing unsupported scope and never reconstructing ActiveSession RAM. T28 executes a previously qualified implementation instead of inventing it after the final owner checkpoint.

## P1 — R3: Security acceptance lacks an explicit independent branch matrix

Affected tasks: T06, T17, T18. T18.md:15-17 anchors Machine/termination/workspace only, and line53's selected Machine/auth/session cases do not enumerate Action and Governance authentication. General wrong-signature/nonce/revocation wording at21 could be satisfied on one channel while the new full34 launcher routes three distinct policies. IntegrationService checks exact branch module/source/profile and shared Schemas at `integration_dispatch.py:17-28`; routing context is merely a locator at43-50. Branch policy and nonce authentication remain distinct obligations, not inherited from a base or Machine PASS.

Fix: specify a producer-bound matrix for Base Reader, Action3, Governance4 and each selected Machine parent family. For each applicable channel preserve original raw challenge/proof signature bytes, challenge consumption, fresh/wrong key, replay, live policy revocation, real expiry at authentication and dispatch, exact public shared profile versus private source scope, independent Actor membership and unchanged selected callback identity. Test cross-branch signature/context/proof reuse and branch-owned operation.inspect/journal ownership through the maintained launcher. Include missing/conflicting independent context, malformed/oversized frame and private payload refusal with exact transport schema/code/digest and no effects. Add actual Action/Governance host/channel/service origins and independently pinned policy construction to the task's inputs and selected case inventory. Unavailable branches are honest refusal evidence, not full34 availability proof.

Acceptance: the final same-family security aggregate explicitly accounts for every applicable branch/case and actual OS exit, full guards and owned cleanup. Passing a Machine suite alone cannot close three-channel authentication.

## P2 — R4: Unknown final owner targets unnecessarily gate the entire technical freeze

Affected edges: T13→T14→T15; T15→T16–T21. T13 correctly stops when unknown owner Decision bytes participate in a semantic target digest. T14 currently requires every T10/T11/T13 target before the execution-family freeze. Consequently D01's unresolved final-target design stops fresh transport regression, dependency installation, documentation and even read-only qualification, although their executable contracts can be selected independently of actual final owner outcomes.

Fix: split accepted **publisher implementation/typed adapter/recovery-contract evidence** from the **actual final-instance target closure/rehearsal**. T15 must include and pin every executable/schema adapter used by the chosen API; it must not quietly omit needed recovery code. Require the fixed whole final target instance and every88-target owner-core disposition at T25, before T26. Permit earlier scoped technical freeze/qualification only when its own complete selected fixtures and source closure are independent and explicitly exclude the unavailable final instance. If the dependency is genuinely executable, retain it and document the concrete code/schema reason rather than treating every package target as an execution dependency.

This is scheduling overblocking, not permission to approve a partial S02 or transfer technical results across revisions. Changed source/targets invalidate their dependent evidence normally.

## P2 — R5: Launch concurrency and shutdown ownership must be selected before security qualification

Affected tasks: T06, T18, T19. Existing stdio `serve.py:55-60` is serialized; Machine owns a state RLock in `machine_transport.py`. Base Reader nonce consumption and Service call-ID/max-call accounting have no equivalent explicit locking in the inspected methods. This is not an observed bypass: the existing serialized process can uphold that boundary. A new composite adapter or Paperclip supervisor must preserve it or prove a different concurrency contract.

Fix: declare serialized per-connection authentication/dispatch as the default maintained transport, or implement and qualify atomic nonce/call-ID/budget and workspace effect locking for a documented concurrent transport. Include concurrent same-proof, same-call-ID and same-effect-key probes only if concurrency is actually exposed. Cover EOF, interrupted startup after one branch authenticates, handler refusal, BaseException shutdown and independent branch/borrower disposal; close an owned Machine without disposing its borrowed parent. Specify ephemeral resource loss on restart and no metadata-based resurrection. Do not assume thread-safety from independent branch policy hashes.

## P2 — R6: Final privacy must cover material authored after T20

Affected tasks: T20, T21, T22, T23, T25. T20 binds the frozen execution package, while maintained docs, actual work/learning, authentic pilot receipts and final target/evidence manifests are authored later. T25 already asks for a whole-bundle carrier/privacy check, which is the correct final gate; make this explicit as a newly bound selected inventory instead of implicitly treating earlier T20 R06 closure as covering unknown future bytes.

Fix: have T25 select every later public/protected target and evidence member, rerun the applicable original R06 boundary checks/currentness for that exact final inventory, and preserve private operator custody/DB/logs outside source/public snapshots. Distinguish unchanged execution-family conformance from changed final-bundle conformance. Any later byte change invalidates the affected boundary proof and owner target binding. Documentation live status updates must remain outside frozen runtime/owner cores, with explicit links to the selected immutable evidence.

## Correctly modeled boundaries to retain

T13's D01 stop and T25's stable unsigned target/core → observed evidence → later real owner response layering correctly avoid fabricated Decision bytes and digest cycles. Retain the full target/native predecessor/owner-role/effect/base-State matrix, all original363 members plus explicit additions, realistic final-instance crash/cold replay, and actual role prerequisites. T26 must receive the **fixed exact** reviewed target instance. A later owner response that changes target semantics cannot be hidden in an envelope; it requires the actual declared revision/review route. T27 admission remains distinct from T28 operation and T30 release.

The full34 dispatcher is present, while the maintained `serve.py:46-53` selects only the base service. T06 correctly calls for a maintained real composition rather than claiming test-only assembly is an operator interface. T17 correctly binds all34 positive/causal negatives to one actual family and keeps release.prepare conformance distinct from real release. These corrections should remain.

Worker9 cause calibration is also correct: exact same-case raw observation `api-integration-v16/receipts/per-call-observations/0cb8537fd64e4bdea5ec9b18a9e64a89.json`, SHA256 `66ef5cfabb93929102f87ef2e8ff8765dfffe21154563e8ec4b1193b63542124`, binds `_cal_final_api_0173_worker_9.test_machine_transport.MachineTransport.test_02_all_seven_public_read_operations_with_actual_Actor` and profile16 to **integrity-failed**. The static Legacy/custody exact-class mismatch is confirmed, but no retained causal trace proves which throwing guard produced that reply. The earlier successful parent-context observation and earlier API14 fixture setup failure are distinct evidence. New causal tracing must not overwrite or misattribute them.

## Recheck requested

Reconcile R1–R3 into task inputs, ordered rules, scopes, acceptance and DAG/SWU mappings; disposition R4–R6 explicitly. Then recheck the updated exact plan and task hashes. No implementation execution approval or runtime qualification is supplied by this review.


## Revised-plan recheck — PASS for planning coherence

The revised35-node/72-edge draft resolves R1–R6 within the integration/operator/security review scope. No remaining material P0/P1/P2 integration issue was found. The original findings above remain as the historical review; this recheck applies only to the exact file hashes listed below. It does not establish runtime readiness, qualify API16/a successor, authorize execution, or supply actual human/role/admission/release evidence.

- **R1 resolved:** T02 explicitly creates a separately authorized and signed current Source8-equivalent source/native reader/mapper/Context/runtime/Lesson/applicability family with new identities; it preserves expired originals and original duration/budget rules. T01 depends on T02, and T03 acceptance selects the current independently authorized lease. T15 binds the successor family before final qualification. Genuine T22 Work remains distinct from controlled fixtures.
- **R2 resolved:** T34 implements the missing versioned operational provisioning/custody-to-private-staging path and origin/ownership/no-follow/preimage/currentness checks, fresh nonce on restart, revocation and uncertain-operation reconciliation. It preserves CandidateScope and makes actual admitted setup wait for T28. T06 now depends on this implementation; technical rehearsal is explicitly isolated.
- **R3 resolved:** T18 requires separate Base Reader, Action, Governance and Machine matrices with real wrong-signature/replay/revocation/expiry/Actor/source/profile causes, cross-branch proof/context/signature refusal and exact effect-state evidence. T17 retains all34 positive/causal-negative same-family qualification through the maintained composition.
- **R4 resolved:** T14 depends on executable publisher/proof/environment/owner-adapter contract closure, rather than all final T10/T11/T13 semantic targets. Its explicit last rule limits this stage to executable/adapter closure. T25 still requires every final member/target/owner/effect/base-State binding, full realistic heterogeneous rehearsal and D01 disposition before T26. Technical decoupling does not narrow final S02 acceptance.
- **R5 resolved:** T06 explicitly serializes stdio nonce/call-ID/budget/dispatch; it specifies bounded framing, EOF/partial-frame/error handling and deterministic owned-resource shutdown. T34 rebuilds fresh authenticated channels instead of restoring RAM or consumed nonces. Any later concurrent transport is outside this selected launcher contract and needs its own implementation/qualification.
- **R6 resolved:** T20 is now preliminary runtime privacy before the pilot. T25 explicitly closes final R06 over all late docs, actual Work/learning, authentic observations and materialized package bytes, with admitted-operation obligations retained for T29/T30.

T33 also closes the previously fixture-only owner-response adapter gap at the plan level: actual human message identity/content must be bound to independently selected trusted host evidence and current governing authority. Caller flags, an agent payload and possession of a fixture key confer no R08 authority. An absent trusted host mechanism is an explicit external prerequisite. Technical positive fixtures do not substitute for the actual approving outcome, which remains absent until T26.

The revised T25 names separate digest domains for immutable execution, unsigned semantic targets/Decision cores, exact rehearsal input, observed evidence, review envelope and later owner response. Receipts bind fixed input cores rather than a future enclosing manifest. Original schemas and D01 must still be proved during implementation. If real Decision bytes change target semantics, execution must stop for the declared revision/owner route; this recheck does not presume that representation issue is solved.

Actual authoring checks in this recheck:35 unique nodes,72 unique edges; edge set equals declared task dependencies; graph is acyclic; all35 task contract paths exist;35 task-local SWUs exist. The reviewed changed task contracts, execution policy and layer model agree with the corrections. No full suites, source-currentness/runtime checks, native calls, live health probes, credentials or effects were used.

### Exact reviewed revised file identities

| File | SHA256 |
| --- | --- |
| `PLAN.md` | `444f8eb4c743af85190803079bb59a9c18d1b4f87639fc3dfe0b9107b03244e3` |
| `dag.json` | `3c982f390a945c349372d2f30d3dad9483d5eabb0081ff3a8b30c4be43340653` |
| `DAG.md` | `9490f92da68dec40942b39c67f05aa23b2c6aab67184cc9ffa31d93638ab9099` |
| `WORK-PACK.md` | `6cf416cf3c07b8477fbcc5495513fa0b4a757d13b27cebabe14b793658eb463a` |
| `EXECUTION-PACK.md` | `827cdc097326b0cb5fc9a7c4332f979554b6c30cdafbb776d873bb95df3e8654` |
| `IMPLEMENTATION-LAYERING.md` | `589b452e205cd07297326a5dc47c8bf343d7558465fc8cb5c127419ced81c264` |
| `swu-manifest.json` | `311f1c0b2f777b983d6ab5c6e92506f66b65a50f691992b15d95046ce73d9249` |
| `work-pack/tasks/T00.md` | `e132504120873c9eb45b857ed0d36b2f0497801ef5ea5cd92c699144a42e3487` |
| `work-pack/tasks/T01.md` | `dfa60ca91c0a1d39227ad7b84ceb08dd18c3ecc005a4e48b75030c231aea6f4d` |
| `work-pack/tasks/T02.md` | `e1b6341c2c47ab303febdd19c9e5aaeeeb51e79cba172af5c96c2fc8e95548e0` |
| `work-pack/tasks/T03.md` | `c20c4b25ca11f5dffa3ea1bb66992fe7837d0b391da44277114c62ed4374d6b5` |
| `work-pack/tasks/T06.md` | `8a70b1650f14c5ee5219a41dbd94f258f4051d52d727d34a041d5a4a10a46c86` |
| `work-pack/tasks/T14.md` | `0f4dea3a49ef8fe880d9bdff1222869b071dacb1b4dc6c761b7f1a6244fe5e32` |
| `work-pack/tasks/T15.md` | `0b43699289ecd80dadad21c30b9978b141aa6a55c78cc786faf9db3fbd95b668` |
| `work-pack/tasks/T18.md` | `292ceaac859bd1d9267b148bd8751e11252841c71d7f14b53fbb1fbc03fb8d60` |
| `work-pack/tasks/T20.md` | `8a5a7da6539f9569a92a0c6bb06afae8cd320195eff5d1e91f638e2f548558a3` |
| `work-pack/tasks/T25.md` | `3407a7c8524b9c9e5fe63465d90b712449096aa43ceac6a4243e53e6f6ba983b` |
| `work-pack/tasks/T33.md` | `1750a1803c28998bc90ee351460e644f61a9980c55ea5e962b868c07312d0e3e` |
| `work-pack/tasks/T34.md` | `2f35cd1884bd285515f8b2d92636858199c06de8b37a24d243d8ea47a8b684e4` |


## Final artifact refresh — PASS for planning coherence (36 tasks)

The current **36-task/36-SWU/73-edge** draft remains coherent within the integration/operator/security review scope. No remaining material integration issue was found. R1–R6 remain resolved. This final refresh supersedes the previous reviewed identities for the current draft while retaining both historical reviews intact.

The new dependency partition is correct: T01 Machine diagnosis and T04 caller refusal handling can begin independently after T00; T35 requires T02's separately signed current Source8-equivalent family; T03 consumes T35's actual phase attribution. The original Machine raw integrity-failed lineage and static exact-class incompatibility remain distinct from an unobserved causal exception. T05 now explicitly selects the exact Legacy/custody generation-helper boundary and conditional versioned origin correction, preserving the old helper and wrong-origin refusal.

T00/T02/T15 and EXECUTION-PACK now distinguish **24h source validity**, **at most30min independently authorized reader grant**, and **at most900s live Session**, always subject to the actual strictest source/assignment/grant/resource deadline. Development diagnostic instances cannot be promoted to indefinitely live final fixtures. Final source construction/freeze is just in time after assembly, measured qualification cost and actual pilot availability are known. Fresh per-attempt credentials are permitted only by an independently selected contract under a still-live source; lapsing immutable source/contract rows require a new frozen family and affected source-bound qualification. Old periods, unsuccessful attempts and expired-source negatives remain unchanged. This is a credible scheduling rule, not proof that a future workload will fit. Actual elapsed costs and availability remain execution measurements.

T03's pure-scope invariants and adversarial substitution/tamper/nesting/exception/revocation/expiry/effect checks now cover the proposed optimization boundary explicitly. Its read scope ends before derived evidence writes and durable Tool/journal claims, with full fresh entry/exit and effect preclaim/posteffect checks retained. T22 requires actual consuming Lesson dataflow or observed later behavior and independently assessed outcomes; metadata correspondence alone cannot prove benefit. A needed producer change returns to successor freeze and affected requalification.

T06/T18/T34 still preserve serialized transport, independent Base/Action/Governance/Machine authentication, exact profile/source/origin binding, cross-branch refusal, durable private custody and fresh nonce staging/restart. T14 technical executable/recovery closure remains decoupled from unresolved final semantic targets. T25 still owns complete fixed target/member/owner/effect/base-State closure, late-payload R06, separate acyclic digest domains and the original schema/D01 stop. T33 actual trusted human ingress and T26–T30 role/owner/admission/operation/release obligations remain external execution gates; planning review supplies none of them.

The updated ANALYSIS and finding/operation coverage keep all34 operations and bounded code/evidence conclusions visible. The root reconciliation and validation report explicitly distinguish plan checks from runtime qualification. Independent read-only checks in this refresh verified36 unique nodes,73 exact declared dependency edges, acyclic topology, all task contract paths,36 SWUs and the listed revised dependency frontiers. The inspected existing validation.json records PASS with576 source-preservation hashes,265 links,46 original tasks,63 original SWUs,13 acceptance conditions,34 operations,10 implementation areas and33 audit findings. That source/link validator was **not rerun by this child**; its exact observed artifact identity is below. No runtime suites, native execution, live health or private credential inspection occurred.

### Exact final reviewed artifact identities

These hashes describe the files observed at this refresh. Subsequent reconciliation/status or validation changes create different artifact identities; this review does not claim they were already observed.

| File | SHA256 |
| --- | --- |
| `PLAN.md` | `2e3dabea1f087e826102c13a3692f25052541fb2fcd2ab311d7f78f3cca99e8d` |
| `ANALYSIS.md` | `be37f0c17c164002d26c0edd9c1622a5ca1d71a74bb17c6a1ee07656ad141713` |
| `dag.json` | `08057d59234a0cae280091c322b58c7ded9710f2a01499d69fe841a0e91e2dfe` |
| `DAG.md` | `9e6088d892219984a5af6c0d6d06ca85d5bfb418dc24553ffb09c47185a353a9` |
| `WORK-PACK.md` | `ee5c1ef95632443e7b4b360d568fb51134f65a5efe641bc74bc3b66e1402885b` |
| `EXECUTION-PACK.md` | `113898b7e63cd3d9fbbdb7f9a5de47579dde6dd3e280ac0ca30e7d80cc9a6a79` |
| `IMPLEMENTATION-LAYERING.md` | `471c44565e44fda5b7cdcf743e024d05b434b6b84f5275b69fd5b3dcd4739be2` |
| `swu-manifest.json` | `5086654713692e6ded6dc1cd7bafde7b87d90f3a41def4ec4eba8a1b4c10fdfd` |
| `coverage.json` | `10d3264a0727656ef34d913d956ccccd5faecfa0afdd8bdf53b48b45303b3b75` |
| `finding-crosswalk.json` | `d7ea44755de877b40d19af4834d2752abe5761aff8f4043c086c35750d6ec291` |
| `obligation-crosswalk.json` | `0061c238925552da5603254a1aabc32596dbb33dfc1170162d9e8e09b0a52e66` |
| `SOURCE-BASELINE.json` | `601f86723d0c1223e4b4ccdc42de795f7357991f94852f5db393f149b9ce2b8f` |
| `REVIEW.md` | `ed68041bb805cd0d887a20a3b3ee2c4d69e673cb3775b8bee9a0c73d411a0a61` |
| `validate_plan.py` | `4dafe96413b1022665548a78aacf8bb4c5c772abf0513e2cc424f21d0620a890` |
| `validation.json` | `8dff7378d3608d1412482f8558b5a56854ae2ab8babae392100acd07854c5158` |
| `work-pack/tasks/T00.md` | `40edf523d68237e6fb6f753ae6b4dedf6c3c0bd51fbf9515c0da84f9990ef67c` |
| `work-pack/tasks/T01.md` | `b501d36fe1f90301f60ae9745fd2a4c32e83f86fbe3a42583568e12e87ae8e62` |
| `work-pack/tasks/T02.md` | `1693567f829dca348aaf4628f41328242e35147d3e6c3d5c684f8c66eb12e8c5` |
| `work-pack/tasks/T03.md` | `83bbc5f3d3c378b6cd74e3dc007dc776ddf9679d3836b6c0d63e31beebc01cbf` |
| `work-pack/tasks/T04.md` | `bca2942bebe3a44797027811bdca14ccdebe2956060943fb04034d924dd00562` |
| `work-pack/tasks/T05.md` | `70da2e2a34d8198514172ba81d226398fb16df97ec580e3a03cc83b5ebfbac0f` |
| `work-pack/tasks/T06.md` | `8a70b1650f14c5ee5219a41dbd94f258f4051d52d727d34a041d5a4a10a46c86` |
| `work-pack/tasks/T14.md` | `0f4dea3a49ef8fe880d9bdff1222869b071dacb1b4dc6c761b7f1a6244fe5e32` |
| `work-pack/tasks/T15.md` | `6d88d148887b4be8a40a5ef05682015c672acae5f14688be272d0534b8e85c43` |
| `work-pack/tasks/T18.md` | `292ceaac859bd1d9267b148bd8751e11252841c71d7f14b53fbb1fbc03fb8d60` |
| `work-pack/tasks/T20.md` | `8a5a7da6539f9569a92a0c6bb06afae8cd320195eff5d1e91f638e2f548558a3` |
| `work-pack/tasks/T22.md` | `1fd4e7289898130eeeb1de45c4d50a291ababa80fb7a377edefdfdf947c395c7` |
| `work-pack/tasks/T25.md` | `3407a7c8524b9c9e5fe63465d90b712449096aa43ceac6a4243e53e6f6ba983b` |
| `work-pack/tasks/T33.md` | `1750a1803c28998bc90ee351460e644f61a9980c55ea5e962b868c07312d0e3e` |
| `work-pack/tasks/T34.md` | `2f35cd1884bd285515f8b2d92636858199c06de8b37a24d243d8ea47a8b684e4` |
| `work-pack/tasks/T35.md` | `7b363a1a7dd3f3a9d39ffa560912429765cbc3200b0c4ef73cf1eaa2836ab0bb` |
