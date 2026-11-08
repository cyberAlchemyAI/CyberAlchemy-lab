# Telegraph-compatible inference API in Alch

Status: tested local HTTP adapter prototype, forwarding to operator-configured
upstreams. Not deployed. No paid inference or on-chain calls have been made.

The public inference/discovery HTTP surface is prepared from Telegraph's Engine
1.0.0 and Miner Dispatcher 2.0.0 contracts, pinned to upstream commit
`4d9f9714e351a2ea80b792ed5631a8c38e1951fc`. See [source provenance](sources.json),
[design and construction DAG](DESIGN.md), and test evidence (referenced result or source binding is not imported).
The upstream specifications declare MIT licensing; their license metadata is
retained. Contract projections omit upstream prose and examples.

## The Alch file

[inference.alch](inference.alch) declares two integrations and two API mounts.
HTTP methods, parameters, request/response schemas and security requirements are
derived from the imported contracts. Authors do not redeclare every field.
There is no TypeScript or Python embedded in this file.

```alch
api EngineAPI:
  contract "./contracts/engine.json"
  mount "/engine"
  integration Engine
  exclude GET "/ws"
```

`compile.py` implements the new `http-contract-v1` profile locally. It emits
the application, operation/integration ontology scaffold, and explicit coverage.
`server.py` interprets that model as HTTP routing and transport. This is an
extension prototype: the existing Alch CLI and VPS semantic-host compiler do
not recognize this profile yet. Their code and live deployment were not changed.
The generated ontology is navigation evidence, not an admitted DomainSpec model.

## Prepared endpoints

| Prefix | Operations |
| --- | --- |
| `/engine` | `POST /v1/ask`, `POST /v1/ask/{subnet_id}`; miner/subnet catalog, intent details/miners/WASM, job details/results |
| `/miner-dispatcher` | chat, responses, embeddings, image generation, moderation; weather/media inference; generic miner proxy; health, integration discovery and x402 test |

There are 32 public HTTP method/path pairs. See [coverage](/home/vlad_/projects/cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/telegraph-inference-v1/generated/coverage.json)
and the exact contracts under `contracts/`. Three documented operations are
excluded: Engine WebSocket `/ws` and Dispatcher internal `/validate` and
`/validate/collector`. This is not full HTTP/WS/on-chain Telegraph conformance.

Request bodies, query strings, status codes, response bodies, payment challenge
headers and receipts pass through. SSE responses stream incrementally. Upstream
services own validation, model inference, intent routing and payment verification.
The adapter does not sign payments, invent receipts, or automatically retry a
payment-bearing request. Redirects return to the caller without being followed.
The configured URL includes the upstream prefix; request data cannot replace it.
Forwarded identity headers and internal secrets are not relayed.

## Build and run

The checked-in projections can be regenerated with `python3 prepare_contracts.py`
(requires PyYAML and network access); every downloaded source is digest-checked.
The compiler, adapter and test suite use only the Python standard library.

From this directory with Python 3.12 or newer:

```sh
python3 compile.py inference.alch --out generated
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_api.py
```

Set `TELEGRAPH_ENGINE_URL` and `TELEGRAPH_DISPATCHER_URL` to operator-selected
HTTPS base URLs including their respective path prefixes, then run:

```sh
python3 server.py inference.alch --host 127.0.0.1 --port 8090
```

Missing upstream configuration produces HTTP 503 rather than an inference result.
The documented upstream sample node uses HTTP; it is not silently selected here.
Plain HTTP is available only through the explicit loopback fixture option in the
test harness. No credentials are stored in the Alch source or generated model.
The standalone adapter needs HTTPS ingress before external operation.

Example client request after configuring an upstream:

```sh
curl -i http://127.0.0.1:8090/engine/v1/ask \
  -H 'Content-Type: application/json' \
  --data '{"query":"Explain what an inference intent is."}'
```

An unpaid upstream request should return its x402 challenge. A payment-capable
client can submit an authorized proof in `PAYMENT-SIGNATURE`. The operator token
for the existing Alch host is not an x402 payment proof and is not forwarded.

## Open Questions

- Backend choice: forwarding is the stated default pending the user's preference.
  Own inference providers require routing, provider bindings and real payment
  verification/settlement, rather than replacing responses with fixtures.
- Which HTTPS Telegraph upstreams should be configured for real integration tests?
- The core Alch CLI/DomainSpec lowering, host policy admission and Rust target for
  this profile remain implementation work. This directory alone does not enable
  uploading the file to the current production host.
- WebSocket wallet authentication/subscriptions need a separate tested transport.
- Production deployment, wallet/payment authority, rate limits, streaming limits,
  and tenant policy require their own exact operational configuration. The local
  prototype has 16 forwarding slots, body caps and per-I/O socket timeouts, not a
  global deadline or a distributed quota system.
