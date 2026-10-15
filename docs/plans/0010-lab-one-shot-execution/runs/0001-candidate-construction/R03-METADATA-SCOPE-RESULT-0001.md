# Durable metadata and declared scope preparation

Status: candidate implementation; API-v23 verification is running. No additional public API or completed task is claimed.

## Actual complete results

| Suite | Actual result | Meaning |
| --- | --- | --- |
| API-v19, 129 cases | FAIL: 100 pass, one failure, 28 errors | Projection refresh hit its request deadline; later participation setup failed. Complete terminal, cases, log and wire are preserved. |
| API-v20, 146 cases | FAIL: 112 pass, 34 errors | All 17 guard, 14 raw API, 47 preparation and 34 original Session cases passed. All 34 raw Session cases failed during setup after the original Assignment expiry. Those cases did not execute a successful live Session journey. |
| API-v22, 84 metadata/scope cases | FAIL: 82 pass, two failures | Fresh metadata access and its restrictions work after expiry. Owner preparation/validation failed because a selected prefix lacked the parent signed-source attribute. |
| Independent diagnostic | Completed; actual validation refusal captured | The actual recorded reason is `'Inspection' object has no attribute 'custody_signed_sources'`. Owned metadata host removed. |

The original Assignment expired at 2026-10-10T02:45:14.443492+00:00. Its period and signed source remain unchanged. No old signer, Agent, or Session memory was restored.

## Implementation under verification

The new metadata policy uses a separately selected owned principal and permits eight operations: status, catalog, artifact inspection/query, candidate preparation/validation, durable operation inspection and disposable projection refresh. It binds the existing development authorization. It forbids all four Context/Session operations, an original reader Principal, Agent assignment claims and Session-control injection.

Metadata grants and live Agent participation are separate. A valid fresh metadata grant can read durable signed Project facts while an expired Assignment remains unusable. No current owner or Agent permission follows from that metadata access.

The scope adapter selects one exact profile outside the caller boundary. It binds the 42 owner target bodies and cores, preserves 21 domain scopes and requires complete paired scope groups. Preparation uses explicitly labeled hypothetical configurations and produces scope evidence; it grants no operational domain admission.

API-v23 fixes the actual prefix guard failure. The adapter requires the original selected SignedSources parent, checks it before and after construction, and compares the selected prefix's original bytes, engine handle, config, baseline, projection, transactions and current head to that parent. Two new cases refuse a missing parent and a modified prefix. The complete current suite has 86 cases: 17 original read guards, 47 original preparation regressions and 22 metadata/scope cases.

## Remaining work

The full goal remains 46 criteria and 34 APIs; current qualified progress remains **35/46 and 12/34**. A passing metadata/scope suite still requires independent source/API/body/core/nonce/idempotency/privacy/recovery audit. Complete current Agent/Session qualification, governing-role coverage, public proposal review and all 22 remaining API contracts remain required. S02 must assemble the exact complete package before the sole final R08 owner checkpoint.

## Evidence

- [Full expired-Assignment suite evidence](custody-api-failed-proof-0003.json)
- [API-v22 actual terminal](metadata-scope-api-terminal-0001.json)
- [Actual refusal diagnostic](metadata-scope-diagnostic-result-0001.json)
- [API-v23 selected source](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/api-v23/source-manifest.json)
- [API-v23 running suite log](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/api-v23/checks-metadata-scope-0001.log)
