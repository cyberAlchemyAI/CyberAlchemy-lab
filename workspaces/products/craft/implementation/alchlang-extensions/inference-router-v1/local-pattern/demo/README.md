# One-command mock inference demo

This runs the accepted Alch/DomainSpec bundle with two deterministic mock engines.
No local LLM, model download, credentials or compiler build is required. Node
26.8.1 or later is supplied by the shared repository toolchain.

From the repository root:

```bash
tools/toolchain/run node language/capabilities/alchlang/plans/general-compiler-v1/extensions/inference-router-v1/local-pattern/demo/run.mjs
```

The command verifies the accepted manifest and every bundle file before importing
it, starts all three listeners on temporary 127.0.0.1 ports, runs 11 API checks,
and shuts everything down. Any failed check produces a nonzero exit code.

To explore the API yourself, add `--serve`. After the same walkthrough completes,
the service stays running and prints its address. Ctrl+C or SIGTERM closes the
service and both engines. No operator configuration file is overwritten.

Copy the printed service address into these examples:

```bash
curl http://127.0.0.1:PORT/v1/models
curl http://127.0.0.1:PORT/v1/capabilities
curl http://127.0.0.1:PORT/v1/inference \
  -H 'Content-Type: application/json' -H 'Idempotency-Key: my-request' \
  -d '{"task":"text.generate","input":{"messages":[{"role":"user","content":"Hello"}]}}'
curl -N http://127.0.0.1:PORT/v1/inference \
  -H 'Content-Type: application/json' \
  -d '{"task":"text.generate","model":"local-chat-b","stream":true,"input":{"messages":[{"role":"user","content":"Hello"}]}}'
```

Automatic selection returns Mock engine A. Explicit local-chat-b selects Mock
engine B. Streaming emits started, delta and completed. Repeating a retained JSON
key returns the same result without another engine call; changing its request
returns 409. Repeating a retained stream key returns 409. Unknown models return
404 and unknown request fields return 400. The runner checks these outcomes and
that rejections do not dispatch extra inference.

The demo is an operator convenience wrapper; API definitions, selection, mappings,
stream transitions and custody remain in the accepted generated service. It uses
public loopback scope and memory custody. Mock outputs demonstrate protocol
behavior, not language-model quality or actual model execution.

## Product progress and Open Questions

This completes the one-command demo and API walkthrough milestone. The remaining
product work is an integrated protected/durable API rehearsal using existing Auth
Foundation, consolidated operator instructions and a final packaged-product
acceptance report. Identity-service availability affects that rehearsal only.
Actual LLM selection and hardware benchmarking remain optional, separately owned
integrations. Acceptance of the base pattern remains unchanged; no deployment,
provisioning or new product approval is inferred from this demo.
