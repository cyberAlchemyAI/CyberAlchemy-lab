# Requests, results and owned execution

The following is a proposed contract, not an implemented public API. Keep it
separate from the existing finite and E00–E06 schemas.

## Callable boundary

`qualify(request_bytes, resolved_profile, source_store, operator_policy)` creates
one new owned job. `inspect_saved(result_ref, trusted_baseline)` checks recorded
evidence/currentness and never recreates a fresh completion event.

Only the adapter resolves trusted profile/build records. The request names a
fixed profile ID and content-addressed inputs, never executable paths, alternate
catalogs, shell commands or arbitrary environment values. JSON decoding retains
our duplicate-key, Unicode, size and nesting checks.

## Request fields

| Field | Required meaning |
| --- | --- |
| request identity and profile | Fixed schema version, request ID, profile ID and exact profile digest. |
| source selection | Exact definition/interpretation or ontology cut, review references, selected view digest, scope and exclusions. |
| required set | Independently resolved complete obligation/goal/population manifest and exact target statements. |
| source artifacts | SHA-256 and byte length for theory, model, view, rules and export policy as appropriate. |
| resource policy | Explicit deadline, memory mode/amount, output/work limits and cancellation policy. |

An illustrative request is in [examples/model-request.json](examples/model-request.json).
Content references in that example are design placeholders and do not claim
that a runnable request or source artifact has been produced.

## Result fields

| Field | Purpose |
| --- | --- |
| status and completion | Distinguish completed, rejected, stale, malformed, unsupported, cancelled and resource-incomplete. |
| native result | Original backend words, outputs, exit status and artifacts. |
| mathematical evidence | Model witness, checked encoded model, checked derivation, refutation or fresh exact kernel theorem. |
| source/export correspondence | Mapping profile, selected bridge theorem/currentness and per-input correspondence checks. |
| source-meaning status | Pending, reviewed-at-partial-scope or another explicitly evidenced disposition. |
| required-set accounting | Every obligation, evidence kind, exact proposition, strength match and any pending result. |
| runtime binding | Copied source, patches, compiler, imports, binary, policy, request and artifact digests. |
| effects | `authority_effect: none`, `application_authorized: false`; writes only inside the owned build/job scope. |

Never construct strong results by deserializing a backend status string. A
fresh completion token is process-local to the new provider and issued only
after supervision, exact statement inspection and final byte/currentness checks.
Do not reuse the accepted v3 issuer for an unrecognized profile.

The adapter checks the whole required set. A missing proof, incomplete export
or mismatched proposition keeps that obligation unresolved. Partial results
remain useful evidence but cannot produce a complete readiness result.

## Reuse the existing batch interface

The selected engine command is a fixed argv array:

```text
[pinned_engine, --no-connect, --data-dir, owned_job_dir,
 --json, batch, -, --bail]
```

Send a JSON array of allowlisted commands using argument arrays. Loading and
analysis occur in this same process; separate standalone load/preserve commands
would not share its in-memory graph. Representative input is
[examples/preserve-batch.json](examples/preserve-batch.json).

Initial generated commands are load, preserve, closure-diff and plan. No caller
can submit arbitrary batch commands. Later shape/refutation profiles add only
their explicitly reviewed operations. Plan writes candidate metadata only to
the owned SQLite data directory. The adapter never permits apply, rollback,
daemon/server startup, remote imports, push/pull or arbitrary SPARQL mutation.

Use a private environment and exact paths for `OO_CERT`, `OO_HORN` and selected
checker binaries. Conservativity does not expose an explicit checker path in
its options, so its environment discovery must be fixed. Verify complete
binary digests; a same-size executable or a self-reported identity is not enough.
Config resolution must use owned configuration, not the operator's live service
configuration. Bind TMPDIR, TMP and TEMP to the owned job's temporary subtree:
the upstream planner writes certificates below the process temporary directory,
so `--data-dir` alone does not contain its outputs. Include that subtree in
artifact collection and owned cleanup. Permit at most one plan analysis per
job; another analysis gets a fresh job and input/artifact binding.

Batch plan takes the whole target and fixes replacement mode, `owl-rl`,
scan limit 10,000 and render limit 1,000,000. The wrapper either accepts an
exact target or materializes G union delta for an additive request. It cannot
claim an arbitrary caller-selected plan profile or limit was honored.

Parse NDJSON command envelopes, command order, embedded domain statuses,
stop-the-line findings and final process exit separately. In particular, a
successful plan process can still report logical risk or undecided analysis.
SHACL's successful process can report non-conformance. Unknown and parse errors
are not false statements about the source.

## Worker and storage boundary

Copy/adapt the existing supervision implementation into a reviewed new owner
root. Include strict policy validation, process-group ownership, deadline/output
limits, cancellation and owned teardown. Required memory enforcement without a
supported host backend is refused; advisory observation stays advisory.
This design does not claim a new filesystem sandbox or a filesystem theorem.
Same-privilege host tampering and compiler/runtime behavior remain named trust
assumptions, as in the existing evidence system.

Each agent gets its own captured input, job directory and local engine state.
An older agent view stays readable while other jobs use newer versions. Keep
review information in the complete view digest: a meaning cursor alone does
not freeze later governance observations.

Publish candidate evidence with create-only/no-follow ownership checks and
final source rehashing. A cache key includes source, profile, mapping, rules,
compiler/import closure and request content. Cache inspection may reuse compiled
dependencies; it cannot manufacture a fresh proof event from saved JSON.
