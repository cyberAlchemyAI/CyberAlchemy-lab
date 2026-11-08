# Alch host service client

A CLI and Python client for the [semantic host controller](../semantic-corrections-v1/README.md). Uses the existing service API and preserves the earlier compiler/runtime candidate.

The product flow is: create a project → submit an Alch revision → wait for its build → prepare → activate → invoke. Each mutation is a separate command. A build never implicitly activates a function.

Definitions: a **revision** is a submitted source/build identity; a **selected function** is a durable route to one ready revision, not proof that its process is currently alive; an **unknown outcome** means the response was lost and the client cannot determine whether the operation committed. These are client views of the controller's existing project/revision/route ontology. The client owns no grants or product approval.

The client reads its token from `ALCH_SERVICE_TOKEN` and URL from `ALCH_SERVICE_URL` (or `--url`). It accepts literal loopback HTTP addresses for the current local service. Start the controller using its existing operator configuration and a fresh registry root first.

```sh
python3 client.py create-project shop
python3 client.py build shop ../semantic-corrections-v1/orders.alch --wait
python3 client.py prepare shop REVISION_ID
python3 client.py --timeout 120 activate shop REVISION_ID
python3 client.py functions shop
python3 client.py invoke shop orders-local --input order.json
```

`order.json`:

```json
{"facts":{"orderId":"o1","payload":{"quantity":2}},"message_id":"m1","expected_version":0}
```

Keep the same envelope when retrying an uncertain invocation. The client never retries POST requests automatically. Build polling has a deadline; a CLI polling failure retains the submitted revision ID so it can be inspected with `revision shop REVISION_ID`. Credentials are not CLI arguments or error output.

Python callers can import `Client` and use `create_project`, `build`, `wait_ready`, `revision`, `functions`, `prepare`, `activate`, and `invoke`. Failures raise `ClientError` with a stable code and an HTTP status when available.

The construction DAG is `meanings and API contract → client → bounded protocol tests → real controller integration → evidence`. Ownership: Alch service/client owner. All work in this packet is product construction. Construction is complete for this client candidate, with seven protocol tests and five real-controller tests passing. The current frontier is product review; no implementation tasks remain in this packet. Live service startup, token issuance, existing-root migration and public deployment remain operational support owned by the operator/platform owner, outside these tests.

Run `python3 test_client.py` for protocol tests and `python3 test_integration.py` for real queued builds, isolated Rust invocation, tenant boundaries and selection recovery. Current completion and hashes are recorded in `validation.json`.
