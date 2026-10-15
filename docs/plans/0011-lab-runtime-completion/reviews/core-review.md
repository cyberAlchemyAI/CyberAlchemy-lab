# Independent core/runtime review

Disposition: **changes requested**. Review date: 2026-10-13; actual clock observed18:36:51UTC. Reviewed `PLAN.md`, `DAG.md`, `dag.json`, `WORK-PACK.md`, `IMPLEMENTATION-LAYERING.md`, `EXECUTION-PACK.md` and all33 task contracts against the six assigned implementation areas and API16 code/retained receipts. This is static plan review; no runtime tests, credentials or live stores were accessed. This review does not grant implementation, owner, admission or operational authority.

The plan correctly preserves original failures and source bytes, separates base28/composite34, distinguishes actual human acceptance, adds Workflow output support and treats native interruption as an inferred risk. T02 already lists both metadata reconstruction variants. The remaining issues are executable prerequisites and proof boundaries, rather than disagreement with those objectives.

## Findings requiring revision

### CR-01 — P0 — T00/T01/T02/T03/T17/T22 lack an explicit current Source8 source-family prerequisite

The selected [Source8 fixture period](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/source8-lesson-fixture-source-v4-action-0148/packages/0001/period.json) ends `2026-10-13T06:58:55.567340+00:00`, already past at this review. T01 requests real positive Source8 reproduction; [T03:42](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/work-pack/tasks/T03.md:42) requires a complete lifetime within the original applicable lease; T17 and T22 rely on the same source-specific paths. [T02:22–24](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/work-pack/tasks/T02.md:22) specifies fixture selectors and an independent period but contains no construction task for a distinct current signed Source8 Assignment/source/reader/mapper/Context/runtime family. T00 inventory alone cannot make the old signed period current.

**Concrete fix:** add an explicit source-family prerequisite task or separately scheduled SWU before Source8 diagnostic/positive paths. It must select a genuinely new current native branch with distinct fixture IDs/key custody/period and exact original signatures, source/store/class/module/producer bindings; independently cold-replay the new source and qualify its reader/mapper/Context. Preserve original Source5/Source8/fixture archives, periods, keys and exclusions as immutable provenance. Record all changed source selectors and expected constants in the AST ledger; never edit a period file, relabel an old SignedSources object, or derive expected origins from the imported actual module. If no new current authority/fixture selection is authorized, block only those positive paths explicitly.

Split T01's Machine diagnostic from its Source8 diagnostic so the still-reproducible legacy case can proceed independently. The new prerequisite should gate the Source8 portion of T01/T03/T17/T22 and the relevant bindings at T15, without making Machine diagnostics wait on unrelated Source8 construction. Clarify that unchanged real Session TTL/deadline rules apply to the new source; the old absolute participation period remains expired.

### CR-02 — P1 — T14 → T15 overblocks technical qualification behind package semantic/owner-response decisions

[T15:7](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/work-pack/tasks/T15.md:7) requires T14. [T14](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/work-pack/tasks/T14.md:7) requires T10/T11/T13; T13 has D01, where unknown final owner Decision bytes may prevent stable semantic target construction. Consequently all T16–T23 work is blocked behind29 representations,230 routes and88 final event-target decisions. This conflicts with the plan's stated rule that semantic/owner stops block only affected descendants, and prevents obtaining technical API repairs/latency evidence needed for genuine Work and human usefulness.

The selected API Governance branch's owned development admission proof is not the final363-member mixed-target repository publisher. Existing [GovernanceService.execute](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/api-governance-integration-v4/service.py:20) performs its independently granted native development-store operations; nothing in its call path requires every final S02 target to exist.

**Concrete fix:** make T15 the corrected **execution** freeze with its actual code/schema/host inputs. Keep T13/T14 and final package target preparation mandatory for T25 and subsequent admission, while allowing T16–T23 to proceed on the independently frozen technical family. T14 may include generic adapter/recovery construction independent of final unknown owner bytes; final-instance proof stays T25. If a publisher adapter is genuinely imported by the selected execution code, gate only that reviewed executable contribution, not materialization of every final package target. Record later changed execution bytes as a new freeze with affected requalification; do not transfer evidence across an executable change.

Likewise classify T32's selected call chains first: native read-only Context need not wait on an unselected batch-append repair. Retain a hard edge to technical freeze/security only when the selected API actually exposes that boundary; always retain the final publisher/native obligation at T25. T31's required Workflow output producer remains a technical capability dependency where imported by the full selected workflow contract.

### CR-03 — P1 — T05 must name the actual Machine generation mismatch and its independently selected helper boundary

The same-case retained [raw observation](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/api-integration-v16/receipts/per-call-observations/0cb8537fd64e4bdea5ec9b18a9e64a89.json:17), SHA256 `66ef5cfabb93929102f87ef2e8ff8765dfffe21154563e8ec4b1193b63542124`, records worker9 method02 `context.get → integrity-failed` at06:07:44.889395UTC under the exact API16 profile. [legacy_context_sessions.view_get:130–135](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/api-integration-v16/legacy_context_sessions.py:130) calls `machine_context_scope.generate`. [machine-context-scope-v1.selected:21–27](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/machine-context-scope-v1/generation.py:21) imports original `custody_context_sessions` and demands its exact MachineContextSessions type; the actual legacy type cannot pass. `generate` invokes this selector at104–105. An earlier guard could still have thrown in the retained run, so dynamic causality remains a T01 requirement.

[T05's source list](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/work-pack/tasks/T05.md:15) omits the legacy runtime and generation helper; generic “Machine/borrowed guard modules” could steer an implementer toward loosening the transport class guard or adding a filename alias.

**Concrete fix:** include the exact legacy `view_get`, wrapper and original generation selector inputs. Plan a separately selected successor helper for the actual runtime/source/producer, conditional on the causal trace. Require exact custodian/PermissionBridge/native source/parent live resource/Schemas/module-origin bindings, and unchanged pure-scope entry/exit proof and live policy checks. Do not mutate the original helper or broaden its original class requirement. Acceptance must include current legacy Machine Context success, wrong-original/foreign-custodian refusal and parent/borrower no-reconstruction/disposal checks, alongside all seven reads. Source8-specific helpers must retain their own actual origins rather than be routed through a generic label.

### CR-04 — P1 — T03 needs explicit pure-scope adversarial acceptance and effect boundaries

T03 correctly forbids cross-call caching and clock changes, but its acceptance currently reduces to full lifecycle timing and existing corruption/revocation/expiry refusals. The actual [LessonHost.guard](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/lesson-host-composition-v45-action-0148/host.py:90) repeats full host, peer, schema, vault and resource checks; [select:278–311](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/lesson-host-composition-v45-action-0148/host.py:278) opens a pure read scope, exits it, rechecks actual deadline, and only then writes derived evidence objects. [machine_auth_scope.source_facts](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/api-integration-v16/machine_auth_scope.py:88) preserves callback identity and requires registry cleanup. Performance reduction must preserve these relationships, not merely pass old broad tests.

**Concrete fix:** T01 records callback count/cost and exact nesting/source identities; T03 lists the causally affected producer/host/preparation modules rather than assuming wrapper-only changes. Add focused acceptance for same-object versus distinct-source alias, borrowed/nested scope rejection, source/code/schema substitution during calculation, policy revocation and real-clock expiry inside the scope, exception cleanup, exit drift discarding staged output, and callbacks/native origins unchanged. Full fresh scope entry/exit source/package guards remain mandatory; sealed pure proofs cannot replace live permission or authorize Tool/journal effects. Scope reuse ends before any real effect. Lock/CPU/native/schema/caller time must appear in the lifetime ledger, including negative-case time; use independent negative fixtures where appropriate rather than burning a positive lease and then extending it.

### CR-05 — P1 — Task-local construction proof and final T15 qualification need separate pin rules

[T03:55–57](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/work-pack/tasks/T03.md:55) requests real successor proof before T15, while its common footer says new digest commands are generated only after T00/T15 selection. T05 similarly requires the full Machine class; T31/T32 require actual effect/cold proofs. [EXECUTION-PACK.md](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/EXECUTION-PACK.md) says qualification starts after T15. The DAG is acyclic, but the proof/pin wording leaves either an implicit procedural freeze cycle or permission to run changed code against predecessor pins.

**Concrete fix:** explicitly allow independently frozen **task-local construction candidates** before T15, with new immutable source/profile/fixture/native pins and unique reports. Such evidence closes construction acceptance only and never qualifies the final common family. T15 then integrates actual reviewed postimages and T16–T18 rerun final-family evidence. An instrumented T01 profile is nonqualification. Define later invalidation of each task-local proof by changed inputs. Resolve exact prospective helper paths at T00 and pin each actual selected helper before its construction test.

### CR-06 — P1 — T22 must distinguish application attribution from actual later Work influence

[T22:21–23](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/work-pack/tasks/T22.md:21) requires genuine later use but does not describe the operational route between public `lesson.apply`, actual task execution and independent outcome. Current [LessonApplication.preflight](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/lesson-application-v3-action-0148/preparation.py:82) prepares attributed candidate content with independent routing/live Session authority; [Assessment2:115–126](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/lesson-assessment-v2-action-0148/preparation.py:115) explicitly verifies `candidate-attributed-no-tool-dispatch` and zero dispatches in the preparation witness. A completed journal is a valid candidate Application input but does not prove actual influence or a genuine observed benefit.

**Concrete fix:** state the chosen real later task, instruction, reviewed Lesson, actual eligible influence and independently authorized Tool/workflow action route. Bind the candidate Application to actual subsequent inputs/outputs/observations and counterevidence without treating application preparation itself as tool execution. Any missing production producer belongs before execution freeze, or requires a separately frozen successor and affected requalification. Replace ambiguous “causal later lesson application/assessment” with “attributable actual use and independent later outcome assessment within the declared causal ceiling”; general/counterfactual benefit is not inferred from one correspondence. Preserve all failed attempts and actual human satisfaction as independent observations, not a synthetic test field.

### CR-07 — P2 — Remove unnecessary diagnostic blocking for the already proven caller defect

T04 depends on completion of T01, but the transport-envelope KeyError is already proved by the retained `source8_episode:432–433` and raw refusal. It can be corrected and unit-checked in a new caller independently of slow Source8 profiling or unresolved Machine causality.

**Concrete fix:** change T04 dependency to T00 plus the exact retained envelope/trace input. Its focused construction tests cover success, domain error and transport refusal, retaining no-retry/uncertainty and ownership-scoped cleanup. Keep full real lifecycle validation in T03/T17. This lets error reporting improve promptly without implying the runtime failure is fixed.

## Confirmed requirements and disposition limits

- T02 must continue to cover both `test_custody_sessions.py:172–176` and `run_session_checks.py:171–175`; both successor changes need a declared AST selector ledger and separate original-origin refusal. Do not relax the original constructor.
- T31 correctly identifies the explicit zero-output guard at `workflow_transition.py:149–151`; required output-bearing templates must get real original-byte producers/current scope and outcome lineage. An explicitly reviewed original-scope exclusion is permissible, arbitrary acceptance narrowing is not.
- T32 correctly asks which selected append path actually exposes `persist_batch`. Static lock/per-file hardlinks at `lib.rs:2176–2234` are a risk, not proof of failure. Retain cold exact replay, recognized/unknown residue, actual commit point and no foreign-byte deletion.
- T18 preserves the core restart rule: durable metadata cannot reconstruct credentials/RAM, and lost-process disposal cannot be asserted. Candidate constructor drift is a fixture issue; actual parent/borrower ownership and disposal remain product invariants.
- T16/T17 must use exact current fixture/source inputs and account for all original methods and all34 operations. Correct blocked readiness is conformance, not actual release. Old API16 failures remain actual failed evidence.

Recheck requested after root revises the affected task details, edges, wave/layer wording and current-source prerequisite. No root plan files were edited by this reviewer. CORE-F04 in the two owned analysis files was updated only to add verified same-case raw reply and static mismatch evidence; it still does not claim the actual throwing guard was dynamically proved.

## Final recheck — PASS within the core/runtime review scope

The revised plan has36 task contracts,36 task-local SWUs and73 edges. I reread the affected contracts and execution/layering rules and independently checked that task Markdown dependencies match the machine DAG and that the graph is acyclic. The parent's full validation result is retained in `validation.json`; this reviewer did not rerun its writer or execute runtime qualification.

| Original finding | Recheck disposition |
| --- | --- |
| CR-01 current Source8 prerequisite | Resolved for planning. T02 now constructs a distinct signed current source/native reader/mapper/Context/runtime/Lesson family, preserves expired originals, and covers both constructor variants. T01 independently diagnoses genuinely current legacy Machine inputs. T35 depends on T02 for cold-verified current Source8 profiling; T03 depends on T35. T00/T15 and the execution pack separately budget24h source validity, at most30min reader grant and900s Session, with just-in-time final source selection, measured duration, pilot availability and expiry stops/new-freeze requalification. |
| CR-02 technical qualification overblocking | Resolved for planning. T14 now depends on executable contract/adapter inputs T08/T09/T33, rather than T10/T11/T13 semantic materialization. Independent DAG ancestry confirms T10/T11/T12/T13 are not ancestors of T15. Their final package/owner obligations remain mandatory at T25. T32 explicitly first maps selected call chains/outer recovery, keeping an unexposed risk distinct from a selected executable defect. |
| CR-03 Machine helper identity | Resolved for planning. T05 names the retained raw receipt, legacy `view_get` and exact original generation selector, requiring causal trace and a versioned origin-specific helper if needed. Original helper/type refusal and live parent/security invariants remain. Static mismatch does not become a claimed observed throwing guard. |
| CR-04 pure-scope safety and latency | Resolved for planning. T35 measures exact callbacks/nesting, native/schema/lock/caller costs and negative-case lifetime use. T03 requires method/code/schema/profile/source/input tamper, nesting, exception cleanup, revocation/expiry and read-scope effect negatives, fresh full entry/exit and effect boundary checks. Actual host/producer/preparation modules are selected from the measured call chain; no cross-call trust cache or lease extension. |
| CR-05 construction pins versus qualification | Resolved for planning. Task contracts now require separate immutable task-local pins and owned outputs before T15. They explicitly do not transfer final qualification. T15 supplies the integrated final source/profile/cut and changed inputs invalidate affected descendants. |
| CR-06 genuine later influence | Resolved for planning. T31 identifies and qualifies the actual eligible Application consumer before final freeze. T22 requires observable consuming dataflow/behavior, falsifiable expected outcome and counterevidence within the declared causal ceiling. Metadata attribution is insufficient; required new code returns to construction/freeze and requalification. |
| CR-07 caller unnecessarily blocked | Resolved. T04 depends on T00, using retained transport/domain evidence independently of unresolved Machine diagnosis/slow Source8 profiling. |

**Verdict: PASS for the revised candidate plan within the six-area core/runtime scope.** No remaining material issue from CR-01–CR-07 blocks this plan review. This accepts the specified construction, diagnosis, evidence and stop rules; it does not assert that the Machine cause, performance correction, new signed source, genuine Work, native recovery guarantee or any runtime qualification has been achieved.

Execution still requires exact authorized scopes and actual current independently verified source/Actor/period inputs. The absolute source-window feasibility check may stop execution; it permits neither artificial extension nor unchanged-family evidence transfer. Current/expired originals remain exact, both metadata-only constructor cases retain no-RAM-reconstruction assertions, and selected native/Workflow output obligations remain evidence requirements. Actual human usefulness, governing roles/host provenance, owner disposition, admission, local operation and release remain separate real gates.

### Exact artifact snapshot reviewed

Paths below are relative to `docs/plans/0011-lab-runtime-completion/`. Hashes identify this reviewed snapshot, including all36 task contracts. A later changed task/graph/source selection requires an affected review recheck; this table is a record of observations, not self-hashing review authority. The reviewer changed only this review file during the final recheck.

| Artifact | SHA-256 |
| --- | --- |
| `PLAN.md` | `2e3dabea1f087e826102c13a3692f25052541fb2fcd2ab311d7f78f3cca99e8d` |
| `DAG.md` | `9e6088d892219984a5af6c0d6d06ca85d5bfb418dc24553ffb09c47185a353a9` |
| `dag.json` | `08057d59234a0cae280091c322b58c7ded9710f2a01499d69fe841a0e91e2dfe` |
| `WORK-PACK.md` | `ee5c1ef95632443e7b4b360d568fb51134f65a5efe641bc74bc3b66e1402885b` |
| `IMPLEMENTATION-LAYERING.md` | `471c44565e44fda5b7cdcf743e024d05b434b6b84f5275b69fd5b3dcd4739be2` |
| `EXECUTION-PACK.md` | `113898b7e63cd3d9fbbdb7f9a5de47579dde6dd3e280ac0ca30e7d80cc9a6a79` |
| `SOURCE-BASELINE.json` | `601f86723d0c1223e4b4ccdc42de795f7357991f94852f5db393f149b9ce2b8f` |
| `swu-manifest.json` | `5086654713692e6ded6dc1cd7bafde7b87d90f3a41def4ec4eba8a1b4c10fdfd` |
| `validation.json` | `8dff7378d3608d1412482f8558b5a56854ae2ab8babae392100acd07854c5158` |
| `work-pack/tasks/T00.md` | `40edf523d68237e6fb6f753ae6b4dedf6c3c0bd51fbf9515c0da84f9990ef67c` |
| `work-pack/tasks/T01.md` | `b501d36fe1f90301f60ae9745fd2a4c32e83f86fbe3a42583568e12e87ae8e62` |
| `work-pack/tasks/T02.md` | `1693567f829dca348aaf4628f41328242e35147d3e6c3d5c684f8c66eb12e8c5` |
| `work-pack/tasks/T03.md` | `83bbc5f3d3c378b6cd74e3dc007dc776ddf9679d3836b6c0d63e31beebc01cbf` |
| `work-pack/tasks/T04.md` | `bca2942bebe3a44797027811bdca14ccdebe2956060943fb04034d924dd00562` |
| `work-pack/tasks/T05.md` | `70da2e2a34d8198514172ba81d226398fb16df97ec580e3a03cc83b5ebfbac0f` |
| `work-pack/tasks/T06.md` | `8a70b1650f14c5ee5219a41dbd94f258f4051d52d727d34a041d5a4a10a46c86` |
| `work-pack/tasks/T07.md` | `c096ecd008311c93c20bc8c306f3f1811d044b2a858e107f9a8355db26484f64` |
| `work-pack/tasks/T08.md` | `897b4cf438a3d6ba9c37747a703bd928550e1f2a4f89e758ac5aac8b4b25e445` |
| `work-pack/tasks/T09.md` | `e345307292c5fffb8ee390f2cf0ce0733da87bff59802dccb77030f350f2876b` |
| `work-pack/tasks/T10.md` | `ba0185f0cbfea1df085008465b81b18f56767d04951a0a2079c6c27ca2bafeb0` |
| `work-pack/tasks/T11.md` | `4b2202fa888adaf8703c2a1031d4ea6cf05da7c796f3e8502aa6811a22a352c5` |
| `work-pack/tasks/T12.md` | `faffe7c3967810037a989384a7c9f23f28a31075ac0d75df2a0ba4dffdef1eb8` |
| `work-pack/tasks/T13.md` | `c93f7fad08297cd6eae937246cfe93509c4e38cf030a402e4cd4579ea69754eb` |
| `work-pack/tasks/T14.md` | `0f4dea3a49ef8fe880d9bdff1222869b071dacb1b4dc6c761b7f1a6244fe5e32` |
| `work-pack/tasks/T15.md` | `6d88d148887b4be8a40a5ef05682015c672acae5f14688be272d0534b8e85c43` |
| `work-pack/tasks/T16.md` | `c0cdf576475177a98eeb14c72b609ea91a7f2e29b4547792baa23d4c1d05f814` |
| `work-pack/tasks/T17.md` | `4d5d71bb4542ad3f3b36ea0ee9065adce5615abfb899b7dc5532ca2481009d50` |
| `work-pack/tasks/T18.md` | `292ceaac859bd1d9267b148bd8751e11252841c71d7f14b53fbb1fbc03fb8d60` |
| `work-pack/tasks/T19.md` | `ce33c3b62af9a58bb84be841c446b699c6dc314a3b20e048eb490d71a4bb539b` |
| `work-pack/tasks/T20.md` | `8a5a7da6539f9569a92a0c6bb06afae8cd320195eff5d1e91f638e2f548558a3` |
| `work-pack/tasks/T21.md` | `51e869abee54e632f5536f58010070ed3e0b81142f772ffced5fd57ca37e7b7e` |
| `work-pack/tasks/T22.md` | `1fd4e7289898130eeeb1de45c4d50a291ababa80fb7a377edefdfdf947c395c7` |
| `work-pack/tasks/T23.md` | `0136c0a6a0071331d7137c72d3e3a0fe07ac749a27b16b6d167415430e8449ad` |
| `work-pack/tasks/T24.md` | `0f28b619e3a0c3b716734a7edcf70d60ec5339da2a6c6383758e47e48ef2e7ec` |
| `work-pack/tasks/T25.md` | `3407a7c8524b9c9e5fe63465d90b712449096aa43ceac6a4243e53e6f6ba983b` |
| `work-pack/tasks/T26.md` | `61f20284825ff6caa2a383a40bb7353f7a91c5dd43dae3d63fd96063f1310e5e` |
| `work-pack/tasks/T27.md` | `d8e65325ef7cf65eb710aa00286b379ac2bd9058b427db74221ec3d3ea7f655c` |
| `work-pack/tasks/T28.md` | `dc3538810ad0e84d3fb04a0c8092fd43e8d8dd524acdae373c402aafcfc6b85a` |
| `work-pack/tasks/T29.md` | `3fb00a3596f51441721600fe552a54ba05922484d11e591c7400b429301eebcc` |
| `work-pack/tasks/T30.md` | `f72225c101e750107d12ccd3465d624d17841f92863368e8f5f4eb5e075fac3b` |
| `work-pack/tasks/T31.md` | `77cdfae4197bc80cf03ee35dbfd7372884b639ac2b11ce6004bbc35196a057e1` |
| `work-pack/tasks/T32.md` | `2c910d4e8ac4451b4e98c02748023a9975f546736d0a0a3f4bfe4b6eecf6840d` |
| `work-pack/tasks/T33.md` | `1750a1803c28998bc90ee351460e644f61a9980c55ea5e962b868c07312d0e3e` |
| `work-pack/tasks/T34.md` | `2f35cd1884bd285515f8b2d92636858199c06de8b37a24d243d8ea47a8b684e4` |
| `work-pack/tasks/T35.md` | `7b363a1a7dd3f3a9d39ffa560912429765cbc3200b0c4ef73cf1eaa2836ab0bb` |

