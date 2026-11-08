# Alch host lifecycle service

This local successor adds actual function status and durable drain, resume and
restart requests to the semantic Alch host service. It retains existing build,
prepare, activate, invoke and schema-derived upgrade behavior. It runs the existing
isolated Rust functions with SQLite state and RWO/Ansible provisioning.

## Start a local service

Use a fresh private registry directory and an operator configuration based on
operator.example.json. The schema is alch.host-lifecycle/v1. Explicitly grant
lifecycle scope to users allowed to control functions; read permission is required
for status and request inspection. Fixture/example token hashes are not credentials
for a live deployment. The service still binds only to loopback.

```sh
python3 control_plane.py --root /tmp/my-alch-lifecycle --config /path/to/operator.json --port 8080
```

Existing build and invocation usage is documented in
[the predecessor client guide](../host-service-client-v1/README.md). Use this packet's
client.py when talking to the successor. Supply ALCH_SERVICE_TOKEN in the environment.

## Observe and control a function

```sh
python3 client.py status shop orders-local
python3 client.py drain shop orders-local --expected FENCE_FROM_STATUS --request-id maintenance-1 --wait
python3 client.py lifecycle-request shop orders-local maintenance-1
python3 client.py status shop orders-local
python3 client.py restart shop orders-local --expected FRESH_FENCE --request-id restart-1 --wait
python3 client.py status shop orders-local
python3 client.py resume shop orders-local --expected FRESH_FENCE --request-id resume-1 --wait
```

The expected field from status is an opaque concurrency token. Refresh it before a
new action. Keep the same request ID and body when resolving a lost response. A
conflicting reuse or outdated fence is rejected. The client never retries POST
automatically. Waiting polls GET; blocked/failed/unknown control results exit nonzero.

Python Client exposes status(project,function), control(project,function,action,
expected,request_id), lifecycle_request(project,function,request_id) and
wait_control(project,function,request_id,timeout=90), alongside the inherited methods.

Status distinguishes selected revision, desired mode, host observation and delivery
counts. Missing/locked/corrupt storage reports unavailable counters. Status never
starts a host. The functions command retains its selected-revision-only meaning.
Private host ports, credentials, storage paths and business payloads are excluded.

Drain blocks new invocations and lets existing delivery finish. Dead letters or a
35-second timeout leave the gate closed. Resume explicitly opens it. Restart drains
a live host and replaces its process while retaining selected code, storage and
desired mode. Restarting a drained function leaves it drained. A confirmed dead
host can be restarted without losing committed state or message deduplication.

Slow control runs on a bounded background worker, so status remains available.
There is at most one outstanding request per function, two per tenant and eight
globally. Activation cannot bypass a pending lifecycle request or a user drain.
On controller startup, durable requests reconcile before traffic can resume. An
ownership lock still held by a prior process blocks recovery with a visible result;
no unverified process is killed. A failed host does not prevent status for other
functions. Unknown control outcomes block conflicting controls until controller
startup reconciliation; there is no force/discard operation.

## Construction and validation

PLAN.md and PLAN.json are the original planning snapshot. execution.json and
product-test.json record the current construction frontier and exact evidence.
The prototype contracts and native adapter do not admit new DomainSpec meta-types.
Existing compiled identities and typed event-storage bindings remain inherited.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 test_lifecycle.py
PYTHONDONTWRITEBYTECODE=1 python3 test_host.py
PYTHONDONTWRITEBYTECODE=1 python3 test_client.py
PYTHONDONTWRITEBYTECODE=1 python3 test_integration.py
```

Integration tests create disposable local registries, build real Alch artifacts,
exercise isolated Rust hosts and remove their owned test resources. Test-only crash
injection is not a service API or operator configuration option. Predecessor sources
and evidence remain unchanged. Candidate and product-test receipts distinguish
construction evidence from product approval.

## Operational support

Long-running service startup/credential issuance belongs to the platform operator;
existing-root migration belongs to the service operator; public deployment belongs
to the platform owner. All are deferred with no affected construction stage and do
not block local product tests. No live service is left running by this work.

## Open Questions

See PLAN.md#open-questions. Stop, automatic recovery, dead-letter redrive, remote
transports and existing-root migration remain future slices. Product approval is
an owner decision over one tested digest and grants no deployment authority.
