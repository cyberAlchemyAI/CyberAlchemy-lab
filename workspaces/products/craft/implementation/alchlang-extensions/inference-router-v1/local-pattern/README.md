# Local inference pattern

Candidate Alch/DomainSpec Node pattern. Authority effect: none. Real-engine
compatibility and production performance have not been established.

The build composes authored public routes, admission, discovery, selection,
request/response mapping, invocation, stream transitions and memory custody.
Native code supplies operator configuration and HTTP/byte/clock/storage ports.
Protocol details: [PROTOCOL.md](PROTOCOL.md).

From the CyberAlchemy-v2 checkout, build with the shared repository toolchain:

```bash
tools/toolchain/run node language/capabilities/alchlang/plans/general-compiler-v1/extensions/inference-router-v1/run.mjs build-local /absolute/new/local-inference
```

The output must not already exist. The builder verifies the pinned sibling
DomainSpec compiler and records generated files, native inputs and hashes in
manifest.json. Each generated component retains its Alch source/compilation trace.
The generated API contract is public-service/routes.json, including typed route
and operation interfaces. The launcher resolves the installed repository compiler;
there is no dependency on a compiler installed under /tmp.
The output is standalone and requires Node 26.8.1 or later; it does not need the
checkout, TypeScript compiler, Rust or model downloads at runtime.

Copy configuration.example.json to an operator-owned file and configure engines
implementing alch-local-text/v1. Example ports are placeholders; the builder does
not start engines. Secrets are referenced by environment variable names and never
written into generated output. Authentication none is confined to numeric
loopback bindings. Upstream bearer auth is separate from caller authentication.

For a deterministic demonstration, run these in two terminals inside the generated
directory (they echo labels; they do not run models):

```bash
node fixture.mjs 9101 A
node fixture.mjs 9102 B
```

Inside a third terminal in the generated directory:

```bash
node start.mjs /absolute/operator-configuration.json 3000
```

The launcher binds 127.0.0.1 only. Requests must use its exact IP/port Host and,
when supplied, matching Origin. Forwarding headers are rejected. This minimal
composition is public to local callers; it grants no tenant identity. The existing
protected Auth Foundation and durable custody compositions remain separate.

```bash
curl http://127.0.0.1:3000/v1/models
curl http://127.0.0.1:3000/v1/capabilities
curl http://127.0.0.1:3000/v1/inference \
  -H 'Content-Type: application/json' -H 'Idempotency-Key: example-1' \
  -d '{"task":"text.generate","input":{"messages":[{"role":"user","content":"Hello"}]}}'
```

Add stream:true for SSE or a model alias for explicit selection. Automatic
selection uses the configured balanced ranks and stable binding-ID tie breaking.
Discovery reports declarations, not engine readiness. Health reports liveness.
Matching retained JSON requests can replay; conflicts and in-progress duplicates
reject. Memory retention is 60 seconds after outcome and transport settlement;
streams are not replayed. Restart drops memory custody.

The configuration has a closed schema enforced before serving: protocol,
timeoutMs, contextBound {version,inputTokens}, and engines. Each engine declares
id/version/model/remoteModel/url/authentication, optional secretEnv for bearer,
contextLimit/outputLimit/streaming/rank/enabled. Context bounds must be justified
for the complete configured catalog; unknown estimates must not be guessed.

Product frontier: local pattern construction and conformance. Operator-owned
real-engine selection, tokenizer evidence, deployment budgets and activation are
separate operational work. Fixture results establish protocol behavior only.

## Open Questions

- Which actual engine will demonstrate this protocol or need declarative mappings?
- What context bound and performance budgets are justified by that engine/hardware?
- Are private-network or in-process variants needed after this loopback pattern?
- Is an additional stream codec required by a concrete engine contract?

These do not block the reference pattern. Product approval of a tested candidate,
real-model compatibility, deployment and activation remain distinct decisions.
