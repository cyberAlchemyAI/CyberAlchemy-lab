# Multi-entry Alch services

`service-v1` assembles two or more existing `declarative-function-v1` sources
behind one generated Node HTTP dispatcher. The service source remains `.alch`;
each entry names exactly one imported compiled function.

```alch
domain policy-service "Policy service"
profile service-v1
owner policy-owner

import ReadinessFunction from "./readiness.alch"
import ExplanationFunction from "./explanation.alch"

service PolicyService:
  meaning "Expose two compiled policy operations."

entry Readiness:
  function ReadinessFunction

entry Explanation:
  function ExplanationFunction
```

Build it with:

```bash
node dist/cli.js check service.alch
node dist/cli.js ontology service.alch
node dist/cli.js build service.alch --out /absolute/new/service-bundle
```

The generated module exports `invoke(entryId, input, env, io)`,
`createInvoker(entryId, observe)`, `handler(request, env, io)`, and the immutable
route list. Callers must name an entry for direct invocation; the runtime never
selects the first entry implicitly. HTTP dispatch selects the exact declared
method and path, returns 404 when no path exists, and returns 405 when a path
exists under a different method.

Every import must be exposed exactly once. The compiler rejects missing entry
bindings, duplicate entry identities, duplicate method/path pairs, escaped
imports, non-Node targets, and ontology identity collisions before creating the
destination. Each child retains its own schemas, result, status mapping,
authentication environment reference, Craft/DomainSpec lowering, compiler
certificate, and generated manifest.

The service bundle adds a deterministic deployment route manifest, a service
ontology with `exposes` relationships, an assembly trace binding every child
source and manifest digest, and a completion manifest. These are candidate
construction evidence and grant no admission or execution authority.

## Current boundary

This slice assembles the existing authenticated POST function profile. GET,
anonymous entries, streaming responses, route-local media declarations, and
Rust service assembly remain outside `service-v1`; they are owned by the later
ISB-04/ISB-06 work in the inference service plan.

## Open Questions

- Should a later profile allow one function to expose multiple HTTP aliases, or
  keep one route per function identity?
- Which typed zero-body contract should represent GET health and discovery
  entries without inventing an empty request record?
- How should streamed output declare media type, cancellation, and terminal
  event guarantees without weakening the current JSON function boundary?
