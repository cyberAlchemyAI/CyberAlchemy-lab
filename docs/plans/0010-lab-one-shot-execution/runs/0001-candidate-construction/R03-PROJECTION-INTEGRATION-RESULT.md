# R03 projection and Session integration result

Status: candidate slice verified; R03 remains in progress. Authority effect: none. Actual owner outcome: absent. The original full plan remains active.

## Current state

- **35/46** original task criteria closed; **12/34** actual public API handlers verified; **22** remain.
- Selected source: `product/lab/release-candidates/v1/interface/api-v16/source-manifest.json`, SHA `a20c7c618cbe545500b8b3de5a202e42482fcf717c567b7fd2a5c324e7196cad`.
- Selected protocol profile: `product/lab/release-candidates/v1/interface/api-v16/contract-profile.json`, SHA `506343b60e960c98fe42f427608d8801be0c6f9139c8d0957474d313a967c45b`.
- Authoritative partial receipt: `product/lab/release-candidates/v1/interface/api-projection-close-v1/receipts/R03-0016.json`, SHA `f0d6e7fa4008654ecf0a15d535f6681abbde50a350cf1dfdff15f4ba92c96a45`.
- All **6,031** parent proof bindings retained, with **8,533** current exact file bindings. Original 77 planning files and 887 source bindings remain unchanged.

## What was implemented

`projection.refresh` now accepts its original request/result contract through the coherent authenticated operator. A separately provisioned private host grant selects the exact projector, SQL schema, compiled contract catalog, source cut and generation budget. The request must match the current generation preimage. The builder populates a complete private SQLite generation from the verified original signed source, verifies original replay parity, byte caches, integrity, foreign keys and watermarks, then rechecks current source/permission and selects it.

Ready means the SQL materialization checks passed. Source semantic gaps remain in the verification evidence, `projection_gap` rows and `artifact.query` output. A cache generation supplies query data; committed source history supplies replay and existing authority facts. Protected historical Session and credential bodies are omitted from optional exact-byte caching.

Durable operation claims precede effects. Same-key exact retries return historical recorded evidence. A changed input conflicts; pending keys require operation inspection. A failed staged build leaves the previous visible generation intact and removes its staging files. Process termination removes the connection's disposable SQLite generations.

## Actual example

The real live stdio process created `generation:R03-query:fcb7a5ebc50b40e888bd29ff8b1fbbed` with posture `ready`. `artifact.query` consumed that exact generation. The process ended with exit 0; all of its replay and SQLite temporary directories were removed.

A second independently authenticated process retried the same key and returned the identical recorded result. It created no SQLite file for that retry. A new permitted key then created `generation:R03-query:3812a56a95574e9db021772e40d255f5`. Its projection query matched the original canonical query. That process also exited 0 and removed every owned temporary directory. Fixture keys and workspaces were removed; these examples are historical proof, not currently live generations.

## Validation

| Selected evidence | Result |
| --- | --- |
| Original refresh tests, including corruption, deadlines, permission, pending claims, exact byte observations, replacement and memory cache checks | 21 passed |
| Original preparation regressions | 47 passed |
| Original Session method coverage | 34 passed |
| Actual stdio processes / original call-reply frames | 2 / 9 |
| Process checks | 61 passed |
| Independent byte/source/wire checks | 8,920 passed |
| Original native regressions for locator recovery | 23 passed |
| Portable locator negative guards | 9 passed |

The Session aggregate retains the exact passing A–D groups from the unchanged v16 source and reruns all eleven E methods with the declared handler count updated to twelve. Each original method is represented once in the selected aggregate. Failed original runs remain preserved. The new E observer archives returned snapshots before the deliberate client mutation in test33. One retained test22 observation contains its parsed noncanonical call and received byte hash; missing original raw wire bytes are not invented.

## Older evidence path reconciliation

O04–O07 have explicit currentness successor receipts. External `refs/heads/main` still resolves to `f74e67fce7b0c704dee6bd859a16eebea0fc40fb`; no external Git state was written. The old loose-ref pathname remains absent. An exact commit-line witness carries the original byte digest. The native executable rebuilt byte-identically with SHA `480d421a438f712db930bb287d2ee1d5e4a0933e1336816defa28d6c284de9c3` and passed all 23 regressions. Its portable local code copy is ignored under `.local/`; the build recipe, source pins, logs and witness receipts are preserved.

The selected checker is `implementation/lab-ontology/candidates/v1/currentness/successors/0001/check_currentness_v2.py`. It checks the full active proof and unchanged original baselines, plus current read-only Git resolution and byte-equivalent code/ref witnesses. Historical receipts are preserved.

## Next work

Close the existing arbitrary original-byte custody followup before affected export/admission, then integrate the classification/failure/operational learning handlers with exact source and current permission closure. All remaining 22 public operations and original R03 journeys remain required. R05 must also bind complete source/package verification at the host entrypoint; the protocol profile does not replace the independently verified source manifest.

R04 actual human pilot, R05 package/environment integration, R06/R07 acceptance, complete S02 owner/registry/target/schema/runtime/Decision-core closure and the one actual final R08 decision remain. Original A01–A04 admitted operational acceptance remains downstream. Source-reader Sessions do not establish Tool/model dispatch or complete Product realization. The original Source Assignment expiry remains `2026-10-10T02:45:14.443492+00:00`; any later period needs a separately sourced successor.

No canonical admission, live-store operation, service activation, source retirement, publication or stable release occurred.
