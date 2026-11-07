# Implementation result

Status: implemented standalone candidate `cyberalchemy-define 0.3.0rc1`; stable-release qualification remains outstanding. No canonical definitions, native admissions, publication, deployment or default-runtime selection occurred.

## What changed

The new distribution is `implementation/define-cli/standalone`. Its public core accepts exact authored request/capture/member bytes and returns a candidate v3 Pack, preparation report and complete frozen package. There is no Lab repository or runtime dependency in the core. Optional Lab registry capture is an explicit source adapter with historical, reported standing.

Interfaces:

- Python: `from define_core import call`.
- Installed `define-api`: one bounded `define.api/v1` JSON request through stdin EOF, one structured response.
- Installed `define-standalone`: explicit local file workflow.
- Repository launcher: `./define/define-standalone`.

Public operations: capabilities, schema, capture, prepare, inspect, reconstruct, materialize, observe-use. API calls accept logical members, not arbitrary host file paths. The API uses one shared dispatcher and the same deterministic preparation code. Caller-owned services may wrap it for HTTP/MCP; those hosted transports are not implemented here.

## Work map

| ID | Work | State |
| --- | --- | --- |
| D1 | New versioned request/Pack/capture/report and API contracts; mapping byte loader | implemented |
| D2 | Local source capture, exact identified reuse, inert reported standing, retained catalogs | implemented |
| D3 | Shared Python/JSON API and thin local CLI | implemented |
| D4 | Bundled exact Definition schema/generator, provenance, package-relative seal | implemented; wheel and source archive built/reviewed |
| D5 | Optional Lab historical registry snapshot adapter | implemented; native v3 consumer mapping remains separate |
| D6 | Self-contained incident source, Pack inputs, first-use/agent/integration documentation | implemented; instructions not executed |
| D7 | Two-role source review, syntax parsing, archive inclusion and predecessor preservation | completed within source/package-review scope |

## Two-round design changes

See `DISTILL.md` for the full role and technique trace. Round 1 removed hidden registry semantics, filesystem loaders and repository resource lookup from the core. Round 2 made source standing explicitly unverified, pinned bundled resources, separated historical Lab capture from current authority and kept the public protocol independent of a network daemon.

The source review additionally corrected file/directory collisions, external parameter-contract generation, mismatched application consumer/use, malformed scalar and nested references, parameter-schema error handling, result-envelope import failures and collection bounds. Both independent reviewers reported no remaining concrete blocker in their final static scope. No behavioral conclusion is inferred from that review.

## Packaging and source evidence

`package-review.json` records exact hashes and checks. Actual operations performed:

- Parsed **20 Python source files** for syntax.
- Explicitly generated seven public schemas and a **27-member package-relative source/resource seal**.
- Built a wheel and source archive with standard Python packaging tooling, without installing dependencies or changing the environment.
- Opened both archives and compared every sealed member against its selected source digest.
- Inspected console-entrypoint metadata and the declared `jsonschema` dependency.
- Checked exact preservation of **552 v1 members**, **29 v2 runtime members**, and **74 members of the previous v2 review envelope**. All were unchanged.
- Read-only source/dependency review found the sole Lab registry path in the explicit `adapters/lab.py` translation. Bundled resource provenance names original repository sources but does not read them at runtime.

Distribution artifacts are in `dist/`. Building and inspecting an archive does not demonstrate successful installation or runtime behavior.

## Remaining qualification

No unit, installation, adversarial, roundtrip or behavioral tests were added or run for this change. Required before claiming stable standalone release:

1. Install the wheel in a fresh isolated environment outside the Lab checkout and complete the local workflow with no Lab path available.
2. Exercise Python and JSON API parity, exact reconstruction, revision lineage, empty-source proposals, local/external parameter contracts and reported-assessment preservation.
3. Exercise malformed versions/JSON/UTF-8/base64, missing/changed members, bounds, path collisions, standing/permission promotion and drift refusal.
4. Exercise explicit materialization and observation with matching, changed and absent current evidence.
5. Confirm interrupted/new-output publication behavior on supported Linux filesystems and document platform outcomes.

These are the next qualification tasks, not claimed completed checks. Hosted HTTP/MCP deployment and current native Lab v3 admission/review/publication are separate integration scopes. A v3 Pack is not compatible with the native v2 owner route merely because the outer byte-package manifest is unchanged.

## Claim ceiling

Implementation and source/package review only. Source integrity is drift detection under a trusted interpreter/bootstrap/dependency environment, not release authentication. Exact content reuse is not semantic acceptance. Mechanical parameter binding is not domain assessment. Reported Lab registry status is not current standing. Reconstructed evidence is not permission. The existing v1/v2 runtime and review artifacts remain untouched.
