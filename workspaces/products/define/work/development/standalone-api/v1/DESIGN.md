# Standalone Define and public integration API

Status: revised design after two Distill rounds; implementation follows this revision. No admission or publication.

## Objective

An agent, script or application can prepare, inspect, export and reconstruct a Definition Pack without installing or running CyberAlchemy Lab. A separate explicit adapter supplies Lab snapshots and their historical standing. Task values, applications and reported assessments remain embedded in the Pack.

## Initial design

A portable Python distribution exposes a versioned JSON request/response API and a Python entrypoint over the same deterministic kernel. CLI file IO is a thin local wrapper. JSON callers supply original bytes as base64 members, not server filesystem paths. Operations: capabilities, schema, capture, prepare, inspect, reconstruct, materialize, observe-use. Pure operations return bytes and records; only the CLI writes a new destination.

Package schemas and generator are included as immutable, versioned resources. A package-relative integrity manifest replaces repository-relative selection. Existing v1/v2 and their evidence remain immutable; the portable successor uses new request, capture and Pack versions where reuse semantics change.

Local catalogs identify exact sources and optionally report standing. Local reuse verifies identity/revision/content and reports unverified standing. It cannot confer Lab admission, qualified execution, current permission or owner outcomes. Lab-specific registry verification lives in an explicit optional adapter; no arbitrary adapter loading from requests.

## Planned sequence

1. Inspect source dependencies and standard API/packaging practices.
2. Distill round 1: proposer and independent balancer identify hidden coupling and unsafe abstractions.
3. Distill round 2: refine versioning, transport, standing and resource boundaries; reconcile before edits.
4. Implement portable package, bundled contracts, exact-byte API and thin CLI.
5. Implement explicit Lab snapshot adapter and self-contained incident example.
6. Review changed source and distribution contents, document compatibility and remaining release qualification.

## Research

- Python Packaging User Guide: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/ (project scripts, build metadata, optional dependencies).
- JSON-RPC 2.0: https://www.jsonrpc.org/specification (transport-independent calls and structured errors). The initial API will use its own explicitly versioned one-shot envelope, not claim JSON-RPC compatibility.

## Scope

No hosted HTTP service, auth server, plugin discovery, model inference, credential provisioning, automatic owner review or remote publication. Future HTTP/MCP adapters call the same public API and own authentication, per-caller storage, timeout/retry policy and deployment. A base64 bundle is bounded; streaming becomes a separate versioned transport when actual volume requires it.

## Revised model

```text
Agent / application / trusted CLI
             | versioned JSON or Python API
             v
     request bytes + captured logical members
             | deterministic portable kernel
             v
     candidate Pack + report + exact package
             | caller-owned storage / external review
             v
     optional Lab adapter and native owner routes
```

- Distribution: `implementation/define-cli/standalone`, Python package `define_core`, version `0.3.0rc1`. Python 3.11+, Linux local publication initially. Wheel and source metadata include required contracts, generator, schemas and package-relative seal. Existing v1/v2 remain byte-for-byte unchanged.
- Contracts: prepare-request/v3, pack/v3, capture-bundle/v2, preparation-report/v3. No implicit migration of v2 reuse or admission semantics. Package manifest/v1 remains an exact-byte container, not a semantic version translator.
- Public protocol: `define.api/v1`, exactly one request per process. Required `api_version`, `id`, `operation`, `params`; bounded string correlation IDs. Fixed `capabilities`, `schema`, `capture`, `prepare`, `inspect`, `reconstruct`, `materialize`, `observe-use` operations. Same dispatcher in Python. Return fixed outcomes, non-sensitive diagnostics and `authority_effect: none`.
- JSON callers supply exact request/capture UTF-8 strings and logical-path-to-canonical-base64 members. No filesystem paths, URL fetches, provider entrypoints, output destinations or process execution are available in this protocol. Aggregate bytes, encoded frame, member count, per-member bytes and canonical paths are bounded before use.
- Source catalog: exact input IDs, file bindings and nullable reported standing. Default catalog covers the explicitly selected request bindings; empty catalog supports wholly embedded meanings. Core capture is local-snapshot with local-files source cut. All rows are local-reference, never admitted-current or host-member. Reusing a meaning verifies bytes, selected identity and revision; an explicit unverified-standing gap remains.
- Lab adapter: trusted explicit CLI/Python local operation reads the supplied repository root and verifies selected registry entries, current lookup, identity, revision, digest, carrier and admission reference. It emits historical reported standing plus retained registry evidence into the same local capture contract. Core does not authenticate those claims or import the adapter. Original v2 Lab semantics are preserved in the original entrypoint.
- Definitions are authored inputs. The deterministic core assembles/checks them; it does not infer meanings, generate model output, run domain assessments or grant permission. A future agent can author input using advertised schemas.
- Materialization: only the bundled exact Definition/v2 carrier and deterministic generator, recorded with origin digests. No user-selected executable. Candidate output still requires semantic fidelity, compatibility and owner review.
- Later-use observation receives an explicit current source-profile byte string or records freshness not established. Frozen package integrity, input freshness and operational authorization remain separate. Missing current evidence never becomes permission.
- Optional connector interface is the request/capture/package contract, not an executable plugin loader. HTTP/MCP services can wrap the API later; they must own principal isolation, retention permission, timeouts, authentication and retry semantics. This change does not implement those transports.

## Compatibility

V3 changes local reuse semantics deliberately. A v3 Pack cannot be sent unchanged to a v2 Lab review route. A connector must explicitly map the carrier and establish actual Lab standing, compatibility, owner scope and permission before any effects. Packaging provenance is drift detection, not publisher authentication. Research terminology here does not add or admit canonical Lab definitions.

## Implementation work map

| Step | Deliverable | Completion evidence |
| --- | --- | --- |
| D1 | Portable contracts and byte loader | No repository path in core, closed new schemas |
| D2 | Local capture and exact reuse | Source catalog and standing gaps preserved |
| D3 | Shared public API and CLI | One dispatcher, no API filesystem access |
| D4 | Portable carrier/resources/seal | Package data and source provenance |
| D5 | Explicit Lab snapshot adapter | Registry evidence preserved as historical reported standing |
| D6 | Incident example and integration guide | Complete first-use inputs, agent and application examples |
| D7 | Source/package review | Report actual checks and unperformed qualification separately |

## Qualification boundary

This request authorizes design, critique and implementation. No new tests or test runs are included without a user request to test/verify. Building the wheel and reviewing its contents are packaging work, not proof of an installed runtime or a qualified release. Standalone runtime qualification and real Lab connector qualification are separate remaining claims.
