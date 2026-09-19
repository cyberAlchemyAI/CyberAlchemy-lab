# ARE Coding-Agent Runtime L2 Vertical

This package carries the D65 candidate chain for one fixture-only,
model-driven coding-agent turn and its controlled live gateway canary. It is owned by the existing Agent Reasoning
Engine Project and binds the research hypothesis to a Product Capability,
capability-local business ontology, DomainSpec v2 authored source,
deterministic generated views, exact implementation bytes, and bounded
conformance evidence.

The implementation builds a deterministic prompt from an exact observation
allowlist and obtains final bytes through an injected transport. Scripted
transport is covered by the fixture witness. The Codex App Server adapter can
also be exercised through the persistent ARE gateway, including authenticated
session resumption and stable-request replay across a gateway restart.
The candidate can replace one existing allowlisted fixture file only after
explicit `approve-each`, then uses a separate verifier process. It is not
installed as a production service and makes no general reliability, production
sandbox, network isolation, security, performance, acceptance, or deployment claim.

Build and validate:

```bash
node --import tsx scripts/build.ts
node scripts/validate.mjs
node scripts/validate-l2.mjs
```

`validate.mjs` freezes and evaluates the L2 product candidate without invoking
a live model. `validate-l2.mjs` is the separate, opt-in real Codex App Server
gateway canary against an ephemeral fixture; it may require a host environment
that permits local sockets.
